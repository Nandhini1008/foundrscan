import json
from functools import lru_cache
import concurrent.futures
from typing import List, Dict

def load_json_objects(filename: str) -> List[dict]:
    """Load a file containing concatenated JSON objects and return a list of dicts."""
    objects = []
    with open(filename, 'r') as f:
        buffer = ''
        for line in f:
            buffer += line.strip()
            # Try to decode a JSON object from the buffer
            try:
                while buffer:
                    obj, idx = json.JSONDecoder().raw_decode(buffer)
                    objects.append(obj)
                    buffer = buffer[idx:].lstrip()
            except json.JSONDecodeError:
                continue  # Need more lines to complete the object
    return objects

def process_competitor(company: dict, valuation_scores: dict) -> dict:
    """Process a single competitor's data."""
    if company['company_name'] in valuation_scores:
        company['valuation_score'] = valuation_scores[company['company_name']]
        return company
    return None

def final():
    """Process and combine competitor analysis results efficiently."""
    # Load and flatten all competitors from concatenated JSON objects
    competitor_analysis_objs = load_json_objects('competitor_analysis_result.json')
    all_competitors = []
    for obj in competitor_analysis_objs:
        if 'competitors' in obj:
            all_competitors.extend(obj['competitors'])

    # Create valuation scores mapping (use 0 if not present)
    valuation_scores = {
        comp['name']: comp.get('valuation_score', 0)
        for comp in all_competitors
    }

    # Load final_output.json (standard array)
    with open('final_output.json', 'r') as f:
        final_output = json.load(f)
    print("phase 1")
    # Process competitors in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_competitor, company, valuation_scores)
            for company in final_output
        ]
        combined_results = [
            future.result() for future in concurrent.futures.as_completed(futures)
            if future.result() is not None
        ]

    # Sort results by valuation score
    combined_results.sort(key=lambda x: float(x.get('valuation_score', 0) or 0), reverse=True)

    # Filter companies with feature_score > 1
    filtered_results = [company for company in combined_results if float(company.get('feature_score', 0) or 0) > 1]

    # Sort results by feature_score in descending order
    filtered_results.sort(key=lambda x: float(x.get('feature_score', 0) or 0), reverse=True)

    # Write results
    if not filtered_results:
        quote = {
            "message": "No competitors found! Remember: 'The only competition you have is with yourself. Keep innovating and having fun!'"
        }
        with open('final_result.json', 'w') as f:
            json.dump(quote, f, indent=2)
    else:
        with open('final_result.json', 'w') as f:
            json.dump(filtered_results, f, indent=2)
    copy_matching_companies()

def is_details_nonempty(details):
    if not isinstance(details, dict):
        return False
    # Exclude if only Social Media, Industries, Verticals are present and all are empty
    allowed_empty_keys = {"Social Media", "Industries", "Verticals"}
    nonempty_found = False
    for k, v in details.items():
        if k in allowed_empty_keys:
            # Check if these are empty
            if isinstance(v, dict) and v:
                nonempty_found = True
            elif isinstance(v, list) and v:
                nonempty_found = True
            elif isinstance(v, str) and v.strip():
                nonempty_found = True
            elif v not in (None, '', [], {}):
                nonempty_found = True
        else:
            # For any other key, if non-empty, return True
            if isinstance(v, dict) and v:
                return True
            if isinstance(v, list) and v:
                return True
            if isinstance(v, str) and v.strip():
                return True
            if v not in (None, '', [], {}):
                return True
    # If only allowed_empty_keys are present and all are empty, return False
    if not nonempty_found:
        return False
    return True

def copy_matching_companies():
    """Copy details of companies from final_output.json to final_result.json if their company_name matches any competitor name in competitor_analysis_result.json with feature_score > 0, and only if details are not all empty."""
    # Load competitor names with feature_score > 0
    competitor_analysis_objs = load_json_objects('competitor_analysis_result.json')
    competitor_names = set()
    for obj in competitor_analysis_objs:
        if 'competitors' in obj:
            for comp in obj['competitors']:
                try:
                    if float(comp.get('feature_score', 0) or 0) > 0:
                        competitor_names.add(comp['name'])
                except Exception:
                    continue

    # Load all companies
    with open('final_output.json', 'r') as f:
        all_companies = json.load(f)

    # Filter companies whose company_name matches any competitor name and details are not all empty
    matching_companies = [
        company for company in all_companies
        if company.get('company_name') in competitor_names and is_details_nonempty(company.get('details', {}))
    ]

    # Write the matching companies to final_result.json
    with open('final_result.json', 'w') as f:
        json.dump(matching_companies, f, indent=2) 
