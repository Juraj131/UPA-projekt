# UPA Projekt 1 - Web Scraping

**Název týmu:** Tým 247208  
**Řešitelé:**
- Juraj Bendik (247208)
- Adam Brezina (247211)

## E-shop

**URL:** https://www.pneuboss.sk  
**Název:** PneumaBoss - slovenský e-shop s pneumatikami

## Význam sloupců TSV výstupu

Výstupný TSV soubor obsahuje **8 sloupců** bez hlavičky:

| Pořadí | Název | Typ | Popis |
|---------|-------|-----|--------|
| 1 | url | ID | URL produktu (identifikace) |
| 2 | název | string | Název pneumatiky |
| 3 | cena | string | Aktuální prodejní cena (např. "54,83 €") |
| 4 | typ_pneu | kategorický | Typ pneumatiky (Osobní pneu, Dodávkové a nákladní pneu) |
| 5 | segment | kategorický | Cenový segment (Ekonomická třída, Střední třída, Prémiová třída) |
| 6 | šířka | číselný | Šířka pneumatiky v mm |
| 7 | profil | číselný | Výška profilu v % |
| 8 | průměr | číselný | Průměr ráfku v palcích |

## Spuštění

### Příprava prostředí:
```bash
# Po klonování/kopírování nastavte execute permissions:
chmod +x build.sh run.sh

# Instalace závislostí:
./build.sh

# Nebo bez chmod použijte:
bash build.sh
```

### Test na prvních 10 produktech:
```bash  
./run.sh
```
*Poznámka: run.sh automaticky vygeneruje url_test.txt se všemi URL a zpracuje prvních 10 produktů*

### Úplné zpracování:
```bash
# 1. Získání všech URL (200+ produktů)
python3 get_urls.py > urls.txt

# 2. Zpracování všech produktů
cat urls.txt | python3 fallback_scraper.py > data.tsv
```

## Poznámky

**Architektura:** Projekt používá dvoustupňový přístup - nejprve se získají URL všech produktů (`get_urls.py`), poté se jednotlivě zpracovávají (`fallback_scraper.py`)..

**Kompatibilita:** Řešení používá pouze standardní Python knihovny (requests, beautifulsoup4) bez závislosti na webovém prohlížeči.