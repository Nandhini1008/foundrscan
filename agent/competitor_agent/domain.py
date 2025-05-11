import os 
import json
import requests
from scraping_domain import main 
import string
LLM_API_URL = "https://api.together.xyz/v1/chat/completions"
HEADERS = {
    "Authorization": "Bearer 542255a9ab6e90c86b0bace418f9d0185b0f989c539e7cc1387232144757ed71",
    "Content-Type": "application/json"
}
def guess_domain_with_llama3(json_data):
    prompt = f"""
You're an expert in categorizing startup and tech data into specific domains.

Given this JSON data, identify the **most relevant subdomain** it fits into.
Make sure that subdomain is a **specific** and **narrow** category.
Identify the **subdomain** most relevent **synonym** as well for the startup that is not dependend on the most relevent subdomain. Make sure that subdomain is a **specific** and **narrow** category also be in a single word and represent the core idea of the startup.
That means it should also be in a single word and represent the core of the startup.
So that it is very easy to search for the best outcomes.

Just give your answer like this:
Specific Domain: <your_answer> Eg: Diabetes
Broad Domain: <your_answer> Eg: Telemedicine


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
    text_response = res.json()['choices'][0]['message']['content'].strip()
    specific, broad = None, None
    for line in text_response.split('\n'):
        if "Specific Domain" in line:
            specific = line.split(":")[1].strip()
        elif "Broad Domain" in line:
            broad = line.split(":")[1].strip()

    if not specific or not broad:
        raise ValueError("Bruhh 🤦‍♀️ Couldn't extract both domains from LLM response.")

    return specific.lower().translate(str.maketrans('', '', string.punctuation)), \
           broad.lower().translate(str.maketrans('', '', string.punctuation))


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
        domain_to_search, major_domain = guess_domain_with_llama3(file_data)

        print(f"📂 File: {file_path}")
        print(f"🔍 Detected Domain: {domain_to_search}")
        print(f"🔍 Major Domain: {major_domain}")


        # 🧠 Form queries using that domain
        prompt1 = f"{domain_to_search} companies f6s in india only"
        prompt2 = f"top {major_domain} companies tracxn in india"

        main(prompt1, prompt2)  # 👉 Launch the scrape with juicy domain prompts