#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jednoduchý test scraper pre prvých 5 pneumatík
Používa rovnakú logiku ako fallback_scraper.py ale spracováva iba 5 produktov
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import sys


def test_scrape_5_tires():
    """
    Spracuje prvých 5 URL z urls.txt a vytvorí test_data.tsv
    """
    print("Spúšťam test extrahovanie pre prvých 5 pneumatík...", file=sys.stderr)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Načítanie prvých 5 URL z urls.txt
    try:
        # Skúsime rôzne kódovania
        for encoding in ['utf-16', 'utf-8-sig', 'utf-8', 'cp1252', 'iso-8859-1']:
            try:
                with open('urls.txt', 'r', encoding=encoding) as f:
                    lines = f.readlines()[:5]
                    urls = []
                    for line in lines:
                        # Vyčistíme URL od BOM a neplatných znakov
                        clean_url = ''.join(c for c in line.strip() if ord(c) < 127 and c.isprintable())
                        if clean_url and clean_url.startswith('http'):
                            urls.append(clean_url)
                    if urls:  # Ak sme našli nejaké platné URL
                        break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            print("Nepodarilo sa načítať platné URLs z urls.txt!", file=sys.stderr)
            return
    except FileNotFoundError:
        print("Súbor urls.txt sa nenašiel!", file=sys.stderr)
        return
    
    processed_count = 0
    
    for i, url in enumerate(urls, 1):
        if not url:
            continue
            
        try:
            print(f"Spracovávam {i}/5: {url}", file=sys.stderr)
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrakcia údajov - nová štruktúra podľa požiadavky
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
            
            # Extrakcia parametrov z názvu - fallback ak nie sú v tabuľke
            if tire_data['nazov']:
                title_text = tire_data['nazov']
                
                # Extrakcia rozmeru typu 165/70 R 14 ak nie je v tabuľke
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
            processed_count += 1
            
            time.sleep(0.5)  # Pauza medzi requestmi
            
        except Exception as e:
            print(f"  Chyba pri spracovaní {url}: {e}", file=sys.stderr)
            continue
    
    print(f"\nSpracovaných: {processed_count}/5 pneumatík", file=sys.stderr)


if __name__ == "__main__":
    test_scrape_5_tires()