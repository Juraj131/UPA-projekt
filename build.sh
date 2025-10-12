#!/bin/bash
# Build skript pre UPA projekt 2
# Instalacia zavislosti a priprava projektu

echo "=== UPA Projekt 1 - Build Script ==="

# Kontrola Python verzie
python3 --version || { echo "Python3 nie je nainstalovany!"; exit 1; }

# Vytvorenie virtualneho prostredia
echo "Tvorba virtualneho prostredia..."
python3 -m venv .venv

# Aktivacia virtualneho prostredia
echo "Aktivacia virtualneho prostredia..."
source .venv/bin/activate

# Instalacia zavislosti
echo "Instalacia zavislosti..."
pip install --upgrade pip
pip install -r requirements.txt


# Nastavenie executable prav
chmod +x run.sh
chmod +x get_urls.py  
chmod +x fallback_scraper.py

echo "=== Build dokonceny uspesne ==="