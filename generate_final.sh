#!/bin/bash
# UPA Projekt 2 - Generovanie finalneho datasetu (230 produktov)
# Tento script nie je sucastou zadania, ale sluzi na vytvorenie kompletnych dat

echo "=== Generovanie finalneho datasetu ==="

# Aktivacia virtualneho prostredia
source .venv/bin/activate

# Pouzijem existujuci urls.txt alebo ho vytvorim
if [ ! -f "urls.txt" ]; then
    echo "1. Ziskavam kompletny zoznam URL produktov..."
    python3 get_urls.py > urls.txt
fi

url_count=$(wc -l < urls.txt)
echo "   ✓ Spracovavam vsetkych $url_count produktov..."

# Generovanie finalneho datasetu
cat urls.txt | python3 fallback_scraper.py scrape > data_final.tsv

# Kontrola vysledkov
if [ -f "data_final.tsv" ]; then
    final_count=$(wc -l < data_final.tsv)
    echo "   ✓ Spracovanych $final_count produktov"
    echo "   ✓ Finalny dataset: data_final.tsv"
else
    echo "ERROR: Nepodarilo sa vytvoriť data_final.tsv!"
    exit 1
fi

echo "=== Finalny dataset vytvoreny uspesne! ==="