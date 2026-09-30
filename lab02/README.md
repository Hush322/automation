# Laboratorul 2 — Interacțiunea cu un Web API folosind Python

## Scopul lucrării

Scopul laboratorului este de a învăța utilizarea unui Web API dintr-un program Python. Aplicația primește din linia de comandă două monede și o dată, trimite o cerere către API-ul Currency Exchange Rate, preia cursul valutar și salvează rezultatul în format JSON.

## Structura proiectului

```text
automation/
├── lab02/
│   ├── currency_exchange_rate.py
│   └── README.md
├── data/
│   ├── USD_MDL_2025-01-01.json
│   ├── USD_MDL_2025-03-05.json
│   ├── USD_MDL_2025-05-07.json
│   ├── USD_MDL_2025-07-11.json
│   └── USD_MDL_2025-09-15.json
└── error.log
```

Directorul `data` este creat automat de program dacă nu există.

## Dependențe

Programul este scris în Python 3 și utilizează următoarele module:

* `sys` — pentru citirea parametrilor din linia de comandă;
* `json` — pentru salvarea răspunsului API în format JSON;
* `logging` — pentru înregistrarea erorilor în `error.log`;
* `pathlib` — pentru lucrul cu directoare și fișiere;
* `datetime` — pentru verificarea și validarea datelor;
* `requests` — pentru trimiterea cererilor HTTP către API.

Biblioteca externă necesară este `requests`.

Verificarea instalării:

```bash
python3 -c "import requests; print(requests.__version__)"
```

## Utilizarea programului

Programul se execută folosind următoarea sintaxă:

```bash
python3 lab02/currency_exchange_rate.py <from> <to> <YYYY-MM-DD>
```

Unde:

* `<from>` — moneda inițială;
* `<to>` — moneda în care se dorește conversia;
* `<YYYY-MM-DD>` — data pentru care se solicită cursul valutar.

### Exemplu

```bash
python3 lab02/currency_exchange_rate.py USD MDL 2025-01-01
```

În cazul unei cereri reușite, programul afișează:

```text
Cererea a fost realizată cu succes.
Date salvate în: /root/automation/data/USD_MDL_2025-01-01.json
```

## Monede suportate

API-ul și programul suportă următoarele monede:

```text
MDL
USD
EUR
RON
RUS
UAH
```

Programul verifică dacă monedele introduse sunt disponibile înainte de trimiterea cererii.

## Perioada datelor

Conform cerințelor laboratorului, sunt acceptate date din perioada:

```text
2025-01-01 — 2025-09-15
```

Programul verifică data introdusă și afișează o eroare dacă aceasta nu respectă perioada permisă.

## Salvarea datelor

Răspunsul primit de la API este salvat în format JSON în directorul `data`.

Numele fișierului conține monedele și data solicitării:

```text
FROM_TO_DATE.json
```

Exemplu:

```text
USD_MDL_2025-01-01.json
```

Structura unui răspuns salvat este de forma:

```json
{
    "error": "",
    "data": {
        "from": "USD",
        "to": "MDL",
        "rate": 0.05411518959256674,
        "date": "2025-01-01"
    }
}
```

## Gestionarea erorilor

Programul verifică mai multe tipuri de erori:

1. Număr incorect de parametri;
2. Monedă nesuportată;
3. Format incorect al datei;
4. Dată în afara perioadei permise;
5. Erori de conectare sau de comunicare cu API-ul;
6. Erori transmise de API.

Erorile sunt afișate în consolă și sunt salvate automat în fișierul:

```text
error.log
```

Exemplu:

```text
Eroare: Moneda 'ABC' nu este suportată.
```

În `error.log`, eroarea este salvată împreună cu data și ora:

```text
2026-09-30 19:31:27,052 - ERROR - Moneda 'ABC' nu este suportată.
```

## Funcțiile principale

### `validate_date()`

Verifică dacă data introdusă are formatul `YYYY-MM-DD` și dacă se află în perioada permisă.

### `validate_currency()`

Verifică dacă moneda introdusă este suportată de API.

### `get_exchange_rate()`

Construiește și trimite cererea HTTP către API și prelucrează răspunsul primit.

### `save_data()`

Creează directorul `data` dacă acesta nu există și salvează răspunsul API în format JSON.

### `log_error()`

Afișează mesajul de eroare în consolă și îl salvează în `error.log`.

### `main()`

Este funcția principală a programului. Primește argumentele din linia de comandă, efectuează validările, solicită datele de la API și salvează rezultatul.

## Logica programului

Programul funcționează în următorul mod:

1. Primește trei argumente din linia de comandă.
2. Verifică numărul argumentelor.
3. Verifică monedele introduse.
4. Verifică data și perioada permisă.
5. Trimite cererea către Web API.
6. Primește răspunsul JSON.
7. Verifică dacă API-ul a returnat o eroare.
8. Salvează rezultatul în directorul `data`.
9. În cazul unei erori, afișează mesajul în consolă și îl salvează în `error.log`.

## Testarea programului

Programul a fost testat pentru cel puțin 5 date din perioada solicitată:

```text
2025-01-01
2025-03-05
2025-05-07
2025-07-11
2025-09-15
```

Pentru fiecare dată a fost creat un fișier JSON corespunzător în directorul `data`.

Au fost testate și situații de eroare:

```bash
python3 lab02/currency_exchange_rate.py
```

```bash
python3 lab02/currency_exchange_rate.py ABC MDL 2025-01-01
```

```bash
python3 lab02/currency_exchange_rate.py USD MDL 2025/01/01
```

```bash
python3 lab02/currency_exchange_rate.py USD MDL 2026-01-01
```

În toate cazurile programul a afișat mesajul corespunzător și a înregistrat eroarea în `error.log`.

## Concluzie

În cadrul laboratorului a fost realizat un script Python care interacționează cu un Web API pentru obținerea cursului valutar. Programul utilizează parametri din linia de comandă, validează datele introduse, gestionează erorile, salvează răspunsurile API în format JSON și înregistrează erorile într-un fișier de log.
