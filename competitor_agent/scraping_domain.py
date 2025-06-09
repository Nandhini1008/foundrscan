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
from competitor_agent.integrate_llm import main2
from concurrent.futures import ThreadPoolExecutor, as_completed
from competitor_agent.process_data import final
from tavily import TavilyClient

SCRAPERAPI_KEY = "35980585e6d064d45abb0bd5a3d32e39"
GOOGLE_API_KEY = ""
GOOGLE_CSE_ID = ""
TAVILY_API_KEY = "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" # Placeholder - user should replace with their actual key

output_data = []

# 💥 Step 1: Google Search with ScraperAPI
def scraperapi_search(query, GOOGLE_API_KEY, GOOGLE_CSE_ID):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    proxies = {"http": f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001"}
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
                client = TavilyClient(api_key=TAVILY_API_KEY)
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

# 💥 Step 2: Scrape first URL for company names
def get_company_names_from_url(url):
    print(f"🕸️ Crawling first URL for companies: {url}")
    soup = None
    try:
        api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}"
        response = requests.get(api_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"⚠️ ScraperAPI failed for {url} with error: {e}. Falling back to TavilyClient.extract...")
        try:
            client = TavilyClient(api_key=TAVILY_API_KEY)
            extract_response = client.extract(urls=[url])
            if extract_response and 'content' in extract_response:
                soup = BeautifulSoup(extract_response['content'], 'html.parser')
            else:
                print(f"❌ TavilyClient.extract returned no content for {url}.")
                return []
        except Exception as tavily_e:
            print(f"❌ Error with TavilyClient.extract fallback for {url}: {tavily_e}")
            return []

    if soup:
        # 🔍 Find all <a> tags with class exactly ["t-accent", "t-heavy"]
        company_tags = soup.find_all('a', class_='t-accent t-heavy')

        # 🧼 Clean the text and filter out anything sus
        companies = [
            tag.text.strip()
            for tag in company_tags
            if tag.text.strip() and "team" not in tag.text.lower()
        ]

        print(f"✅ Found {len(companies)} companies.\n")
        return companies[:15]  # 🎯 Top 15 only, 'cause we fancy
    return []

# 💥 Step 3: Scraping company pitchbook details (same as before)
def extract_company_details(soup):
    details = {}

    quick_facts = soup.select('div[role="list"][aria-label="Quick Facts"] div[data-pp-overview-item]')
    for fact in quick_facts:
        label = fact.select_one('li.dont-break.text-small')
        value = fact.select_one('span.pp-overview-item__title')
        if label and value:
            details[label.text.strip()] = value.text.strip()

    description = soup.select_one('div[data-general-info-description] p.pp-description_text')
    if description:
        details['Description'] = description.text.strip()

    contact_info = soup.select('div.pp-contact-info div.pp-contact-info_item')
    for info in contact_info:
        label = info.select_one('h5, div.font-weight-bold')
        value = info.select_one('a, div.font-weight-normal')
        if label and value:
            details[label.text.strip()] = value.text.strip()

    office = soup.select_one('div.pp-contact-info_corporate-office')
    if office:
        address_lines = office.select('ul.list-type-none li')
        details['Address'] = [line.text.strip() for line in address_lines]

    social_links = soup.select('div.info-item__social a')
    details['Social Media'] = {link.get('aria-label').replace(' link', ''): link.get('href') for link in social_links}

    industries = soup.select('div.pp-contact-info_item div.font-weight-normal')
    details['Industries'] = [industry.text.strip() for industry in industries if 'Industry' in industry.find_previous('div').text]

    verticals = soup.select('div.pp-contact-info_item a.font-underline')
    details['Verticals'] = [vertical.text.strip() for vertical in verticals]

    faqs = soup.select('ul.pp-faqs-table li')
    for faq in faqs:
        question = faq.select_one('h3')
        answer = faq.select_one('p')
        if question and answer:
            details[question.text.strip()] = answer.text.strip()

    return details

# fallback to selenium if cloudscraper fails
def scrape_with_selenium(url):
    print(f"🌐 Scraping with Selenium: {url}")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(10)
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        return extract_company_details(soup)
    finally:
        driver.quit()

def scrape_with_cloudscraper(url, max_retries=3, backoff_factor=5):
    print(f"🌐 Scraping with cloudscraper: {url}")
    for attempt in range(max_retries):
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return extract_company_details(soup)
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                wait = backoff_factor * (2 ** attempt)
                print(f"⚠️ 429 Too Many Requests")
            else:
                print(f"⚠️ Cloudscraper HTTP error: {e}, switching to Selenium...")
                return scrape_with_selenium(url)
        except Exception as e:
            print(f"⚠️ Cloudscraper failed with: {e}, switching to Selenium...")
            return scrape_with_selenium(url)
    print("⚠️ Max retries reached for cloudscraper, switching to Selenium...")
    return scrape_with_selenium(url)

def save_json(data, filename='final_output.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"💾 Saved to {filename}")

# 💥 Full Flow: Run it all
def extract_company_names_from_url(url):
    print(f"🕸️ Crawling via ScraperAPI: {url}")
    soup = None
    try:
        api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}"
        response = requests.get(api_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"⚠️ ScraperAPI failed for {url} with error: {e}. Falling back to TavilyClient.extract...")
        try:
            client = TavilyClient(api_key=TAVILY_API_KEY)
            extract_response = client.extract(urls=[url])
            if extract_response and 'content' in extract_response:
                soup = BeautifulSoup(extract_response['content'], 'html.parser')
            else:
                print(f"❌ TavilyClient.extract returned no content for {url}.")
                return []
        except Exception as tavily_e:
            print(f"❌ Error with TavilyClient.extract fallback for {url}: {tavily_e}")
            return []
    
    if soup:
        # Check for anchor tags with company names (existing selectors)
        company_tags = [
            tag for tag in soup.find_all('a')
            if set(tag.get('class', [])) == set(['txn--font-16', 'txn--text-color-mine-shaft'])
        ]
        companies = [tag.text.strip() for tag in company_tags if tag.text.strip() and "team" not in tag.text.lower()]
        print(f"DEBUG: Initial Companies: {companies}")

        # Additional scraping method to cover other domains (existing)
        additional_tags = [
            tag for tag in soup.find_all('a')
            if set(tag.get('class', [])) == set(['txn--text-color-mine-shaft'])
        ]
        additional_companies = [tag.text.strip() for tag in additional_tags if tag.text.strip() and "team" not in tag.text.lower()]  # Limit to top 10
        print(f"DEBUG: Additional Companies: {additional_companies}")

        # NEW: Also extract from <a class="txn--text-decoration-none txn--text-color-mine-shaft">
        extra_tags = [
            tag for tag in soup.find_all('a')
            if set(tag.get('class', [])) == set(['txn--text-decoration-none', 'txn--text-color-mine-shaft'])
        ]
        extra_companies = [tag.text.strip() for tag in extra_tags if tag.text.strip() and "team" not in tag.text.lower()]
        print(f"DEBUG: Extra Companies: {extra_companies}")

        # Combine all lists and deduplicate
        all_companies = companies + additional_companies + extra_companies
        print(f"DEBUG: All Companies (combined): {all_companies}")
        # Filter only valid company names (excluding social media and email links)
        valid_companies = [company for company in all_companies if not any(platform in company.lower() for platform in ['linkedin', 'twitter', 'facebook', 'email', 'contact', 'team', 'overview','companies','company','about'])]
        print(f"DEBUG: Valid Companies (after filtering): {valid_companies}")
        # Deduplicate while preserving order
        seen = set()
        deduped_companies = []
        for company in valid_companies:
            if company not in seen:
                deduped_companies.append(company)
                seen.add(company)
        # Limit to top 20 results
        deduped_companies = deduped_companies[:20]
        print(f"DEBUG: Deduped Companies (final): {deduped_companies}")
        print(f"✅ Found companies:\n{deduped_companies}")
        return deduped_companies
    return []
    
def scrape_company(company, api_key, cse_id):
    try:
        pitchbook_query = f"{company} pitchbook"
        pitchbook_url = scraperapi_search(pitchbook_query, api_key, cse_id)
        if pitchbook_url:
            details = scrape_with_cloudscraper(pitchbook_url)
            return {
                "company_name": company,
                "searched_url": pitchbook_url,
                "details": details
            }
        else:
            print(f"❌ Skipped {company} (no pitchbook URL)")
            return None
    except Exception as e:
        print(f"❌ Error scraping company {company}: {e}")
        return None

def main(primary_prompt, secondary_prompt, third_prompt, fourth_prompt):
    all_companies = []
    with open("final_output.json", 'w', encoding='utf-8') as f:
        json.dump([], f)
    with open("competitor_analysis_result.json", 'w', encoding='utf-8') as f1:
        json.dump([], f1)
    GOOGLE_API_KEY = "AIzaSyBJ0TM9Rs73RvK2akpesypWZIvgYdc_aQQ"
    GOOGLE_CSE_ID = "0436fecd901594865"
    search_url = scraperapi_search(primary_prompt, GOOGLE_API_KEY, GOOGLE_CSE_ID)
    print(f"DEBUG: Primary Search URL: {search_url}")
    if not search_url:
        print("🛑 Ending - couldn't get primary search result")
        return
    all_companies += get_company_names_from_url(search_url)
    fourth_url = scraperapi_search(fourth_prompt, GOOGLE_API_KEY, GOOGLE_CSE_ID)
    print(f"DEBUG: Fourth Search URL: {fourth_url}")
    if not fourth_url:
        print("🛑 Ending - couldn't get primary search result")
        return
    all_companies += get_company_names_from_url(fourth_url)
    secondary_url = scraperapi_search(secondary_prompt, GOOGLE_API_KEY, GOOGLE_CSE_ID)
    print(f"DEBUG: Secondary Search URL: {secondary_url}")
    if secondary_url:
        all_companies += extract_company_names_from_url(secondary_url)
    else:
        print("⚠️ Couldn't get secondary result. Moving on...")
    third_url = scraperapi_search(third_prompt, GOOGLE_API_KEY, GOOGLE_CSE_ID)
    print(f"DEBUG: Third Search URL: {third_url}")
    if third_url:
        all_companies += extract_company_names_from_url(third_url)
    else:
        print("⚠️ Couldn't get third result. Moving on...")
    print(all_companies)
    # exit()
    all_companies = list(dict.fromkeys(all_companies))
    all_companies = all_companies[:30]
    print(all_companies)  # Limit to 20 for speed
    output_data = []
    # Define API keys and CSE IDs
    api_keys = [
        "AIzaSyB8wQpkh34DyemOFGHUwEjlueoWkeEVS8c",# api1
        "AIzaSyCL-bUJvm3Ogl7PMGju3kD7u7fN-MODyfM", #api2
        "AIzaSyCabKX66OW1m7B8UnnwYwSJd4FGQfaDTwU"  # api3
    ]
    cse_ids = [
        "b3ee74b6f109d4785",  # cse1 for api1
        "42eb1d25454e645a8",  # cse2 for api1
        "a1b28e802924c4f19",# cse1 for api2
        "20fb97ef555d749c7",  # cse2 for api2
        "b47601a1bd9d447a5", # cse1 for api3
        "a103b097949ad4886"  # cse2 for api3
    ]
    api_cse_pairs = [
        (api_keys[0], cse_ids[0]),  # api1 + cse1
        (api_keys[0], cse_ids[1]),  # api1 + cse2
        (api_keys[1], cse_ids[2]),  # api2 + cse1
        (api_keys[1], cse_ids[3]),  # api2 + cse2
        (api_keys[2], cse_ids[4]),  # api3 + cse1
        (api_keys[2], cse_ids[5])   # api3 + cse2
    ]
    # Parallel scrape company details
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for idx, company in enumerate(all_companies):
            api_key, cse_id = api_cse_pairs[idx % 6]
            futures.append(executor.submit(scrape_company, company, api_key, cse_id))
        for future in as_completed(futures):
            result = future.result()
            if result:
                output_data.append(result)
    # Per-company LLM call (sequential, for token safety)
    for i, company_data in enumerate(output_data):
        print(f"🤖 Sending company {i+1}/{len(output_data)} to LLM...")
        asyncio.run(main2([company_data]))
    save_json(output_data)
    final()
    print(f"✅ All companies processed and saved.")


    



