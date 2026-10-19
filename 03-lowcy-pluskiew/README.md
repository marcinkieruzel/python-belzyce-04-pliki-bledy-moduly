![Logotypy: Fundusze Europejskie dla Lubelskiego, Rzeczpospolita Polska, Dofinansowane przez Unię Europejską, Lubelskie](../materialy/logotypy-fe.png)

Projekt „Czas zawodowców” współfinansowany przez Unię Europejską w ramach Europejskiego Funduszu Społecznego Plus

# 03. Łowcy pluskiew — testy, które łapią błędy

W zespole Oli punkty w quizie liczy plik `punkty.py`: zwykłe punkty, premia za serię dobrych odpowiedzi i słowna ocena na koniec gry. Ten plik zmienia się co tydzień — ktoś dodaje premię, ktoś poprawia próg, ktoś „tylko przestawia kolejność”. Za każdym razem może przy tym coś zepsuć, a gracze zauważą to dopiero na hackathonie.

Twoje zadanie: napisz testy jednostkowe, które złapią każdą pomyłkę w `punkty.py`. Strażnik ma przygotowanych 9 zepsutych wersji tego pliku — pluskiew. Każda różni się od poprawnej jednym drobiazgiem. Złapiesz pluskwę, gdy choć jeden twój test się na niej wywróci.

**Czas:** ok. 25 minut · **Dzień 2** (30.11)

## Start

```bash
cd ~/python-belzyce-04-pliki-bledy-moduly/03-lowcy-pluskiew
python3 -m unittest -v
python3 sprawdz.py
code .
```

W folderze są:

- `punkty.py` — cztery funkcje: `czy_poprawna`, `policz_punkty`, `punkty_z_seria`, `ocena_slowna`. Kod jest poprawny — **nie zmieniaj go**. Docstringi (opisy w potrójnym cudzysłowie) to specyfikacja: z nich wiesz, co każda funkcja ma zwrócić.
- `test_punkty.py` — twoje testy. Na początku jest jeden przykładowy test i lista przypadków do pokrycia.
- `sprawdz.py` — strażnik. Używa własnej kopii poprawnego `punkty.py`, więc zmiany w `punkty.py` nic mu nie dadzą.

Na starcie:

<!-- wynik:03-unittest-start -->
```text
$ python3 -m unittest -v
test_dobry_wybor_to_true (test_punkty.TestCzyPoprawna.test_dobry_wybor_to_true) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```
<!-- /wynik -->

<!-- wynik:03-sprawdz-start -->
```text
$ python3 sprawdz.py
============================================================
  ŁOWCY PLUSKIEW (ćwiczenie 03)
============================================================
  OK      testy na poprawnym punkty.py: uruchomionych 1, wszystkie przechodzą
  POPRAW  Złapane pluskwy: 1/9
          - pluskwa 2 przeżyła (policz_punkty): brakuje testu na listy pytań i wyborów różnej
            długości (assertRaises)
          - pluskwa 3 przeżyła (punkty_z_seria): brakuje testu dokładnie na granicy premii: ile
            punktów dają dwie, a ile trzy poprawne z rzędu?
          - pluskwa 4 przeżyła (punkty_z_seria): brakuje testu na dłuższą serię - czwarta i
            piąta poprawna z rzędu też dostają premię
          - pluskwa 5 przeżyła (punkty_z_seria): brakuje testu, w którym błędna odpowiedź
            przerywa serię, a po niej jest jeszcze kilka poprawnych
          - pluskwa 6 przeżyła (ocena_slowna): brakuje testu z wynikiem dokładnie na progu
            najwyższej oceny (90%)
          - pluskwa 7 przeżyła (ocena_slowna): brakuje testu z wynikiem dokładnie na najniższym
            progu (50%)
          - pluskwa 8 przeżyła (ocena_slowna): brakuje testu, że maks równe 0 zgłasza ValueError
            (a nie inny wyjątek)
          - pluskwa 9 przeżyła (ocena_slowna): brakuje testu z wynikiem między 0 a maks, który
            daje wysoką ocenę, np. 9 z 10 - czy procent na pewno liczy się z ułamkiem?

Popraw i uruchom mnie jeszcze raz.
```
<!-- /wynik -->

Jeden test łapie już jedną pluskwę. Twój cel: `Złapane pluskwy: 9/9`.

## Testy w unittest w trzech minutach

```python
import unittest


class TestPrzyklad(unittest.TestCase):
    def test_najwieksza_z_listy(self):
        self.assertEqual(max([3, 7, 2]), 7)          # wynik ma być równy oczekiwanemu

    def test_pusty_tekst_jest_falszem(self):
        self.assertFalse(bool(""))                    # assertTrue / assertFalse

    def test_int_z_liter_zglasza_blad(self):
        with self.assertRaises(ValueError):           # kod w bloku ma zgłosić ten wyjątek
            int("abc")
```

- Test to metoda, której nazwa zaczyna się od `test_`, w klasie dziedziczącej po `unittest.TestCase`.
- Jeden test sprawdza jeden przypadek. Nazwa mówi, jaki: `test_dwie_poprawne_bez_premii`.
- `python3 -m unittest -v` sam znajduje pliki `test_*.py`, uruchamia wszystkie testy i pokazuje, które przeszły (`ok`), a które nie (`FAIL`, `ERROR`).
- Zwykłe `assert x == 7` w kodzie też działa, ale zatrzymuje program na pierwszym błędzie. `unittest` uruchamia wszystkie testy i pokazuje pełny raport.

## Zadanie

Napisz w `test_punkty.py` testy dla wszystkich czterech funkcji — lista przypadków jest w komentarzu na dole pliku. Oczekiwane wyniki policz sam z docstringów w `punkty.py`, na kartce albo w głowie, a nie przez uruchomienie funkcji.

Pracuj w pętli:

1. dopisz kilka testów,
2. `python3 -m unittest -v` — wszystkie mają przechodzić na poprawnym `punkty.py`; jeśli któryś nie przechodzi, to test jest zły, a nie kod,
3. `python3 sprawdz.py` — ile pluskiew złapanych i w której funkcji szukać dalej.

Strażnik mówi, w której funkcji przeżyła pluskwa i jakiego przypadku brakuje, ale nie zdradza, co dokładnie jest w niej zepsute.

<details>
<summary>Podpowiedź 1</summary>

Najwięcej pluskiew siedzi na granicach: tam, gdzie zaczyna się premia, i dokładnie na progach procentowych. Testuj wynik tuż przed granicą, na granicy i tuż za nią. Przy progach wygodnie liczyć na 10 punktach: 9 z 10 to dokładnie 90%.
</details>

<details>
<summary>Podpowiedź 2</summary>

`punkty_z_seria` policz na kartce dla kilku list. Przykład z docstringu: `[True, True, True, True]` daje 1 + 1 + 2 + 2 = 6. Policz też listę, w której seria się przerywa: `[True, True, False, True, True, True]`.
</details>

<details>
<summary>Podpowiedź 3</summary>

Kilka sprawdzeń w jednym teście jest w porządku, jeśli dotyczą tego samego przypadku:

```python
def test_tekst_bez_liczby(self):
    with self.assertRaises(ValueError):
        int("abc")
    with self.assertRaises(ValueError):
        int("4,5")
```

`assertRaises(ValueError)` nie przejdzie, gdy funkcja zgłosi inny wyjątek, np. `ZeroDivisionError`. Sprawdź osobno każdy przypadek, który według docstringu ma zgłaszać `ValueError` — każdy we własnym `with`.
</details>

## Dla chętnych: dziesiąta pluskwa

Skopiuj `punkty.py` do innego katalogu razem ze swoimi testami i zepsuj w nim jedną rzecz tak, żeby twoje testy tego **nie** zauważyły. Daj kopię koledze z zespołu: niech dopisze test, który ją złapie. Taka zabawa nazywa się testowaniem mutacyjnym — tak sprawdza się, ile są warte testy.
