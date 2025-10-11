#!/bin/bash
# Skript na naklonvanie len potrebnych suborov na Merlin server

echo "=== Nastavenie ciste UPA Projekt instalacie na Merlin ==="

# Vytvorenie priecinku
mkdir -p ~/upa-projekt/UPA-projekt-clean
cd ~/upa-projekt/UPA-projekt-clean

# Inicializacia git repo
git init
git remote add origin https://github.com/Juraj131/UPA-projekt.git

# Nastavenie sparse checkout
git config core.sparseCheckout true
echo "fallback_scraper.py" > .git/info/sparse-checkout
echo "build.sh" >> .git/info/sparse-checkout  
echo "run.sh" >> .git/info/sparse-checkout
echo "requirements.txt" >> .git/info/sparse-checkout
echo "README.md" >> .git/info/sparse-checkout
echo ".gitignore" >> .git/info/sparse-checkout

# Pull len vybranych suborov
git pull origin main

echo "✅ Naklonované len potrebné súbory:"
ls -la

echo "=== Setup dokončený ==="