# UPA Projekt 2 - Web Scraping

**Názov týmu:** UPA-Team-2025  
**Riešitelia:** 
- Juraj Bendik, Adam Brezina

## E-shop

**URL:** https://www.pneuboss.sk  
**Názov:** PneumaBoss - slovenský e-shop s pneumatikami  
**Kategória:** Zimné pneumatiky  

Dôvod výberu: Špecializovaný e-shop s podrobnými parametrami pneumatík v tabuľkách, menej známy než hlavné e-shopy, slovenský obsah.

## Implementácia

**Skripty:**
- `get_urls.py` - Získava zoznam URL produktov (zimných pneumatík)
- `fallback_scraper.py` - Extrahuje detailné informácie z produktových stránok
- `build.sh` - Inštalácia závislostí a príprava
- `run.sh` - Testovací skript

**Technológie:**
- Python 3 + virtuálne prostredie (venv)
- Playwright (automatizácia prehliadača)
- BeautifulSoup4 (parsovanie HTML)
- Requests (HTTP requesty)

## Inštalácia

1. Uistite sa, že máte Python 3.7+ nainštalovaný
2. Aktivujte virtuálne prostredie (už vytvorené)
3. Balíky sú už nainštalované v projekte

## Význam stĺpcov TSV výstupu

Výstupný TSV súbor obsahuje **8 stĺpcov** bez hlavičky:

| Poradie | Názov | Typ | Popis |
|---------|-------|-----|--------|
| 1 | url | ID | URL produktu (identifikácia) |
| 2 | nazov | string | Názov pneumatiky |
| 3 | cena | string | Aktuálna predajná cena (napr. "54,83 €") |
| 4 | typ_pneu | kategorický | Typ pneumatiky (Osobné pneu, Dodávkové a nákladní pneu) |
| 5 | segment | kategorický | Cenový segment (Ekonomická trieda, Stredná trieda, Prémiová trieda) |
| 6 | sirka | číselný | Šírka pneumatiky v mm |
| 7 | profil | číselný | Výška profilu v % |
| 8 | priemer | číselný | Priemer ráfiku v palcoch |

## Spustenie

### Príprava prostredia:
```bash
./build.sh
```

### Test na prvých 10 produktoch:
```bash  
./run.sh
```

### Úplné spracovanie:
```bash
# 1. Získanie všetkých URL (150+)
python3 get_urls.py > urls.txt

# 2. Spracovanie všetkých produktov
cat urls.txt | python3 scraper.py > data.tsv
```

## Poznámky

**Záložné riešenie:** V prípade problémov s Playwright na serveri merlin je k dispozícii `fallback_scraper.py` ktorý používa iba requests + BeautifulSoup.

**Použitie záložného scrapera:**
```bash
# Získanie URL
python3 fallback_scraper.py > urls.txt

# Spracovanie produktov  
cat urls.txt | python3 fallback_scraper.py scrape > data.tsv
```

**Ohľaduplnosť k serveru:** Skripty obsahujú časové pauzy medzi requestmi (0.5-1s) aby nezatežovali server.

**Testované URL:** Všetky uvedené URL boli testované a sú funkčné k dátumu vytvorenia projektu.

## Výstup

Skript vytvorí TSV súbor `produkty.tsv` s nasledujúcimi stĺpcami:

1. **url** - URL produktu
2. **nazov** - Názov/meno produktu
3. **cena** - Cena produktu
4. **kategoria_1** až **kategoria_5** - Päť kategórií z tabuľky alebo breadcrumbs

## Príklady použitia

### Pre e-shop s produktmi:
```
URL: https://example-eshop.sk/produkty
CSS selektor: .product-item a
Počet produktov: 50
```

### Pre stránku s katalógom:
```
URL: https://katalog.sk/kategoria/elektronika
CSS selektor: a[href*="/produkt/"]
Počet produktov: 20
```

## Funkcie

### ProductScraper trieda

- **`get_product_links()`** - Nájde všetky linky na produkty
- **`scrape_product_details()`** - Extrahuje detaily konkrétneho produktu
- **`scrape_products()`** - Hlavná metóda na spracovanie všetkých produktov
- **`save_to_tsv()`** - Uloží dáta do TSV súboru

### Automatická detekcia

Scraper sa pokúsi automaticky detegovať:
- Produktové linky (rôzne pattern-y)
- Názvy produktov (h1, h2, .title, .product-name, atď.)
- Ceny (.price, .product-price, [data-price], atď.)
- Kategórie (breadcrumbs, tabuľky, meta tagy)

## Riešenie problémov

### Nenachádzajú sa produkty
1. Spustite `page_analyzer.py` na analýzu štruktúry
2. Použijte konkrétny CSS selektor
3. Skontrolujte, či stránka načítava obsah cez JavaScript

### Prázdne údaje
1. Stránka môže potrebovať viac času na načítanie (upravte `time.sleep()`)
2. Elementi môžu mať iné CSS triedy/selektory
3. Obsah môže byť generovaný dynamicky

### Chyby pri spustení
1. Uistite sa, že máte Chrome nainštalovaný
2. Skontrolujte internetové pripojenie
3. Niektoré stránky môžu blokovať automatizované requesty

## Prispôsobenie

### Pridanie vlastných selektorov:

V `product_scraper.py` môžete upraviť:

```python
# Pre názvy produktov
name_selectors = [
    'h1',
    '.custom-product-title',  # Váš vlastný selektor
    '.product-name'
]

# Pre ceny
price_selectors = [
    '.price',
    '.custom-price-class',    # Váš vlastný selektor
    '[data-custom-price]'
]
```

### Zmena výstupu:

Môžete pridať ďalšie stĺpce v metóde `scrape_product_details()`:

```python
product = {
    'url': product_url,
    'nazov': '',
    'cena': '',
    'popis': '',              # Nový stĺpec
    'dostupnost': '',         # Nový stĺpec
    'kategoria_1': '',
    # ... atď
}
```

## Technické detaily

- **Selenium WebDriver** - Pre interakciu s dynamickým obsahom
- **BeautifulSoup** - Pre parsovanie HTML
- **Pandas** - Pre prácu s dátami a export
- **ChromeDriver** - Automaticky spravovaný cez webdriver-manager

## Licencia

Tento projekt je určený na vzdelávacie účely pre UPA projekt na VUT FIT.
