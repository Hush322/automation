# Laboratorul 3 – Automatizarea cu Cron și Docker

## Scopul lucrării
Automatizarea executării periodice a unui script Python care obține cursuri valutare de la un API și salvează rezultatele în fișiere JSON.

## Fișierele proiectului
- `currency_exchange_rate.py` – scriptul Python.
- `Dockerfile` – construirea imaginii Docker.
- `docker-compose.yml` – configurarea containerului.
- `cronjob` – sarcinile programate.
- `entrypoint.sh` – pornirea serviciului Cron.
- `data/` – rezultatele în format JSON.
- `logs/` – jurnalele aplicației.

## Pornirea proiectului
Executați din directorul `lab03`:

    docker compose up -d --build

## Sarcini programate
- Zilnic la ora 06:00: cursul MDL–EUR pentru ziua precedentă.
- Vinerea la ora 17:00: cursul MDL–USD pentru data calculată cu șapte zile în urmă.

## Testare manuală
    docker exec currency-cron python3 /app/currency_exchange_rate.py MDL EUR 2025-09-15
    docker exec currency-cron python3 /app/currency_exchange_rate.py MDL USD 2025-09-15

Rezultatele sunt salvate în directorul `data/`.

## Observație
API-ul local conține date istorice până în septembrie 2025. Pentru date curente este necesară o sursă API cu date actualizate.

## Concluzie
A fost configurat un container Docker cu serviciul Cron pentru executarea automată a unui script Python. Testele au confirmat funcționarea scriptului și salvarea rezultatelor în fișiere JSON.
