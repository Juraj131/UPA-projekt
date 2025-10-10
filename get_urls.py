#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skript 1: get_urls.py
Extrakcia URL adries produktov z kategórie/zoznamu
Podľa architektúry z prednášky - slide 7, 30-34
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import sys
import time


async def get_product_urls(base_url, max_pages=5):
    """
    Extrahuje URL produktov zo stránky pomocou Playwright
    
    Args:
        base_url (str): Základná URL kategórie/zoznamu
        max_pages (int): Maximálny počet stránok na prechádzanie
    
    Returns:
        list: Zoznam URL produktov
    """
    print(f"🌐 Spúšťam extrakciu URL z: {base_url}", file=sys.stderr)
    print(f"📄 Max stránok: {max_pages}", file=sys.stderr)
    
    async with async_playwright() as p:
        # Spustenie prehliadača v headless režime (slide 30)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        all_product_urls = []
        
        try:
            for page_num in range(1, max_pages + 1):
                print(f"🔄 Spracovávam stránku {page_num}/{max_pages}", file=sys.stderr)
                
                # Vytvorenie URL pre stránku
                if '?' in base_url:
                    page_url = f"{base_url}&page={page_num}"
                else:
                    page_url = f"{base_url}?page={page_num}"
                
                print(f"📡 Načítavam: {page_url}", file=sys.stderr)
                
                # Navigácia na stránku (slide 31)
                await page.goto(page_url, wait_until="networkidle")
                
                # Čakanie na vykonanie JavaScript (slide 32-33)
                await page.wait_for_timeout(2000)  # 2 sekundy na JS
                
                # Pokus o čakanie na produktový kontajner
                try:
                    await page.wait_for_selector('[class*="product"], .item, article', timeout=5000)
                except:
                    print(f"⚠️ Timeout - pokračujem bez čakania na selektor", file=sys.stderr)
                
                # Získanie finálneho HTML (slide 27)
                html_content = await page.content()
                
                # Parsovanie pomocou BeautifulSoup (slide 27)
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extrakcia produktových linkov (slide 24 - CSS selektory)
                page_urls = extract_product_links(soup, base_url)
                
                if page_urls:
                    all_product_urls.extend(page_urls)
                    print(f"✅ Stránka {page_num}: {len(page_urls)} produktov", file=sys.stderr)
                else:
                    print(f"❌ Stránka {page_num}: Žiadne produkty - končím", file=sys.stderr)
                    break
                
                # Pauza medzi stránkami
                await asyncio.sleep(1)
        
        except Exception as e:
            print(f"❌ Chyba pri spracovaní: {e}", file=sys.stderr)
        
        finally:
            await browser.close()
        
        return list(set(all_product_urls))  # Odstránenie duplikátov


def extract_product_links(soup, base_url):
    """
    Extrahuje linky na produkty zo soup objektu
    Špecializované na PneumaBoss štruktúru
    """
    product_urls = []
    
    # CSS selektory špecifické pre PneumaBoss
    selectors = [
        'a[href*="/pneu-"]',        # Hlavný pattern pre produkty
        'a[href*="pneumatik"]',      # Alternatívny pattern  
        '.product-item a',          # Produktové kontajnery
        '.tire-item a',             # Pneumatikové kontajnery
        'a[title*="pneu"]'          # Linky s pneumatikami v title
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        
        if elements:
            print(f"🎯 Našiel som {len(elements)} linkov: {selector}", file=sys.stderr)
            
            for element in elements:
                href = element.get('href')
                if href and href not in product_urls:
                    # Vytvorenie absolútnej URL
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = 'https://www.pneuboss.sk' + href
                    else:
                        full_url = base_url.rstrip('/') + '/' + href
                    
                    # Filtrovanie relevantných pneumatík 
                    if ('pneuboss.sk' in full_url and 
                        any(keyword in full_url.lower() for keyword in ['/pneu-', 'pneumatik', 'tire']) and
                        not any(skip in full_url.lower() for skip in ['kategoria', 'filter', 'search', 'cart'])):
                        product_urls.append(full_url)
            
            if len(product_urls) > 20:  # Ak našiel dostatok, prestaň hľadať
                break
    
    return product_urls


async def main():
    """
    Hlavná funkcia - vstupný bod
    Získa minimálne 150 URL produktov podľa zadania
    """
    # Základná URL pre zimné pneumatiky na pneuboss.sk
    base_url = "https://www.pneuboss.sk/pneumatiky/zimne"
    max_pages = 20  # Dostatok stránok pre 150+ produktov
    
    print(f"Začínam extrahovať URL zimných pneumatík z {base_url}", file=sys.stderr)
    print(f"Cieľ: minimálne 150 produktov", file=sys.stderr)
    
    # Extrakcia URL produktov
    product_urls = await get_product_urls(base_url, max_pages)
    
    # Filtrovanie - iba relevantné pneumatiky
    filtered_urls = []
    for url in product_urls:
        if any(keyword in url.lower() for keyword in ['pneu', 'tire', 'winter', 'zimn']):
            # Kontrola že nie je to duplicita alebo nerelevantný link
            if url not in filtered_urls and 'pneuboss.sk' in url:
                filtered_urls.append(url)
    
    print(f"Extrahovalo sa {len(filtered_urls)} relevantných URL produktov", file=sys.stderr)
    
    # Zabezpečenie minimálne 150 produktov
    if len(filtered_urls) < 150:
        print(f"UPOZORNENIE: Našlo sa len {len(filtered_urls)} produktov, požadovaných je 150+", file=sys.stderr)
    
    # Výstup URL na štandardný výstup (bez hlavičky, jeden URL na riadok)
    for url in filtered_urls:
        print(url)  # stdout pre ďalší skript


if __name__ == "__main__":
    asyncio.run(main())