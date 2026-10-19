![Logotypy: Fundusze Europejskie dla Lubelskiego, Rzeczpospolita Polska, Dofinansowane przez Unię Europejską, Lubelskie](../materialy/logotypy-fe.png)

Projekt „Czas zawodowców” współfinansowany przez Unię Europejską w ramach Europejskiego Funduszu Społecznego Plus

# 01. Dziennik z błędami

Poniedziałek, 7:50. W weekend padł serwer e-dziennika. Informatyk odzyskał z kopii eksport ocen klasy 3TI z września i października, ale plik jest poharatany: w jednych wierszach zamiast oceny jest „nb” albo „piątka”, w innych brakuje pola, ktoś wkleił wiersz z przecinkami, a w środku pliku powtarza się nagłówek.

Wychowawczyni, pani Lis, potrzebuje na jutrzejszą radę klasyfikacyjną dwóch rzeczy: średnich każdego ucznia z każdego przedmiotu i listy wierszy, które sekretariat musi poprawić ręcznie. Ręcznie tego nie zrobi — napisz program, który zrobi to za nią i nie wywróci się na pierwszym zepsutym wierszu.

**Czas:** ok. 45 minut · **Dzień 1** (10.11) — krok 1 po części o CSV, kroki 2–4 po części o błędach

## Start

```bash
cd ~/python-belzyce-04-pliki-bledy-moduly/01-dziennik-z-bledami
code .
```

W folderze są:

- `dane/oceny.csv` — eksport ocen: kodowanie UTF-8, separator `;`, nagłówek `uczen;przedmiot;ocena;data`. Obejrzyj go w VS Code — numery linii po lewej przydadzą się w kroku 1.
- `dziennik.py` — twój program. Stałe ze ścieżkami i funkcja `main()` są gotowe; funkcje z komentarzem `# Twój kod` piszesz ty.
- `sprawdz.py` — strażnik. Nie zmieniaj go.

Zasady dziennika:

- Wiersz jest **dobry**, gdy ma dokładnie 4 pola, a ocena to liczba całkowita od 1 do 6. Spacje wokół oceny są w porządku: `" 5 "` to 5.
- Każdy inny wiersz trafia do **odrzuconych** razem z numerem linii w pliku (nagłówek to linia 1) i powodem.
- Puste linie pomijasz bez zgłaszania — `csv.DictReader` robi to sam.

## Krok 1. Wczytaj i policz (po części o CSV)

Napisz `wczytaj_oceny(sciezka)` i `policz_srednie(oceny)` w najprostszej wersji: otwórz plik, czytaj go `csv.DictReader(plik, delimiter=";")`, każdą ocenę zamień `int(...)` i dopisz do listy `oceny` jako krotkę `(uczen, przedmiot, ocena)`. `policz_srednie` ma zwrócić słownik `{(uczen, przedmiot): (srednia, liczba_ocen)}`.

Uruchom `python3 dziennik.py`. Program się wysypie — to zamierzone. Zapisz (w zeszycie albo w komentarzu na górze `dziennik.py`): **numer linii pliku z ocenami**, na której się wysypał, i **nazwę wyjątku** z ostatniej linii komunikatu.

<details>
<summary>Podpowiedź 1</summary>

Plik CSV otwieraj zawsze z kodowaniem i bez tłumaczenia końców linii:

```python
with open(sciezka, encoding="utf-8", newline="") as plik:
    czytnik = csv.DictReader(plik, delimiter=";")
    for wiersz in czytnik:
        print(wiersz)       # słownik: {"uczen": ..., "przedmiot": ..., "ocena": ..., "data": ...}
```

`with` sam zamknie plik, nawet gdy program się wysypie.
</details>

<details>
<summary>Podpowiedź 2</summary>

Średnią policzysz w dwóch przejściach: najpierw zbierz oceny w słowniku list, potem podziel sumę przez długość.

```python
zebrane = {}
for uczen, przedmiot, ocena in oceny:
    zebrane.setdefault((uczen, przedmiot), []).append(ocena)
```

`setdefault` wstawia pustą listę, gdy klucza jeszcze nie ma, i zwraca listę spod klucza.
</details>

<details>
<summary>Podpowiedź 3</summary>

Numer linii pliku, którą `DictReader` właśnie przeczytał, jest w `czytnik.line_num`. Wypisz go w pętli przed `int(...)`: `print(czytnik.line_num, wiersz["ocena"])` — ostatni wypisany numer to linia, na której program się wysypał.
</details>

## Krok 2. Wyłap błędy (po części o wyjątkach)

1. Napisz `zamien_na_ocene(tekst)`: zwraca ocenę jako `int` albo zgłasza `ValueError` z czytelnym powodem — osobnym dla pustej oceny, dla tekstu, który nie jest liczbą, i dla liczby spoza skali.
2. Napisz `sprawdz_pola(wiersz)`: zgłasza `ValueError`, gdy wiersz nie ma dokładnie 4 pól.
3. W pętli w `wczytaj_oceny` obie funkcje wywołaj w `try`. W `except ValueError as blad:` dopisz do listy `odrzucone` krotkę `(czytnik.line_num, str(blad), tresc_wiersza(wiersz))`. W `else:` dopisz ocenę do listy `oceny`.

Uruchom `python3 dziennik.py` — tym razem program ma przejść przez cały plik i wypisać, ile ocen wczytał, a ile wierszy odrzucił.

<details>
<summary>Podpowiedź 1</summary>

`raise` zgłasza wyjątek z twoim opisem, a `except ... as blad` go łapie — `str(blad)` to ten opis:

```python
if not 1 <= ocena <= 6:
    raise ValueError(f"ocena spoza skali 1-6: {ocena}")
```

Blok `else` po `try` wykonuje się tylko wtedy, gdy w `try` nie było wyjątku — tam dopisuj dobre oceny.
</details>

<details>
<summary>Podpowiedź 2</summary>

`int("nb")` sam zgłasza `ValueError`, ale z angielskim opisem. Złap go i zgłoś własny:

```python
try:
    ocena = int(tekst)
except ValueError:
    raise ValueError(f"ocena to nie liczba całkowita: {tekst!r}")
```
</details>

<details>
<summary>Podpowiedź 3</summary>

Jeśli program wysypuje się teraz z `AttributeError` albo `TypeError` i słowem `NoneType` — to wiersz z za małą liczbą pól. `DictReader` brakującym polom wpisuje `None`, a nadmiarowe pola odkłada na listę pod kluczem `None`. Dlatego `sprawdz_pola` wystarczy:

```python
if None in wiersz:            # są nadmiarowe pola
    ...
if None in wiersz.values():   # brakuje pól
    ...
```

Wywołaj `sprawdz_pola` przed `zamien_na_ocene`.
</details>

## Krok 3. Zapisz wyniki

1. `zapisz_srednie(sciezka, srednie)` — plik `wyniki/srednie.csv` z nagłówkiem `uczen;przedmiot;srednia;liczba_ocen`, posortowany po uczniu, a potem po przedmiocie, średnia z dwoma miejscami po przecinku.
2. `zapisz_odrzucone(sciezka, odrzucone)` — plik `wyniki/odrzucone.csv` z nagłówkiem `wiersz;powod;tresc`.

Oba pliki zapisuj `csv.writer(plik, delimiter=";")`, tak jak plik z ocenami. Katalog `wyniki/` tworzy już `main()`.

<details>
<summary>Podpowiedź 1</summary>

```python
with open(sciezka, "w", encoding="utf-8", newline="") as plik:
    pisarz = csv.writer(plik, delimiter=";")
    pisarz.writerow(["uczen", "przedmiot", "srednia", "liczba_ocen"])
```

Tryb `"w"` tworzy plik od nowa przy każdym uruchomieniu — tu tego chcemy.
</details>

<details>
<summary>Podpowiedź 2</summary>

`sorted(srednie.items())` sortuje pary `((uczen, przedmiot), (srednia, liczba))` po kluczu, czyli najpierw po uczniu, potem po przedmiocie. Dwa miejsca po przecinku: `f"{srednia:.2f}"`.
</details>

<details>
<summary>Podpowiedź 3</summary>

`csv.writer` sam weźmie w cudzysłów pole, w którym jest średnik — dlatego treść odrzuconego wiersza zapisuj przez `writerow` / `writerows`, a nie sklejaj tekstu ręcznie.
</details>

## Oczekiwany wynik

W konsoli:

<!-- wynik:01-konsola -->
```text
$ python3 dziennik.py
Wczytano ocen: 64. Odrzucono wierszy: 10.
Średnie: wyniki/srednie.csv, do ręcznej poprawy: wyniki/odrzucone.csv
```
<!-- /wynik -->

Początek `wyniki/srednie.csv`:

<!-- wynik:01-srednie -->
```text
uczen;przedmiot;srednia;liczba_ocen
Adamczyk Oliwia;fizyka;5.00;1
Adamczyk Oliwia;informatyka;4.00;1
Adamczyk Oliwia;język angielski;6.00;1
Adamczyk Oliwia;matematyka;5.50;2
Banaś Kacper;fizyka;3.50;2
Banaś Kacper;informatyka;3.00;2
... (razem 40 wierszy z danymi)
```
<!-- /wynik -->

Cały `wyniki/odrzucone.csv` (powody mogą brzmieć inaczej — ważne są numery wierszy):

<!-- wynik:01-odrzucone -->
```text
wiersz;powod;tresc
16;ocena to nie liczba całkowita: 'nb';"Dudek Szymon;fizyka;nb;2026-09-16"
21;ocena spoza skali 1-6: 7;"Dudek Szymon;matematyka;7;2026-09-17"
24;za mało pól: 3 zamiast 4;"Dudek Szymon;matematyka;6"
28;pusta ocena;"Pawlak Hanna;język angielski;;2026-09-21"
31;za mało pól: 1 zamiast 4;Pawlak Hanna,fizyka,5,2026-09-25
37;ocena to nie liczba całkowita: 'ocena';"uczen;przedmiot;ocena;data"
40;ocena to nie liczba całkowita: 'piątka';"Dudek Szymon;fizyka;piątka;2026-09-30"
56;za dużo pól: 5 zamiast 4;"Adamczyk Oliwia;informatyka;3;2026-10-15;poprawa"
63;ocena spoza skali 1-6: 0;"Banaś Kacper;język angielski;0;2026-10-22"
65;ocena to nie liczba całkowita: '4,5';"Adamczyk Oliwia;język angielski;4,5;2026-10-23"
```
<!-- /wynik -->

## Krok 4. Sprawdź

```bash
python3 sprawdz.py
```

Strażnik uruchamia twój program trzy razy:

1. **w folderze ćwiczenia** — i porównuje `wyniki/srednie.csv` (średnie z dokładnością do 0,01; kropka albo przecinek) i numery wierszy w `wyniki/odrzucone.csv`; stare pliki w `wyniki/` usuwa przed uruchomieniem,
2. **z innego katalogu**, tak jakbyś wpisał `cd ~` i `python3 python-belzyce-04-pliki-bledy-moduly/01-dziennik-z-bledami/dziennik.py` — wtedy wychodzi na jaw, czy ścieżki liczysz od pliku programu (`Path(__file__).parent`), czy od katalogu, w którym stoisz,
3. **na innym dzienniku** — wygenerowanym pliku z innymi uczniami i innymi błędami, żeby sprawdzić, czy program liczy z danych, a nie ma wyników wpisanych na sztywno.

## Dla chętnych: plusy i minusy

Prawdziwy dziennik ma oceny z plusem i minusem. Przyjmij, że plus dodaje pół oceny, a minus odejmuje ćwierć: `4+` = 4,5, `4-` = 3,75. Plus pasuje do ocen 1–5, minus do ocen 2–6 — `6+` i `1-` wychodzą poza skalę i trafiają do odrzuconych.

Rozbuduj `zamien_na_ocene` tak, żeby rozumiała plusy i minusy (zwraca wtedy liczbę z ułamkiem), i sprawdź:

```bash
python3 sprawdz.py --plusy
```

Strażnik podstawi wtedy pod `dane/oceny.csv` plik `dane/oceny-plusy.csv`. Żeby uruchomić program na tym pliku samemu, zmień na chwilę stałą `DANE` na `KATALOG / "dane" / "oceny-plusy.csv"`.

## Gdy coś pójdzie nie tak

- **Zmieniłeś coś w `dane/` przez pomyłkę?** `python3 sprawdz.py --przywroc-dane` odtworzy oba pliki z ocenami.
- **Chcesz zacząć od zera?** `git checkout -- dziennik.py` przywróci plik startowy (twoje zmiany przepadną).
