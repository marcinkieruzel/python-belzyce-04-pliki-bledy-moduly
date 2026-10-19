![Logotypy: Fundusze Europejskie dla Lubelskiego, Rzeczpospolita Polska, Dofinansowane przez Unię Europejską, Lubelskie](../materialy/logotypy-fe.png)

Projekt „Czas zawodowców” współfinansowany przez Unię Europejską w ramach Europejskiego Funduszu Społecznego Plus

# 04. Quiz w paczkach — projekt końcowy, część 2

Po ćwiczeniu 02 quiz to jeden plik na ponad 200 linii: menu, pytania, punkty, pliki — wszystko razem. W zespole trzy osoby edytują ten sam plik, więc co chwilę wchodzą sobie w drogę, a żeby przetestować liczenie punktów, trzeba za każdym razem przeklikać całą grę.

Rozłożysz quiz na **pakiet** — katalog z modułami, z których każdy robi jedną rzecz. Do tego dwa własne wyjątki dla błędów quizu i testy jednostkowe, które sprawdzają punkty i pytania bez uruchamiania gry.

**Czas:** ok. 30 minut na zajęciach, dokończenie w repozytorium zespołu · **Dzień 2** (30.11) · element projektu końcowego: test jednostkowy funkcji liczącej punkty

## Cel

```text
projekt/
├── dane/
│   └── pytania.json
├── quiz/                  pakiet: katalog z plikiem __init__.py
│   ├── __init__.py        pusty albo z docstringiem - oznacza „to jest pakiet”
│   ├── __main__.py        uruchamia main() przy python3 -m quiz
│   ├── bledy.py           class BladQuizu(Exception), class BladPytania(BladQuizu)
│   ├── main.py            menu i rozgrywka - jedyny moduł z print i input
│   ├── punkty.py          czy_poprawna, policz_punkty
│   ├── pytania.py         sprawdz_pytanie, wczytaj_pytania
│   └── wyniki.py          zapisz_wynik, wczytaj_ranking
└── testy/
    ├── __init__.py        pusty
    ├── test_punkty.py
    └── test_pytania.py
```

Uruchamiasz wszystko z katalogu `projekt/`:

```bash
python3 -m quiz            # gra
python3 -m unittest -v     # testy
```

## Dlaczego wcześniej działało `from pytania import PYTANIA`

Gdy uruchamiasz `python3 quiz/main.py`, Python dopisuje na początek listy miejsc, w których szuka modułów (`sys.path`), **katalog uruchomionego pliku** — tu `quiz/`. Dlatego w module 3 `from pytania import PYTANIA` znajdowało `quiz/pytania.py`.

W pakiecie moduły importują się nawzajem z nazwą pakietu: `from quiz.punkty import policz_punkty`. Żeby Python znalazł pakiet `quiz`, szukanie musi zacząć się w katalogu **nad** nim, czyli w `projekt/`. To robi `python3 -m quiz`: przy `-m` na początek `sys.path` trafia katalog, w którym jesteś w terminalu. Stary sposób uruchamiania nie znajdzie już pakietu:

<!-- wynik:04-modulenotfound -->
```text
$ python3 quiz/main.py
Traceback (most recent call last):
  File "/home/uczen/python-belzyce-04-pliki-bledy-moduly/04-quiz-w-paczkach/projekt/quiz/main.py", line 9, in <module>
    from quiz.bledy import BladQuizu
ModuleNotFoundError: No module named 'quiz'
```
<!-- /wynik -->

## Krok 0. Kopia startowa

```bash
cd ~/python-belzyce-04-pliki-bledy-moduly/04-quiz-w-paczkach
cp -r start projekt
cd projekt
python3 quiz.py
```

`start/` to wzorcowy stan po ćwiczeniu 02: jeden plik `quiz.py`, pytania w `dane/pytania.json`, wyniki w `dane/wyniki.csv`. Pracujesz w kopii `projekt/` — `start/` zostaje nietknięty, gdybyś chciał zacząć od nowa.

## Krok 1. Szkielet pakietu

```bash
mkdir quiz testy
touch quiz/__init__.py testy/__init__.py
```

## Krok 2. Własne wyjątki — `quiz/bledy.py`

Utwórz dwie klasy wyjątków: `BladQuizu` (dziedziczy po `Exception`) i `BladPytania` (dziedziczy po `BladQuizu`). Ciało klasy może być samym docstringiem.

<details>
<summary>Podpowiedź</summary>

```python
class BladQuizu(Exception):
    """Błąd, przez który quiz nie może działać."""
```

Skoro `BladPytania` dziedziczy po `BladQuizu`, to `except BladQuizu:` złapie oba — tak jak `except Exception:` łapie prawie wszystko.
</details>

## Krok 3. Punkty — `quiz/punkty.py`

Przenieś z `quiz.py` funkcje `czy_poprawna` i `policz_punkty`. Dopisz do `policz_punkty` jedną rzecz: gdy listy `pytania` i `wybory` mają różną długość, funkcja zgłasza `ValueError`.

## Krok 4. Pytania — `quiz/pytania.py`

1. Napisz `sprawdz_pytanie(pytanie, nr)`: gdy pytanie ma zły format, zgłasza `BladPytania` z numerem pytania i powodem, np. `raise BladPytania(f"pytanie nr {nr}: brakuje klucza „kategoria”")`. Zły format to: brak któregoś z kluczy `pytanie`, `odpowiedzi`, `poprawna`, `kategoria`; inna liczba odpowiedzi niż 4; `poprawna` spoza 0–3.
2. Przenieś `wczytaj_pytania(sciezka)` i zmień ją: zamiast `print` i `sys.exit(1)` zgłasza `BladQuizu` z opisem błędu (brak pliku, uszkodzony JSON), a po wczytaniu wywołuje `sprawdz_pytanie` dla każdego pytania, numerując od 1.

O tym, co pokazać graczowi i czy zakończyć program, decyduje teraz `main()`.

<details>
<summary>Podpowiedź 1</summary>

Najpierw sprawdź klucze, potem resztę — inaczej `pytanie["odpowiedzi"]` przy brakującym kluczu zgłosi `KeyError`, a nie `BladPytania`:

```python
for klucz in ["pytanie", "odpowiedzi", "poprawna", "kategoria"]:
    if klucz not in pytanie:
        raise BladPytania(...)
```
</details>

<details>
<summary>Podpowiedź 2</summary>

```python
except FileNotFoundError:
    raise BladQuizu(f"nie znalazłem pliku z pytaniami: {sciezka}")
```

Numer pytania dla ludzi liczy się od 1: `for nr, pytanie in enumerate(pytania, start=1):`.
</details>

## Krok 5. Wyniki — `quiz/wyniki.py`

Przenieś `zapisz_wynik` i `wczytaj_ranking` razem z nagłówkiem pliku wyników. Tu nic nie zmieniasz.

## Krok 6. Menu i gra — `quiz/main.py` i `quiz/__main__.py`

1. Przenieś do `quiz/main.py` wszystko, co zostało w `quiz.py`: `ramka`, `pokaz_menu`, `wczytaj_wybor`, `zadaj_pytanie`, `rozegraj`, `pokaz_ranking`, `pokaz_zasady` i `main`. Na górze dopisz importy z pakietu, np. `from quiz.punkty import czy_poprawna, policz_punkty`.
2. Popraw ścieżki do danych: `main.py` leży teraz w `quiz/`, a katalog `dane/` jest piętro wyżej — `KATALOG = Path(__file__).parent.parent`.
3. W `main()` wczytanie pytań weź w `try`, złap `BladQuizu`, wypisz przyjazny komunikat i zakończ program `sys.exit(1)`.
4. Utwórz `quiz/__main__.py` z dwiema linijkami: import `main` z `quiz.main` i jej wywołanie.
5. Usuń stary `quiz.py` i zagraj: `python3 -m quiz`.

Zepsuj na chwilę jedno pytanie w `dane/pytania.json` (np. `"poprawna": 7` w trzecim pytaniu) i uruchom quiz jeszcze raz:

<!-- wynik:04-zle-pytanie -->
```text
$ python3 -m quiz
Quiz nie wystartuje: pytanie nr 3: „poprawna” to indeks od 0 do 3, a jest 7
```
<!-- /wynik -->

<details>
<summary>Podpowiedź</summary>

`if __name__ == "__main__": main()` na dole `main.py` nie jest już potrzebne — `main()` wywołuje `__main__.py`. Moduły pakietu przy imporcie mają tylko definiować funkcje i stałe; nic nie wypisują i o nic nie pytają.
</details>

## Krok 7. Testy — `testy/test_punkty.py` i `testy/test_pytania.py`

Napisz co najmniej 5 testów (`unittest`, jak w ćwiczeniu 03), importując funkcje z pakietu (`from quiz.punkty import policz_punkty`):

- `test_punkty.py` — co najmniej 3 testy, w tym `assertRaises(ValueError)` dla list różnej długości,
- `test_pytania.py` — poprawne pytanie przechodzi przez `sprawdz_pytanie` bez wyjątku, a `assertRaises(BladPytania)` łapie: `poprawna` równe 7, tylko 3 odpowiedzi, brak klucza.

```bash
python3 -m unittest -v
```

<details>
<summary>Podpowiedź</summary>

Każdy test psuje własną kopię dobrego pytania — wtedy testy nie wpływają na siebie nawzajem:

```python
def dobre_pytanie():
    return {"pytanie": "Stolica Polski to:", "odpowiedzi": ["Kraków", "Warszawa", "Gniezno", "Poznań"],
            "poprawna": 1, "kategoria": "geografia"}
```
</details>

## Krok 8. Sprawdź

```bash
cd ~/python-belzyce-04-pliki-bledy-moduly/04-quiz-w-paczkach
python3 sprawdz.py
```

Strażnik pracuje na kopii `projekt/` i sprawdza: strukturę, czy moduły importują się bez wypisywania czegokolwiek, wyjątki, funkcje z `punkty.py`, `pytania.py` i `wyniki.py`, czy `print` i `input` są tylko w `main.py`, czy testy przechodzą (i czy łapią zepsute `policz_punkty` oraz `sprawdz_pytanie`), a na końcu gra w `python3 -m quiz`.

**Jak gra strażnik:** podkłada trzy pytania kontrolne i wpisuje po kolei: `1`, imię, `abc` (quiz ma zapytać jeszcze raz), trzy razy `1`, `2` (Ranking), `0`. Potem podkłada plik z błędnym szóstym pytaniem i usuwa plik z pytaniami — quiz ma wtedy wypisać komunikat, a nie traceback.

## W repozytorium zespołu

To samo zróbcie w repozytorium projektu z modułu 1 (np. `~/quiz-o-kosmosie`). Katalogi `quiz/`, `dane/` i `testy/` już tam są, a w `quiz/` leżą `main.py` i `pytania.py` z modułów 2–3.

1. Wszyscy: `git pull`. Jedna osoba przy klawiaturze, reszta czyta i podpowiada; po każdym kroku commit i zamiana miejsc.
2. Najpierw to, co zrobiliście w ćwiczeniu 02: wyeksportujcie `PYTANIA` z `quiz/pytania.py` do `dane/pytania.json` (skrypt jak `eksportuj.py`, ścieżki dopasowane do repo) i dopiszcie `wczytaj_pytania`, `zapisz_wynik` oraz `wczytaj_ranking`. Listę `PYTANIA` z `quiz/pytania.py` usuńcie — zostaną tam `sprawdz_pytanie` i `wczytaj_pytania`. Stary `dane/pytania.txt` z modułu 1 też: `git rm dane/pytania.txt`.
3. Kroki 1–7 z tego ćwiczenia. `testy/.gitkeep` nie jest już potrzebny: `git rm testy/.gitkeep`.
4. Dopiszcie `dane/wyniki.csv` do `.gitignore` — każdy ma swoje wyniki, a wspólny plik w repo dawałby konflikty przy każdym `git pull`.
5. W `README.md` zespołu zmieńcie instrukcję uruchamiania na `python3 -m quiz` i dopiszcie `python3 -m unittest -v`.
6. Sprawdźcie: `python3 ~/python-belzyce-04-pliki-bledy-moduly/04-quiz-w-paczkach/sprawdz.py ~/quiz-o-kosmosie`. Jeśli wasze menu różni się od tego z modułu 3, dodajcie `--bez-gry` — strażnik sprawdzi wtedy wszystko poza graniem.
7. `git push`.

Przykładowe opisy commitów:

```text
Pytania w pliku dane/pytania.json zamiast listy w kodzie
Wyniki graczy zapisywane w dane/wyniki.csv
Pakiet quiz: moduły bledy, pytania, punkty, wyniki i main
Własne wyjątki BladQuizu i BladPytania
Testy jednostkowe punktów i sprawdzania pytań
```
