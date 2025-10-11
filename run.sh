#!/bin/bash
# UPA Projekt 2 - Testovaci skript (podla zadania)
# Spusti ziskanie URL, ulozi do url_test.txt a spracuje prvych 10 produktov

echo "=== UPA Projekt 2 - Testovaci Script ==="

# Aktivacia virtualneho prostredia
source .venv/bin/activate

# Krok 1: Ziskanie zoznamu URL produktov a ulozenie do url_test.txt
echo "1. Ziskavam zoznam URL produktov..."
python3 get_urls.py > url_test.txt

# Kontrola ci sa vytvorili URL
if [ ! -s url_test.txt ]; then
    echo "ERROR: Nepodarilo sa ziskat URL produktov!"
    exit 1
fi

url_count=$(wc -l < url_test.txt)
echo "   ✓ Ziskalo sa $url_count URL produktov, ulozene do url_test.txt"

# Krok 2: Spracovanie prvych 10 URL a vypis na stdout
echo "2. Spracovavam prvych 10 produktov (vystup na stdout)..."
head -10 url_test.txt | python3 fallback_scraper.py

echo "=== Testovaci script dokonceny ==="