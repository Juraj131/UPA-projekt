#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Záložný scraper iba s requests - pre prípad problémov s Playwright na serveri merlin
"""

import sys
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin


def get_tire_urls_simple():
    """
    Získa URL zimných pneumatík pomocou requests
    """
    base_url = "https://www.pneuboss.sk/pneumatiky/zimne"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    all_urls = []
    
    # Prechádzanie stránok - potrebujeme ísť na 20+ stránok pre 200+ produktov
    # Na každej stránke získavame ~12 unikátnych produktov, takže 20 stránok = ~240 produktov
    for page in range(1, 21):  # Max 20 stránok pre 200+ produktov
        try:
            url = f"{base_url}?page={page}"
            print(f"Spracovávam stránku {page}: {url}", file=sys.stderr)
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Hľadanie produktových linkov
            links = soup.find_all('a', href=True)
            page_urls = []
            
            for link in links:
                href = link.get('href')
                if href and '/pneu-' in href:
                    if href.startswith('/'):
                        full_url = 'https://www.pneuboss.sk' + href
                    else:
                        full_url = href
                    
                    if full_url not in all_urls:
                        all_urls.append(full_url)
                        page_urls.append(full_url)
            
            print(f"  Našiel som {len(page_urls)} produktov", file=sys.stderr)
            
            if len(page_urls) == 0:
                break  # Žiadne produkty na stránke

            time.sleep(1)  # Pauza medzi requestmi

        except Exception as e:
            print(f"  Chyba na stránke {page}: {e}", file=sys.stderr)
            continue
    
    print(f"Celkovo extrahovalo sa {len(all_urls)} URL", file=sys.stderr)
    
    # Výstup na stdout
    for url in all_urls:
        print(url)


def scrape_tire_simple():
    """
    Jednoduchý scraper pre pneumatiky - načíta URL z urls.txt
    """
    print("Spúšťam extrahovanie informácií o pneumatikách...", file=sys.stderr)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    # Čítanie URL zo stdin (pipeline komunikácia)
    for line_no, line in enumerate(sys.stdin, 1):
        url = line.strip()
        if not url:
            continue
            
        try:
            print(f"Spracovávam {line_no}: {url}", file=sys.stderr)
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrakcia údajov
            tire_data = {
                'url': url,
                'nazov': '',
                'cena': '',
                'typ_pneu': '',
                'segment': '',
                'sirka': '',
                'profil': '',
                'priemer': ''
            }
            
            # Názov
            title_elem = soup.find('h1')
            if title_elem:
                tire_data['nazov'] = title_elem.get_text(strip=True)
            
            # Cena - hľadáme hlavnú cenu produktu, nie doplnkové služby
            # Najprv skúsime nájsť cenu s textom "Cena" 
            cena_found = False
            
            # Hľadáme elementy ktoré obsahujú "Cena" a číslo s €
            cena_elements = soup.find_all(string=re.compile(r'Cena\s*\d+[,.]?\d*\s*€', re.IGNORECASE))
            if cena_elements:
                for elem in cena_elements:
                    price_match = re.search(r'(\d+[,.]?\d*\s*€)', elem)
                    if price_match:
                        tire_data['cena'] = price_match.group(1)
                        cena_found = True
                        break
            
            # Ak nenájdeme "Cena", hľadáme v span elementoch ale vylúčime "od" ceny
            if not cena_found:
                price_spans = soup.select('span[class*="price"]')
                for span in price_spans:
                    price_text = span.get_text(strip=True)
                    # Preskočíme ceny s "od" (to sú doplnkové služby)
                    if 'od' in price_text.lower():
                        continue
                    # Hľadáme text s číslom a € ale bez "od"
                    if re.search(r'\d+[,.]?\d*\s*€', price_text):
                        tire_data['cena'] = price_text
                        cena_found = True
                        break
            
            # Ak stále nemáme cenu, skúsime všetky texty s cenou ale uprednostníme tie bez "od"
            if not cena_found:
                all_prices = []
                for elem in soup.find_all(string=re.compile(r'\d+[,.]?\d*\s*€')):
                    price_match = re.search(r'(\d+[,.]?\d*\s*€)', elem)
                    if price_match:
                        price_val = price_match.group(1)
                        # Uprednostníme ceny bez "od"
                        if 'od' not in elem.lower():
                            tire_data['cena'] = price_val
                            cena_found = True
                            break
                        else:
                            all_prices.append(price_val)
                
                # Ak máme len "od" ceny, vezmeme prvú
                if not cena_found and all_prices:
                    tire_data['cena'] = all_prices[0]
            
            # Parametre zo span elementov - nová logika podľa štruktúry stránky
            param_mapping = {
                'Typ pneu': 'typ_pneu',
                'Segment': 'segment', 
                'Šírka': 'sirka',
                'Profil': 'profil',
                'Priemer': 'priemer'
            }
            
            for param_name, data_key in param_mapping.items():
                spans = soup.find_all('span', string=param_name)
                for span in spans:
                    next_span = span.find_next_sibling('span')
                    if next_span:
                        tire_data[data_key] = next_span.get_text(strip=True)
                        break
            
            # Extrakcia parametrov z názvu - fallback ak nie sú v span elementoch
            if tire_data['nazov']:
                title_text = tire_data['nazov']
                
                # Extrakcia rozmeru typu 165/70 R 14 ak nie je v span elementoch
                size_match = re.search(r'(\d+)/(\d+)\s*R\s*(\d+)', title_text)
                if size_match:
                    if not tire_data['sirka']:
                        tire_data['sirka'] = size_match.group(1)
                    if not tire_data['profil']:
                        tire_data['profil'] = size_match.group(2)  
                    if not tire_data['priemer']:
                        tire_data['priemer'] = size_match.group(3)
                
            
            # TSV výstup - nová štruktúra: URL, názov, cena, typ pneu, segment, šírka, profil, priemer
            output = "\t".join([
                tire_data['url'],
                tire_data['nazov'],
                tire_data['cena'],
                tire_data['typ_pneu'],
                tire_data['segment'],
                tire_data['sirka'],
                tire_data['profil'],
                tire_data['priemer']
            ])
            print(output)
            
            time.sleep(0.5)  # Pauza medzi requestmi
            
        except Exception as e:
            print(f"  Chyba: {e}", file=sys.stderr)
            continue


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "scrape":
        scrape_tire_simple()
    else:
        get_tire_urls_simple()