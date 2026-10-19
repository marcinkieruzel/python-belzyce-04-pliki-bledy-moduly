![Logotypy: Fundusze Europejskie dla Lubelskiego, Rzeczpospolita Polska, Dofinansowane przez Unię Europejską, Lubelskie](../materialy/logotypy-fe.png)

Projekt „Czas zawodowców” współfinansowany przez Unię Europejską w ramach Europejskiego Funduszu Społecznego Plus

# 02. Quiz na dysku — projekt końcowy, część 1

Quiz z modułu 3 działa, ale ma dwie wady. Pytania siedzą w kodzie, więc żeby dopisać pytanie, trzeba grzebać w Pythonie i łatwo przy tym coś zepsuć. A ranking znika, gdy zamkniesz program — jutro nikt nie uwierzy, że miałeś 5 na 5.

W tym ćwiczeniu quiz zacznie korzystać z dysku: pytania przeczyta z pliku JSON, który da się edytować w zwykłym edytorze, a każdy wynik dopisze do pliku CSV. Ten sam plik CSV wykorzystasz w module 6 do wykresów.

**Czas:** ok. 50 minut · **Dzień 1** (10.11) · element projektu końcowego: pytania z pliku JSON, wyniki w CSV

## Start

```bash
cd ~/python-belzyce-04-pliki-bledy-moduly/02-quiz-na-dysku
python3 quiz.py
code .
```

W folderze są:

- `quiz.py` — quiz w stanie z końca modułu 3: menu, rozgrywka, ranking z bieżącej sesji. Ten plik rozbudowujesz.
- `pytania.py` — baza 14 pytań z modułu 3 (lista `PYTANIA`). Po kroku 2 quiz przestanie jej używać.
- `dane/` — pusty katalog na pliki z danymi.
- `sprawdz.py` — strażnik. Nie zmieniaj go.

Pytanie ma ten sam format co w modułach 2 i 3: `{"pytanie": tekst, "odpowiedzi": [4 teksty], "poprawna": 0–3, "kategoria": tekst}`. `poprawna` to indeks liczony od 0, a gracz wpisuje numer od 1 do 4.

## Krok 1. Pytania do pliku JSON

Napisz skrypt `eksportuj.py`, który zapisze listę `PYTANIA` z `pytania.py` do pliku `dane/pytania.json` — z polskimi literami (nie `ą`) i z wcięciami, żeby plik dało się czytać. Uruchom go **raz**:

```bash
python3 eksportuj.py
```

Otwórz `dane/pytania.json` w VS Code i dopisz na końcu listy **dwa własne pytania** — w pliku ma być co najmniej 16.

> Każde kolejne uruchomienie `eksportuj.py` nadpisze plik razem z twoimi pytaniami. Od teraz bazę pytań edytujesz w pliku JSON.

<details>
<summary>Podpowiedź 1</summary>

```python
import json

from pytania import PYTANIA

with open("dane/pytania.json", "w", encoding="utf-8") as plik:
    json.dump(PYTANIA, plik, ensure_ascii=False, indent=2)
```

`ensure_ascii=False` zostawia polskie litery, `indent=2` rozpisuje każde pole w osobnej linii.
</details>

<details>
<summary>Podpowiedź 2</summary>

Najprościej dopisać pytanie tak: zaznacz ostatnie pytanie od `{` do `}`, skopiuj, wstaw za nim przecinek i wklej, potem zmień treść. Między pytaniami musi być przecinek, a po ostatnim — nie. Teksty są w podwójnym cudzysłowie, liczby (`"poprawna": 2`) bez cudzysłowu.
</details>

## Krok 2. Quiz czyta pytania z pliku

1. W `quiz.py` napisz funkcję `wczytaj_pytania(sciezka)`, która zwraca listę pytań wczytaną `json.load`.
2. Gdy pliku nie ma, funkcja wypisuje przyjazny komunikat ze ścieżką do pliku i kończy program: `sys.exit(1)`. Gdy plik jest uszkodzony (`json.JSONDecodeError`), komunikat podaje numer linii z błędem: `blad.lineno`. Żadnego tracebacku.
3. Usuń `from pytania import PYTANIA`. W `main()` wczytaj pytania na samym początku i przekaż je do `rozegraj(pytania)`; liczbę pytań w rundzie (do wypisania wyniku) licz z tej listy.

Sprawdź oba błędy: zmień na chwilę nazwę pliku (`mv dane/pytania.json dane/x.json`, potem z powrotem), a potem usuń w nim jeden przecinek.

<details>
<summary>Podpowiedź 1</summary>

```python
try:
    with open(sciezka, encoding="utf-8") as plik:
        return json.load(plik)
except FileNotFoundError:
    ...
```

Jeden `try` może mieć kilka bloków `except` — każdy dla innego wyjątku.
</details>

<details>
<summary>Podpowiedź 2</summary>

`except json.JSONDecodeError as blad:` daje dostęp do szczegółów: `blad.lineno` (linia), `blad.colno` (kolumna), `blad.msg` (co Pythonowi nie pasuje). `sys.exit(1)` kończy program z kodem 1 — tak w Linuksie zgłasza się, że coś poszło źle (dodaj `import sys`).
</details>

## Krok 3. Wyniki do pliku CSV

Napisz `zapisz_wynik(sciezka, imie, punkty, maks)`, która **dopisuje** jeden wiersz na końcu `dane/wyniki.csv`:

- kolumny oddzielone przecinkiem, nagłówek `data,imie,punkty,maks` — zapisany tylko wtedy, gdy pliku jeszcze nie ma,
- data i godzina gry: `datetime.now().isoformat(timespec="seconds")`, np. `2026-11-10T09:41:07`,
- zapis przez `csv.writer` — gracz może wpisać imię z przecinkiem (spróbuj: `Ola, 3TI`).

W `main()` wywołaj ją zaraz po rozegraniu rundy.

<details>
<summary>Podpowiedź 1</summary>

Tryb `"a"` (*append*) dopisuje na końcu pliku, a gdy pliku nie ma — tworzy go. Tryb `"w"` za każdym razem zaczyna od pustego pliku. Czy plik istnieje, sprawdzisz przed otwarciem: `sciezka.exists()`.
</details>

<details>
<summary>Podpowiedź 2</summary>

```python
nowy_plik = not sciezka.exists()
with open(sciezka, "a", encoding="utf-8", newline="") as plik:
    pisarz = csv.writer(plik)
    if nowy_plik:
        pisarz.writerow(["data", "imie", "punkty", "maks"])
    ...
```

`from datetime import datetime` na górze pliku.
</details>

## Krok 4. Ranking z pliku

Napisz `wczytaj_ranking(sciezka)`, która czyta `dane/wyniki.csv` przez `csv.DictReader` i zwraca listę słowników `{"imie": ..., "punkty": ...}` — dokładnie taką, jakiej używa `pokaz_ranking` z modułu 3. Punkty zamieniaj na `int`.

- Wiersz, którego punktów nie da się zamienić na liczbę (ktoś grzebał w pliku), pomiń: `try` / `except ValueError` przy `int(...)`.
- Gdy pliku jeszcze nie ma, zwróć pustą listę — wtedy ranking napisze „Ranking jest pusty — zagraj pierwszy!”.

W `main()` zamień `ranking = []` na `ranking = wczytaj_ranking(PLIK_WYNIKOW)`, a po `zapisz_wynik` odśwież ranking tak samo. `dodaj_wynik` nie jest już potrzebna — możesz ją usunąć. Zmień też ostatnią linię zasad, bo ranking nie znika już po wyjściu z programu. `pokaz_ranking` zostaje bez zmian.

<details>
<summary>Podpowiedź 1</summary>

```python
with open(sciezka, encoding="utf-8", newline="") as plik:
    for wiersz in csv.DictReader(plik):
        print(wiersz)      # {"data": "...", "imie": "Ola", "punkty": "3", "maks": "5"} - same teksty
```

Wszystko, co przychodzi z pliku, jest tekstem — dlatego `int(...)`. Bez tego ranking posortuje punkty jak teksty i „10” wyląduje za „3”.
</details>

<details>
<summary>Podpowiedź 2</summary>

`continue` w `except` przechodzi do następnego wiersza. Wiersz z brakującą kolumną da w `DictReader` wartość `None`, a `int(None)` to `TypeError` — jeśli chcesz być odporny i na to, łap oba: `except (ValueError, TypeError):`.
</details>

## Krok 5. Quiz działa z każdego katalogu

Wejdź do katalogu domowego i uruchom quiz stamtąd:

```bash
cd ~
python3 python-belzyce-04-pliki-bledy-moduly/02-quiz-na-dysku/quiz.py
```

Jeśli quiz nie znajduje pytań — ścieżka `dane/pytania.json` liczy się od katalogu, w którym stoisz w terminalu, a nie od pliku `quiz.py`. Zbuduj ścieżki od pliku programu:

```python
from pathlib import Path

KATALOG = Path(__file__).parent
PLIK_PYTAN = KATALOG / "dane" / "pytania.json"
PLIK_WYNIKOW = KATALOG / "dane" / "wyniki.csv"
```

To samo zrób w `eksportuj.py`.

## Oczekiwany wynik

Gra po wszystkich krokach (wcześniej w pliku były już wyniki Kuby i Natalii; pytania są losowane, więc u ciebie będą inne):

<!-- wynik:02-sesja -->
```text
$ python3 quiz.py

###############
# QUIZ WIEDZY #
#             #
# 1) Graj     #
# 2) Ranking  #
# 3) Zasady   #
# 0) Wyjście  #
###############
Twój wybór: 1
Twoje imię: Ola

Pytanie 1/5
[Linux] Co oznacza znak ~ na początku ścieżki, np. ~/projekty?
  1) katalog główny /
  2) katalog domowy użytkownika
  3) katalog nadrzędny
  4) katalog tymczasowy
Twoja odpowiedź: abc
Nie ma takiej opcji. Wpisz jedno z: 1, 2, 3, 4.
Twoja odpowiedź: 7
Nie ma takiej opcji. Wpisz jedno z: 1, 2, 3, 4.
Twoja odpowiedź: 2
Dobrze!

Pytanie 2/5
[Linux] Jakim poleceniem skopiujesz plik w terminalu Linuksa?
  1) mv
  2) rm
  3) cp
  4) cat
Twoja odpowiedź: 3
Dobrze!

Pytanie 3/5
[Python] Co wypisze print(7 // 2)?
  1) 3.5
  2) 3
  3) 4
  4) 3.0
Twoja odpowiedź: 1
Źle. Poprawna odpowiedź: 3

Pytanie 4/5
[Python] Który moduł Pythona czyta i zapisuje pliki JSON?
  1) csv
  2) json
  3) pickle
  4) os
Twoja odpowiedź: 4
Źle. Poprawna odpowiedź: json

Pytanie 5/5
[informatyka] Ile bitów ma bajt?
  1) 4
  2) 8
  3) 16
  4) 32
Twoja odpowiedź: 2
Dobrze!

Ola: 3/5 pkt

###############
# QUIZ WIEDZY #
#             #
# 1) Graj     #
# 2) Ranking  #
# 3) Zasady   #
# 0) Wyjście  #
###############
Twój wybór: 2

RANKING
 1. Kuba            4 pkt
 2. Ola             3 pkt
 3. Natalia         2 pkt

###############
# QUIZ WIEDZY #
#             #
# 1) Graj     #
# 2) Ranking  #
# 3) Zasady   #
# 0) Wyjście  #
###############
Twój wybór: 0
Do zobaczenia!
```
<!-- /wynik -->

`dane/wyniki.csv` po tej grze:

<!-- wynik:02-wyniki -->
```text
data,imie,punkty,maks
2026-11-10T08:21:05,Kuba,4,5
2026-11-10T08:24:47,Natalia,2,5
2026-11-10T09:41:07,Ola,3,5
```
<!-- /wynik -->

Uszkodzony plik z pytaniami (brak przecinka) i brak pliku:

<!-- wynik:02-zepsuty -->
```text
$ python3 quiz.py
Plik pytania.json jest uszkodzony: linia 176, kolumna 5 (Expecting ',' delimiter).
```
<!-- /wynik -->

<!-- wynik:02-brak -->
```text
$ python3 quiz.py
Nie znalazłem pliku z pytaniami: /home/uczen/python-belzyce-04-pliki-bledy-moduly/02-quiz-na-dysku/dane/pytania.json
```
<!-- /wynik -->

## Jak gra strażnik

```bash
python3 sprawdz.py
```

Strażnik sprawdza twój `dane/pytania.json`, a potem kopiuje `quiz.py` do katalogu tymczasowego z trzema własnymi pytaniami kontrolnymi (w każdym poprawna jest odpowiedź 1) i gra za ciebie. Wpisuje odpowiedzi po kolei, w takim porządku:

1. `1` (Graj), potem imię, np. `Testowy Gracz`,
2. na każde pytanie numer odpowiedzi; na pierwsze najpierw `abc` i `9`, które quiz ma odrzucić i zapytać jeszcze raz,
3. po rundzie `2` (Ranking), a na koniec `0` (Wyjście).

Dlatego quiz po wybraniu `1` pyta tylko o imię, po rundzie wraca do menu i nie pyta o nic więcej (np. „Zagrać jeszcze raz?”). Strażnik gra kilka razy: sprawdza dopisywanie do `dane/wyniki.csv`, ranking z podłożonego pliku z uszkodzonymi wierszami, brak pliku z wynikami, brak i uszkodzenie pliku z pytaniami, a na końcu uruchamia quiz z innego katalogu. Twoje pliki w `dane/` zostają nietknięte.
