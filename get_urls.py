"""
Skript 1: get_urls.py
Extrakcia URL adries produktov z kategorie/zoznamu pomocou requests
"""

import sys
import requests
from bs4 import BeautifulSoup
import time


def get_tire_urls_simple():
    """
    Ziska URL zimnych pneumatik pomocou requests
    """
    base_url = "https://www.pneuboss.sk/pneumatiky/zimne"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    all_urls = []
    
    # Prechadzavanie stranok - 20+ stranok pre 200+ produktov
    for page in range(1, 21):
        try:
            url = f"{base_url}?page={page}"
            print(f"Stranka {page}: {url}", file=sys.stderr)
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Hladanie produktovych linkov
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
            
            print(f"  Dostupnych {len(page_urls)} produktov", file=sys.stderr)
            
            if len(page_urls) == 0:
                break

            time.sleep(1)

        except Exception as e:
            print(f"  Chyba na stranke {page}: {e}", file=sys.stderr)
            continue
    
    print(f"Extrahovanych {len(all_urls)} URLs", file=sys.stderr)
    
    # Vystup na stdout
    for url in all_urls:
        print(url)


def main():
    """
    Hlavna funkcia - vstupny bod
    Ziska minimalne 150 URLs
    """
    print(f"Extrakcia URL zimnych pneumatik z https://www.pneuboss.sk/pneumatiky/zimne", file=sys.stderr)
    print(f"Minimalne 150 produktov", file=sys.stderr)
    
    get_tire_urls_simple()


if __name__ == "__main__":
    main()