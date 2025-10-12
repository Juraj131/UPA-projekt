#!/bin/bash
# ziskani URL --> ulozi urls do url_test.txt --> spracuje prvnich 10 produktu

source .venv/bin/activate

echo "Ziskani seznamu URL produktu"
python3 get_urls.py > url_test.txt

# Kontrola zda se vytvorily URL
if [ ! -s url_test.txt ]; then
    echo "ERROR: Nepodarilo se ziskat URL produkty!"
    exit 1
fi

url_count=$(wc -l < url_test.txt)
echo "Ziskalo se $url_count URL produktu, viz. url_test.txt"

echo "Zpracovani prvnich 10 produktu"
head -10 url_test.txt | python3 fallback_scraper.py

echo "=== Skript byl dokoncen ==="