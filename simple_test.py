#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jednoduchy test scraper pre prvych 5 pneumatik
Pouziva rovnaku logiku ako fallback_scraper.py ale spracovava iba 5 produktov
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import sys


def test_scrape_5_tires():
    """
    Spracuje prvych 5 URL z urls.txt a vytvori test_data.tsv
    """
    print("Spustam test extrahovanie pre prvych 5 pneumatik...", file=sys.stderr)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Nacitanie prvych 5 URL z urls.txt
    try:
        # Skusime rozne kodovania
        for encoding in ['utf-16', 'utf-8-sig', 'utf-8', 'cp1252', 'iso-8859-1']:
            try:
                with open('urls.txt', 'r', encoding=encoding) as f:
                    lines = f.readlines()[:5]
                    urls = []
                    for line in lines:
                        # Vycistime URL od BOM a neplatnych znakov
                        clean_url = ''.join(c for c in line.strip() if ord(c) < 127 and c.isprintable())
                        if clean_url and clean_url.startswith('http'):
                            urls.append(clean_url)
                    if urls:  # Ak sme nasli nejake platne URL
                        break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            print("Nepodarilo sa nacitat platne URLs z urls.txt!", file=sys.stderr)
            return
    except FileNotFoundError:
        print("Subor urls.txt sa nenasiel!", file=sys.stderr)
        return
    
    processed_count = 0
    
    for i, url in enumerate(urls, 1):
        if not url:
            continue
            
        try:
            print(f"Spracovavam {i}/5: {url}", file=sys.stderr)
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrakcia udajov - nova struktura podla poziadavky
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
            
            # Nazov
            title_elem = soup.find('h1')
            if title_elem:
                tire_data['nazov'] = title_elem.get_text(strip=True)
            
            # Cena - hladame hlavnu cenu produktu, nie doplnkove sluzby
            # Najprv skusime najst cenu s textom "Cena" 
            cena_found = False
            
            # Hladame elementy ktore obsahuju "Cena" a cislo s €
            cena_elements = soup.find_all(string=re.compile(r'Cena\s*\d+[,.]?\d*\s*€', re.IGNORECASE))
            if cena_elements:
                for elem in cena_elements:
                    price_match = re.search(r'(\d+[,.]?\d*\s*€)', elem)
                    if price_match:
                        tire_data['cena'] = price_match.group(1)
                        cena_found = True
                        break
            
            # Ak nenajdeme "Cena", hladame v span elementoch ale vylucime "od" ceny
            if not cena_found:
                price_spans = soup.select('span[class*="price"]')
                for span in price_spans:
                    price_text = span.get_text(strip=True)
                    # Preskocime ceny s "od" (to su doplnkove sluzby)
                    if 'od' in price_text.lower():
                        continue
                    # Hladame text s cislom a € ale bez "od"
                    if re.search(r'\d+[,.]?\d*\s*€', price_text):
                        tire_data['cena'] = price_text
                        cena_found = True
                        break
            
            # Ak stale nemame cenu, skusime vsetky texty s cenou ale uprednostnime tie bez "od"
            if not cena_found:
                all_prices = []
                for elem in soup.find_all(string=re.compile(r'\d+[,.]?\d*\s*€')):
                    price_match = re.search(r'(\d+[,.]?\d*\s*€)', elem)
                    if price_match:
                        price_val = price_match.group(1)
                        # Uprednostnime ceny bez "od"
                        if 'od' not in elem.lower():
                            tire_data['cena'] = price_val
                            cena_found = True
                            break
                        else:
                            all_prices.append(price_val)
                
                # Ak mame len "od" ceny, vezmeme prvu
                if not cena_found and all_prices:
                    tire_data['cena'] = all_prices[0]
            
            # Parametre zo span elementov - nova logika podla struktury stranky
            param_mapping = {
                'Typ pneu': 'typ_pneu',
                'Segment': 'segment', 
                'Sirka': 'sirka',
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
            
            # Extrakcia parametrov z nazvu - fallback ak nie su v tabulke
            if tire_data['nazov']:
                title_text = tire_data['nazov']
                
                # Extrakcia rozmeru typu 165/70 R 14 ak nie je v tabulke
                size_match = re.search(r'(\d+)/(\d+)\s*R\s*(\d+)', title_text)
                if size_match:
                    if not tire_data['sirka']:
                        tire_data['sirka'] = size_match.group(1)
                    if not tire_data['profil']:
                        tire_data['profil'] = size_match.group(2)  
                    if not tire_data['priemer']:
                        tire_data['priemer'] = size_match.group(3)
            
            # TSV vystup - nova struktura: URL, nazov, cena, typ pneu, segment, sirka, profil, priemer
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
            processed_count += 1
            
            time.sleep(0.5)  # Pauza medzi requestmi
            
        except Exception as e:
            print(f"  Chyba pri spracovani {url}: {e}", file=sys.stderr)
            continue
    
    print(f"\nSpracovanych: {processed_count}/5 pneumatik", file=sys.stderr)


if __name__ == "__main__":
    test_scrape_5_tires()