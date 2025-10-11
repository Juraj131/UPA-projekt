#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skript 1: get_urls.py
Extrakcia URL adries produktov z kategorie/zoznamu
"""

import asyncio
import sys
import time
from bs4 import BeautifulSoup
import requests

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


async def get_product_urls(base_url, max_pages=5):
    """
    Extrahuje URL produktov zo stranky pomocou Playwright
    
    Args:
        base_url (str): Zakladna URL kategorie/zoznamu
        max_pages (int): Maximalny pocet stranok na prechadzavanie
    
    Returns:
        list: Zoznam URL produktov
    """
    print(f"Extrakciu URL z: {base_url}", file=sys.stderr)
    print(f"Max stranok: {max_pages}", file=sys.stderr)
    
    async with async_playwright() as p:
        # Spustenie prehliadaca v headless rezime
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        all_product_urls = []
        
        try:
            for page_num in range(1, max_pages + 1):
                print(f"Stranka {page_num}/{max_pages}", file=sys.stderr)
                
                # Vytvorenie URL pre stranku
                if '?' in base_url:
                    page_url = f"{base_url}&page={page_num}"
                else:
                    page_url = f"{base_url}?page={page_num}"
                
                print(f"Nacitavanie: {page_url}", file=sys.stderr)
            
                # Navigacia na stranku
                await page.goto(page_url, wait_until="networkidle")
                
                # Cakanie na vykonanie JavaScript
                await page.wait_for_timeout(2000)  # 2 sekundy na JS
                
                # Pokus o cakanie na produktovy kontajner
                try:
                    await page.wait_for_selector('[class*="product"], .item, article', timeout=5000)
                except:
                    print(f"Timeout", file=sys.stderr)

                # Ziskanie finalneho HTML
                html_content = await page.content()

                # Parsovanie pomocou BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extrakcia produktovych linkov
                page_urls = extract_product_links(soup, base_url)
                
                if page_urls:
                    all_product_urls.extend(page_urls)
                    print(f"Stranka {page_num}: {len(page_urls)} produktov", file=sys.stderr)
                else:
                    print(f"Stranka {page_num}: Ziadne produkty - koncim", file=sys.stderr)
                    break
                
                # Pauza medzi strankami
                await asyncio.sleep(1)
        
        except Exception as e:
            print(f"Chyba pri spracovani: {e}", file=sys.stderr)
        
        finally:
            await browser.close()
        
        return list(set(all_product_urls))  # Odstranenie duplikatov


def extract_product_links(soup, base_url):
    """
    Extrahuje linky na produkty zo soup objektu
    Specializovane na PneumaBoss strukturu
    """
    product_urls = []
    
    # CSS selektory specificke pre PneumaBoss
    selectors = [
        'a[href*="/pneu-"]',        # Hlavny pattern pre produkty
        'a[href*="pneumatik"]',      # Alternativny pattern  
        '.product-item a',          # Produktove kontajnery
        '.tire-item a',             # Pneumatikove kontajnery
        'a[title*="pneu"]'          # Linky s pneumatikami v title
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        
        if elements:
            print(f"Najdenych {len(elements)} linkov: {selector}", file=sys.stderr)
            
            for element in elements:
                href = element.get('href')
                if href and href not in product_urls:
                    # Vytvorenie absolutnej URL
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = 'https://www.pneuboss.sk' + href
                    else:
                        full_url = base_url.rstrip('/') + '/' + href
                    
                    # Filtrovanie relevantnych pneumatik 
                    if ('pneuboss.sk' in full_url and 
                        any(keyword in full_url.lower() for keyword in ['/pneu-', 'pneumatik', 'tire']) and
                        not any(skip in full_url.lower() for skip in ['kategoria', 'filter', 'search', 'cart'])):
                        product_urls.append(full_url)
            
            if len(product_urls) > 20:
                break
    
    return product_urls


def get_urls_fallback(base_url, max_pages):
    """
    Fallback metoda bez Playwright - iba requests
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    all_urls = []
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}?page={page}"
            print(f"Stranka {page}/{max_pages}", file=sys.stderr)
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            page_urls = []
            links = soup.find_all('a', href=True)
            
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
            
            print(f"Stranka {page}: {len(page_urls)} produktov", file=sys.stderr)
            
            if len(page_urls) == 0:
                break
                
            time.sleep(1)
            
        except Exception as e:
            print(f"Chyba pri spracovani: {e}", file=sys.stderr)
            continue
    
    return all_urls


async def main():
    """
    Hlavna funkcia - vstupny bod
    Ziska minimalne 150 URL produktov podla zadania
    """
    # Zakladna URL pre zimne pneumatiky na pneuboss.sk
    base_url = "https://www.pneuboss.sk/pneumatiky/zimne"
    max_pages = 20  # Dostatok stranok pre 150+ produktov

    print(f"Extrakcia URL zimnych pneumatik z {base_url}", file=sys.stderr)
    print(f"Ciel: minimalne 150 produktov", file=sys.stderr)
    
    # Skus Playwright, ak zlyhá pouzi fallback
    product_urls = []
    if PLAYWRIGHT_AVAILABLE:
        try:
            print("Pouzivam Playwright...", file=sys.stderr)
            product_urls = await get_product_urls(base_url, max_pages)
        except Exception as e:
            print(f"Playwright zlyhal: {e}", file=sys.stderr)
            print("Prepnutie na fallback metodu...", file=sys.stderr)
            product_urls = get_urls_fallback(base_url, max_pages)
    else:
        print("Playwright nie je dostupny, pouzivam fallback...", file=sys.stderr)
        product_urls = get_urls_fallback(base_url, max_pages)
    
    # Filtrovanie - iba relevantne pneumatiky
    filtered_urls = []
    for url in product_urls:
        if any(keyword in url.lower() for keyword in ['pneu', 'tire', 'winter', 'zimn']):
            # Kontrola ze nie je to duplicita alebo nerelevantny link
            if url not in filtered_urls and 'pneuboss.sk' in url:
                filtered_urls.append(url)
    
    print(f"Extrahovalo sa {len(filtered_urls)} relevantnych URL produktov", file=sys.stderr)
    
    # Zabezpecenie minimalne 150 produktov
    if len(filtered_urls) < 150:
        print(f"UPOZORNENIE: Naslo sa len {len(filtered_urls)} produktov, pozadovanych je 150+", file=sys.stderr)
    
    # Vystup URL na standardny vystup (bez hlavicky, jeden URL na riadok)
    for url in filtered_urls:
        print(url)  # stdout pre dalsi skript


if __name__ == "__main__":
    asyncio.run(main())