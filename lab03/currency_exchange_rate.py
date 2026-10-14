import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

import requests


API_URL = os.getenv("API_URL", "http://localhost:8080/")
API_KEY = "EXAMPLE_API_KEY"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ERROR_LOG = PROJECT_ROOT / "error.log"

MIN_DATE = datetime.strptime("2025-01-01", "%Y-%m-%d").date()
MAX_DATE = datetime.strptime("2025-09-15", "%Y-%m-%d").date()

SUPPORTED_CURRENCIES = {"MDL", "USD", "EUR", "RON", "RUS", "UAH"}


logging.basicConfig(
    filename=ERROR_LOG,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log_error(message):
    """Afișează eroarea în consolă și o salvează în error.log."""
    print(f"Eroare: {message}")
    logging.error(message)


def validate_date(date_string):
    """Verifică formatul și perioada datei."""
    try:
        date = datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Data trebuie să fie în formatul YYYY-MM-DD.")

    if date < MIN_DATE or date > MAX_DATE:
        raise ValueError(
            "Data trebuie să fie în perioada 2025-01-01 - 2025-09-15."
        )

    return date


def validate_currency(currency):
    """Verifică dacă moneda este suportată de API."""
    currency = currency.upper()

    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError(
            f"Moneda '{currency}' nu este suportată. "
            f"Monede disponibile: {', '.join(sorted(SUPPORTED_CURRENCIES))}"
        )

    return currency


def get_exchange_rate(from_currency, to_currency, date):
    """Trimite cererea către API și returnează datele primite."""
    params = {
        "from": from_currency,
        "to": to_currency,
        "date": date
    }

    response = requests.post(
        API_URL,
        params=params,
        data={"key": API_KEY},
        timeout=10
    )

    response.raise_for_status()

    result = response.json()

    if result.get("error"):
        raise ValueError(result["error"])

    return result


def save_data(result, from_currency, to_currency, date):
    """Salvează rezultatul primit în format JSON."""
    DATA_DIR.mkdir(exist_ok=True)

    filename = f"{from_currency}_{to_currency}_{date}.json"
    output_file = DATA_DIR / filename

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    return output_file


def main():
    """Funcția principală a programului."""
    if len(sys.argv) != 4:
        log_error(
            "Număr invalid de parametri. "
            "Utilizare: python3 currency_exchange_rate.py "
            "<from> <to> <YYYY-MM-DD>"
        )
        sys.exit(1)

    from_currency = sys.argv[1].upper()
    to_currency = sys.argv[2].upper()
    date_string = sys.argv[3]

    try:
        from_currency = validate_currency(from_currency)
        to_currency = validate_currency(to_currency)

        validate_date(date_string)

        result = get_exchange_rate(
            from_currency,
            to_currency,
            date_string
        )

        output_file = save_data(
            result,
            from_currency,
            to_currency,
            date_string
        )

        print("Cererea a fost realizată cu succes.")
        print(f"Date salvate în: {output_file}")

    except requests.exceptions.RequestException as error:
        log_error(f"Eroare la conectarea la API: {error}")
        sys.exit(1)

    except (ValueError, json.JSONDecodeError) as error:
        log_error(str(error))
        sys.exit(1)


if __name__ == "__main__":
    main()
