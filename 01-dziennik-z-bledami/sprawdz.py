#!/usr/bin/env python3
"""Strażnik ćwiczenia 01 „Dziennik z błędami”.

  python3 sprawdz.py                  sprawdź dziennik.py
  python3 sprawdz.py --plusy          sprawdź też oceny z plusami i minusami (zadanie dla chętnych)
  python3 sprawdz.py --przywroc-dane  przywróć oryginalne pliki w dane/, jeśli coś w nich zmienisz

Strażnik uruchamia dziennik.py trzy razy: w tym folderze, z innego katalogu i na innym, wygenerowanym
dzienniku (żeby sprawdzić, czy program naprawdę liczy z danych).
"""
import csv
import io
import random
import re
import sys
import tempfile
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path

CWICZENIE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(CWICZENIE.parent / "materialy"))
import straznik  # noqa: E402

PROGRAM = CWICZENIE / "dziennik.py"
DANE = CWICZENIE / "dane" / "oceny.csv"
DANE_PLUSY = CWICZENIE / "dane" / "oceny-plusy.csv"
LIMIT = 20

UCZNIOWIE = ["Adamczyk Oliwia", "Banaś Kacper", "Czarnecka Maja", "Dudek Szymon", "Górska Lena",
             "Jasiński Filip", "Kowalczyk Zofia", "Nowicki Antoni", "Pawlak Hanna", "Wróbel Igor"]
PRZEDMIOTY = ["matematyka", "fizyka", "informatyka", "język angielski"]
NAGLOWEK = "uczen;przedmiot;ocena;data"
NAGLOWEK_SREDNIE = ["uczen", "przedmiot", "srednia", "liczba_ocen"]
NAGLOWEK_ODRZUCONE = ["wiersz", "powod", "tresc"]
ZIARNO_DANYCH = 310        # dane/oceny.csv
ZIARNO_PLUSOW = 311        # dane/oceny-plusy.csv
ZIARNO_KONTROLNE = 404     # inny dziennik: czy program liczy z danych, a nie wypisuje gotowych wyników

RODZAJE = ["nb", "poza_skala", "malo_pol", "pusta", "przecinki", "naglowek", "slowo", "duzo_pol", "zero", "ulamek"]
RODZAJE_PLUSOW = ["szesc_plus", "jeden_minus", "sam_plus"]
POWODY = {
    "nb": "ocena to nie liczba",
    "poza_skala": "ocena spoza skali 1-6",
    "zero": "ocena spoza skali 1-6",
    "slowo": "ocena zapisana słowem, a nie liczbą",
    "ulamek": "ocena nie jest liczbą całkowitą",
    "pusta": "ocena jest pusta",
    "malo_pol": "wiersz ma 3 pola zamiast 4 (csv.DictReader wpisuje brakującym polom None)",
    "duzo_pol": "wiersz ma 5 pól zamiast 4 (csv.DictReader odkłada nadmiarowe pola na listę pod kluczem None)",
    "przecinki": "pola są oddzielone przecinkami, więc csv.DictReader widzi jedno pole zamiast 4",
    "naglowek": "to powtórzony nagłówek, a nie ocena",
    "szesc_plus": "6+ jest ponad skalą",
    "jeden_minus": "1- jest poniżej skali",
    "sam_plus": "sam plus bez cyfry to nie ocena",
}


# --- generator dzienników -----------------------------------------------------------------------
class Dziennik:
    """Wygenerowany plik ocen i to, co program powinien z niego policzyć."""

    def __init__(self, linie, odrzucone, oceny):
        self.linie = linie                  # linie pliku; linie[0] to nagłówek (linia 1)
        self.odrzucone = odrzucone          # {numer linii: rodzaj uszkodzenia}
        self.oceny = oceny                  # {(uczen, przedmiot): [wartości poprawnych ocen]}
        self.tekst = "\n".join(linie) + "\n"

    @property
    def liczba_ocen(self):
        return sum(len(v) for v in self.oceny.values())


def _dni_szkolne():
    dzien, dni = date(2026, 9, 1), []
    while dzien <= date(2026, 10, 30):
        if dzien.weekday() < 5 and dzien != date(2026, 10, 14):
            dni.append(dzien.isoformat())
        dzien += timedelta(days=1)
    return dni


def _zly_wiersz(rodzaj, u, p, d, los, oryginal):
    def wybierz(pierwsza, *inne):
        return pierwsza if oryginal else los.choice([pierwsza, *inne])
    o = los.randint(1, 6)
    return {
        "nb": f"{u};{p};{wybierz('nb', 'np', 'zw')};{d}",
        "poza_skala": f"{u};{p};{wybierz('7', '8', '10')};{d}",
        "zero": f"{u};{p};{wybierz('0', '-1')};{d}",
        "slowo": f"{u};{p};{wybierz('piątka', 'dobry', 'celujący')};{d}",
        "ulamek": f"{u};{p};{wybierz('4,5', '3,5', '2.5')};{d}",
        "pusta": f"{u};{p};;{d}",
        "malo_pol": f"{u};{p};{o}",
        "duzo_pol": f"{u};{p};{o};{d};{wybierz('poprawa', 'kartkówka')}",
        "przecinki": f"{u},{p},{o},{d}",
        "naglowek": NAGLOWEK,
        "szesc_plus": f"{u};{p};6+;{d}",
        "jeden_minus": f"{u};{p};1-;{d}",
        "sam_plus": f"{u};{p};+;{d}",
    }[rodzaj]


def generuj(ziarno, plusy=False, oryginal=True):
    """Buduje dziennik ocen; ten sam numer ziarna daje zawsze ten sam plik."""
    los = random.Random(ziarno)
    dni = _dni_szkolne()
    uczniowie = list(UCZNIOWIE) if oryginal else sorted(los.sample(UCZNIOWIE, 8))
    poziom = {u: los.choice([2, 3, 3, 4, 4, 5]) for u in uczniowie}
    dobre = []
    for u in uczniowie:
        for p in PRZEDMIOTY:
            for _ in range(los.choice([1, 2, 2])):
                ocena = min(6, max(1, poziom[u] + los.choice([-1, 0, 0, 1, 1, 2])))
                tekst, wartosc = str(ocena), Fraction(ocena)
                if plusy and los.random() < 0.35:
                    if ocena == 1 or (ocena < 6 and los.random() < 0.5):
                        tekst, wartosc = f"{ocena}+", ocena + Fraction(1, 2)
                    else:
                        tekst, wartosc = f"{ocena}-", ocena - Fraction(1, 4)
                dobre.append([los.choice(dni), u, p, tekst, wartosc])
    los.shuffle(dobre)
    dobre.sort(key=lambda w: w[0])
    for wiersz in los.sample(dobre, 2):                 # spacje wokół oceny są dozwolone
        wiersz[3] = los.choice([f" {wiersz[3]}", f"{wiersz[3]} ", f" {wiersz[3]} "])

    rodzaje = list(RODZAJE)
    if not oryginal:
        los.shuffle(rodzaje)
    if plusy:
        for rodzaj in RODZAJE_PLUSOW:
            rodzaje.insert(los.randint(1, len(rodzaje)), rodzaj)
    miejsca = sorted(los.sample(range(3, len(dobre)), len(rodzaje)))
    zle = {}
    for miejsce, rodzaj in zip(miejsca, rodzaje):
        zle[miejsce] = (rodzaj, _zly_wiersz(rodzaj, los.choice(uczniowie), los.choice(PRZEDMIOTY),
                                            dobre[miejsce - 1][0], los, oryginal))
    tresc = []                                           # (tekst linii, rodzaj uszkodzenia albo None)
    for i, (d, u, p, tekst, _) in enumerate(dobre):
        if i in zle:
            tresc.append((zle[i][1], zle[i][0]))
        tresc.append((f"{u};{p};{tekst};{d}", None))
    for miejsce in sorted(los.sample(range(4, len(tresc), 3), 2), reverse=True):
        tresc.insert(miejsce, ("", None))                # puste linie: pomijane bez zgłaszania

    linie = [NAGLOWEK] + [t for t, _ in tresc]
    odrzucone = {nr: rodzaj for nr, (_, rodzaj) in enumerate(tresc, start=2) if rodzaj}
    oceny = {}
    for _, u, p, _, wartosc in dobre:
        oceny.setdefault((u, p), []).append(wartosc)
    return Dziennik(linie, odrzucone, oceny)


# --- odczyt wyników ucznia ----------------------------------------------------------------------
def wczytaj_wynik(sciezka, naglowek, nazwa, wyglada_na_dane):
    """(wiersze bez nagłówka, braki); wiersze = None, gdy pliku nie da się sprawdzić."""
    if not sciezka.is_file():
        return None, [f"nie ma pliku {nazwa}"]
    try:
        tekst = sciezka.read_text(encoding="utf-8").lstrip("﻿")
    except UnicodeDecodeError:
        return None, [f'{nazwa} nie jest zapisany w UTF-8 - dodaj encoding="utf-8" w open(..., "w")']
    if not tekst.strip():
        return None, [f"{nazwa} jest pusty"]
    pierwsza = tekst.splitlines()[0]
    if ";" not in pierwsza and ("," in pierwsza or "\t" in pierwsza):
        return None, [f"{nazwa}: kolumny mają być oddzielone średnikiem, jak w pliku z ocenami - "
                      'csv.writer(plik, delimiter=";")']
    wiersze = [w for w in csv.reader(io.StringIO(tekst), delimiter=";") if any(p.strip() for p in w)]
    gora = [p.strip() for p in wiersze[0]]
    if gora != naglowek:
        if wyglada_na_dane(gora):
            return None, [f"{nazwa}: w pierwszej linii brakuje nagłówka {';'.join(naglowek)}"]
        return None, [f"{nazwa}: pierwsza linia to {';'.join(gora)}, a ma być nagłówek {';'.join(naglowek)}"]
    return wiersze[1:], []


def sprawdz_srednie(katalog, dz):
    nazwa = "wyniki/srednie.csv"
    wiersze, braki = wczytaj_wynik(katalog / "wyniki" / "srednie.csv", NAGLOWEK_SREDNIE, nazwa,
                                   lambda g: bool(g) and g[0] in UCZNIOWIE)
    if wiersze is None:
        return braki
    wynik, kolejnosc, zly_format = {}, [], None
    for nr, w in enumerate(wiersze, start=2):
        if len(w) != 4:
            braki.append(f"{nazwa}, linia {nr}: {len(w)} pól zamiast 4 ({';'.join(w)})")
            continue
        uczen, przedmiot, srednia, liczba = (p.strip() for p in w)
        if zly_format is None and not re.fullmatch(r"-?\d+[.,]\d{2}", srednia):
            zly_format = f"{srednia} w linii {nr}"
        try:
            wartosc = float(srednia.replace(",", "."))
            ile = int(liczba)
        except ValueError:
            braki.append(f"{nazwa}, linia {nr}: średnia i liczba ocen mają być liczbami, a są: {srednia}, {liczba}")
            continue
        if (uczen, przedmiot) in wynik:
            braki.append(f"{nazwa}: para {uczen} / {przedmiot} występuje więcej niż raz")
        wynik[(uczen, przedmiot)] = (wartosc, ile)
        kolejnosc.append((uczen, przedmiot))
    if zly_format:
        braki.append("średnia ma mieć dokładnie 2 miejsca po przecinku, np. 4.50 albo 3.67 "
                     f"(jest: {zly_format}) - f\"{{srednia:.2f}}\"")
    oczekiwane = {k: (float(sum(v) / len(v)), len(v)) for k, v in dz.oceny.items()}
    brak = [f"{u} / {p}" for (u, p) in oczekiwane if (u, p) not in wynik]
    nadmiar = [f"{u} / {p}" for (u, p) in wynik if (u, p) not in oczekiwane]
    if brak:
        braki.append(f"brakuje średnich ({len(brak)}): {straznik.skrot_listy(brak, 4)} - każdy uczeń ma mieć "
                     "wiersz z każdego przedmiotu, z którego ma choć jedną poprawną ocenę")
    if nadmiar:
        braki.append(f"średnie, których nie powinno być: {straznik.skrot_listy(nadmiar, 4)} - pochodzą "
                     "z uszkodzonego wiersza (np. powtórzonego nagłówka albo wiersza z przecinkami)")
    za_malo, za_duzo, zla_srednia = [], [], []
    for k, (srednia, ile) in oczekiwane.items():
        if k not in wynik:
            continue
        if wynik[k][1] < ile:
            za_malo.append(f"{k[0]} / {k[1]}: {wynik[k][1]} zamiast {ile}")
        elif wynik[k][1] > ile:
            za_duzo.append(f"{k[0]} / {k[1]}: {wynik[k][1]} zamiast {ile}")
        elif abs(wynik[k][0] - srednia) > 0.01:
            zla_srednia.append(f"{k[0]} / {k[1]} ({wynik[k][0]:.2f})")
    if za_malo:
        braki.append(f"za mało ocen w liczba_ocen: {straznik.skrot_listy(za_malo, 3)} - czy nie odrzucasz "
                     "poprawnych wierszy, np. ze spacją wokół oceny?")
    if za_duzo:
        braki.append(f"za dużo ocen w liczba_ocen: {straznik.skrot_listy(za_duzo, 3)} - czy nie liczysz "
                     "ocen z wierszy, które powinny trafić do odrzuconych?")
    if zla_srednia:
        braki.append(f"zła średnia: {straznik.skrot_listy(zla_srednia, 3)} - liczba ocen się zgadza, "
                     "więc sprawdź samo liczenie: suma ocen / liczba ocen")
    if not braki and kolejnosc != sorted(kolejnosc):
        braki.append(f"{nazwa}: wiersze mają być posortowane po uczniu, a potem po przedmiocie "
                     "(sorted() na kluczach (uczen, przedmiot))")
    return braki


def _opis_linii(dz, nr):
    return dz.linie[nr - 1] if 1 <= nr <= len(dz.linie) else None


def sprawdz_odrzucone(katalog, dz, plusy=False):
    nazwa = "wyniki/odrzucone.csv"
    wiersze, braki = wczytaj_wynik(katalog / "wyniki" / "odrzucone.csv", NAGLOWEK_ODRZUCONE, nazwa,
                                   lambda g: bool(g) and g[0].isdigit())
    if wiersze is None:
        return braki
    numery, bez_powodu = [], []
    for nr, w in enumerate(wiersze, start=2):
        if not w[0].strip().isdigit():
            braki.append(f"{nazwa}, linia {nr}: w kolumnie wiersz ma być numer linii z pliku z ocenami, "
                         f"a jest: {w[0]}")
            continue
        numery.append(int(w[0]))
        if len(w) < 2 or not w[1].strip():
            bez_powodu.append(w[0].strip())
    if braki:
        return braki
    zbior, oczekiwane = set(numery), set(dz.odrzucone)
    if len(zbior) != len(numery):
        braki.append(f"{nazwa}: ten sam wiersz zgłoszony kilka razy")
    if zbior != oczekiwane:
        bez_pustych, licznik = {}, 1
        for nr, linia in enumerate(dz.linie[1:], start=2):
            if linia.strip():
                licznik += 1
                bez_pustych[nr] = licznik
        przesuniecie = next((d for d in (-2, -1, 1, 2) if {n + d for n in oczekiwane} == zbior), None)
        if przesuniecie:
            braki.append(f"numery wierszy są przesunięte o {przesuniecie}: numer to linia w pliku z ocenami, "
                         "nagłówek to linia 1, pierwsza ocena - linia 2. Najprościej: czytnik.line_num "
                         "zaraz po odczytaniu wiersza")
            return braki
        for d in (0, -1):
            if {bez_pustych[n] + d for n in oczekiwane} == zbior:
                braki.append("numeracja rozjeżdża się po pustej linii: liczysz wiersze (np. enumerate), "
                             "a puste linie też są liniami pliku. Użyj czytnik.line_num")
                return braki
        brakujace = sorted(oczekiwane - zbior)
        nadmiarowe = sorted(zbior - oczekiwane)
        for nr in brakujace[:6]:
            braki.append(f"wiersz {nr} ({_opis_linii(dz, nr)}) przeszedł, a powinien trafić do odrzuconych: "
                         f"{POWODY[dz.odrzucone[nr]]}")
        if len(brakujace) > 6:
            braki.append(f"... i jeszcze {len(brakujace) - 6} takich wierszy")
        plusiki = [nr for nr in nadmiarowe if (_opis_linii(dz, nr) or "").count(";") == 3
                   and re.search(r"\d\s*[+-]\s*$", _opis_linii(dz, nr).split(";")[2])]
        if plusy and len(plusiki) >= 3:
            braki.append(f"zamien_na_ocene nie rozumie jeszcze plusów i minusów: odrzucono {len(plusiki)} "
                         f"poprawnych ocen, np. wiersz {plusiki[0]} ({_opis_linii(dz, plusiki[0])})")
            nadmiarowe = [nr for nr in nadmiarowe if nr not in plusiki]
        for nr in nadmiarowe[:6]:
            linia = _opis_linii(dz, nr)
            if linia is None:
                braki.append(f"w odrzuconych jest wiersz {nr}, a plik z ocenami ma tylko {len(dz.linie)} linii")
            elif nr == 1:
                braki.append("linia 1 to nagłówek - DictReader czyta go sam, nie zgłaszaj go jako błędu")
            elif not linia.strip():
                braki.append(f"linia {nr} jest pusta - puste linie pomijamy bez zgłaszania "
                             "(DictReader robi to sam)")
            else:
                dopisek = ""
                pola = linia.split(";")
                if len(pola) == 4 and pola[2] != pola[2].strip():
                    dopisek = " - spacje wokół oceny są dozwolone (strip())"
                braki.append(f"wiersz {nr} ({linia}) jest poprawny, a trafił do odrzuconych{dopisek}")
        if len(nadmiarowe) > 6:
            braki.append(f"... i jeszcze {len(nadmiarowe) - 6} poprawnych wierszy w odrzuconych")
    if not braki and bez_powodu:
        braki.append(f"{nazwa}: pusty powód w wierszach {straznik.skrot_listy(bez_powodu)} - wpisz tam "
                     "komunikat z ValueError (str(blad))")
    return braki


# --- uruchomienia -------------------------------------------------------------------------------
def przygotuj_kopie(baza, dz):
    """Kopia dziennik.py z podanym plikiem ocen w katalogu tymczasowym; zwraca katalog kopii."""
    katalog = baza / "cwiczenie"
    (katalog / "dane").mkdir(parents=True)
    (katalog / "dziennik.py").write_bytes(PROGRAM.read_bytes())
    (katalog / "dane" / "oceny.csv").write_text(dz.tekst, encoding="utf-8")
    return katalog


def opis_awarii(wynik, katalog):
    opis = straznik.opisz_przebieg(wynik, katalog, LIMIT)
    if opis and "invalid literal for int()" in opis:
        opis += ("\nTo spodziewane po kroku 1: zapisz numer linii pliku i nazwę wyjątku, a potem zrób krok 2 "
                 "(zamien_na_ocene i try/except).")
    return opis


def podsumowanie_w_konsoli(wynik, dz):
    liczby = re.findall(r"\d+", wynik.out)
    if str(dz.liczba_ocen) in liczby and str(len(dz.odrzucone)) in liczby:
        return []
    return [f"w konsoli brakuje podsumowania z liczbą wczytanych ocen ({dz.liczba_ocen}) "
            f"i odrzuconych wierszy ({len(dz.odrzucone)})"]


def etap_w_folderze(raport, oryginal):
    for plik in ("srednie.csv", "odrzucone.csv"):
        (CWICZENIE / "wyniki" / plik).unlink(missing_ok=True)
    wynik = straznik.uruchom([sys.executable, PROGRAM], CWICZENIE, limit=LIMIT)
    awaria = opis_awarii(wynik, CWICZENIE)
    if awaria:
        raport.popraw("python3 dziennik.py w folderze ćwiczenia", [awaria])
        return False
    wyniki = CWICZENIE / "wyniki"
    if not (wyniki / "srednie.csv").exists() and not (wyniki / "odrzucone.csv").exists():
        raport.popraw("python3 dziennik.py w folderze ćwiczenia",
                      ["program skończył się bez błędu, ale nie zapisał wyników w wyniki/. Zacznij od kroku 1 "
                       "(wczytaj_oceny i policz_srednie), zapis plików to krok 3"])
        return False
    raport.ok(f"python3 dziennik.py działa (poprawnych ocen: {oryginal.liczba_ocen}, wierszy do poprawy: "
              f"{len(oryginal.odrzucone)})")
    dobrze = raport.etap(f"wyniki/srednie.csv (średnich: {len(oryginal.oceny)})",
                         sprawdz_srednie(CWICZENIE, oryginal))
    dobrze &= raport.etap(f"wyniki/odrzucone.csv (wierszy z powodem: {len(oryginal.odrzucone)})",
                          sprawdz_odrzucone(CWICZENIE, oryginal))
    if dobrze:
        dobrze = raport.etap("podsumowanie w konsoli", podsumowanie_w_konsoli(wynik, oryginal))
    return dobrze


def etap_inny_katalog(raport, oryginal):
    opis = "uruchomienie z innego katalogu (cd ~ && python3 .../dziennik.py)"
    with tempfile.TemporaryDirectory(prefix="straznik-01-") as tmp:
        katalog = przygotuj_kopie(Path(tmp), oryginal)
        inny = Path(tmp) / "inny-katalog"
        inny.mkdir()
        wynik = straznik.uruchom([sys.executable, katalog / "dziennik.py"], inny, limit=LIMIT)
        braki = []
        awaria = straznik.opisz_przebieg(wynik, katalog, LIMIT)
        if awaria:
            braki.append(awaria)
        if (inny / "wyniki").exists() or any(inny.glob("*.csv")):
            braki.append("wyniki trafiły do katalogu, z którego uruchomiono program, a nie obok dziennik.py")
        if braki:
            braki.append("Ścieżka względna, np. \"dane/oceny.csv\", liczy się od katalogu, w którym stoisz "
                         "w terminalu. Buduj ścieżki od pliku programu: Path(__file__).parent / \"dane\" / "
                         "\"oceny.csv\" - tak jak stałe DANE, SREDNIE i ODRZUCONE na górze dziennik.py")
            raport.popraw(opis, braki)
            return False
        braki = sprawdz_srednie(katalog, oryginal) + sprawdz_odrzucone(katalog, oryginal)
        return raport.etap(opis, braki)


def etap_inny_dziennik(raport, oryginal):
    inny_dz = generuj(ZIARNO_KONTROLNE, oryginal=False)
    opis = (f"inny dziennik (uczniów: {len({u for u, _ in inny_dz.oceny})}, linii: {len(inny_dz.linie)}, "
            f"uszkodzonych: {len(inny_dz.odrzucone)}) - program liczy z danych, a nie z pamięci")
    with tempfile.TemporaryDirectory(prefix="straznik-01-") as tmp:
        katalog = przygotuj_kopie(Path(tmp), inny_dz)
        wynik = straznik.uruchom([sys.executable, katalog / "dziennik.py"], katalog, limit=LIMIT)
        awaria = straznik.opisz_przebieg(wynik, katalog, LIMIT)
        if awaria:
            raport.popraw(opis, [awaria])
            return False
        braki = sprawdz_srednie(katalog, inny_dz) + sprawdz_odrzucone(katalog, inny_dz)
        if braki and not (sprawdz_srednie(katalog, oryginal) + sprawdz_odrzucone(katalog, oryginal)):
            braki = ["program zapisał wyniki oryginalnego dziennika, chociaż dostał inny plik - wyniki "
                     "wpisane na sztywno? Program ma je liczyć z danych"]
        return raport.etap(opis, braki[:8])


def etap_plusy(raport):
    dz = generuj(ZIARNO_PLUSOW, plusy=True)
    opis = "oceny z plusami i minusami (dane/oceny-plusy.csv)"
    with tempfile.TemporaryDirectory(prefix="straznik-01-") as tmp:
        katalog = przygotuj_kopie(Path(tmp), dz)
        wynik = straznik.uruchom([sys.executable, katalog / "dziennik.py"], katalog, limit=LIMIT)
        awaria = straznik.opisz_przebieg(wynik, katalog, LIMIT)
        if awaria:
            raport.popraw(opis, [awaria])
            return False
        braki = sprawdz_odrzucone(katalog, dz, plusy=True)
        if not any(b.startswith("zamien_na_ocene nie rozumie") for b in braki):
            braki = sprawdz_srednie(katalog, dz) + braki
        return raport.etap(opis, braki[:8])


def przywroc_dane():
    DANE.parent.mkdir(exist_ok=True)
    DANE.write_text(generuj(ZIARNO_DANYCH).tekst, encoding="utf-8")
    DANE_PLUSY.write_text(generuj(ZIARNO_PLUSOW, plusy=True).tekst, encoding="utf-8")
    print("Przywrócono oryginalne pliki: dane/oceny.csv i dane/oceny-plusy.csv.")
    return 0


def main():
    if "--przywroc-dane" in sys.argv[1:]:
        return przywroc_dane()
    plusy = "--plusy" in sys.argv[1:]
    raport = straznik.Raport("STRAŻNIK DZIENNIKA (ćwiczenie 01)")
    if not PROGRAM.is_file():
        raport.popraw("dziennik.py", ["nie ma pliku dziennik.py w folderze ćwiczenia (przywróć go: "
                                      "git checkout -- dziennik.py)"])
        return raport.koniec("")
    skladnia = straznik.blad_skladni(PROGRAM)
    if skladnia:
        raport.popraw("dziennik.py", [skladnia])
        return raport.koniec("")
    oryginal = generuj(ZIARNO_DANYCH)
    try:
        dane = DANE.read_text(encoding="utf-8").replace("\r\n", "\n")
    except (OSError, UnicodeDecodeError):
        dane = None
    if dane != oryginal.tekst:
        raport.popraw("dane/oceny.csv", ["plik z ocenami różni się od oryginału albo go nie ma - strażnik "
                                         "sprawdza wyniki dla oryginału. Przywróć go: "
                                         "python3 sprawdz.py --przywroc-dane"])
        return raport.koniec("")

    dobrze = etap_w_folderze(raport, oryginal)
    if dobrze:
        dobrze = etap_inny_katalog(raport, oryginal)
    else:
        raport.czeka("uruchomienie z innego katalogu (sprawdzę, gdy wyniki w folderze będą dobre)")
    if dobrze:
        dobrze = etap_inny_dziennik(raport, oryginal)
    else:
        raport.czeka("inny dziennik (sprawdzę, gdy poprzednie punkty będą zaliczone)")
    if plusy:
        if dobrze:
            etap_plusy(raport)
        else:
            raport.czeka("oceny z plusami i minusami (najpierw zadanie główne)")
    for uwaga in straznik.uwagi_o_plikach(PROGRAM, newline=True):
        raport.uwaga(uwaga)
    sukces = (f"Pani Lis drukuje zestawienie: {len(oryginal.oceny)} średnich trafia na jutrzejszą radę "
              f"klasyfikacyjną, a {len(oryginal.odrzucone)} uszkodzonych wierszy - do sekretariatu do ręcznej "
              "poprawy. Eksport po awarii uratowany.")
    if plusy:
        sukces += " Plusy i minusy też się liczą."
    else:
        sukces += " Dla chętnych: python3 sprawdz.py --plusy"
    return raport.koniec(sukces)


if __name__ == "__main__":
    sys.exit(main())
