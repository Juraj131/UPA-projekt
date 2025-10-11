#!/bin/bash
# Build skript pre UPA projekt 2
# Instalacia zavislosti a priprava projektu

echo "=== UPA Projekt 2 - Build Script ==="

# Kontrola Python verzie
python3 --version || { echo "Python3 nie je nainstalowany!"; exit 1; }

# Vytvorenie virtualneho prostredia
echo "Vytvaram virtualne prostredie..."
python3 -m venv .venv

# Aktivacia virtualneho prostredia
echo "Aktivujem virtualne prostredie..."
source .venv/bin/activate

# Instalacia zavislosti
echo "Instalujem zavislosti..."
pip install --upgrade pip
pip install playwright beautifulsoup4 requests lxml

# Instalacia prehliadacov pre Playwright
echo "Instalujem prehliadace..."
playwright install chromium

# Nastavenie executable práv
chmod +x run.sh
chmod +x get_urls.py  
chmod +x fallback_scraper.py

echo "=== Build dokonceny uspesne ==="
echo "Mozete spustit: ./run.sh"