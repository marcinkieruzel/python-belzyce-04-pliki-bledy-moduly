#!/usr/bin/env python3
"""Strażnik ćwiczenia 04 „Quiz w paczkach”.

  python3 sprawdz.py                       sprawdź katalog projekt/ obok tego pliku
  python3 sprawdz.py ~/quiz-o-kosmosie     sprawdź inny katalog, np. repozytorium zespołu
  python3 sprawdz.py KATALOG --bez-gry     bez grania w quiz (gdy wasze menu różni się od tego z README)

Strażnik pracuje na kopii projektu w katalogu tymczasowym - twoich plików nie zmienia.
"""
import json
import re
import sys
import tempfile
from pathlib import Path

CWICZENIE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(CWICZENIE.parent / "materialy"))
import straznik  # noqa: E402

LIMIT = 15
WYMAGANE = ["quiz/__init__.py", "quiz/__main__.py", "quiz/main.py", "quiz/bledy.py", "quiz/pytania.py",
            "quiz/punkty.py", "quiz/wyniki.py", "dane/pytania.json", "testy/__init__.py",
            "testy/test_punkty.py", "testy/test_pytania.py"]
MODULY = ["quiz", "quiz.bledy", "quiz.punkty", "quiz.pytania", "quiz.wyniki", "quiz.main"]
KONTROLNE = [
    {"pytanie": f"Pytanie kontrolne strażnika nr {nr}: wybierz odpowiedź A",
     "odpowiedzi": ["A", "B", "C", "D"], "poprawna": 0, "kategoria": "kontrola"} for nr in range(1, 4)
]
ZLE_PYTANIE = 6           # w pliku z 7 pytaniami szóste ma zły format
GRA = ["1", "Gracz Paczka", "abc", "1", "1", "1", "2", "0"]
GRA_BLAD = ["1", "Gracz Paczka", "1", "1", "1", "1", "1", "0", "0"]

KONTROLA = r'''
import contextlib, importlib, io, json, sys, tempfile, traceback
from pathlib import Path
katalog = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(katalog))
sys.stdin = io.StringIO("")
sys.dont_write_bytecode = True
W = {}

def wykonaj(funkcja):
    bufor = io.StringIO()
    try:
        with contextlib.redirect_stdout(bufor):
            wynik = funkcja()
        return {"ok": True, "wynik": repr(wynik)[:200], "wypisal": bufor.getvalue()[:300]}
    except BaseException as blad:
        return {"ok": False, "typ": type(blad).__name__, "tekst": str(blad)[:300],
                "mro": [k.__name__ for k in type(blad).__mro__], "tb": traceback.format_exc()[-4000:],
                "wypisal": bufor.getvalue()[:300]}

W["importy"] = {n: wykonaj(lambda n=n: importlib.import_module(n) and None) for n in MODULY}
DOBRE = {"pytanie": "Stolica Polski to:", "odpowiedzi": ["Kraków", "Warszawa", "Gniezno", "Poznań"],
         "poprawna": 1, "kategoria": "geografia"}
def kopia(**zmiany):
    p = dict(DOBRE, **zmiany)
    return {k: v for k, v in p.items() if v is not None}
try:
    from quiz.bledy import BladQuizu, BladPytania
    klasy = isinstance(BladQuizu, type) and isinstance(BladPytania, type)
    W["bledy"] = {"klasy": klasy}
    if klasy:
        W["bledy"].update(quizu_exception=issubclass(BladQuizu, Exception),
                          pytania_quizu=issubclass(BladPytania, BladQuizu),
                          rozne=BladQuizu is not BladPytania)
except BaseException:
    W["bledy"] = {"blad": traceback.format_exc()[-4000:]}
try:
    from quiz.punkty import czy_poprawna, policz_punkty
    W["punkty"] = {"czy_true": wykonaj(lambda: czy_poprawna(DOBRE, 1)),
                   "czy_false": wykonaj(lambda: czy_poprawna(DOBRE, 0)),
                   "policz": wykonaj(lambda: policz_punkty([DOBRE, DOBRE, DOBRE], [1, 0, 1])),
                   "rozna": wykonaj(lambda: policz_punkty([DOBRE, DOBRE], [1]))}
except BaseException:
    W["punkty"] = {"blad": traceback.format_exc()[-4000:]}
try:
    from quiz.pytania import sprawdz_pytanie, wczytaj_pytania
    W["sprawdz"] = {"dobre": wykonaj(lambda: sprawdz_pytanie(kopia(), 4)),
                    "poprawna = 7": wykonaj(lambda: sprawdz_pytanie(kopia(poprawna=7), 4)),
                    "3 odpowiedzi": wykonaj(lambda: sprawdz_pytanie(kopia(odpowiedzi=["a", "b", "c"]), 4)),
                    "brak klucza kategoria": wykonaj(lambda: sprawdz_pytanie(kopia(kategoria=None), 4))}
    tmp = Path(tempfile.mkdtemp())
    zle = [kopia() for _ in range(7)]
    zle[ZLE_PYTANIE - 1]["poprawna"] = 7
    (tmp / "zle.json").write_text(json.dumps(zle, ensure_ascii=False), encoding="utf-8")
    (tmp / "zepsuty.json").write_text('[{"pytanie": "x" "odpowiedzi": []}]', encoding="utf-8")
    W["sprawdz"]["wczytaj"] = {"wlasny": wykonaj(lambda: len(wczytaj_pytania(katalog / "dane" / "pytania.json"))),
                    "zle_pytanie": wykonaj(lambda: wczytaj_pytania(tmp / "zle.json")),
                    "brak_pliku": wykonaj(lambda: wczytaj_pytania(tmp / "nie-ma-takiego.json")),
                    "zepsuty": wykonaj(lambda: wczytaj_pytania(tmp / "zepsuty.json"))}
except BaseException:
    W["sprawdz"] = {"blad": traceback.format_exc()[-4000:]}
try:
    from quiz.wyniki import wczytaj_ranking, zapisz_wynik
    tmp = Path(tempfile.mkdtemp())
    plik_wynikow = tmp / "wyniki.csv"
    W["wyniki"] = {"brak_pliku": wykonaj(lambda: wczytaj_ranking(tmp / "nie-ma.csv")),
                   "zapis1": wykonaj(lambda: zapisz_wynik(plik_wynikow, "Ola", 4, 5)),
                   "zapis2": wykonaj(lambda: zapisz_wynik(plik_wynikow, "Kuba, 3TI", 2, 5))}
    W["wyniki"]["plik"] = plik_wynikow.read_text(encoding="utf-8") if plik_wynikow.exists() else None
    W["wyniki"]["ranking"] = wykonaj(lambda: wczytaj_ranking(plik_wynikow))
    zly = tmp / "zly.csv"
    zly.write_text("data,imie,punkty,maks\n2026-11-30T08:00:00,Ala,abc,5\n2026-11-30T08:01:00,Ela,3,5\n",
                   encoding="utf-8")
    W["wyniki"]["uszkodzony"] = wykonaj(lambda: wczytaj_ranking(zly))
except BaseException:
    W["wyniki"] = {"blad": traceback.format_exc()[-4000:]}
with open(sys.argv[2], "w", encoding="utf-8") as plik:
    json.dump(W, plik)
'''.replace("MODULY", repr(MODULY)).replace("ZLE_PYTANIE", str(ZLE_PYTANIE))

NADPISZ_PUNKTY = '''

def policz_punkty(pytania, wybory):  # dopisane przez strażnika: wersja bez ValueError
    return sum(1 for pytanie, wybor in zip(pytania, wybory) if wybor == pytanie["poprawna"])
'''
NADPISZ_PYTANIA = '''

def sprawdz_pytanie(pytanie, nr):  # dopisane przez strażnika: wersja, która niczego nie sprawdza
    return None
'''


def importy_bez_pakietu(opis):
    m = re.search(r"No module named '(\w+)'", opis)
    if m and m.group(1) in ("pytania", "punkty", "bledy", "wyniki", "main"):
        return (f"\nW pakiecie importuj z nazwą pakietu: from quiz.{m.group(1)} import ..., a nie "
                f"from {m.group(1)} import ... (README: „Dlaczego wcześniej działało”)")
    return ""


def opis_wyniku(r, katalog):
    """Opis wyjątku z raportu kontroli."""
    return straznik.opisz_blad(r["tb"], katalog) + importy_bez_pakietu(r.get("tekst", ""))


def etap_importy(raport, W, katalog):
    braki = []
    for nazwa in MODULY:
        r = W["importy"][nazwa]
        if not r["ok"]:
            if r["typ"] == "EOFError":
                braki.append(f"import {nazwa} woła input() - kod, który rozmawia z graczem, ma być w funkcjach "
                             "uruchamianych z main(), a main() wywołuje tylko quiz/__main__.py")
            elif r["typ"] == "SystemExit":
                braki.append(f"import {nazwa} kończy program (sys.exit poza funkcją)")
            else:
                braki.append(f"import {nazwa}: " + opis_wyniku(r, katalog))
        elif r["wypisal"].strip():
            pierwsza = r["wypisal"].strip().splitlines()[0][:80]
            braki.append(f"import {nazwa} coś wypisał („{pierwsza}”) - moduł przy imporcie ma tylko definiować "
                         "funkcje; menu uruchamia main() wywołane z quiz/__main__.py")
    return raport.etap("moduły pakietu importują się i nic przy tym nie wypisują", braki)


def etap_wyjatki(raport, W, katalog):
    b = W.get("bledy", {})
    if "blad" in b:
        return raport.etap("quiz/bledy.py: własne wyjątki", ["nie da się zaimportować BladQuizu i BladPytania "
                                                             "z quiz.bledy: " + straznik.opisz_blad(b["blad"], katalog)])
    braki = []
    if not b.get("klasy"):
        braki.append("BladQuizu i BladPytania mają być klasami: class BladQuizu(Exception): ...")
    else:
        if not b["quizu_exception"]:
            braki.append("BladQuizu ma dziedziczyć po Exception: class BladQuizu(Exception)")
        if not b["pytania_quizu"] or not b["rozne"]:
            braki.append("BladPytania ma dziedziczyć po BladQuizu: class BladPytania(BladQuizu) - wtedy main() "
                         "łapie oba jednym except BladQuizu")
    return raport.etap("quiz/bledy.py: BladPytania dziedziczy po BladQuizu, a ten po Exception", braki)


def etap_punkty(raport, W, katalog):
    p = W.get("punkty", {})
    if "blad" in p:
        return raport.etap("quiz/punkty.py", ["nie da się zaimportować czy_poprawna i policz_punkty z quiz.punkty: "
                                              + straznik.opisz_blad(p["blad"], katalog)])
    braki = []
    if p["czy_true"].get("wynik") != "True" or p["czy_false"].get("wynik") != "False":
        braki.append("czy_poprawna(pytanie, wybor) ma zwracać True, gdy wybor == pytanie[\"poprawna\"], inaczej False")
    if p["policz"].get("wynik") != "2":
        braki.append("policz_punkty dla 3 pytań i 2 dobrych odpowiedzi ma zwrócić 2, a zwraca "
                     + (p["policz"].get("wynik") or p["policz"].get("typ", "?")))
    rozna = p["rozna"]
    if rozna["ok"]:
        braki.append("policz_punkty dla list różnej długości ma zgłosić ValueError")
    elif "ValueError" not in rozna["mro"]:
        braki.append(f"policz_punkty dla list różnej długości zgłasza {rozna['typ']}, a ma ValueError")
    return raport.etap("quiz/punkty.py: czy_poprawna i policz_punkty (z ValueError)", braki)


def etap_pytania(raport, W, katalog):
    s = W.get("sprawdz", {})
    if "blad" in s:
        return raport.etap("quiz/pytania.py", ["nie da się zaimportować sprawdz_pytanie i wczytaj_pytania "
                                               "z quiz.pytania: " + straznik.opisz_blad(s["blad"], katalog)])
    braki = []
    if not s["dobre"]["ok"]:
        braki.append("sprawdz_pytanie zgłasza błąd dla poprawnego pytania: " + opis_wyniku(s["dobre"], katalog))
    bez_numeru = False
    for opis in ("poprawna = 7", "3 odpowiedzi", "brak klucza kategoria"):
        r = s[opis]
        if r["ok"]:
            braki.append(f"sprawdz_pytanie przepuszcza złe pytanie ({opis}) - ma zgłosić BladPytania")
        elif "BladPytania" not in r["mro"]:
            dopisek = (" - sprawdź, czy klucz jest w słowniku, zanim go użyjesz" if r["typ"] == "KeyError" else "")
            braki.append(f"dla złego pytania ({opis}) poleciał {r['typ']}, a ma BladPytania{dopisek}")
        elif not re.search(r"\b4\b", r["tekst"]):
            bez_numeru = True
    if bez_numeru:
        braki.append("komunikat BladPytania ma zawierać numer pytania (parametr nr), np. „pytanie nr 4: ...”")
    w = s["wczytaj"]
    if not w["wlasny"]["ok"]:
        braki.append("wasz dane/pytania.json nie przechodzi kontroli wczytaj_pytania: "
                     + (w["wlasny"]["tekst"] if "BladQuizu" in w["wlasny"]["mro"] else opis_wyniku(w["wlasny"], katalog)))
    r = w["zle_pytanie"]
    if r["ok"]:
        braki.append(f"wczytaj_pytania przepuszcza plik, w którym pytanie nr {ZLE_PYTANIE} ma zły format - "
                     "wywołaj sprawdz_pytanie(pytanie, nr) dla każdego pytania (enumerate od 1)")
    elif "BladQuizu" in r["mro"] and not re.search(rf"\b{ZLE_PYTANIE}\b", r["tekst"]):
        braki.append(f"przy złym pytaniu nr {ZLE_PYTANIE} komunikat nie podaje jego numeru - numeruj od 1: "
                     "enumerate(pytania, start=1)")
    elif "BladQuizu" not in r["mro"]:
        braki.append(f"plik ze złym pytaniem: wczytaj_pytania zgłasza {r['typ']}, a ma BladPytania")
    for klucz, co, wyjatek in (("brak_pliku", "brak pliku", "FileNotFoundError"),
                               ("zepsuty", "uszkodzony JSON", "json.JSONDecodeError")):
        r = w[klucz]
        if r["ok"]:
            braki.append(f"{co}: wczytaj_pytania nie zgłasza żadnego błędu")
        elif r["typ"] == "SystemExit":
            braki.append(f"{co}: wczytaj_pytania kończy program (sys.exit) - w pakiecie złap {wyjatek} "
                         "i zgłoś BladQuizu z opisem; o wyjściu z programu decyduje main()")
        elif "BladQuizu" not in r["mro"]:
            braki.append(f"{co}: wczytaj_pytania zgłasza {r['typ']} - złap {wyjatek} i zgłoś BladQuizu z opisem")
    return raport.etap("quiz/pytania.py: sprawdz_pytanie i wczytaj_pytania zgłaszają BladPytania/BladQuizu", braki)


def etap_wyniki(raport, W, katalog):
    w = W.get("wyniki", {})
    opis = "quiz/wyniki.py: zapisz_wynik dopisuje, wczytaj_ranking czyta i pomija uszkodzone wiersze"
    if "blad" in w:
        return raport.etap(opis, ["nie da się zaimportować zapisz_wynik i wczytaj_ranking z quiz.wyniki: "
                                  + straznik.opisz_blad(w["blad"], katalog)])
    braki = []
    r = w["brak_pliku"]
    if not r["ok"]:
        braki.append(f"wczytaj_ranking dla nieistniejącego pliku zgłasza {r['typ']} - ma zwrócić pustą listę")
    elif r["wynik"] != "[]":
        braki.append(f"wczytaj_ranking dla nieistniejącego pliku ma zwrócić [], a zwraca {r['wynik']}")
    for klucz in ("zapis1", "zapis2"):
        if not w[klucz]["ok"]:
            braki.append("zapisz_wynik(sciezka, imie, punkty, maks): " + opis_wyniku(w[klucz], katalog))
            return raport.etap(opis, braki)
    linie = [l for l in (w["plik"] or "").splitlines() if l.strip()]
    if len(linie) == 1 and "Kuba" in linie[0]:
        braki.append('zapisz_wynik nadpisuje plik: po dwóch wywołaniach jest w nim tylko ostatni wynik - '
                     'otwieraj go w trybie dopisywania: open(sciezka, "a", ...)')
    elif not linie or linie[0].strip() != "data,imie,punkty,maks":
        braki.append("plik wyników ma się zaczynać nagłówkiem data,imie,punkty,maks")
    elif len(linie) != 3:
        braki.append(f"po dwóch wywołaniach zapisz_wynik w pliku ma być nagłówek i 2 wiersze, a jest linii: "
                     f"{len(linie)} (tryb \"a\", nagłówek tylko dla nowego pliku)")
    elif '"Kuba, 3TI"' not in linie[2]:
        braki.append("imię z przecinkiem rozjechało kolumny - zapisuj przez csv.writer")
    if braki:
        return raport.etap(opis, braki)
    r = w["ranking"]
    oczekiwany = repr([{"imie": "Ola", "punkty": 4}, {"imie": "Kuba, 3TI", "punkty": 2}])
    if not r["ok"]:
        braki.append("wczytaj_ranking: " + opis_wyniku(r, katalog))
    elif r["wynik"] != oczekiwany:
        braki.append(f"wczytaj_ranking ma zwrócić listę słowników z kluczami imie i punkty (int), np. "
                     f"{oczekiwany[:60]}..., a zwraca {r['wynik'][:80]}")
    r = w["uszkodzony"]
    if not r["ok"]:
        braki.append(f"wczytaj_ranking wywraca się na wierszu z punktami „abc” ({r['typ']}) - pomiń taki wiersz")
    elif r["wynik"] != repr([{"imie": "Ela", "punkty": 3}]):
        braki.append(f"z pliku z jednym uszkodzonym wierszem wczytaj_ranking ma zwrócić tylko dobry wiersz, "
                     f"a zwraca {r['wynik'][:80]}")
    return raport.etap(opis, braki)


def etap_print(raport, katalog):
    braki = []
    for plik in sorted((katalog / "quiz").glob("*.py")):
        if plik.name in ("main.py", "__main__.py"):
            continue
        for linia, nazwa in straznik.wywolania(plik, {"print", "input"}):
            braki.append(f"quiz/{plik.name}, linia {linia}: {nazwa}() - w pakiecie z graczem rozmawia tylko "
                         "quiz/main.py; pozostałe moduły zwracają wartości albo zgłaszają wyjątki")
    return raport.etap("print() i input() tylko w quiz/main.py", braki[:6])


def uruchom_testy(katalog):
    return straznik.uruchom([sys.executable, "-m", "unittest", "-v"], katalog, limit=60)


def bloki_bledow(err):
    """Lista (nazwa testu, opis) z wyjścia unittest."""
    wynik = []
    czesci = re.split(r"^={50,}\n", err, flags=re.M)
    for czesc in czesci[1:]:
        m = re.match(r"(FAIL|ERROR): (\S+) \(([^)]*)\)", czesc)
        if not m:
            continue
        tresc = czesc.split("-" * 70, 1)[-1]
        tresc = re.split(r"^-{50,}\nRan ", tresc, flags=re.M)[0]
        wynik.append((m.group(2), m.group(3), tresc))
    return wynik


def etap_testy(raport, baza, projekt):
    braki = []
    tp, tq = projekt / "testy" / "test_punkty.py", projekt / "testy" / "test_pytania.py"
    kopia = baza / "testy"
    straznik.kopiuj_katalog(projekt, kopia)
    wynik = uruchom_testy(kopia)
    m = re.search(r"^Ran (\d+) tests? in", wynik.err, re.M)
    if wynik.czas_minal:
        return raport.etap("testy: python3 -m unittest -v", ["testy nie skończyły się w 60 s"])
    if not m:
        return raport.etap("testy: python3 -m unittest -v", [straznik.opisz_przebieg(wynik, kopia) or "brak wyniku"])
    ile = int(m.group(1))
    for nazwa, klasa, tresc in bloki_bledow(wynik.err):
        if "_FailedTest" in klasa:
            braki.append(f"nie da się zaimportować pliku z testami {nazwa}: " + straznik.opisz_blad(tresc, kopia)
                         + importy_bez_pakietu(tresc))
        else:
            typ, komunikat, _ = straznik.rozbierz_traceback(tresc)
            braki.append(f"test {nazwa} nie przechodzi: {typ}: {komunikat}")
    if ile == 0:
        braki.append("unittest nie znalazł testów - czy testy/ ma (pusty) plik __init__.py, pliki nazywają się "
                     "test_*.py, a metody test_...? Uruchamiaj z katalogu projektu")
    elif ile < 5 and not braki:
        braki.append(f"uruchomionych testów: {ile}, a ma być co najmniej 5 (test_punkty.py i test_pytania.py)")
    if braki:
        return raport.etap("testy: python3 -m unittest -v", braki)
    tekst_p = tp.read_text(encoding="utf-8", errors="replace")
    tekst_q = tq.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"assertRaises\(\s*ValueError", tekst_p):
        braki.append("testy/test_punkty.py: brakuje testu z assertRaises(ValueError) dla list różnej długości")
    if not re.search(r"assertRaises\(\s*(?:\w+\.)*BladPytania", tekst_q):
        braki.append("testy/test_pytania.py: brakuje testów złych pytań z assertRaises(BladPytania)")
    for nazwa, plik, dopisek, co in (("punkty", "quiz/punkty.py", NADPISZ_PUNKTY,
                                      "policz_punkty nie zgłasza ValueError przy listach różnej długości"),
                                     ("pytania", "quiz/pytania.py", NADPISZ_PYTANIA,
                                      "sprawdz_pytanie niczego nie sprawdza")):
        zepsuta = baza / f"testy-{nazwa}"
        straznik.kopiuj_katalog(projekt, zepsuta)
        with open(zepsuta / plik, "a", encoding="utf-8") as f:
            f.write(dopisek)
        if uruchom_testy(zepsuta).kod == 0:
            braki.append(f"testy przechodzą nawet wtedy, gdy {co} - dopisz test, który to wyłapie")
    return raport.etap(f"testy: python3 -m unittest -v (uruchomionych: {ile}, wszystkie przechodzą)", braki)


def etap_gra(raport, baza, projekt):
    katalog = baza / "gra"
    straznik.kopiuj_katalog(projekt, katalog)
    (katalog / "dane" / "wyniki.csv").unlink(missing_ok=True)
    (katalog / "dane" / "pytania.json").write_text(json.dumps(KONTROLNE, ensure_ascii=False, indent=2),
                                                   encoding="utf-8")
    braki = []
    wynik = straznik.uruchom([sys.executable, "-m", "quiz"], katalog, GRA, limit=LIMIT)
    awaria = straznik.opisz_przebieg(wynik, katalog, LIMIT)
    if awaria or "Pytanie kontrolne strażnika" not in wynik.out:
        tekst = awaria or ("python3 -m quiz nie pokazał pytań z dane/pytania.json"
                           + ("\n" + straznik.ostatnie_linie(wynik.out, 3) if wynik.out.strip() else ""))
        if re.search(r"quiz[/\\]dane", wynik.out + wynik.err):
            tekst += ("\nŚcieżka prowadzi do quiz/dane/, a dane leżą w katalogu projektu. main.py jest w quiz/, "
                      "więc katalog projektu to Path(__file__).parent.parent")
        braki.append(tekst + importy_bez_pakietu(wynik.err))
        if "EOFError" in tekst or wynik.czas_minal:
            braki.append("strażnik wpisał po kolei: " + ", ".join(GRA) + " (README: „Jak gra strażnik”)")
    else:
        plik = katalog / "dane" / "wyniki.csv"
        if not plik.is_file() or "Gracz Paczka" not in plik.read_text(encoding="utf-8", errors="replace"):
            braki.append("po rundzie nie ma wyniku w dane/wyniki.csv (main() ma wywołać zapisz_wynik z quiz.wyniki)")
        elif "Gracz Paczka" not in straznik.uruchom([sys.executable, "-m", "quiz"], katalog, ["2", "0"], limit=LIMIT).out:
            braki.append("po ponownym uruchomieniu opcja 2 (Ranking) nie pokazuje zapisanego wyniku "
                         "(na starcie main(): ranking = wczytaj_ranking(PLIK_WYNIKOW))")
    if not braki:
        zle = [dict(KONTROLNE[0]) for _ in range(7)]
        zle[ZLE_PYTANIE - 1] = dict(zle[0], poprawna=7)
        (katalog / "dane" / "pytania.json").write_text(json.dumps(zle, ensure_ascii=False, indent=2), encoding="utf-8")
        wynik = straznik.uruchom([sys.executable, "-m", "quiz"], katalog, GRA_BLAD, limit=LIMIT)
        if wynik.traceback or wynik.czas_minal:
            braki.append(f"plik z pytaniem nr {ZLE_PYTANIE} w złym formacie wywraca quiz: "
                         + straznik.opisz_przebieg(wynik, katalog, LIMIT)
                         + "\nmain() ma złapać BladQuizu (except BladQuizu as blad) i wypisać przyjazny komunikat")
        elif not re.search(rf"\b{ZLE_PYTANIE}\b", wynik.out):
            braki.append(f"przy złym pytaniu nr {ZLE_PYTANIE} quiz ma wypisać komunikat z numerem tego pytania")
        (katalog / "dane" / "pytania.json").unlink()
        wynik = straznik.uruchom([sys.executable, "-m", "quiz"], katalog, GRA_BLAD, limit=LIMIT)
        if wynik.traceback or wynik.czas_minal:
            braki.append("brak pliku dane/pytania.json wywraca quiz: " + straznik.opisz_przebieg(wynik, katalog, LIMIT))
        elif not wynik.out.strip():
            braki.append("gdy nie ma pliku z pytaniami, quiz ma wypisać przyjazny komunikat")
    return raport.etap("python3 -m quiz: gra, ranking, złe pytanie i brak pliku bez wywrotki", braki)


def main():
    argumenty = [a for a in sys.argv[1:] if not a.startswith("--")]
    bez_gry = "--bez-gry" in sys.argv[1:]
    projekt = Path(argumenty[0]).expanduser().resolve() if argumenty else CWICZENIE / "projekt"
    raport = straznik.Raport("STRAŻNIK PACZEK (ćwiczenie 04)")
    print(f"Sprawdzam: {projekt}")
    if not projekt.is_dir():
        raport.popraw("katalog projektu", ["nie ma katalogu projekt/ - zacznij od kroku 0: cp -r start projekt"
                                           if not argumenty else f"nie ma katalogu {projekt}"])
        return raport.koniec("")
    brak = [p for p in WYMAGANE if not (projekt / p).is_file()]
    twarde = [f"brakuje: {straznik.skrot_listy(brak, 6)}"] if brak else []
    for plik in sorted(projekt.glob("quiz/*.py")) + sorted(projekt.glob("testy/*.py")):
        skladnia = straznik.blad_skladni(plik, projekt)
        if skladnia:
            twarde.append(skladnia)
    miekkie = []
    if (projekt / "quiz.py").exists():
        miekkie.append("w katalogu projektu został stary quiz.py - kod jest już w pakiecie quiz/, usuń go")
    raport.etap("struktura projektu: pakiet quiz/, dane/ i testy/", twarde + miekkie)
    if twarde:
        raport.czeka("reszta (sprawdzę, gdy wszystkie pliki będą na miejscu i bez błędów składni)")
        return raport.koniec("")

    with tempfile.TemporaryDirectory(prefix="straznik-04-") as tmp:
        baza = Path(tmp)
        kopia = baza / "kontrola"
        straznik.kopiuj_katalog(projekt, kopia)
        (baza / "_straznik_kontrola.py").write_text(KONTROLA, encoding="utf-8")
        wynik = straznik.uruchom([sys.executable, baza / "_straznik_kontrola.py", kopia, baza / "raport.json"],
                                 kopia, limit=LIMIT)
        try:
            W = json.loads((baza / "raport.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raport.popraw("kontrola modułów", [straznik.opisz_przebieg(wynik, kopia, LIMIT) or "brak wyniku kontroli"])
            return raport.koniec("")
        importy_ok = etap_importy(raport, W, kopia)
        etap_wyjatki(raport, W, kopia)
        etap_punkty(raport, W, kopia)
        etap_pytania(raport, W, kopia)
        etap_wyniki(raport, W, kopia)
        etap_print(raport, projekt)
        etap_testy(raport, baza, projekt)
        if bez_gry:
            print("  --      gra pominięta (--bez-gry)")
        elif importy_ok:
            etap_gra(raport, baza, projekt)
        else:
            raport.czeka("python3 -m quiz (sprawdzę, gdy wszystkie moduły będą się importować)")
    return raport.koniec("Quiz spakowany: pakiet quiz z modułami bledy, pytania, punkty, wyniki i main, testy "
                         "zielone. Teraz to samo w repozytorium zespołu - ostatnia część README.")


if __name__ == "__main__":
    sys.exit(main())
