# UPA Projekt 2 - Web Scraping

**Nazov tymu:** UPA-Team-2025  
**Riesitelia:**
- Juraj Bendik, Adam Brezina

## E-shop

**URL:** https://www.pneuboss.sk  
**Nazov:** PneumaBoss - slovensky e-shop s pneumatikami  
**Kategoria:** Zimne pneumatiky  

Dovod vyberu: Specializovany e-shop s podrobnymi parametrami pneumatik v tabulkach, menej znamy nez hlavne e-shopy, slovensky obsah.

## Implementácia

**Skripty:**
- `get_urls.py` - Ziskava zoznam URL produktov (zimnych pneumatik)
- `fallback_scraper.py` - Extrahuje detailne informacie z produktovych stranok
- `build.sh` - Instalacia zavislosti a priprava
- `run.sh` - Testovaci skript

**Technologie:**
- Python 3 + virtualne prostredie (venv)
- Playwright (automatizacia prehliadaca)
- BeautifulSoup4 (parsovanie HTML)
- Requests (HTTP requesty)

## Instalacia

1. Uistite sa, ze mate Python 3.7+ nainstalovany
2. Aktivujte virtualne prostredie (uz vytvorene)
3. Baliky su uz nainstalovane v projekte

## Vyznam stlpcov TSV vystupu

Vystupny TSV subor obsahuje **8 stlpcov** bez hlavicky:

| Poradie | Nazov | Typ | Popis |
|---------|-------|-----|--------|
| 1 | url | ID | URL produktu (identifikacia) |
| 2 | nazov | string | Nazov pneumatiky |
| 3 | cena | string | Aktualna predajna cena (napr. "54,83 €") |
| 4 | typ_pneu | kategoricky | Typ pneumatiky (Osobne pneu, Dodavkove a nakladni pneu) |
| 5 | segment | kategoricky | Cenovy segment (Ekonomicka trieda, Stredna trieda, Premiova trieda) |
| 6 | sirka | ciselny | Sirka pneumatiky v mm |
| 7 | profil | ciselny | Vyska profilu v % |
| 8 | priemer | ciselny | Priemer rafiku v palcoch |

## Spustenie

### Priprava prostredia:
```bash
./build.sh
```

### Test na prvych 10 produktoch:
```bash  
./run.sh
```

### Uplne spracovanie:
```bash
# 1. Ziskanie vsetkych URL (150+)
python3 get_urls.py > urls.txt

# 2. Spracovanie vsetkych produktov
cat urls.txt | python3 scraper.py > data.tsv
```

## Poznamky

**Zalozne riesenie:** V pripade problemov s Playwright na serveri merlin je k dispozicii `fallback_scraper.py` ktory pouziva iba requests + BeautifulSoup.

**Pouzitie zalozneho scrapera:**
```bash
# Ziskanie URL
python3 fallback_scraper.py > urls.txt

# Spracovanie produktov  
cat urls.txt | python3 fallback_scraper.py scrape > data.tsv
```

**Ohladuplnost k serveru:** Skripty obsahuju casove pauzy medzi requestmi (0.5-1s) aby nezatazovali server.

**Testovane URL:** Vsetky uvedene URL boli testovane a su funkcne k datumu vytvorenia projektu.

## Výstup

Skript vytvori TSV subor `produkty.tsv` s nasledujucimi stlpcami:

1. **url** - URL produktu
2. **nazov** - Nazov/meno produktu
3. **cena** - Cena produktu
4. **kategoria_1** az **kategoria_5** - Pat kategorii z tabulky alebo breadcrumbs

## Priklady pouzitia

### Pre e-shop s produktmi:
```
URL: https://example-eshop.sk/produkty
CSS selektor: .product-item a
Pocet produktov: 50
```

### Pre stranku s katalogom:
```
URL: https://katalog.sk/kategoria/elektronika
CSS selektor: a[href*="/produkt/"]
Pocet produktov: 20
```

## Funkcie

### ProductScraper trieda

- **`get_product_links()`** - Najde vsetky linky na produkty
- **`scrape_product_details()`** - Extrahuje detaily konkretneho produktu
- **`scrape_products()`** - Hlavna metoda na spracovanie vsetkych produktov
- **`save_to_tsv()`** - Ulozi data do TSV suboru

### Automaticka detekcia

Scraper sa pokusi automaticky detegovat:
- Produktove linky (rozne pattern-y)
- Nazvy produktov (h1, h2, .title, .product-name, atd.)
- Ceny (.price, .product-price, [data-price], atd.)
- Kategorie (breadcrumbs, tabulky, meta tagy)

## Riesenie problemov

### Nenachadzaju sa produkty
1. Spustite `page_analyzer.py` na analyzu struktury
2. Pouzijte konkretny CSS selektor
3. Skontrolujte, ci stranka nacitava obsah cez JavaScript

### Prazdne udaje
1. Stranka moze potrebovat viac casu na nacitanie (upravte `time.sleep()`)
2. Elementi mozu mat ine CSS triedy/selektory
3. Obsah moze byt generovany dynamicky

### Chyby pri spusteni
1. Uistite sa, ze mate Chrome nainstalovany
2. Skontrolujte internetove pripojenie
3. Niektore stranky mozu blokovat automatizovane requesty

## Prisposobenie

### Pridanie vlastnych selektorov:

V `product_scraper.py` mozete upravit:

```python
# Pre nazvy produktov
name_selectors = [
    'h1',
    '.custom-product-title',  # Vas vlastny selektor
    '.product-name'
]

# Pre ceny
price_selectors = [
    '.price',
    '.custom-price-class',    # Vas vlastny selektor
    '[data-custom-price]'
]
```

### Zmena vystupu:

Mozete pridat dalsie stlpce v metode `scrape_product_details()`:

```python
product = {
    'url': product_url,
    'nazov': '',
    'cena': '',
    'popis': '',              # Novy stlpec
    'dostupnost': '',         # Novy stlpec
    'kategoria_1': '',
    # ... atd
}
```

## Technicke detaily

- **Selenium WebDriver** - Pre interakciu s dynamickym obsahom
- **BeautifulSoup** - Pre parsovanie HTML
- **Pandas** - Pre pracu s datami a export
- **ChromeDriver** - Automaticky spravovany cez webdriver-manager

## Licencia

<<<<<<< HEAD
Tento projekt je urceny na vzdelacie ucely pre UPA projekt na VUT FIT.
=======
Tento projekt je určený na vzdelávacie účely pre UPA projekt na VUT FIT.
>>>>>>> 5ccc079c2203dded64ae5c509d538c82c3fe90c2
