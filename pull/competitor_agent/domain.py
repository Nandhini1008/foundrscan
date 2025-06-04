import os 
import json
import requests
from scraping_domain import main 

LLM_API_URL = ""
HEADERS = {
    "Authorization": "Bearer ",
    "Content-Type": "application/json"
}

def guess_domain_with_llama3(json_data):
    prompt = f"""
You are an expert in categorizing startup and tech data into specific domains.

Given this JSON data, please analyze and provide two key pieces of information:

1. major_domain: Identify the main domain/industry that this startup primarily operates in.
   - This should be a broad category that represents the core business
   - Example: "AI", "Telemedicine", "Fintech", "E-commerce", etc.

2. domain_search: Identify the most discussed or specific subdomain/topic within the startup.
   - This should be more specific and represent the main focus area
   - If it's difficult to identify a specific subdomain, use the major_domain as domain_search
   -It should be a single word that captures the essence of the startup's focus
   - Example: If major_domain is "Telemedicine", domain_search could be "Diabetes" or "AI Diagnostics"

JSON data to analyze:
{json_data}

Please provide your response in JSON format like this:
{{
    "major_domain": "",
    "domain_search": ""
}}
"""
    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": "You are a domain classification assistant. Always respond in JSON format with major_domain and domain_search fields."},
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
            if not all(key in result for key in ['major_domain', 'domain_search']):
                raise ValueError("Response missing required fields")
            return result
        except json.JSONDecodeError:
            # If parsing fails, fall back to old behavior
            return {"major_domain": response, "domain_search": response}
    except Exception as e:
        print(f"Error in domain classification: {str(e)}")
        return {"major_domain": "Unknown", "domain_search": "Unknown"}

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return json.dumps(data, indent=2)

domain_to_search = ""



# 🚀 MAIN
if __name__ == "__main__":
    file_path = r""
    if not os.path.exists(file_path):
        print("Bruhhh 🫠 File not found!")
        exit()
    else:
        file_data = read_json_file(file_path)
        domain_info = guess_domain_with_llama3(file_data)
        major_domain = domain_info.get('major_domain', 'Unknown')
        domain_search = domain_info.get('domain_search', major_domain)  # Use major_domain as fallback

        print(f"📂 File: {file_path}")
        print(f"🔍 Detected Major Domain: {major_domain}")
        print(f"🔍 Detected Search Domain: {domain_search}")

        # 🧠 Form queries using that domain
        prompt1 = f"{domain_search} startups f6s india"
        prompt2 = f"top {major_domain} companies tracxn india"

        main(prompt1, prompt2)  # 👉 Launch the scrape with juicy domain prompts