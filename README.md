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

## Ściąga

### Pliki, CSV i JSON

| Kod | Co robi |
| --- | --- |
| `with open(p, encoding="utf-8") as f:` | otwiera plik i sam go zamyka, także przy błędzie |
| `open(p, "w")` / `open(p, "a")` | zapis od zera (kasuje plik!) / dopisanie na końcu |
| `f.read()` · `for w in f:` · `w.rstrip()` | cały plik jako tekst · wiersz po wierszu · wiersz bez `\n` |
| `Path(__file__).parent / "dane"` | katalog obok programu, niezależnie od tego, skąd go uruchomisz |
| `csv.DictReader(f, delimiter=";")` | wiersze CSV jako słowniki; średnik dla plików z polskiego Excela |
| `csv.DictWriter(f, fieldnames=…)` | zapis słowników; przy `open` dla CSV dodaj `newline=""` |
| `json.load(f)` / `json.dump(o, f, ensure_ascii=False, indent=2)` | plik JSON ↔ obiekt Pythona |
| `json.loads(t)` / `json.dumps(o)` | tekst JSON ↔ obiekt Pythona |

### Wyjątki, moduły i testy

| Kod | Co robi |
| --- | --- |
| `try:` … `except ValueError as e:` | obsługa wybranego wyjątku |
| `else:` / `finally:` | gdy w `try` nie było wyjątku / zawsze, na końcu |
| `raise ValueError("opis")` | zgłoszenie błędu |
| `class BladPytania(Exception):` | własny wyjątek |
| `assert warunek, "opis"` | sprawdzenie własnego założenia (wyłącza je `python3 -O`) |
| `sys.exit("komunikat")` | koniec programu z komunikatem i kodem 1 |
| `import modul` · `from pakiet.modul import f` | import całego modułu · wybranej funkcji |
| `if __name__ == "__main__":` | kod tylko przy uruchomieniu pliku, nie przy imporcie |
| `python3 -m quiz` | uruchomienie pakietu (z katalogu nad nim) |
| `python3 -m unittest -v` | uruchomienie testów `test*.py` |
| `self.assertEqual(a, b)` · `with self.assertRaises(E):` | porównanie w teście · test, że wystąpi wyjątek |

## Co jest w repozytorium

- `01-dziennik-z-bledami/` … `04-quiz-w-paczkach/` — ćwiczenia; każde ma własne `README.md` z instrukcją i strażnika `sprawdz.py`.
- `materialy/` — pliki wspólne: logotypy projektu i `straznik.py`, wspólny kod strażników (nie musisz go czytać).
- `.gitignore` — lista plików, których Git ma nie śledzić: środowiska `.venv/`, `__pycache__/` i pliki wynikowe ćwiczeń.
