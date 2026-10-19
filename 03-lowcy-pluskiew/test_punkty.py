"""Testy funkcji z punkty.py.

Uruchom:   python3 -m unittest -v
Sprawdź:   python3 sprawdz.py
"""
import unittest

from punkty import czy_poprawna, ocena_slowna, policz_punkty, punkty_z_seria

STOLICA = {
    "pytanie": "Stolica Polski to:",
    "odpowiedzi": ["Kraków", "Warszawa", "Gniezno", "Poznań"],
    "poprawna": 1,
    "kategoria": "geografia",
}
PLANETA = {
    "pytanie": "Która planeta jest najbliżej Słońca?",
    "odpowiedzi": ["Wenus", "Mars", "Merkury", "Ziemia"],
    "poprawna": 2,
    "kategoria": "nauka",
}


class TestCzyPoprawna(unittest.TestCase):
    def test_dobry_wybor_to_true(self):
        self.assertTrue(czy_poprawna(STOLICA, 1))


# Przypadki do pokrycia. Każdy zapisz jako osobną metodę test_... w klasie dziedziczącej
# po unittest.TestCase (możesz dopisać klasy TestPoliczPunkty, TestPunktyZSeria, TestOcenaSlowna).
#
# czy_poprawna
#   - zły wybór
#   - wybór 0 przy pytaniu, w którym poprawna jest pierwsza odpowiedź
# policz_punkty
#   - wszystkie odpowiedzi dobre, wszystkie złe, część dobra
#   - puste listy pytań i wyborów
#   - listy różnej długości (assertRaises)
# punkty_z_seria
#   - pusta lista
#   - jedna, dwie, trzy, cztery, pięć poprawnych z rzędu
#   - same błędne odpowiedzi
#   - seria przerwana błędną odpowiedzią, a potem znowu kilka poprawnych
# ocena_slowna
#   - wynik w środku każdego przedziału: mistrz, ekspert, uczeń, nowicjusz
#   - wyniki dokładnie na progach: 90%, 70%, 50%
#   - wynik tuż pod progiem
#   - maks równe 0, maks ujemne, punkty ujemne, punkty większe niż maks (assertRaises)
