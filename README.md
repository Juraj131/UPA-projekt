# UPA Projekt 2 - Web Scraping

**Název týmu:** UPA-Team-2025  
**Řešitelé:**
- Juraj Bendik
- Adam Brezina

## E-shop

**URL:** https://www.pneuboss.sk  
**Název:** PneumaBoss - slovenský e-shop s pneumatikami  
**Kategorie:** Zimní pneumatiky

Důvod výběru: Specializovaný e-shop s podrobnými parametry pneumatik v tabulkách, méně známý než hlavní e-shopy, slovenský obsah s dostatečným množstvím produktů.

## Implementace

**Skripty:**
- `get_urls.py` - Extrakce URL adres produktů ze stránky e-shopu
- `fallback_scraper.py` - Zpracování jednotlivých produktů a extrakce detailních informací
- `build.sh` - Instalace závislostí a příprava virtuálního prostředí
- `run.sh` - Testovací skript (první 10 produktů)

**Pipeline:**
```bash
python3 get_urls.py > urls.txt                    # Extrakce URL
cat urls.txt | python3 fallback_scraper.py > data.tsv   # Zpracování produktů
```

**Technologie:**
- Python 3 + virtuální prostředí (venv)
- BeautifulSoup4 (parsování HTML)
- Requests (HTTP požadavky)

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

### Úplné zpracování:
```bash
# 1. Získání všech URL (200+ produktů)
python3 get_urls.py > urls.txt

# 2. Zpracování všech produktů
cat urls.txt | python3 fallback_scraper.py > data.tsv
```

## Poznámky

**Architektura:** Projekt používá dvoustupňový přístup - nejprve se získají URL všech produktů (`get_urls.py`), poté se jednotlivě zpracovávají (`fallback_scraper.py`). Toto řešení je spolehlivé na všech systémech (Windows, Linux) a nevyžaduje GUI.

**Získané množství dat:** Skript extrahuje přibližně 230+ produktů zimních pneumatik, což splňuje požadavek minimálně 150 položek.

**Kompatibilita:** Řešení používá pouze standardní Python knihovny (requests, beautifulsoup4) bez závislosti na webovém prohlížeči.

**Ohleduplnost k serveru:** Skripty obsahují časové pauzy mezi požadavky (0.5-1s), aby nezatěžovaly server.