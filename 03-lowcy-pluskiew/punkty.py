"""Funkcje liczące punkty w quizie.

Ten kod jest poprawny - nie zmieniaj go. Docstringi to specyfikacja: opisują, co każda funkcja
ma robić. Twoje testy w test_punkty.py mają pilnować, żeby kod trzymał się tej specyfikacji.
"""


def czy_poprawna(pytanie, wybor):
    """Czy wybór gracza to poprawna odpowiedź na pytanie.

    pytanie - słownik z kluczem "poprawna": indeks poprawnej odpowiedzi, liczony od 0,
    wybor   - indeks odpowiedzi wybranej przez gracza, też liczony od 0.
    Zwraca True albo False.
    """
    return wybor == pytanie["poprawna"]


def policz_punkty(pytania, wybory):
    """Liczba poprawnych odpowiedzi.

    pytania - lista pytań (słowników jak wyżej),
    wybory  - lista indeksów wybranych odpowiedzi; wybory[i] to odpowiedź na pytania[i].
    Gdy listy mają różną długość, zgłasza ValueError.
    """
    if len(pytania) != len(wybory):
        raise ValueError(f"pytań jest {len(pytania)}, a odpowiedzi {len(wybory)}")
    punkty = 0
    for pytanie, wybor in zip(pytania, wybory):
        if czy_poprawna(pytanie, wybor):
            punkty += 1
    return punkty


def punkty_z_seria(wyniki):
    """Punkty z premią za serię poprawnych odpowiedzi.

    wyniki - lista True/False: czy kolejne odpowiedzi były poprawne.
    Każda poprawna odpowiedź daje 1 punkt. Trzecia poprawna z rzędu i każda następna w tej samej
    serii daje dodatkowo 1 punkt premii. Błędna odpowiedź daje 0 punktów i przerywa serię.
    Pusta lista daje 0.

    Przykład: [True, True, True, True] -> 1 + 1 + 2 + 2 = 6
    """
    punkty = 0
    seria = 0
    for poprawna in wyniki:
        if poprawna:
            seria += 1
            punkty += 1
            if seria >= 3:
                punkty += 1
        else:
            seria = 0
    return punkty


def ocena_slowna(punkty, maks):
    """Słowna ocena wyniku na podstawie procentu zdobytych punktów.

    procent = punkty * 100 / maks
    co najmniej 90 -> "mistrz", co najmniej 70 -> "ekspert", co najmniej 50 -> "uczeń",
    mniej niż 50 -> "nowicjusz".
    Gdy maks <= 0 albo punkty są spoza zakresu od 0 do maks, zgłasza ValueError.
    """
    if maks <= 0:
        raise ValueError(f"maks musi być większe od zera, a jest {maks}")
    if not 0 <= punkty <= maks:
        raise ValueError(f"punkty muszą być od 0 do {maks}, a są {punkty}")
    procent = punkty * 100 / maks
    if procent >= 90:
        return "mistrz"
    if procent >= 70:
        return "ekspert"
    if procent >= 50:
        return "uczeń"
    return "nowicjusz"
