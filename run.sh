#!/bin/bash
# UPA Projekt 2 - Testovací skript (podľa zadania)
# Spustí získanie URL, uloží do url_test.txt a spracuje prvých 10 produktov

echo "=== UPA Projekt 2 - Testovací Script ==="

# Aktivácia virtuálneho prostredia
source .venv/bin/activate

# Krok 1: Získanie zoznamu URL produktov a uloženie do url_test.txt
echo "1. Získavam zoznam URL produktov..."
python3 get_urls.py > url_test.txt

# Kontrola či sa vytvorili URL
if [ ! -s url_test.txt ]; then
    echo "ERROR: Nepodarilo sa získať URL produktov!"
    exit 1
fi

url_count=$(wc -l < url_test.txt)
echo "   ✓ Získalo sa $url_count URL produktov, uložené do url_test.txt"

# Krok 2: Spracovanie prvých 10 URL a výpis na stdout
echo "2. Spracovávam prvých 10 produktov (výstup na stdout)..."
head -10 url_test.txt | python3 fallback_scraper.py scrape

echo "=== Testovací script dokončený ==="