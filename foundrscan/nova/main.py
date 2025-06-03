import json
from pathlib import Path
import os

# Load input JSONs
with open("../agents/output/startup_summary.json", "r") as f:
    startup_json = json.load(f)

# Save to file
output_dir = Path("data")
output_dir.mkdir(exist_ok=True)
output_path = output_dir / "market_insights.json"

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