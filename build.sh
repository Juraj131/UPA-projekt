#!/bin/bash
# Build skript pre UPA projekt 2
# Inštalácia závislostí a príprava projektu

echo "=== UPA Projekt 2 - Build Script ==="

# Kontrola Python verzie
python3 --version || { echo "Python3 nie je nainštalovaný!"; exit 1; }

# Vytvorenie virtuálneho prostredia
echo "Vytváram virtuálne prostredie..."
python3 -m venv .venv

# Aktivácia virtuálneho prostredia
echo "Aktivujem virtuálne prostredie..."
source .venv/bin/activate

# Inštalácia závislostí
echo "Inštalujem závislosti..."
pip install --upgrade pip
pip install playwright beautifulsoup4 requests lxml

# Inštalácia prehliadačov pre Playwright
echo "Inštalujem prehliadače..."
playwright install chromium

# Nastavenie executable práv
chmod +x run.sh
chmod +x get_urls.py  
chmod +x fallback_scraper.py

echo "=== Build dokončený úspešne ==="
echo "Môžete spustiť: ./run.sh"