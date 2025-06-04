import json
from insight_gen import build_market_insight_chain
from prompt_templates import prompt, parser
from dataclasses import asdict

# Load input JSONs
with open("foundrscan/agents/nova_agent/data/startup_input.json", "r") as f:
    startup_json = json.load(f)

with open("foundrscan/agents/nova_agent/data/scraped_text.json", "r") as f:
    scraped_text = f.read()

# Run the chain
chain = build_market_insight_chain()
result = chain.invoke({
    "startup_json": json.dumps(startup_json, indent=2),  # stringified JSON
    "scraped_text": scraped_text,
    "format_instructions": parser.get_format_instructions()
})

# Print to console
print("\n📊 Market Insights:")
print(result)

# Save to file
output_path = "foundrscan/agents/nova_agent/data/market_insights.json"
with open(output_path, "w") as outfile:
    # Check if result contains a Pydantic model under 'text' key
    if isinstance(result, dict) and 'text' in result and hasattr(result['text'], 'model_dump'):
        # Pydantic v2
        result_dict = result['text'].model_dump()
    elif isinstance(result, dict) and 'text' in result and hasattr(result['text'], 'dict'):
        # Pydantic v1
        result_dict = result['text'].dict()
    elif hasattr(result, 'model_dump'):
        # Direct Pydantic v2 object
        result_dict = result.model_dump()
    elif hasattr(result, 'dict'):
        # Direct Pydantic v1 object
        result_dict = result.dict()
    else:
        # Try using asdict if it's a dataclass
        try:
            result_dict = asdict(result)
        except (TypeError, AttributeError):
            # Last resort - might still fail if contains non-serializable objects
            result_dict = result
        
    json.dump(result_dict, outfile, indent=2)

print(f"\n✅ Insights saved to {output_path}")