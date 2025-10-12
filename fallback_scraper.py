#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
from bs4 import BeautifulSoup
import re
import time

# Funkcia get_tire_urls_simple() bola prenesená do get_urls.py

def scrape_tire_simple():
    """
    Scraper pro pneuboss.sk - nacita URL z urls.txt
    """
    print("Extrahovani informacii o pneu...", file=sys.stderr)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    # Cteni URL z stdin
    for line_no, line in enumerate(sys.stdin, 1):
        url = line.strip()
        if not url:
            continue
            
        try:
            print(f"Spracovanie {line_no}: {url}", file=sys.stderr)
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # udaje o pneu
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
            
            # Nazev pneu
            title_elem = soup.find('h1')
            if title_elem:
                tire_data['nazov'] = title_elem.get_text(strip=True)
            
            cena_found = False
            
            # Main hledani ceny
            cena_elements = soup.find_all(string=re.compile(r'Cena\s*\d+[,.]?\d*\s*€', re.IGNORECASE))
            if cena_elements:
                for elem in cena_elements:
                    price_match = re.search(r'(\d+[,.]?\d*\s*€)', elem)
                    if price_match:
                        tire_data['cena'] = price_match.group(1)
                        #debug print
                        print(f"Cena nalezena pres 'Cena'")
                        cena_found = True
                        break
            
            # Fallback hledani ceny ve span elementech"
            if not cena_found:
                price_spans = soup.select('span[class*="price"]')
                for span in price_spans:
                    price_text = span.get_text(strip=True)
                    # Skip doplnkovych cen ("od" ceny)
                    if 'od' in price_text.lower():
                        continue
                    # Hledame text s cislem a € ale bez "od"
                    if re.search(r'\d+[,.]?\d*\s*€', price_text):
                        tire_data['cena'] = price_text
                        #debug print
                        print(f"Cena nalezena pres span")
                        cena_found = True
                        break
            
            # Parametry ze span elementu
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
            
            # Fallback - extrakce z nazvu pneu 
            if tire_data['nazov']:
                title_text = tire_data['nazov']
                
                # Extrakce rozmeru typu 165/70 R 14 kdyz neni v span elementech
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
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  Chyba: {e}", file=sys.stderr)
            continue 


if __name__ == "__main__":
    scrape_tire_simple()