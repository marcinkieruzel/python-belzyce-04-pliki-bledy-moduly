#!/usr/bin/env python3
"""Strażnik ćwiczenia 02 „Quiz na dysku”.

  python3 sprawdz.py

Sprawdza twój plik dane/pytania.json, a potem kopiuje quiz.py do katalogu tymczasowego z własnymi
pytaniami kontrolnymi i gra za ciebie: wpisuje odpowiedzi w kolejności opisanej w README
(„Jak gra strażnik”). Twoje pliki w dane/ zostają nietknięte.
"""
import csv
import io
import json
import re
import sys
import tempfile
from pathlib import Path

CWICZENIE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(CWICZENIE.parent / "materialy"))
import straznik  # noqa: E402

QUIZ = CWICZENIE / "quiz.py"
EKSPORT = CWICZENIE / "eksportuj.py"
PYTANIA_UCZNIA = CWICZENIE / "dane" / "pytania.json"
LIMIT = 10
MIN_PYTAN = 16             # 14 pytań z pytania.py + 2 własne
KLUCZE = ["pytanie", "odpowiedzi", "poprawna", "kategoria"]
NAGLOWEK_WYNIKOW = ["data", "imie", "punkty", "maks"]
DATA = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

# Pytania kontrolne: w każdym poprawna jest odpowiedź nr 1 (indeks 0).
KONTROLNE = [
    {"pytanie": "Pytanie kontrolne strażnika nr 1: ile to 2 + 2?",
     "odpowiedzi": ["4", "5", "22", "0"], "poprawna": 0, "kategoria": "kontrola"},
    {"pytanie": "Pytanie kontrolne strażnika nr 2: ile dni ma tydzień?",
     "odpowiedzi": ["7", "5", "10", "6"], "poprawna": 0, "kategoria": "kontrola"},
    {"pytanie": "Pytanie kontrolne strażnika nr 3: jaki kolor ma śnieg?",
     "odpowiedzi": ["biały", "zielony", "czerwony", "niebieski"], "poprawna": 0, "kategoria": "kontrola"},
]
ZEPSUTY_JSON = """[
  {
    "pytanie": "Pytanie kontrolne strażnika nr 1: ile to 2 + 2?",
    "odpowiedzi": ["4", "5", "22", "0"],
    "poprawna": 0
    "kategoria": "kontrola"
  }
]
"""
# Wejście, które strażnik wpisuje za gracza (README, „Jak gra strażnik”).
GRA_1 = ["1", "Testowy Gracz", "abc", "9", "1", "1", "1", "2", "0"]  # 3/3, dwie złe odpowiedzi, potem ranking
GRA_2 = ["1", "Ola, 3TI", "2", "2", "1", "0"]                         # 1/3, imię z przecinkiem
RANKING = ["2", "0"]
GRA_PROSTA = ["1", "Gracz Kontrolny", "1", "1", "1", "0"]
TOP = [("Gracz Jeden", 10), ("Gracz Dwa", 8), ("Gracz Trzy", 7), ("Gracz Cztery", 6), ("Gracz Piec", 5)]
PLIK_TOP = """data,imie,punkty,maks
2026-11-10T08:05:00,Gracz Siedem,1,10
2026-11-10T08:10:00,Gracz Jeden,10,10
2026-11-10T08:15:00,Zepsuty Wiersz,abc,10
2026-11-10T08:20:00,Gracz Trzy,7,10
2026-11-10T08:22:00,Pusty Wynik,,10
2026-11-10T08:25:00,Gracz Szesc,3,10
2026-11-10T08:30:00,Gracz Dwa,8,10
2026-11-10T08:35:00,Gracz Piec,5,10
2026-11-10T08:40:00,Gracz Cztery,6,10
"""


# --- krok 1: plik z pytaniami ucznia ------------------------------------------------------------
def problem_pytania(p):
    if not isinstance(p, dict):
        return "to nie jest obiekt {...} z kluczami"
    brak = [k for k in KLUCZE if k not in p]
    if brak:
        inne = [k for k in p if k not in KLUCZE]
        return (f"brakuje klucza {', '.join(brak)}"
                + (f" (jest za to {', '.join(inne)} - literówka?)" if inne else ""))
    if not isinstance(p["pytanie"], str) or not p["pytanie"].strip():
        return "treść pytania ma być niepustym tekstem"
    if not isinstance(p["odpowiedzi"], list) or len(p["odpowiedzi"]) != 4:
        ile = len(p["odpowiedzi"]) if isinstance(p["odpowiedzi"], list) else "nie lista"
        return f"mają być dokładnie 4 odpowiedzi w liście [...], a jest: {ile}"
    if not all(isinstance(o, str) and o.strip() for o in p["odpowiedzi"]):
        return "każda odpowiedź ma być niepustym tekstem w cudzysłowie"
    poprawna = p["poprawna"]
    if isinstance(poprawna, bool) or not isinstance(poprawna, int):
        return f"poprawna ma być liczbą całkowitą bez cudzysłowu (indeks od 0 do 3), a jest {poprawna!r}"
    if not 0 <= poprawna <= 3:
        return f"poprawna to indeks od 0 do 3, a jest {poprawna} - indeksy liczymy od 0"
    if not isinstance(p["kategoria"], str) or not p["kategoria"].strip():
        return "kategoria ma być niepustym tekstem"
    return None


def sprawdz_plik_pytan():
    braki = []
    if not EKSPORT.is_file():
        braki.append("nie ma pliku eksportuj.py - napisz skrypt, który zapisze PYTANIA do dane/pytania.json")
    if not PYTANIA_UCZNIA.is_file():
        braki.append("nie ma pliku dane/pytania.json" + (" - uruchom raz: python3 eksportuj.py"
                                                         if EKSPORT.is_file() else ""))
        return braki
    try:
        tekst = PYTANIA_UCZNIA.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return braki + ['dane/pytania.json nie jest zapisany w UTF-8 - zapisuj z encoding="utf-8"']
    try:
        dane = json.loads(tekst)
    except json.JSONDecodeError as blad:
        return braki + [f"dane/pytania.json ma błąd składni w linii {blad.lineno}, kolumna {blad.colno} "
                        f"({blad.msg}). Najczęściej przy dopisywaniu pytań: brak przecinka między "
                        "pytaniami {...}, {...}, przecinek po ostatnim elemencie albo tekst bez cudzysłowu"]
    if not isinstance(dane, list):
        return braki + ["w dane/pytania.json ma być lista pytań w nawiasach [ ... ]"]
    problemy = []
    for nr, pytanie in enumerate(dane, start=1):
        problem = problem_pytania(pytanie)
        if problem:
            tytul = pytanie.get("pytanie") if isinstance(pytanie, dict) else None
            tytul = f" ({tytul[:40]})" if isinstance(tytul, str) else ""
            problemy.append(f"pytanie nr {nr}{tytul}: {problem}")
    if len(dane) < MIN_PYTAN:
        braki.append(f"pytań w pliku: {len(dane)}, a ma być co najmniej {MIN_PYTAN} - dopisz w VS Code dwa własne "
                     "(skopiuj cały blok {...} razem z przecinkiem i zmień treść)")
    braki += problemy[:5]
    if len(problemy) > 5:
        braki.append(f"... i jeszcze {len(problemy) - 5} pytań z błędami")
    if re.search(r"\\u0[0-9a-fA-F]{3}", tekst):
        braki.append("polskie litery są zapisane jako \\u0105 i podobne - dodaj ensure_ascii=False w json.dump")
    if tekst.count("\n") < len(dane):
        braki.append("plik jest w jednej linii - dodaj indent=2 w json.dump, żeby dało się go czytać i edytować")
    return braki


# --- granie za ucznia ---------------------------------------------------------------------------
def przygotuj(baza, pytania=KONTROLNE):
    katalog = baza / "quiz"
    (katalog / "dane").mkdir(parents=True)
    (katalog / "quiz.py").write_bytes(QUIZ.read_bytes())
    if pytania is not None:
        (katalog / "dane" / "pytania.json").write_text(json.dumps(pytania, ensure_ascii=False, indent=2),
                                                       encoding="utf-8")
    return katalog


def graj(katalog, wejscie, cwd=None):
    return straznik.uruchom([sys.executable, katalog / "quiz.py"], cwd or katalog, wejscie, limit=LIMIT)


def opis_awarii(wynik, katalog, wejscie):
    opis = straznik.opisz_przebieg(wynik, katalog, LIMIT)
    if opis and "wyniki.csv" in opis and "FileNotFoundError" in opis:
        opis += ("\nGdy pliku dane/wyniki.csv jeszcze nie ma (pierwsze uruchomienie), wczytaj_ranking ma zwrócić "
                 "pustą listę: sprawdź sciezka.exists() przed otwarciem (krok 4)")
    if opis and "KeyError" in opis and "wczytaj_ranking" in opis:
        opis += ("\ncsv.DictReader bierze pierwszą linię pliku za nagłówek - czy dane/wyniki.csv zaczyna się od "
                 "data,imie,punkty,maks? (krok 3)")
    if opis and ("EOFError" in opis or wynik.czas_minal):
        opis += ("\nStrażnik wpisał po kolei: " + ", ".join(wejscie) + ". Zobacz w README „Jak gra strażnik”: "
                 "imię zaraz po wybraniu 1, po złej odpowiedzi (abc, 9) quiz pyta jeszcze raz, po rundzie wraca "
                 "do menu i nie pyta o nic więcej.")
    return opis


def wczytaj_wyniki(sciezka):
    """(wiersze, braki) z pliku wyników; wiersze bez pustych linii, razem z nagłówkiem."""
    try:
        tekst = sciezka.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, ['dane/wyniki.csv nie jest zapisany w UTF-8 - encoding="utf-8" w open()']
    pierwsza = (tekst.splitlines() or [""])[0]
    if ";" in pierwsza and "," not in pierwsza:
        return None, ["dane/wyniki.csv: kolumny oddzielaj przecinkiem (domyślny csv.writer), "
                      "bo ten plik przeczyta potem pandas w module 6"]
    return [w for w in csv.reader(io.StringIO(tekst)) if any(p.strip() for p in w)], []


def sprawdz_wiersz(wiersz, gracz, punkty, maks, ile_dobrze):
    if len(wiersz) != 4:
        return f"wiersz {','.join(wiersz)} ma {len(wiersz)} pól zamiast 4 (data,imie,punkty,maks)"
    data, kto, pkt, mx = (p.strip() for p in wiersz)
    if not DATA.fullmatch(data):
        return (f"data ma wyglądać tak: 2026-11-10T09:15:00, a jest {data} - "
                'datetime.now().isoformat(timespec="seconds")')
    if kto != gracz:
        return f"w kolumnie imie jest {kto}, a gracz przedstawił się jako {gracz}"
    if pkt != str(punkty):
        return (f"{gracz}: zapisane punkty {pkt}, a gracz odpowiedział dobrze na {ile_dobrze} z {maks} pytań "
                "(strażnik wpisuje 1 tam, gdzie poprawna jest pierwsza odpowiedź) - sprawdź zamianę "
                "numeru 1-4 na indeks 0-3")
    if mx != str(maks):
        return f"{gracz}: maks to liczba pytań w rundzie ({maks}), a jest {mx}"
    return None


def problem_naglowka(katalog):
    plik = katalog / "dane" / "wyniki.csv"
    if not plik.is_file():
        return []
    wiersze, braki = wczytaj_wyniki(plik)
    if wiersze is None:
        return braki
    if wiersze and [p.strip() for p in wiersze[0]] != NAGLOWEK_WYNIKOW:
        return ["pierwsza linia dane/wyniki.csv ma być nagłówkiem: data,imie,punkty,maks"]
    return []


def sprawdz_wyniki_po_grach(katalog):
    plik = katalog / "dane" / "wyniki.csv"
    if not plik.is_file():
        inne = [str(p.relative_to(katalog)) for p in katalog.rglob("*.csv")]
        if inne:
            return [f"wynik trafił do {', '.join(inne)}, a ma być w dane/wyniki.csv obok quiz.py"]
        return ["po rundzie nie powstał plik dane/wyniki.csv - czy main() wywołuje zapisz_wynik "
                "zaraz po rozegraj()?"]
    wiersze, braki = wczytaj_wyniki(plik)
    if wiersze is None:
        return braki
    naglowki = [w for w in wiersze if [p.strip() for p in w] == NAGLOWEK_WYNIKOW]
    dane = [w for w in wiersze if [p.strip() for p in w] != NAGLOWEK_WYNIKOW]
    if not wiersze or [p.strip() for p in wiersze[0]] != NAGLOWEK_WYNIKOW:
        braki.append("pierwsza linia dane/wyniki.csv ma być nagłówkiem: data,imie,punkty,maks")
    if len(naglowki) > 1:
        braki.append("nagłówek jest dopisywany przy każdej grze - pisz go tylko wtedy, gdy pliku jeszcze nie ma "
                     "(sprawdź sciezka.exists() przed otwarciem)")
    testowy = [w for w in dane if len(w) > 1 and w[1].strip() == "Testowy Gracz"]
    ola = [w for w in dane if w and "Ola" in ",".join(w)]
    if not testowy and ola:
        braki.append('po drugiej grze w pliku jest tylko jej wynik - plik jest nadpisywany. Otwieraj go '
                     'w trybie dopisywania: open(..., "a", ...)')
        return braki
    if len(dane) != 2:
        braki.append(f"po dwóch grach w pliku ma być 2 wierszy z wynikami, a jest {len(dane)}")
    if testowy:
        problem = sprawdz_wiersz(testowy[0], "Testowy Gracz", 3, 3, 3)
        if problem:
            braki.append(problem)
    elif not braki:
        braki.append("w pliku nie ma wyniku pierwszej gry (imię: Testowy Gracz)")
    if ola:
        if len(ola[0]) != 4 or ola[0][1].strip() != "Ola, 3TI":
            braki.append("imię z przecinkiem („Ola, 3TI”) rozjechało kolumny - nie sklejaj wiersza "
                         "przecinkami, zapisuj przez csv.writer (sam weźmie takie imię w cudzysłów)")
        else:
            problem = sprawdz_wiersz(ola[0], "Ola, 3TI", 1, 3, 1)
            if problem:
                braki.append(problem)
    elif not braki:
        braki.append("w pliku nie ma wyniku drugiej gry (imię: Ola, 3TI)")
    return braki


def sprawdz_ranking_po_grach(katalog):
    wynik = graj(katalog, RANKING)
    awaria = opis_awarii(wynik, katalog, RANKING)
    if awaria:
        return [f"opcja 2 (Ranking): {awaria}"]
    if "Testowy Gracz" not in wynik.out or "Ola, 3TI" not in wynik.out:
        return ["po ponownym uruchomieniu quizu Ranking nie pokazuje wcześniejszych gier - na starcie main() "
                "ranking ma przyjść z pliku: ranking = wczytaj_ranking(PLIK_WYNIKOW)"]
    if wynik.out.index("Testowy Gracz") > wynik.out.index("Ola, 3TI"):
        return ["ranking ma być od najlepszego wyniku: Testowy Gracz (3 pkt) przed Ola, 3TI (1 pkt)"]
    return []


def sprawdz_ranking_top(baza):
    katalog = przygotuj(baza / "top")
    (katalog / "dane" / "wyniki.csv").write_text(PLIK_TOP, encoding="utf-8")
    wynik = graj(katalog, RANKING)
    awaria = opis_awarii(wynik, katalog, RANKING)
    if awaria:
        return [f"ranking z pliku, w którym są uszkodzone wiersze (punkty „abc” i puste): {awaria}"
                "\nUszkodzone wiersze pomijaj: try/except ValueError przy zamianie punktów na int"]
    out, braki = wynik.out, []
    if not any(n in out for n, _ in TOP + [("Gracz Szesc", 3), ("Gracz Siedem", 1), ("Zepsuty Wiersz", 0)]):
        return ["Ranking nie pokazuje wyników z pliku: strażnik podłożył dane/wyniki.csv z kilkoma wynikami, "
                "a opcja 2 nie pokazała żadnego. Krok 4: wczytaj_ranking czyta plik przez csv.DictReader, "
                "a main() zaczyna od ranking = wczytaj_ranking(PLIK_WYNIKOW)"]
    if "Zepsuty Wiersz" in out or "Pusty Wynik" in out:
        braki.append("uszkodzony wiersz (punkty „abc” albo puste) trafił do rankingu - pomiń go")
    nazwy = [n for n, _ in TOP]
    if "Gracz Jeden" not in out and "Gracz Szesc" in out:
        braki.append("Gracz Jeden (10 pkt) nie trafił do 5 najlepszych, a Gracz Szesc (3 pkt) tak - sortujesz "
                     "punkty jak tekst („10” < „3”)? Zamień je na int przed sortowaniem")
        return braki
    brak = [n for n in nazwy if n not in out]
    if brak:
        braki.append(f"w rankingu brakuje: {', '.join(brak)} (to 5 najlepszych wyników z pliku)")
    nadmiar = [n for n in ("Gracz Szesc", "Gracz Siedem") if n in out]
    if nadmiar:
        braki.append(f"ranking ma pokazać 5 najlepszych, a pokazuje też: {', '.join(nadmiar)} - "
                     "pokaz_ranking z modułu 3 robi to sam, nie zmieniaj go")
    if not brak and [n for n in sorted(nazwy, key=out.index)] != nazwy:
        braki.append("ranking ma być od najlepszego wyniku - pokaz_ranking z modułu 3 sortuje sam, "
                     "jeśli punkty są liczbami (int)")
    return braki


def sprawdz_ranking_bez_pliku(baza):
    katalog = przygotuj(baza / "pusty")
    wynik = graj(katalog, RANKING)
    awaria = opis_awarii(wynik, katalog, RANKING)
    if awaria:
        return [f"Ranking, gdy pliku z wynikami jeszcze nie ma: {awaria}"]
    if "ranking jest pusty" not in wynik.out.lower():
        return ["gdy pliku dane/wyniki.csv jeszcze nie ma, wczytaj_ranking ma zwrócić pustą listę, "
                "a Ranking napisać „Ranking jest pusty — zagraj pierwszy!” (jak w module 3)"]
    return []


def sprawdz_bledne_pliki(baza):
    braki = []
    katalog = przygotuj(baza / "brak", pytania=None)
    wynik = graj(katalog, GRA_PROSTA)
    if wynik.traceback or wynik.czas_minal:
        braki.append("brak pliku dane/pytania.json wywraca quiz: " + straznik.opisz_przebieg(wynik, katalog, LIMIT)
                     + "\nZłap FileNotFoundError w wczytaj_pytania, wypisz przyjazny komunikat i zakończ: sys.exit(1)")
    elif wynik.kod == 0:
        braki.append("gdy nie ma pliku z pytaniami, quiz ma wypisać komunikat i zakończyć się: sys.exit(1)")
    elif "pytania.json" not in wynik.out + wynik.err:
        braki.append("komunikat o brakującym pliku ma mówić, którego pliku brakuje (wypisz ścieżkę)")

    katalog = przygotuj(baza / "zepsuty", pytania=None)
    (katalog / "dane" / "pytania.json").write_text(ZEPSUTY_JSON, encoding="utf-8")
    try:
        json.loads(ZEPSUTY_JSON)
        linia = None
    except json.JSONDecodeError as blad:
        linia = blad.lineno
    wynik = graj(katalog, GRA_PROSTA)
    if wynik.traceback or wynik.czas_minal:
        braki.append("uszkodzony JSON (brak przecinka) wywraca quiz: " + straznik.opisz_przebieg(wynik, katalog, LIMIT)
                     + "\nZłap json.JSONDecodeError, wypisz komunikat z numerem linii (blad.lineno) i sys.exit(1)")
    elif wynik.kod == 0:
        braki.append("gdy plik z pytaniami jest uszkodzony, quiz ma wypisać komunikat i zakończyć się: sys.exit(1)")
    elif str(linia) not in re.findall(r"\d+", wynik.out + wynik.err):
        braki.append(f"komunikat o uszkodzonym pliku ma podać numer linii z błędem: blad.lineno "
                     f"(w pliku strażnika to linia {linia})")
    return braki


def main():
    raport = straznik.Raport("STRAŻNIK QUIZU (ćwiczenie 02)")
    if not QUIZ.is_file():
        raport.popraw("quiz.py", ["nie ma pliku quiz.py (przywróć go: git checkout -- quiz.py)"])
        return raport.koniec("")
    skladnia = straznik.blad_skladni(QUIZ)
    if skladnia:
        raport.popraw("quiz.py", [skladnia])
        return raport.koniec("")

    raport.etap("krok 1: dane/pytania.json", sprawdz_plik_pytan())

    with tempfile.TemporaryDirectory(prefix="straznik-02-") as tmp:
        baza = Path(tmp)
        # krok 2: pytania z pliku JSON
        braki2 = []
        if straznik.importuje(QUIZ, "pytania"):
            braki2.append("quiz.py wciąż importuje pytania.py - pytania mają przychodzić z dane/pytania.json "
                          "(wczytaj_pytania z json.load)")
        gra = przygotuj(baza / "gra")
        wynik1 = graj(gra, GRA_1)
        pokazal = "Pytanie kontrolne strażnika" in wynik1.out
        if not pokazal and not braki2:
            awaria = opis_awarii(wynik1, gra, GRA_1)
            if awaria and "wczytaj_ranking" in awaria:
                braki2.append(f"quiz wywraca się na starcie przy wczytywaniu rankingu: {awaria}")
            else:
                braki2.append("quiz nie pokazał pytań z pliku dane/pytania.json (strażnik podłożył własne)"
                              + (f": {awaria}" if awaria else " - czy main() wczytuje pytania z PLIK_PYTAN?"))
        if not braki2:
            braki2 += sprawdz_bledne_pliki(baza)
        krok2 = raport.etap("krok 2: pytania z pliku JSON, brak pliku i uszkodzony JSON bez wywrotki", braki2)

        # krok 3: zapis wyników
        krok3 = False
        if pokazal:
            awaria = opis_awarii(wynik1, gra, GRA_1)
            if awaria:
                raport.popraw("krok 3: wyniki dopisywane do dane/wyniki.csv",
                              [f"pierwsza gra: {awaria}"] + problem_naglowka(gra))
            else:
                wynik2 = graj(gra, GRA_2)
                awaria = opis_awarii(wynik2, gra, GRA_2)
                krok3 = raport.etap("krok 3: wyniki dopisywane do dane/wyniki.csv",
                                    [f"druga gra: {awaria}"] + problem_naglowka(gra) if awaria
                                    else sprawdz_wyniki_po_grach(gra))
        else:
            raport.czeka("krok 3: zapis wyników (sprawdzę, gdy quiz pokaże pytania z JSON-a)")

        # krok 4: ranking z pliku
        if krok2:
            braki4 = sprawdz_ranking_top(baza)
            if not braki4:
                braki4 = sprawdz_ranking_bez_pliku(baza)
            if not braki4 and krok3:
                braki4 = sprawdz_ranking_po_grach(gra)
            if not braki4 and krok3 and wynik1.out.count("Testowy Gracz") < 2:
                braki4 = ["zaraz po grze Ranking nie pokazuje nowego wyniku - po zapisz_wynik odśwież ranking: "
                          "ranking = wczytaj_ranking(PLIK_WYNIKOW)"]
            if braki4 or krok3:
                raport.etap("krok 4: Ranking z dane/wyniki.csv, uszkodzone wiersze pominięte", braki4)
            else:
                raport.czeka("krok 4: Ranking czyta plik dobrze; sprawdzę go jeszcze po prawdziwych grach, "
                             "gdy zadziała zapis wyników")
        else:
            raport.czeka("krok 4: ranking (sprawdzę, gdy quiz będzie czytał pytania z JSON-a)")

        # krok 5: inny katalog
        if pokazal and not opis_awarii(wynik1, gra, GRA_1):
            inny_quiz = przygotuj(baza / "inny")
            inny = baza / "inny-katalog"
            inny.mkdir()
            wejscie = ["1", "Z innego katalogu", "1", "1", "1", "0"]
            wynik = graj(inny_quiz, wejscie, cwd=inny)
            braki5 = []
            awaria = opis_awarii(wynik, inny_quiz, wejscie)
            if awaria or "Pytanie kontrolne strażnika" not in wynik.out:
                braki5.append("uruchomiony z innego katalogu (cd ~ && python3 .../quiz.py) quiz nie działa"
                              + (f": {awaria}" if awaria else ": nie znalazł pytań"))
            if (inny / "dane").exists() or any(inny.glob("*.csv")):
                braki5.append("quiz zapisał wyniki w katalogu, z którego go uruchomiono, a nie obok quiz.py")
            if not braki5 and krok3 and not (inny_quiz / "dane" / "wyniki.csv").is_file():
                braki5.append("po grze z innego katalogu nie ma wyniku w dane/wyniki.csv obok quiz.py")
            if braki5:
                braki5.append("Ścieżka względna, np. \"dane/pytania.json\", liczy się od katalogu, w którym stoisz "
                              "w terminalu. Buduj ścieżki od pliku programu: KATALOG = Path(__file__).parent, "
                              "potem KATALOG / \"dane\" / \"pytania.json\"")
            raport.etap("krok 5: quiz działa uruchomiony z innego katalogu", braki5)
        else:
            raport.czeka("krok 5: start z innego katalogu (sprawdzę, gdy runda przejdzie bez błędów)")

    for uwaga in straznik.uwagi_o_plikach(QUIZ):
        raport.uwaga(uwaga)
    if EKSPORT.is_file():
        for uwaga in straznik.uwagi_o_plikach(EKSPORT):
            raport.uwaga(uwaga)
    return raport.koniec("Quiz pamięta: pytania czyta z dane/pytania.json, a każdy wynik dopisuje do "
                         "dane/wyniki.csv. Ten plik CSV wykorzystasz w module 6 do wykresów.")


if __name__ == "__main__":
    sys.exit(main())
