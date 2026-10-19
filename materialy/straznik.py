"""Wspólny kod strażników (pliki sprawdz.py) z ćwiczeń modułu 4. Żeby zrobić ćwiczenia, nie musisz go czytać.

Strażnik uruchamia twój program tak jak ty w terminalu: w osobnym procesie, z przygotowanymi danymi
i z odpowiedziami wpisanymi za ciebie. Gdy program się wysypie, strażnik nie wkleja surowego komunikatu
Pythona, tylko mówi, co się stało, w której linii i co to zwykle znaczy.
"""
import ast
import os
import re
import shutil
import subprocess
import sys
import textwrap
import threading
from pathlib import Path

sys.dont_write_bytecode = True

SZEROKOSC = 96
LIMIT_WYJSCIA = 200_000          # tyle znaków wyjścia programu strażnik zapamiętuje (reszta przepada)
POMIJANE = shutil.ignore_patterns(".git", ".venv", "venv", "__pycache__", "*.pyc", ".ipynb_checkpoints")


# --- wypisywanie raportu ------------------------------------------------------------------------
def naglowek(tytul):
    print("=" * 60)
    print(f"  {tytul}")
    print("=" * 60)


def _zawin(tekst, pierwsze, kolejne):
    linie = []
    for i, akapit in enumerate(str(tekst).split("\n")):
        if not akapit.strip():
            continue
        linie.append(textwrap.fill(akapit, SZEROKOSC, initial_indent=pierwsze if i == 0 else kolejne,
                                   subsequent_indent=kolejne, break_long_words=False, break_on_hyphens=False))
    return "\n".join(linie)


class Raport:
    """Lista punktów kontrolnych: OK, POPRAW (z listą braków) albo CZEKA (sprawdzę później)."""

    def __init__(self, tytul):
        naglowek(tytul)
        self.bledy = 0
        self.uwagi = []

    def ok(self, opis):
        print(_zawin(opis, "  OK      ", "          "))

    def popraw(self, opis, braki=()):
        self.bledy += 1
        print(_zawin(opis, "  POPRAW  ", "          "))
        for brak in braki:
            print(_zawin(brak, "          - ", "            "))

    def czeka(self, opis):
        self.bledy += 1
        print(_zawin(opis, "  CZEKA   ", "          "))

    def etap(self, opis, braki):
        """OK, gdy lista braków jest pusta; w przeciwnym razie POPRAW. Zwraca True/False."""
        if braki:
            self.popraw(opis, braki)
            return False
        self.ok(opis)
        return True

    def uwaga(self, tekst):
        self.uwagi.append(tekst)

    def koniec(self, sukces):
        """Wypisuje uwagi i podsumowanie; zwraca kod wyjścia: 0 sukces, 1 jest coś do poprawy."""
        if self.uwagi:
            print()
            print("Uwagi (nie blokują zaliczenia):")
            for uwaga in self.uwagi:
                print(_zawin(uwaga, "  - ", "    "))
        print()
        if self.bledy:
            print("Popraw i uruchom mnie jeszcze raz.")
            return 1
        print(_zawin(sukces, "", ""))
        return 0


def skrot_listy(elementy, ile=5):
    """'a, b, c' albo 'a, b, c, d, e i jeszcze 3'."""
    elementy = [str(e) for e in elementy]
    if len(elementy) <= ile:
        return ", ".join(elementy)
    return ", ".join(elementy[:ile]) + f" i jeszcze {len(elementy) - ile}"


def ostatnie_linie(tekst, ile=4):
    linie = [l.rstrip() for l in tekst.splitlines() if l.strip()]
    return "\n".join("  | " + l[:150] for l in linie[-ile:])


# --- uruchamianie programu ucznia ---------------------------------------------------------------
class Wynik:
    def __init__(self, kod, out, err, czas_minal):
        self.kod = kod
        self.out = out
        self.err = err
        self.czas_minal = czas_minal

    @property
    def traceback(self):
        return "Traceback (most recent call last)" in self.err or bool(re.search(r"^\w*Error\b", self.err, re.M))


def srodowisko(**dodatkowe):
    env = dict(os.environ)
    for zmienna in ("PYTHONPATH", "PYTHONSAFEPATH", "PYTHONSTARTUP", "PYTHONHOME"):
        env.pop(zmienna, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env.update(dodatkowe)
    return env


def uruchom(polecenie, cwd, wejscie=None, limit=15, env=None):
    """Uruchamia polecenie (listę) w katalogu cwd i podaje na wejście linie z listy `wejscie`, potem koniec danych.

    Zwraca Wynik(kod, out, err, czas_minal). Program, który działa dłużej niż `limit` sekund, zostaje przerwany.
    """
    if isinstance(wejscie, (list, tuple)):
        wejscie = "".join(f"{linia}\n" for linia in wejscie)
    proces = subprocess.Popen([str(p) for p in polecenie], cwd=str(cwd), stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env or srodowisko())
    bufory = [bytearray(), bytearray()]

    def czytaj(strumien, bufor):
        while True:
            kawalek = strumien.read1(65536) if hasattr(strumien, "read1") else strumien.read(65536)
            if not kawalek:
                break
            if len(bufor) < LIMIT_WYJSCIA:
                bufor.extend(kawalek[:LIMIT_WYJSCIA - len(bufor)])

    watki = [threading.Thread(target=czytaj, args=(proces.stdout, bufory[0]), daemon=True),
             threading.Thread(target=czytaj, args=(proces.stderr, bufory[1]), daemon=True)]
    for watek in watki:
        watek.start()
    try:
        if wejscie:
            proces.stdin.write(wejscie.encode("utf-8"))
        proces.stdin.close()
    except (BrokenPipeError, OSError):
        pass
    czas_minal = False
    try:
        proces.wait(timeout=limit)
    except subprocess.TimeoutExpired:
        czas_minal = True
        proces.kill()
        proces.wait()
    for watek in watki:
        watek.join(timeout=5)
    return Wynik(proces.returncode, bufory[0].decode("utf-8", "replace"),
                 bufory[1].decode("utf-8", "replace"), czas_minal)


def kopiuj_katalog(zrodlo, cel):
    shutil.copytree(zrodlo, cel, ignore=POMIJANE)


# --- tłumaczenie błędów -------------------------------------------------------------------------
_RAMKA = re.compile(r'^\s*File "(?P<plik>[^"]+)", line (?P<linia>\d+)(?:, in (?P<funkcja>.+))?\s*$')


def rozbierz_traceback(err):
    """Z tekstu błędu Pythona wyciąga (typ, komunikat, ramki); ramka = (plik, linia, funkcja, kod)."""
    linie = err.splitlines()
    poczatki = [i for i, l in enumerate(linie) if l.startswith("Traceback (most recent call last)")]
    blok = linie[poczatki[-1]:] if poczatki else linie
    ramki = []
    for i, linia in enumerate(blok):
        dopasowanie = _RAMKA.match(linia)
        if dopasowanie:
            kod = ""
            if i + 1 < len(blok) and blok[i + 1].startswith("    ") and not _RAMKA.match(blok[i + 1]):
                kod = blok[i + 1].strip()
            ramki.append((dopasowanie["plik"], int(dopasowanie["linia"]), dopasowanie["funkcja"], kod))
    wyjatek = ""
    for linia in reversed(blok):
        if linia.strip() and not linia.startswith((" ", "\t", "Traceback")):
            wyjatek = linia.strip()
            break
    typ, _, komunikat = wyjatek.partition(":")
    typ = typ.strip().split(".")[-1]
    if not re.fullmatch(r"[A-Za-z_]\w*", typ or "-"):
        return "", wyjatek, ramki
    return typ, komunikat.strip(), ramki


def _czy_biblioteka(plik):
    return (plik.startswith("<") or f"{os.sep}lib{os.sep}python3" in plik
            or Path(plik).name.startswith("_straznik_"))


def _pokaz_sciezke(plik, katalog):
    if katalog:
        try:
            return str(Path(plik).resolve().relative_to(Path(katalog).resolve()))
        except (ValueError, OSError):
            pass
    return Path(plik).name


def podpowiedz(typ, komunikat):
    """Ogólne wyjaśnienie wyjątku po polsku (albo None)."""
    if typ == "ValueError" and "invalid literal for int()" in komunikat:
        return ("int() dostał tekst, który nie jest liczbą całkowitą. Taki tekst trzeba sprawdzić wcześniej "
                "albo wyłapać: try/except ValueError.")
    if typ == "ValueError" and "could not convert string to float" in komunikat:
        return "float() dostał tekst, który nie jest liczbą (np. przecinek zamiast kropki albo słowo)."
    if typ in ("TypeError", "AttributeError") and "NoneType" in komunikat:
        return ("w zmiennej jest None tam, gdzie miał być tekst albo liczba. Najczęściej: brakujące pole "
                "w wierszu CSV (DictReader wpisuje wtedy None) albo funkcja, która nic nie zwraca (brak return).")
    if typ == "FileNotFoundError":
        return ("Python nie znalazł pliku. Ścieżka względna, np. dane/plik.csv, liczy się od katalogu, "
                "w którym jesteś w terminalu, a nie od pliku .py. Pewniejsza jest ścieżka zbudowana "
                "z Path(__file__).parent.")
    if typ == "ImportError" and "cannot import name" in komunikat:
        return ("moduł się znalazł, ale nie ma w nim takiej nazwy: literówka w nazwie funkcji albo klasy "
                "albo funkcja, której jeszcze nie napisałeś.")
    if typ in ("ModuleNotFoundError", "ImportError"):
        return ("Python nie znalazł modułu. Przy python3 plik.py szuka modułów obok uruchomionego pliku, "
                "a przy python3 -m pakiet - w katalogu, w którym jesteś.")
    if typ == "EOFError":
        return ("program czekał na input(), a strażnik nie miał już nic do wpisania. Zobacz w README, "
                "w jakiej kolejności strażnik wpisuje odpowiedzi.")
    if typ == "KeyError":
        return ("w słowniku nie ma takiego klucza: literówka w nazwie, inny separator CSV niż w pliku "
                "albo brakujący klucz w danych.")
    if typ == "IndexError":
        return "indeks spoza listy: lista jest krótsza, niż zakłada program."
    if typ == "ZeroDivisionError":
        return "dzielenie przez zero, np. średnia z pustej listy albo maks równe 0."
    if typ == "NameError":
        return "Python nie zna tej nazwy: literówka, brakujący import albo zmienna użyta przed przypisaniem."
    if typ in ("SyntaxError", "IndentationError", "TabError"):
        return ("błąd składni, więc Python nie zaczął nawet wykonywać programu. Sprawdź wskazaną linię "
                "i tę nad nią: nawiasy, cudzysłowy, dwukropki, wcięcia.")
    if typ == "UnicodeDecodeError":
        return 'plik ma inne kodowanie niż to, którym go czytasz. Dodaj encoding="utf-8" w open().'
    if typ == "JSONDecodeError":
        return "plik JSON ma błąd składni (przecinek, cudzysłów, nawias)."
    if typ == "RecursionError":
        return "funkcja wywołuje samą siebie bez końca."
    if typ == "PermissionError":
        return "brak uprawnień do pliku albo katalogu (sprawdź: ls -l)."
    if typ == "TypeError":
        return "operacja na złym typie, np. tekst zamiast liczby albo zła liczba argumentów funkcji."
    return None


def opisz_blad(err, katalog=None):
    """Zamienia komunikat błędu Pythona na kilka zdań: co, gdzie, co to znaczy."""
    typ, komunikat, ramki = rozbierz_traceback(err)
    if not typ:
        ostatnie = ostatnie_linie(err, 3)
        return "program zakończył się błędem" + (f":\n{ostatnie}" if ostatnie else "")
    linie = [f"program zakończył się wyjątkiem {typ}" + (f": {komunikat}" if komunikat else "")]
    ramka = next((r for r in reversed(ramki) if not _czy_biblioteka(r[0])), None)
    if ramka:
        plik, nr, funkcja, kod = ramka
        gdzie = f"miejsce: {_pokaz_sciezke(plik, katalog)}, linia {nr}"
        if funkcja and funkcja != "<module>":
            gdzie += f" (funkcja {funkcja})"
        if kod:
            gdzie += f": {kod}"
        linie.append(gdzie)
    wyjasnienie = podpowiedz(typ, komunikat)
    if wyjasnienie:
        linie.append(f"co to znaczy: {wyjasnienie}")
    return "\n".join(linie)


def opisz_przebieg(wynik, katalog=None, limit=None):
    """Opis nieudanego uruchomienia (wyjątek, przekroczony czas, kod wyjścia) albo None, gdy wszystko gra."""
    if wynik.czas_minal:
        return (f"program nie skończył się w {limit or 'kilkanaście'} s. Czeka na input(), którego nikt nie wpisze, "
                "albo kręci się w pętli bez końca (np. except, który łapie wszystko, także koniec danych).")
    if wynik.traceback:
        return opisz_blad(wynik.err, katalog)
    if wynik.kod != 0:
        ostatnie = ostatnie_linie(wynik.out + "\n" + wynik.err, 4)
        return f"program zakończył się kodem {wynik.kod}" + (f"; ostatnie linie:\n{ostatnie}" if ostatnie else "")
    return None


# --- sprawdzanie kodu bez uruchamiania ----------------------------------------------------------
def blad_skladni(plik, katalog=None):
    """Opis błędu składni w pliku albo None."""
    plik = Path(plik)
    try:
        zrodlo = plik.read_bytes()
    except OSError as blad:
        return f"nie mogę przeczytać pliku {plik.name}: {blad.strerror}"
    try:
        compile(zrodlo, str(plik), "exec")
    except SyntaxError as blad:
        kod = (blad.text or "").strip()
        return (f"{_pokaz_sciezke(plik, katalog)}, linia {blad.lineno}: błąd składni ({blad.msg})"
                + (f": {kod}" if kod else "") + "\nco to znaczy: " + podpowiedz("SyntaxError", ""))
    except ValueError as blad:
        return f"{plik.name}: {blad}"
    return None


def drzewo(plik):
    try:
        return ast.parse(Path(plik).read_bytes())
    except (OSError, SyntaxError, ValueError):
        return None


def wywolania(plik, nazwy):
    """Lista (linia, nazwa) wywołań funkcji o podanych nazwach, np. print i input."""
    korzen = drzewo(plik)
    if korzen is None:
        return []
    znalezione = []
    for wezel in ast.walk(korzen):
        if isinstance(wezel, ast.Call) and isinstance(wezel.func, ast.Name) and wezel.func.id in nazwy:
            znalezione.append((wezel.lineno, wezel.func.id))
    return sorted(znalezione)


def importuje(plik, modul):
    """Czy plik importuje moduł (import modul / from modul import ...)."""
    korzen = drzewo(plik)
    if korzen is None:
        return False
    for wezel in ast.walk(korzen):
        if isinstance(wezel, ast.Import) and any(a.name.split(".")[0] == modul for a in wezel.names):
            return True
        if isinstance(wezel, ast.ImportFrom) and wezel.level == 0 and (wezel.module or "").split(".")[0] == modul:
            return True
    return False


def uwagi_o_plikach(plik, newline=False):
    """Uwagi o open()/read_text()/write_text() bez encoding (i bez newline="", gdy newline=True)."""
    korzen = drzewo(plik)
    if korzen is None:
        return []
    uwagi = []
    for wezel in ast.walk(korzen):
        if not isinstance(wezel, ast.Call):
            continue
        nazwa = wezel.func.id if isinstance(wezel.func, ast.Name) else (
            wezel.func.attr if isinstance(wezel.func, ast.Attribute) else None)
        klucze = {k.arg for k in wezel.keywords}
        if nazwa == "open":
            tryb = ""
            if len(wezel.args) > 1 and isinstance(wezel.args[1], ast.Constant):
                tryb = str(wezel.args[1].value)
            for k in wezel.keywords:
                if k.arg == "mode" and isinstance(k.value, ast.Constant):
                    tryb = str(k.value.value)
            if "b" in tryb:
                continue
            if "encoding" not in klucze:
                uwagi.append(f'{Path(plik).name}, linia {wezel.lineno}: open() bez encoding="utf-8" - '
                             "na Windowsie polskie litery w pliku się rozsypią")
            if newline and "newline" not in klucze:
                uwagi.append(f'{Path(plik).name}, linia {wezel.lineno}: plik CSV otwieraj z newline="" - '
                             "bez tego csv na Windowsie dopisuje puste linie między wierszami")
        elif nazwa in ("read_text", "write_text") and "encoding" not in klucze:
            uwagi.append(f'{Path(plik).name}, linia {wezel.lineno}: {nazwa}() bez encoding="utf-8"')
    return uwagi
