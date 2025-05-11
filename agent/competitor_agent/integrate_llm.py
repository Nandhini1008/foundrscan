import json
import textwrap
from typing import Dict, List, Any
from together import Together


# Together API Configuration
TOGETHER_API_KEY = "542255a9ab6e90c86b0bace418f9d0185b0f989c539e7cc1387232144757ed71"

# Initialize the Together client
client = Together(api_key=TOGETHER_API_KEY)

def clean_json_to_text(data: Any, title="") -> str:
    """Convert JSON into clean readable format with size limit."""
    text = f"\n📌 {title}:\n"
    
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                text += f"{k}:\n"
                for sk, sv in v.items():
                    text += f" - {sk}: {sv}\n"
            elif isinstance(v, list):
                # Limit list items to first 5
                items = v[:5]
                text += f"{k}: {', '.join(map(str, items))}\n"
                if len(v) > 5:
                    text += f" - ... and {len(v) - 5} more items\n"
            else:
                text += f"{k}: {v}\n"
    elif isinstance(data, list):
        # Limit list items to first 5
        items = data[:5]
        for i, item in enumerate(items):
            text += f"Item {i + 1}:\n"
            if isinstance(item, dict):
                for k, v in item.items():
                    text += f" - {k}: {v}\n"
            else:
                text += f" - {item}\n"
        if len(data) > 5:
            text += f" - ... and {len(data) - 5} more items\n"
    
    return text

def load_json_files() -> tuple[Dict, Dict]:
    try:
        path1 = r"C:\Users\Nandhini Prakash\startup_ai\foundrscan\agents\output\startup_summary.json"
        with open(path1, 'r', encoding='utf-8') as f:
            startup_data = json.load(f)
        return startup_data
    except FileNotFoundError as e:
        print(f"Error loading JSON files: {e}")
        return {}

def prepare_optimized_prompt(startup_data: Dict, competitor_data: Dict) -> List[Dict]:
    """Prepare an optimized prompt that fits within token limits."""
    # Extract essential information with size limits
    startup_info = {
        "name": startup_data.get("name", ""),
        "desc": startup_data.get("description", "")[:100],  # Reduced from 150 to 100
        "web": startup_data.get("website", ""),
        "feat": startup_data.get("features", [])[:2] if startup_data.get("features") else ["Feature 1", "Feature 2"],
        "price": startup_data.get("pricing", "") or "Subscription-based model",
        "fund": startup_data.get("funding", "")
    }
    
    # Process competitors with size limits and sort by funding
    competitors_info = []
    for comp in competitor_data:
        details = comp.get("details", {})
        company_name = comp.get("company_name", "")
        
        # Extract funding information
        funding_key = f"How much funding has {company_name} raised over time?"
        funding_info = details.get(funding_key, "")
        
        # Extract funding amount
        funding_amount = 0
        if funding_info:
            import re
            numbers = re.findall(r'\d+\.?\d*', funding_info)
            if numbers:
                funding_amount = float(numbers[0])
        
        # Extract investors
        investors_key = f"Who are {company_name}'s investors?"
        investors = details.get(investors_key, "")
        if investors:
            # Extract first 3 investors
            investors = [inv.strip() for inv in investors.split(",")[:3]]
        
        # Get features from description
        description = details.get("Description", "")[:100]  # Reduced from 150 to 100
        features = []
        if description:
            # Extract key features from description
            sentences = [s.strip() for s in description.split(".") if s.strip()]
            features = [s for s in sentences[:2] if len(s) > 10]  # Only use meaningful sentences
        if not features:
            features = ["Core Service 1", "Core Service 2"]
        
        # Determine pricing model
        pricing = "Contact for pricing"
        if "subscription" in description.lower() or "monthly" in description.lower():
            pricing = "Subscription-based model"
        elif "free" in description.lower() or "freemium" in description.lower():
            pricing = "Freemium model"
        elif "pay" in description.lower() or "per" in description.lower():
            pricing = "Pay-per-use model"
        
        # Create a compact competitor info structure
        comp_info = {
            "n": company_name,
            "d": description,
            "w": details.get("Website", ""),
            "f": features,
            "p": pricing,
            "fd": funding_info,
            "funding_amount": funding_amount,
            "ad": {
                "type": details.get("Primary Industry", ""),
                "founded": details.get("Founded", ""),
                "employees": details.get("Employees", ""),
                "location": details.get("Address", [""])[0] if isinstance(details.get("Address"), list) else "",
                "investors": investors[:3] if investors else [],
                "status": details.get("Status", ""),
                "deal_type": details.get("Latest Deal Type", ""),
                "deal_amount": details.get("Latest Deal Amount", "")
            }
        }
        competitors_info.append(comp_info)
    
    # Sort competitors by funding amount
    competitors_info.sort(key=lambda x: x["funding_amount"], reverse=True)

    # System message to enforce JSON-only output
    system_message = {
    "role": "system",
    "content": """You are a JSON generator. Your ONLY task is to return a valid JSON object.
        The output MUST be a single, valid JSON object that can be parsed by json.loads().
        The output MUST start with { and end with }.
        The output MUST NOT contain any text, explanations, markdown, or code blocks.
        The output MUST NOT contain any newlines or extra spaces.
        The output MUST be proper JSON format with all strings in double quotes.
        You MUST use the actual company names and data provided in the input.
        You MUST follow the exact JSON structure provided.
        You MUST NOT return any text before or after the JSON object..
        You MUST include a field called 'feature_score' inside each competitor object.
        You MUST calculate 'feature_score' by comparing the startup's key features with each competitor's features.
        The feature_score MUST be between 0 and 10 based on how many startup features are matched by the competitor.
        The score you are providing (score) MUST be based ONLY on this feature_score.
        The higher the overlap of relevant features, the higher the score.
        If a company has only unrelated or random features not in the startup idea, the score MUST be low.
        The score must not be so low for the companies that have atleast one feature to match.
        Companies with feature_score >= 7 MUST be included in the competitors list.
        Companies with feature_score < 7 MUST be excluded entirely.
        The score field MUST match the feature_score value (rounded if needed).
        You MUST include all competitor details only if their feature_score is 7 or more.
        You MUST sort the competitors by funding amount in descending order.
        You MUST include market_analysis and collaboration_opportunities in the final object.
        All fields must contain actual data from the input. No nulls or empty strings.
        You MUST include complete company details including investors and deal information.
        The output MUST be compact and fit within token limits while preserving required structure."""
}

    user_message = {
        "role": "user",
        "content": f"""Return ONLY a valid JSON object with this EXACT structure, using the actual data provided:

    {{
    "competitors": [
        {{
        "name": "company_name",
        "description": "detailed_description",
        "website": "company_website",
        "features": ["feature1", "feature2"],
        "feature_score": 0-10,
        "pricing": "pricing_details",
        "funding": "funding_amount",
        "details": {{
            "type": "company_type",
            "employees": "employee_count",
            "location": "company_location",
            "investors": ["investor1", "investor2", "investor3"],
            "status": "company_status",
            "deal_type": "latest_deal_type",
            "deal_amount": "latest_deal_amount"
        }}
        }}
    ],
    "market_analysis": {{
        "total_market_size": "market_size_value",
        "growth_rate": "growth_rate_value",
        "key_trends": ["trend1", "trend2"]
    }},
    "collaboration_opportunities": ["opportunity1", "opportunity2"]
    }}

    Data to analyze:
    Startup: {json.dumps(startup_info)}
    Competitors: {json.dumps(competitors_info)}

    IMPORTANT:
    1. Return ONLY the JSON object, nothing else
    2. Use the exact structure shown above
    3. Replace all placeholder values with actual data
    4. Ensure all strings are in double quotes
    5. Do not add any comments or explanations 
    6. Do not include any text before or after the JSON object
    7. Do not include any newlines or extra spaces
    8. Do not include any text, explanations, or code blocks
    9. Do not include any additional information or context
    10. Do not include any markdown formatting
    11. The output must be valid JSON that can be parsed by json.loads()
    12. Sort competitors by funding amount in descending order
    13. Do not include any empty strings or null values
    14. All fields must contain actual data from the input
    15. Include complete company details including investors and deal information
    16. Add market analysis information
    17. Include key achievements for top competitors
    18. Keep descriptions and features concise to stay within token limits
    19. Compare the startup features with each competitor’s features
    20. The feature_score is calculated based on how many relevant startup features are matched
    21. Use feature_score as the score field as well
    22. If features don’t align, score must be low and the company excluded
    23. Return the result in a JSON object with all strings in double quotes"""
    }


    return [system_message, user_message]

def is_valid_json(text: str) -> bool:
    """Check if the text is valid JSON."""
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False

def analyze_with_llm(messages: List[Dict], max_retries: int = 3) -> str:
    """Analyze data using Together API with JSON validation and retry logic."""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=messages,
                max_tokens=1000,  # Reduced from 1200 to 1000
                temperature=0.1,
                top_p=0.9
            )
            result = response.choices[0].message.content.strip()
            
            # Clean the result
            result = result.replace("```json", "").replace("```", "").strip()
            result = result.replace("\n", "").replace("  ", " ")
            
            # Ensure proper JSON format
            if not result.startswith("{"):
                result = "{" + result
            if not result.endswith("}"):
                result = result + "}"
            
            # Validate JSON
            if is_valid_json(result):
                # Additional validation for required fields
                data = json.loads(result)
                required_fields = ["competitors", "market_analysis", "collaboration_opportunities"]
                for field in required_fields:
                    if field not in data or not data[field]:
                        raise ValueError(f"Missing or empty required field: {field}")
            
                # Validate data completeness
                for competitor in data["competitors"]:
                    required_competitor_fields = ["name", "description", "website", "features", "pricing", "funding", "details"]
                    for field in required_competitor_fields:
                        if field not in competitor or not competitor[field]:
                            raise ValueError(f"Missing or empty required field in competitor: {field}")
                
                return result
            else:
                print(f"⚠️ Attempt {attempt + 1}: Invalid JSON received, retrying...")
                messages.append({
                    "role": "user",
                    "content": "Your response was not valid JSON. Return ONLY a valid JSON object that matches the exact structure provided, with all strings in double quotes and no additional text."
                })
        except Exception as e:
            print(f"Error in LLM analysis (attempt {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                return ""
    
    return ""

def save_analysis_result(result: str, filename: str = 'competitor_analysis_result.json'):
    try:
        # Clean the result
        result = result.strip()
        if not result.startswith("{"):
            result = "{" + result
        if not result.endswith("}"):
            result = result + "}"
        
        # Validate JSON format
        data = json.loads(result)

        # Ensure all required fields are present and populated
        required_fields = ["competitors", "market_analysis", "collaboration_opportunities"]
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field: {field}")
                return
            if not data[field]:  # Check if field is empty
                print(f"❌ Empty field: {field}")
                return
        print(data)
        s_score = int(data['competitors'][0]['feature_score'])
        if s_score < 4:
            data = {'1'}
        with open(filename, 'a', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Analysis saved to {filename}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON output from the model: {str(e)}")
        print("Raw output:", result)
    except Exception as e:
        print(f"❌ Error saving analysis: {e}")

def main2(company_data):
    print("🚀 Starting competitor analysis...")
    
    # Load the JSON files
    startup_data = load_json_files()
    
    if not startup_data:
        print("❌ Failed to load required JSON files")
        return
    
    # Prepare optimized prompt
    messages = prepare_optimized_prompt(startup_data, company_data)
    
    # Analyze with LLM
    print("🤖 Generating analysis...")
    result = analyze_with_llm(messages)
    
    if result:
        save_analysis_result(result)
    else:
        print("❌ Failed to generate valid JSON analysis")
 # Replace with actual company data to analyze
