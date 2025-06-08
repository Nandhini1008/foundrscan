from langchain_together import Together
from langchain.chains import LLMChain
from prompt_templates import prompt, parser

import os
from dotenv import load_dotenv

load_dotenv()

def build_market_insight_chain():

    from langchain.output_parsers import ResponseSchema
    from langchain.output_parsers import StructuredOutputParser



    response_schemas = [
        ResponseSchema(name="industry", description="Industry category with NACE code if possible"),
        ResponseSchema(name="market_trend", description="Market trend with stats, e.g., CAGR"),
        ResponseSchema(name="TAM_SAM_SOM", description="Dict with TAM, SAM, SOM values in USD"),
        ResponseSchema(name="customer_segments", description="List of customer segments with details"),
        ResponseSchema(name="pricing_opportunity", description="Pricing models and strategies"),
        ResponseSchema(name="market_opportunities", description="List of market opportunities"),
        ResponseSchema(name="market_risks", description="List of market risks with examples"),
        ResponseSchema(name="recent_investments", description="List of recent investments with details")
    ]

    structured_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = structured_parser.get_format_instructions()


    llm = Together(
        model="meta-llama/Llama-Vision-Free",
        temperature=0.2,
        max_tokens=4000,
        api_key = os.getenv("TOGETHER_API_KEY")  
    )

    chain = prompt | llm | parser
    return chain
