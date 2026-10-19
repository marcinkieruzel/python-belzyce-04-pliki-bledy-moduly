![Logotypy: Fundusze Europejskie dla Lubelskiego, Rzeczpospolita Polska, Dofinansowane przez Unię Europejską, Lubelskie](materialy/logotypy-fe.png)

Projekt „Czas zawodowców” współfinansowany przez Unię Europejską w ramach Europejskiego Funduszu Społecznego Plus

# Moduł 4 — Pliki, błędy i moduły

**Kurs „Python Developer”** · Bełżyce · zajęcia 10 i 30 listopada 2026

Ćwiczenia do czwartego modułu kursu. Uratujesz uszkodzony eksport ocen z e-dziennika, nauczysz quiz zapamiętywać pytania i wyniki w plikach, napiszesz testy, które złapią zepsuty kod, i podzielisz quiz na pakiet z modułami — tak jak będzie wyglądał w projekcie końcowym.

## Jak pobrać ćwiczenia

W terminalu, w katalogu domowym:

```bash
cd ~
git clone https://github.com/marcinkieruzel/python-belzyce-04-pliki-bledy-moduly.git
cd python-belzyce-04-pliki-bledy-moduly
```

Jeśli nie masz Gita, pobierz repozytorium jako ZIP: zielony przycisk **Code** → **Download ZIP**, a potem rozpakuj je w katalogu domowym. Polecenia w ćwiczeniach zakładają, że repozytorium leży w `~/python-belzyce-04-pliki-bledy-moduly`.

## Ćwiczenia

| Nr | Ćwiczenie | Co ćwiczysz | Czas | Dzień |
| --- | --- | --- | --- | --- |
| 01 | [Dziennik z błędami](01-dziennik-z-bledami/) — CSV z uszkodzonymi wierszami | `open`, `with`, `csv.DictReader` i `csv.writer`, `try` / `except` / `else`, `raise ValueError`, `Path(__file__).parent` | ok. 45 min | 1 (10.11) |
| 02 | [Quiz na dysku](02-quiz-na-dysku/) — projekt końcowy, część 1 | `json.dump` / `json.load`, dopisywanie do CSV, pętla z `try`, `sys.exit`, ścieżki od pliku programu | ok. 50 min | 1 (10.11) |
| 03 | [Łowcy pluskiew](03-lowcy-pluskiew/) — testy, które łapią błędy | `unittest`, `assertEqual`, `assertRaises`, przypadki brzegowe | ok. 25 min | 2 (30.11) |
| 04 | [Quiz w paczkach](04-quiz-w-paczkach/) — projekt końcowy, część 2 | moduły i pakiety, `__init__.py`, `__main__.py`, `python3 -m`, własne wyjątki, testy pakietu | ok. 30 min + dokończenie w zespołach | 2 (30.11) |

Ćwiczenia robisz po kolei. Wszystko działa w terminalu Linuksa (na zajęciach: Ubuntu) z Pythonem 3.10 lub nowszym, bez instalowania dodatkowych bibliotek.

Każde ćwiczenie ma strażnika — skrypt `sprawdz.py`. Uruchamiasz go w folderze ćwiczenia (`python3 sprawdz.py`), a on uruchamia twój program, sprawdza wyniki i mówi po ludzku, czego jeszcze brakuje. Twoich plików nie poprawia i nie zdradza rozwiązania.

## Przed zajęciami 30 listopada

Między zajęciami są trzy tygodnie przerwy. Przed drugim dniem pobierz poprawki ćwiczeń:

```bash
cd ~/python-belzyce-04-pliki-bledy-moduly
git add -A
git commit -m "Moje rozwiązania z 10 listopada"
git pull
```

Commit zabezpiecza twoje rozwiązania, zanim Git dociągnie zmiany. Pliki, które tworzą programy z ćwiczeń (`wyniki/`, `dane/wyniki.csv`), są w `.gitignore`, więc `git pull` ich nie ruszy.

## Co jest w repozytorium

- `01-dziennik-z-bledami/` … `04-quiz-w-paczkach/` — ćwiczenia; każde ma własne `README.md` z instrukcją i strażnika `sprawdz.py`.
- `materialy/` — pliki wspólne: logotypy projektu i `straznik.py`, wspólny kod strażników (nie musisz go czytać).
- `.gitignore` — lista plików, których Git ma nie śledzić: środowiska `.venv/`, `__pycache__/` i pliki wynikowe ćwiczeń.
