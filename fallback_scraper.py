#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zalozny scraper iba s requests - pre pripad problemov s Playwright na serveri merlin
"""

import sys
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin


# Funkcia get_tire_urls_simple() bola prenesená do get_urls.py


def scrape_tire_simple():
    """
    Jednoduchy scraper pre pneumatiky - nacita URL z urls.txt
    """
    print("Spustam extrahovanie informacii o pneumatikach...", file=sys.stderr)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    # Citanie URL zo stdin (pipeline komunikacia)
    for line_no, line in enumerate(sys.stdin, 1):
        url = line.strip()
        if not url:
            continue
            
        try:
            print(f"Spracovavam {line_no}: {url}", file=sys.stderr)
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrakcia udajov
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
            
            # Extrakcia parametrov z nazvu - fallback ak nie su v span elementoch
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
            
            time.sleep(0.5)  # Pauza medzi requestmi
            
        except Exception as e:
            print(f"  Chyba: {e}", file=sys.stderr)
            continue


if __name__ == "__main__":
    # Tento skript teraz slúži iba na scrapovanie
    # URL extrakcia je v get_urls.py
    scrape_tire_simple()