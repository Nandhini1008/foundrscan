# 🚀 All-in-One Competitor Analysis Tool for Startups 🔍

import requests
from bs4 import BeautifulSoup
import json
import re
import tiktoken
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
scraped_data1 = []
# API Keys & Configs 🔑
GOOGLE_API_KEY = ""
CSE_ID = ""
LLM_API_URL = ""
HEADERS = {
    "Authorization": "Bearer ",
    "Content-Type": "application/json"
}

# 🔍 Use Google Custom Search to get results from a specific site
def scrape_with_google(query, site, max_results=5):
    results = []
    search_url = ""
    params = {
        "key": GOOGLE_API_KEY,
        "cx": CSE_ID,
        "q": f"site:{site} {query}",
        "num": max_results
    }
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        search_results = response.json().get("items", [])
        for item in search_results:
            results.append({"title": item["title"], "link": item["link"]})
        return results
    except Exception as e:
        print(f"❌ Error during Google Search: {e}")
        return []

# 🧹 Full-on scraper for the URL content
def scrape_data_from_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        page_title = title_tag.get_text().strip() if title_tag else 'No page title found'
        headings = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 20]
        metas = {
            meta.get('name', meta.get('property', f'meta-{i}')): meta.get('content')
            for i, meta in enumerate(soup.find_all('meta'))
            if meta.get('content')
        }
        json_ld_data = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                json_ld_data.append(json.loads(script.string))
            except:
                continue
        return {
            'Page Title': page_title,
            'Headings': headings,
            'Paragraphs': paragraphs[:30],
            'Meta Tags': metas,
            'JSON-LD': json_ld_data,
            'URL': url
        }
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

# 🔢 Count tokens

def count_tokens(text, model_name="gpt-3.5-turbo"):
    try:
        enc = tiktoken.encoding_for_model(model_name)
    except:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

# 🧠 LLM-Based Competitor Analysis
def analyze_competitor_data(user_prompt, competitors_data, json_data1, max_token_limit=8193, max_new_tokens=2048):

    base_prompt = {
        "role": "system",
        "content":  """You're a smart startup analyst and a startup coach helping understand a founder's idea. Your job is to: 
       Understand the user startup idea and analyze the competitors.And provide the blow needed details. 
       Make sure to understand the user startup idea crystal clear. 

Once enough info is gathered, analyze competitor data and organize output into this JSON format:
Make sure to select the top companies from the list of competitiors from each sub domain.
Select top 3 companies from each sub domain and then analyze the data.

Avoid all your extra text, explanations, or markdown. Just understand the data for each company and return the json like this:
Only json format output (no extra not even markdown:)
{
  "direct_competitors": [],
  "indirect_competitors": [],
  "feature_comparison_table": {
    "Your Startup": [],
    "Competitor X": []
  },
  "pricing_comparison": {
    "Your Startup": "",
    "Competitor X": ""
  },
  "differentiation_score": "0-10",
  "potential_collaboration_opportunities": []
}

⚠️ For any missing data, perform a secondary Google search with the company name and fetch info from reliable sources. Ensure each competitor profile is fully completed — no blanks.

❌ Do not include explanations, markdown, or think-aloud reasoning. Just clean JSON output only.

Finally, compare the competitor business models with the user's startup idea and highlight key differences clearly."""
    }
    user_prefix = f"Here's the competitor data for the startup idea '{json_data1}':\n"
    combined_data = json.dumps(competitors_data, indent=2)
    full_user_msg = user_prefix + combined_data
    total_tokens = count_tokens(full_user_msg) + count_tokens(base_prompt["content"]) + max_new_tokens

    if total_tokens > max_token_limit:
        print(f"⚠️ Trimming input: {total_tokens} tokens exceeds {max_token_limit}. Trimming now...")
        trimmed = []
        for entry in competitors_data:
            trial_data = json.dumps(trimmed + [entry], indent=2)
            trial_tokens = count_tokens(user_prefix + trial_data) + count_tokens(base_prompt["content"]) + max_new_tokens
            if trial_tokens >= max_token_limit:
                break
            trimmed.append(entry)
        print(f"✅ Trimmed to {len(trimmed)} competitors.")
        combined_data = json.dumps(trimmed, indent=2)

    data = {
        "model": "meta-llama/Llama-3.3-70B-Instructo-Free",
        "messages": [base_prompt, {"role": "user", "content": user_prefix + combined_data}]
    }
    try:
        res = requests.post(LLM_API_URL, headers=HEADERS, json=data)
        res_data = res.json()
        return res_data.get('choices', [{}])[0].get('message', {}).get('content', "⚠️ No valid analysis returned.")
    except Exception as e:
        print(f"❌ Error with LLM analysis: {e}")
        return "🚫 Something went wrong with the analysis."

# 🧼 Clean and Append JSON Output
def clean_llm_json_output(raw_output):
    match = re.search(r"{", raw_output)
    cleaned = raw_output[match.start():] if match else raw_output
    cleaned = cleaned.replace("“", "\"").replace("”", "\"").r-Turbeplace("‘", "'").replace("’", "'")
    return cleaned

def write_new_summary_to_json(analysis_summary, filename="final_strategy_report.json"):
    try:
        cleaned_summary = clean_llm_json_output(analysis_summary)
        analysis_data = json.loads(cleaned_summary)
        
        # This will overwrite the file every time 🔥
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(analysis_data, file, indent=4, ensure_ascii=False)

        print(f"✅ Created NEW JSON file: {filename} 🆕📁✨")
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode fail: {e}\n🛠️ Raw Output:\n{analysis_summary}")
    
    except Exception as e:
        print(f"❌ File save failed: {e}")


# 🌐 Crawl Inc42 Links
def crawl_inc42_profile_links(domain):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    print("🚀 Launching Inc42 website...")
    driver.get("https://inc42.com/company/?itm_medium=website&itm_source=dl-sidebar&itm_campaign=discover-company&itm_content=company&itm_term=1")
    time.sleep(2)

    try:
        search_input = driver.find_element(By.ID, "global_search")
        search_input.clear()
        search_input.send_keys(domain)
        search_input.send_keys(Keys.RETURN)
        print(f"🔍 Auto-searching for: {domain}")
    except Exception as e:
        print("💥 Search failed:", e)
        driver.quit()
        return []

    time.sleep(2)
    print("🕸 Grabbing profile links...")
    link_elements = driver.find_elements(By.CSS_SELECTOR, "li.headerStyled__UnitedSearchLi-sc-x7q6wh-9 a.links")
    profile_links = []
    for elem in link_elements:
        href = elem.get_attribute("href")
        if href:
            full_link = "https://inc42.com" + href if href.startswith("/company/") else href
            profile_links.append(full_link)
    driver.quit()
    return profile_links

# 🔎 Scrape Inc42 Company Details
def scrape_inc42_company_details(url, retry_limit=2):
    print(f"🔍 Scraping: {url}")
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.page_load_strategy = 'normal'

    retries = 0
    while retries < retry_limit:
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.set_page_load_timeout(30)

            driver.get(url)
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            data = {}
            company_name_div = soup.find('div', class_='companyDetailStyle__HeadingText-sc-1rlp5q9-23')

            # Get the clean text
            company_name = company_name_div.get_text(strip=True) if company_name_div else 'No company name found'
            search_query = f"{company_name} startuptalky"
            url1 = google_search(search_query)
            if url1:
                scraped_data1 = scrape_page1(url1)
            else:
                scraped_data1 = None

            items = soup.find_all('li')
            for item in items:
                heading = item.find('div', class_='about-heading')
                value = item.find('span', class_='info-value') or item.find('span', class_='d-block info-value')
                if heading and value:
                    key = heading.get_text(strip=True)
                    val = value.get_text(strip=True)
                    data[key] = val

            founders_block = soup.find('div', class_='founder-items')
            if founders_block:
                founder_text = founders_block.find('span', class_='info-value')
                more_founders_btn = founders_block.find('button')
                more_founders = more_founders_btn.find('a').get('aria-label') if more_founders_btn and more_founders_btn.find('a') else None
                if more_founders:
                    data['Founders'] = more_founders
                elif founder_text:
                    data['Founders'] = founder_text.get_text(strip=True)

            data['URL'] = url
            if scraped_data1 != None or {} :
                data.update(scraped_data1)

            print("✅ Scraped Company Details")
            
            return data

        except (TimeoutException, WebDriverException) as e:
            retries += 1
            print(f"🔁 Retrying... ({retries}/{retry_limit})")

        finally:
            try:
                driver.quit()
            except:
                pass

    print(f"🚫 Skipping {url} after {retry_limit} retries 😤")
    return None


def google_search(query):
    print(f"🔎 Searching for: {query}")
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={CSE_ID}"
    response = requests.get(url)
    data = response.json()
    
    if 'items' in data and data['items']:
        first_url = data['items'][0]['link']
        return first_url
    else:
        print("❌ No results found.")
        return None

def scrape_page1(url):
    print(f"🕷️ Scraping: {url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # Look for Business Model and Revenue Model sections
    business_model_heading = soup.find('h2', string=lambda text: text and 'Business Model' in text)
    revenue_model_heading = soup.find('h2', string=lambda text: text and 'Revenue Model' in text)

    business_model_content = ""
    revenue_model_content = ""

    # If Business Model section is found, grab the next available content
    if business_model_heading:
        business_model_content = extract_content_after_heading(business_model_heading)

    # If Revenue Model section is found, grab the next available content
    if revenue_model_heading:
        revenue_model_content = extract_content_after_heading(revenue_model_heading)

    # If both are found together, we can grab content accordingly
    if not business_model_content and not revenue_model_content:
        print("⚠️ Both Business and Revenue Model headings are missing, trying to extract based on alternate methods.")
        business_model_content, revenue_model_content = extract_alternate_content(soup)

    return {
        "url": url,
        "business_model": business_model_content,
        "revenue_model": revenue_model_content
    }

def extract_content_after_heading(heading):
    # Extract content following the heading, check for both text and lists
    content = ""
    next_sibling = heading.find_next_sibling()
    
    while next_sibling and next_sibling.name not in ['h2', 'h3']:  # Stop when next heading is found
        if next_sibling.name == 'p':
            content += next_sibling.get_text() + "\n"
        elif next_sibling.name in ['ul', 'ol']:  # If it's a list, extract the list items
            list_items = next_sibling.find_all('li')
            for item in list_items:
                content += item.get_text() + "\n"
        next_sibling = next_sibling.find_next_sibling()
    
    return content.strip() if content else "No content found"

def extract_alternate_content(soup):
    # A fallback method for extracting content when headings aren't found (e.g., the content is together).
    content = soup.get_text(separator=" ").lower()
    
    # Try to find business model and revenue model context
    if 'business model' in content and 'revenue model' in content:
        start = content.find('business model')
        end = content.find('revenue model')
        if start != -1 and end != -1:
            return content[start:end], content[end:]
    return "No content found", "No content found"

def guess_domain_with_llama3(json_data):
    prompt = f"""
You're an expert in categorizing startup and tech data into specific domains.

Given this JSON data, identify the **most relevant subdomain** it fits into.
Make sure that subdomain is a **specific** and **narrow** category.
That means it should also be in a single word and represent the core of the startup.
So that it is very easy to search for the best outcomes.
JSON:
{json_data}
"""
    payload = {
        "model":"meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": "You are a domain classification assistant."},
            {"role": "user", "content": prompt}
        ],
    }

    res = requests.post(LLM_API_URL, headers=HEADERS, json=payload)
    res.raise_for_status()
    return res.json()['choices'][0]['message']['content'].strip()


def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return json.dumps(data, indent=2)

domain_to_search = ""

# 🚀 MAIN
if __name__ == "__main__":
    file_path = "output/startup_summary.json"  # Change this to your file path
    if not os.path.exists(file_path):
        print("Bruhhh 🫠 File not found!")
    else:
        file_data = read_json_file(file_path)
        domain_to_search = guess_domain_with_llama3(file_data)
        print(f"📂 File: {file_path}")
        print(f"🔍 Detected Domain: {domain_to_search}")
    links = crawl_inc42_profile_links(domain_to_search)
    scraped_data = []
    for link in links:
        print(f"🚀 Scraping details from: {link}")
        details = scrape_inc42_company_details(link)
        if details:
            scraped_data.append(details)
    print("🧠 Sending collected data to LLM for analysis...")
    file_data1 = read_json_file(file_path)
    summary = analyze_competitor_data(domain_to_search, scraped_data, file_data1)
    write_new_summary_to_json(summary)
    print("🎯 Done! All set boss 🔥")
