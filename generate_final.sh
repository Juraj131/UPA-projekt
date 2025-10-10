#!/bin/bash
# UPA Projekt 2 - Generovanie finálneho datasetu (230 produktov)
# Tento script nie je súčasťou zadania, ale slúži na vytvorenie kompletných dát

echo "=== Generovanie finálneho datasetu ==="

# Aktivácia virtuálneho prostredia
source .venv/bin/activate

# Použijem existujúci urls.txt alebo ho vytvorím
if [ ! -f "urls.txt" ]; then
    echo "1. Získavam kompletný zoznam URL produktov..."
    python3 get_urls.py > urls.txt
fi

url_count=$(wc -l < urls.txt)
echo "   ✓ Spracovávam všetkých $url_count produktov..."

# Generovanie finálneho datasetu
cat urls.txt | python3 fallback_scraper.py scrape > data_final.tsv

# Kontrola výsledkov
if [ -f "data_final.tsv" ]; then
    final_count=$(wc -l < data_final.tsv)
    echo "   ✓ Spracovaných $final_count produktov"
    echo "   ✓ Finálny dataset: data_final.tsv"
else
    echo "ERROR: Nepodarilo sa vytvoriť data_final.tsv!"
    exit 1
fi

echo "=== Finálny dataset vytvorený úspešne! ==="