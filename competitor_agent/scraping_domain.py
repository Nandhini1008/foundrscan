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
from integrate_llm import main2

SCRAPERAPI_KEY = ""
GOOGLE_API_KEY = ""
GOOGLE_CSE_ID = ""

output_data = []

# 💥 Step 1: Google Search with ScraperAPI
def scraperapi_search(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
    proxies = {"http": f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001"}
    print(f"🔍 Searching via Google: {query}")
    response = requests.get(search_url, proxies=proxies)
    response.raise_for_status()
    results = response.json()
    if 'items' in results and len(results['items']) > 0:
        link = results['items'][0]['link']
        print(f"🔗 Got link: {link}")
        return link
    print("❌ No results found")
    return None

# 💥 Step 2: Scrape first URL for company names
def get_company_names_from_url(url):
    print(f"🕸️ Crawling first URL for companies: {url}")
    api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}"
    response = requests.get(api_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    company_tags = soup.select('a.t-accent.t-heavy')
    companies = [tag.text.strip() for tag in company_tags]
    # Slice to get only top 10 companies
    companies = companies[:10]
    print(f"✅ Found {len(companies)} companies.\n")
    return companies

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
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        return extract_company_details(soup)
    finally:
        driver.quit()

def scrape_with_cloudscraper(url):
    print(f"🌐 Scraping with cloudscraper: {url}")
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return extract_company_details(soup)
    except Exception as e:
        print(f"⚠️ Cloudscraper failed with: {e}, switching to Selenium...")
        return scrape_with_selenium(url)

def save_json(data, filename='final_output.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"💾 Saved to {filename}")

# 💥 Full Flow: Run it all
def extract_company_names_from_url(url):
    print(f"🕸️ Crawling second URL for extra companies via Cloudscraper: {url}")
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        company_tags = soup.find_all('a', class_="txn--text-decoration-none txn--text-color-mine-shaft")
        companies = [tag.text.strip() for tag in company_tags if tag.text.strip()]
        companies = companies[:10]
        print(f"✨ Found {len(companies)} bonus companies.\n")
        return companies
    except Exception as e:
        print(f"❌ Cloudscraper failed on second URL: {e}")
        return []


def extract_company_names_from_url(url):
    print(f"🕸️ Crawling via Cloudscraper: {url}")
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for anchor tags with company names
        company_tags = soup.find_all('a', class_="txn--font-16 txn--text-color-mine-shaft")
        companies = [tag.text.strip() for tag in company_tags if tag.text.strip() and "team" not in tag.text.lower()]

        # Additional scraping method to cover other domains
        additional_tags = soup.find_all('a', class_="txn--text-color-mine-shaft")
        additional_companies = [tag.text.strip() for tag in additional_tags if tag.text.strip() and "team" not in tag.text.lower()]
        additional_companies = additional_companies[:10]  # Limit to top 10

        # Combine both lists
        companies.extend(additional_companies)
        print(len(companies), "companies found")
        
        # Filter only valid company names (excluding social media and email links)
        valid_companies = [company for company in companies if not any(platform in company.lower() for platform in ['linkedin', 'twitter', 'facebook', 'email', 'contact', 'team', 'overview'])]

        # Limit to top 10 results
        print(f"✅ Found companies:\n{valid_companies}")
        return valid_companies
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return []
    
def main(primary_prompt, secondary_prompt):
    global output_data
    all_companies = []

    # 🔍 Step 1: Google Search + ScraperAPI crawl
    search_url = scraperapi_search(primary_prompt)
    if not search_url:
        print("🛑 Ending - couldn't get primary search result")
        return
    all_companies += get_company_names_from_url(search_url)

    # ✨ Step 2: Google Search + Cloudscraper crawl
    secondary_url = scraperapi_search(secondary_prompt)
    if secondary_url:
        all_companies += extract_company_names_from_url(secondary_url)
    else:
        print("⚠️ Couldn't get secondary result. Moving on...")

    # 🎯 Cleanup: remove duplicates + limit to 10
    all_companies = list(dict.fromkeys(all_companies))

    # 🔎 Go deep with pitchbook scraping
    for company in all_companies:
        print(f"\n🚀 Working on company: {company}")
        pitchbook_query = f"{company} pitchbook"
        pitchbook_url = scraperapi_search(pitchbook_query)

        if pitchbook_url:
            details = scrape_with_cloudscraper(pitchbook_url)
            output_data.append({
                "company_name": company,
                "searched_url": pitchbook_url,
                "details": details
            })
            print(f"✅ Scraped {company}")
        else:
            print(f"❌ Skipped {company} (no pitchbook URL)")

        cooldown = random.uniform(8, 15)
        print(f"🧊 Cooling down for {round(cooldown, 2)}s...")
        time.sleep(cooldown)

    save_json(output_data)

    main2()



