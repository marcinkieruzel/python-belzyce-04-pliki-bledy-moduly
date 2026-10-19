"""Dziennik z błędami: średnie ocen klasy 3TI z uszkodzonego eksportu e-dziennika.

Uruchom:   python3 dziennik.py
Sprawdź:   python3 sprawdz.py
"""
import csv
from pathlib import Path

# Folder, w którym leży ten plik - niezależnie od tego, z jakiego katalogu uruchomisz program.
KATALOG = Path(__file__).parent
DANE = KATALOG / "dane" / "oceny.csv"
WYNIKI = KATALOG / "wyniki"
SREDNIE = WYNIKI / "srednie.csv"
ODRZUCONE = WYNIKI / "odrzucone.csv"
POLA = ["uczen", "przedmiot", "ocena", "data"]


def zamien_na_ocene(tekst):
    """Zamienia tekst z kolumny ocena na liczbę całkowitą od 1 do 6 i ją zwraca.

    Spacje wokół są dozwolone: " 5 " to 5.
    Gdy tekst nie jest poprawną oceną, zgłasza ValueError z powodem, np.:
        raise ValueError("ocena spoza skali 1-6: 7")
    """
    # Twój kod (krok 2)


def sprawdz_pola(wiersz):
    """Zgłasza ValueError, gdy wiersz z csv.DictReader nie ma dokładnie 4 pól.

    DictReader przy za małej liczbie pól wpisuje brakującym polom wartość None,
    a nadmiarowe pola odkłada na listę pod kluczem None.
    """
    # Twój kod (krok 2)


def tresc_wiersza(wiersz):
    """Odtwarza linię pliku ze słownika z csv.DictReader (do raportu odrzuconych). Gotowa - nie zmieniaj."""
    pola = [wiersz[pole] for pole in POLA if wiersz.get(pole) is not None]
    pola += wiersz.get(None, [])
    return ";".join(pola)


def wczytaj_oceny(sciezka):
    """Czyta plik CSV z ocenami (separator ;) i zwraca krotkę (oceny, odrzucone).

    oceny      - lista krotek (uczen, przedmiot, ocena), ocena jako liczba,
    odrzucone  - lista krotek (numer_linii, powod, tresc) dla wierszy, których nie da się użyć.
    Numer linii liczymy jak w edytorze: nagłówek to linia 1.
    """
    oceny = []
    odrzucone = []
    # Twój kod (krok 1, potem krok 2)
    return oceny, odrzucone


def policz_srednie(oceny):
    """Zwraca słownik {(uczen, przedmiot): (srednia, liczba_ocen)}."""
    srednie = {}
    # Twój kod (krok 1)
    return srednie


def zapisz_srednie(sciezka, srednie):
    """Zapisuje średnie do CSV z nagłówkiem uczen;przedmiot;srednia;liczba_ocen.

    Wiersze posortowane po uczniu i przedmiocie, średnia z 2 miejscami po przecinku (np. 4.33).
    """
    # Twój kod (krok 3)


def zapisz_odrzucone(sciezka, odrzucone):
    """Zapisuje odrzucone wiersze do CSV z nagłówkiem wiersz;powod;tresc."""
    # Twój kod (krok 3)


def main():
    oceny, odrzucone = wczytaj_oceny(DANE)
    srednie = policz_srednie(oceny)
    WYNIKI.mkdir(exist_ok=True)
    zapisz_srednie(SREDNIE, srednie)
    zapisz_odrzucone(ODRZUCONE, odrzucone)
    print(f"Wczytano ocen: {len(oceny)}. Odrzucono wierszy: {len(odrzucone)}.")
    print(f"Średnie: {SREDNIE.relative_to(KATALOG)}, do ręcznej poprawy: {ODRZUCONE.relative_to(KATALOG)}")


if __name__ == "__main__":
    main()
