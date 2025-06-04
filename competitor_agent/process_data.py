import json


def final():
    # Read the competitor analysis result file
    with open('competitor_analysis_result.json', 'r') as f:
        competitor_analysis = json.load(f)  

    # Read the final output file
    with open('final_output.json', 'r') as f:
        final_output = json.load(f)

    # Create a dictionary to store the combined results
    combined_results = []

    # Create a dictionary mapping company names to their valuation scores
    valuation_scores = {comp['name']: comp.get('valuation_score', 0) for comp in competitor_analysis['competitors']}

    # Match and combine data
    for company in final_output:
        if company['company_name'] in valuation_scores:
            # Add valuation score to the company details
            company['valuation_score'] = valuation_scores[company['company_name']]
            combined_results.append(company)

    # Sort the results by valuation score in descending order
    combined_results.sort(key=lambda x: x.get('valuation_score', 0), reverse=True)

    # Write the combined results to a new file
    with open('competitor_agent/final_result.json', 'w') as f:
        json.dump(combined_results, f, indent=2) 