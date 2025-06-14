import requests
import json
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import cloudscraper
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from tavily import TavilyClient
from dotenv import load_dotenv, find_dotenv
import os
import shutil
import platform
load_dotenv(find_dotenv())

scraper_api = os.environ.get("SCRAPERAPI_KEY")

# Remove webdriver_manager cache directory
cache_dir = os.path.expanduser("~/.wdm")
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)

print("Python:", platform.architecture())
print("ChromeDriverManager path:", ChromeDriverManager().install())

def scraperapi_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    proxies = {"http": f"http://scraperapi:{scraper_api}@proxy-server.scraperapi.com:8001"}
    print(f"🔍 Searching via Google: {query}")
    try:
        response = requests.get(search_url, proxies=proxies)
        response.raise_for_status()
        results = response.json()
        if 'items' in results and len(results['items']) > 0:
            link = results['items'][0]['link']
            print(f"🔗 Got link: {link}")
            return link
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"⚠️ Google Search (ScraperAPI) returned 429. Falling back to Tavily API...")
            try:
                client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
                tavily_results = client.search(
                    query=query,
                    search_depth="basic",
                    include_answer=False,
                    include_images=False,
                    max_results=1
                )
                if 'results' in tavily_results and len(tavily_results['results']) > 0:
                    link = tavily_results['results'][0]['url']
                    print(f"🔗 Got link from Tavily: {link}")
                    return link
                else:
                    print("❌ No results found from Tavily API.")
            except Exception as tavily_e:
                print(f"❌ Error with Tavily API fallback: {tavily_e}")
        else:
            print(f"❌ HTTP error during Google search: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred during Google search: {e}")
    print("❌ No results found")
    return None

def main3(primary_prompt, secondary_prompt):
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY4")
    GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID7")
    search_url = scraperapi_search(primary_prompt, GOOGLE_API_KEY, GOOGLE_CSE_ID)
    print(f"venture url: {search_url}")
    if not search_url:
        print("🛑 Ending - couldn't get venture capitalist")
        return
    investors = scrape_page(search_url, 'venture.json')
    angel_url = scraperapi_search(secondary_prompt, GOOGLE_API_KEY, GOOGLE_CSE_ID)
    print(f"angel investors URL: {angel_url}")
    if not angel_url:
        print("🛑 Ending - couldn't get primary search result")
        return
    ind_investors = scrape_page(angel_url, 'angel.json')

def scrape_page(url, filename):
    """
    Scrapes all investor details from the given URL using cloudscraper + BeautifulSoup as primary,
    and Selenium as a backup. Saves results in the specified filename (e.g., venture.json or angel.json).
    """
    from selenium.webdriver.common.by import By
    import json
    import os
    import time
    from bs4 import BeautifulSoup
    import cloudscraper

    data = {}
    success = False
    # --- Primary: cloudscraper + BeautifulSoup ---
    try:
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(url)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # All .last__menu blocks
            menus = soup.find_all(class_='last__menu')
            all_investors = []
            for menu in menus:
                investor = {}
                name_tag = menu.find(class_='investor__name')
                meta_tag = menu.find(class_='investor__meta')
                investor['name'] = name_tag.get_text(strip=True) if name_tag else None
                investor['meta'] = meta_tag.get_text(strip=True) if meta_tag else None
                all_investors.append(investor)
            data['investors'] = all_investors
            # All descriptions
            desc_tags = soup.select('div.desc[data-canonical-name]')
            data['descriptions'] = [desc.get_text(strip=True) for desc in desc_tags]
            # All investment focus and highlights
            focus_blocks = soup.find_all(class_='portfolio-feature-list')
            investment_focus = []
            portfolio_highlights = []
            for block in focus_blocks:
                feature_name = block.find(class_='feature-name')
                feature = feature_name.get_text(strip=True) if feature_name else ''
                if 'Investment focus' in feature:
                    focus_list = [li.get_text(strip=True) for li in block.find_all('li')]
                    investment_focus.extend(focus_list)
                if 'Portfolio highlights' in feature:
                    highlights = []
                    for li in block.find_all('li'):
                        a = li.find('a')
                        url = a['href'] if a and a.has_attr('href') else None
                        title = a.get_text(strip=True) if a else ''
                        desc = li.get_text(strip=True).replace(title, '').replace('—', '').strip()
                        highlights.append({'title': title, 'url': url, 'description': desc})
                    portfolio_highlights.extend(highlights)
            data['investment_focus'] = investment_focus
            data['portfolio_highlights'] = portfolio_highlights
            success = True
        else:
            print(f"cloudscraper failed to fetch page, status code: {resp.status_code}")
            data['error'] = f"cloudscraper status code: {resp.status_code}"
    except Exception as ce:
        print(f"cloudscraper failed: {ce}")
        data['error'] = f"cloudscraper error: {ce}"

    # --- Backup: Selenium ---
    if not success:
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            time.sleep(3)  # Wait for page to load
            # All .last__menu blocks
            menus = driver.find_elements(By.CLASS_NAME, 'last__menu')
            all_investors = []
            for menu in menus:
                investor = {}
                try:
                    investor['name'] = menu.find_element(By.CLASS_NAME, 'investor__name').text.strip()
                except Exception:
                    investor['name'] = None
                try:
                    investor['meta'] = menu.find_element(By.CLASS_NAME, 'investor__meta').text.strip()
                except Exception:
                    investor['meta'] = None
                all_investors.append(investor)
            data['investors'] = all_investors
            # All descriptions
            desc_tags = driver.find_elements(By.CSS_SELECTOR, 'div.desc[data-canonical-name]')
            data['descriptions'] = [desc.text.strip() for desc in desc_tags]
            # All investment focus and highlights
            focus_blocks = driver.find_elements(By.CLASS_NAME, 'portfolio-feature-list')
            investment_focus = []
            portfolio_highlights = []
            for block in focus_blocks:
                try:
                    feature = block.find_element(By.CLASS_NAME, 'feature-name').text.strip()
                except Exception:
                    feature = ''
                if 'Investment focus' in feature:
                    focus_list = [li.text.strip() for li in block.find_elements(By.TAG_NAME, 'li')]
                    investment_focus.extend(focus_list)
                if 'Portfolio highlights' in feature:
                    highlights = []
                    for li in block.find_elements(By.TAG_NAME, 'li'):
                        try:
                            a = li.find_element(By.TAG_NAME, 'a')
                            url = a.get_attribute('href')
                            title = a.text.strip()
                        except Exception:
                            url = None
                            title = ''
                        desc = li.text.replace(title, '').replace('—', '').strip()
                        highlights.append({'title': title, 'url': url, 'description': desc})
                    portfolio_highlights.extend(highlights)
            data['investment_focus'] = investment_focus
            data['portfolio_highlights'] = portfolio_highlights
            driver.quit()
        except Exception as e:
            print(f"Selenium backup also failed: {e}")
            data['error'] = f"Selenium error: {e}"
    # Save to the specified file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

if __name__ == "__main__":
    main3("telemedicine sector venture capitalist shizune india", "telemedicine sector angel investors shizune india")