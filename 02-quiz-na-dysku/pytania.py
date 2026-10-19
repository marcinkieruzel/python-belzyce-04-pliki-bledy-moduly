"""Baza pytań quizu: lista słowników.

Każde pytanie to słownik z czterema kluczami:
    "pytanie"     treść pytania (tekst),
    "odpowiedzi"  lista 4 odpowiedzi (tekstów),
    "poprawna"    numer poprawnej odpowiedzi na liście: 0, 1, 2 albo 3 — LICZONY OD 0 (gracz wpisuje 1–4),
    "kategoria"   temat pytania (tekst).

To ten sam format co w module 2. W repozytorium zespołu zostaje wasza baza z modułu 2 (quiz/pytania.py).
Po zmianie bazy sprawdź ją: python3 sprawdz.py (pierwsza linia raportu).
"""

PYTANIA = [
    {
        "pytanie": "Co wypisze print(7 // 2)?",
        "odpowiedzi": ["3.5", "3", "4", "3.0"],
        "poprawna": 1,
        "kategoria": "Python",
    },
    {
        "pytanie": "Ile razy wykona się pętla for i in range(2, 10, 3)?",
        "odpowiedzi": ["3", "2", "4", "8"],
        "poprawna": 0,
        "kategoria": "Python",
    },
    {
        "pytanie": "Jakim słowem zaczyna się definicja funkcji w Pythonie?",
        "odpowiedzi": ["function", "fun", "def", "func"],
        "poprawna": 2,
        "kategoria": "Python",
    },
    {
        "pytanie": "Co zwraca funkcja, w której nie ma instrukcji return?",
        "odpowiedzi": ["0", "False", "pusty tekst", "None"],
        "poprawna": 3,
        "kategoria": "Python",
    },
    {
        "pytanie": "Które słowo od razu przechodzi do następnego obrotu pętli?",
        "odpowiedzi": ["break", "pass", "continue", "next"],
        "poprawna": 2,
        "kategoria": "Python",
    },
    {
        "pytanie": "Co wypisze print(len([1, [2, 3], 4]))?",
        "odpowiedzi": ["4", "3", "2", "nic, będzie błąd"],
        "poprawna": 1,
        "kategoria": "Python",
    },
    {
        "pytanie": "Jakim poleceniem sprawdzisz, w którym katalogu jesteś?",
        "odpowiedzi": ["pwd", "ls", "cd", "whoami"],
        "poprawna": 0,
        "kategoria": "Linux",
    },
    {
        "pytanie": "Co robi polecenie chmod +x skrypt.py?",
        "odpowiedzi": ["usuwa plik", "zmienia nazwę pliku", "nadaje prawo wykonywania", "kopiuje plik do /bin"],
        "poprawna": 2,
        "kategoria": "Linux",
    },
    {
        "pytanie": "Jak nazywa się menedżer pakietów w Ubuntu?",
        "odpowiedzi": ["dnf", "apt", "brew", "winget"],
        "poprawna": 1,
        "kategoria": "Linux",
    },
    {
        "pytanie": "Co oznacza znak ~ na początku ścieżki, np. ~/projekty?",
        "odpowiedzi": ["katalog główny /", "katalog domowy użytkownika", "katalog nadrzędny", "katalog tymczasowy"],
        "poprawna": 1,
        "kategoria": "Linux",
    },
    {
        "pytanie": "Ile bitów ma bajt?",
        "odpowiedzi": ["4", "8", "16", "32"],
        "poprawna": 1,
        "kategoria": "informatyka",
    },
    {
        "pytanie": "Jak zapisać liczbę 5 w systemie dwójkowym?",
        "odpowiedzi": ["110", "100", "111", "101"],
        "poprawna": 3,
        "kategoria": "informatyka",
    },
    {
        "pytanie": "Ile prób zawsze wystarczy, żeby metodą połowienia zgadnąć liczbę od 1 do 100?",
        "odpowiedzi": ["7", "10", "50", "100"],
        "poprawna": 0,
        "kategoria": "informatyka",
    },
    {
        "pytanie": "Które urządzenie w komputerze nazywa się CPU?",
        "odpowiedzi": ["pamięć operacyjna", "procesor", "karta graficzna", "dysk SSD"],
        "poprawna": 1,
        "kategoria": "informatyka",
    },
]
