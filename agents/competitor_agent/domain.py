import os 
import json
import requests
from scraping_domain import main 

LLM_API_URL = "https://api.together.xyz/v1/chat/completions"
HEADERS = {
    "Authorization": "Bearer 542255a9ab6e90c86b0bace418f9d0185b0f989c539e7cc1387232144757ed71",
    "Content-Type": "application/json"
}

def guess_domain_with_llama3(json_data):
    prompt = f"""
You are an expert in analyzing startup and tech data. Your task is to:

1. Carefully read the provided JSON data about a startup.
2. Return the following information in JSON format:
   - major_domain: The main domain/industry this startup operates in (one word, e.g., "AI", "Fintech","Telemedicine").
   - domain_search: The most specific subdomain or focus area (one word, e.g., "Diabetes").
   - best_title: The most specific, unique, and apt title for this startup idea, based on the data. This should be a concise, creative, and accurate name that captures the essence of the startup. Avoid generic names; be as specific as possible.(For example : "Diabeteic Teleconsultation")

JSON data to analyze:
{json_data}

Please provide your response in JSON format like this:
{{
    "major_domain": "",
    "domain_search": "",
    "best_title": ""
}}
"""
    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": "You are a domain classification and naming assistant. Always respond in JSON format with major_domain, domain_search, and best_title fields."},
            {"role": "user", "content": prompt}
        ],
    }

    try:
        res = requests.post(LLM_API_URL, headers=HEADERS, json=payload)
        res.raise_for_status()
        response = res.json()['choices'][0]['message']['content'].strip()
        
        # Parse the JSON response
        try:
            result = json.loads(response)
            if not all(key in result for key in ['major_domain', 'domain_search', 'best_title']):
                raise ValueError("Response missing required fields")
            return result
        except json.JSONDecodeError:
            # If parsing fails, fall back to old behavior
            return {"major_domain": response, "domain_search": response, "best_title": response}
    except Exception as e:
        print(f"Error in domain classification: {str(e)}")
        return {"major_domain": "Unknown", "domain_search": "Unknown", "best_title": "Unknown"}

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return json.dumps(data, indent=2)

def get_domain_name_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data.get('title', 'Unknown')

domain_to_search = ""



# 🚀 MAIN
if __name__ == "__main__":
    file_path = r"C:/Users/niran/Desktop/foundrscan/agents/output/startup_summary.json"
    if not os.path.exists(file_path):
        print("Bruhhh 🫠 File not found!")
        exit()
    else:
        # Print the domain name from the 'title' key
        domain_name = get_domain_name_from_json(file_path)
        print(f"🌐 Domain Name (from title): {domain_name}")
        
        file_data = read_json_file(file_path)
        domain_info = guess_domain_with_llama3(file_data)
        major_domain = domain_info.get('major_domain', 'Unknown')
        domain_search = domain_info.get('domain_search', major_domain) # Use major_domain as fallback
        best_title = domain_info.get('best_title', domain_name)

        print(f"📂 File: {file_path}")
        print(f"🔍 Detected Major Domain: {major_domain}")
        print(f"🔍 Detected Search Domain: {domain_search}")
        print(f"🏷️  Most Specific Title: {best_title}")

        # 🧠 Form queries using that domain and best title
        prompt1 = f"{domain_search} startups f6s india"
        prompt2 = f"top {major_domain} companies tracxn india"

        main(prompt1, prompt2)  # 👉 Launch the scrape with juicy domain promptsS