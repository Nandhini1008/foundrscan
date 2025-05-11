import os 
import json
import requests
from scraping_domain import main 
LLM_API_URL = "https://api.together.xyz/v1/chat/completions"
HEADERS = {
    "Authorization": "Bearer ",
    "Content-Type": "application/json"
}
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
    file_path = r"C:\Users\Nandhini Prakash\startup_ai\foundrscan\agents\output\startup_summary.json"
    if not os.path.exists(file_path):
        print("Bruhhh 🫠 File not found!")
        exit()
    else:
        file_data = read_json_file(file_path)
        domain_to_search = guess_domain_with_llama3(file_data)

        print(f"📂 File: {file_path}")
        print(f"🔍 Detected Domain: {domain_to_search}")

        # 🧠 Form queries using that domain
        prompt1 = f"{domain_to_search} startups f6s india"
        prompt2 = f"top {domain_to_search} companies tracxn india"

        main(prompt1, prompt2)  # 👉 Launch the scrape with juicy domain prompts