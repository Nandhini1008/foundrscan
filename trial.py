from together import Together
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize Together client
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))  # Add this key to your .env

# Unified query function using Together's LLaMA 3
def query_model(prompt, conversation_history=""):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    if conversation_history:
        # Split history into lines and alternate between user/assistant roles
        lines = conversation_history.strip().split("\n")
        for line in lines:
            if line.startswith("User:"):
                messages.append({"role": "user", "content": line.replace("User:", "").strip()})
            elif line.startswith("Assistant:") or line.startswith("System:"):
                messages.append({"role": "assistant", "content": line.replace("Assistant:", "").replace("System:", "").strip()})

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        messages=messages,
        max_tokens=1024,
        temperature=0.7,  # you can modify this
    )

    return response.choices[0].message.content.strip()


# Contextual chat loop
def interactive_idea_extractor():
    print("🧠 Tell me your startup idea (ex: AI for diabetes care):")
    user_idea = input("> ").strip()
    
    system_prompt = """
You're a smart startup assistant helping understand a founder's idea.
Your job is to:
1. Understand their startup idea.
2. Ask follow-up questions across these categories (if relevant):
   - Technical Details
   - Business Viability
   - Team
   - Traction & Timeline
   - Challenges & Risks
   - Long-term Vision
Only ask one question at a time. Be curious but friendly.
When you think you have all the information, say: '✅ I'm ready to summarize your startup now.'
"""
    
    # Initialize conversation history
    conversation = f"System: {system_prompt}\nUser: My startup idea: {user_idea}\n"
    
    # First response from AI
    response = query_model(f"You are a helpful assistant. Respond to this startup idea: {user_idea}")
    print(f"\n🤖 {response}")
    conversation += f"Assistant: {response}\n"
    
    # Chat loop
    while True:
        if "✅ I'm ready to summarize" in response:
            break
            
        user_reply = input("💬 You: ").strip()
        conversation += f"User: {user_reply}\n"
        
        response = query_model(f"Continue this conversation about a startup idea. Remember to ask good questions and eventually say you're ready to summarize when you have enough information.", conversation)
        print(f"\n🤖 {response}")
        conversation += f"Assistant: {response}\n"
    
    return user_idea, conversation

# Generate a proper summary from conversation
def summarize_startup(user_idea, conversation):
    summary_prompt = f"""

You are IdeaGPT, an AI startup idea analyzer.

User's Idea: {user_idea}

Your task is to:
1. Understand the idea (even if it's short or unclear).
2. Ask smart, context-aware follow-up questions to fill in gaps.
3. Only when you have enough info, summarize the idea clearly and output it in this JSON format:

{{
  "title": "One-line Title",
  "description": "A clear explanation of the startup idea",
  "target_users": [],
  "problem": "",
  "solution": "",
  "tech_stack": [],
  "business_model": "",
  "monetization": "",
  "competition": "",
  "differentiator": "",
  "risks": [],
  "vision": ""
}}

If the input is too vague, ask your first clarifying question: "Can you tell me more about what the startup does, who it helps, and how it works?"
"""

    
    response = query_model(summary_prompt )

    # Try to extract just the JSON part if there's extra text
    if "```json" in response:
        json_part = response.split("```json")[1].split("```")[0].strip()

    elif "```" in response:
        json_part = response.split("```")[1].split("```")[0].strip()
        return json_part
    else:
        return response

# Main run
if __name__ == "__main__":
    idea, conversation = interactive_idea_extractor()
    print("\n📦 Generating your startup summary...\n")
    summary = summarize_startup(idea, conversation)
    print(summary)





    from together import Together
import os
import re
from dotenv import load_dotenv
load_dotenv()

# Initialize Together client
client = Together()  # Remove API key as it's not needed in new format

# Unified query function using Together's LLaMA 3
def query_model(prompt, conversation_history=""):
    system_content = """You're a smart startup assistant helping understand a founder's idea. Your job is to: 1. Understand their startup idea. 2. Ask follow-up questions across these categories (if relevant): - Technical Details - Business Viability - Team - Traction & Timeline - Challenges & Risks - Long-term Vision Only ask one question at a time. Be curious but friendly. Do not provide reasons or explanations for your questions. When you think you have all the information, say: '✅ I'm ready to summarize your startup now.'
Your task is to:
1. Understand the idea (even if it's short or unclear).
2. Ask smart, context-aware follow-up questions to fill in gaps.
3. Only when you have enough info, summarize the idea clearly and output it in this JSON format:

{
  "title": "One-line Title",
  "description": "A clear explanation of the startup idea",
  "target_users": [],
  "problem": "",
  "solution": "",
  "tech_stack": [],
  "business_model": "",
  "monetization": "",
  "competition": "",
  "differentiator": "",
  "risks": [],
  "vision": ""
}

If the input is too vague, ask your first clarifying question: "Can you tell me more about what the startup does, who it helps, and how it works?"
"""
    
    messages = [{"role": "system", "content": system_content}]

    if conversation_history:
        # Split history into lines and alternate between user/assistant roles
        lines = conversation_history.strip().split("\n")
        for line in lines:
            if line.startswith("User:"):
                messages.append({"role": "user", "content": line.replace("User:", "").strip()})
            elif line.startswith("Assistant:") or line.startswith("System:"):
                messages.append({"role": "assistant", "content": line.replace("Assistant:", "").replace("System:", "").strip()})

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=messages
    )

    response_text = response.choices[0].message.content.strip()
    return response_text


# Contextual chat loop
def interactive_idea_extractor():
    print("🧠 Tell me your startup idea (ex: AI for diabetes care):")
    user_idea = input("> ").strip()
    
    system_prompt = """
You're a smart startup assistant helping understand a founder's idea.
Your job is to:
1. Understand their startup idea.
2. Ask follow-up questions across these categories (if relevant):
   - Technical Details
   - Business Viability
   - Team
   - Traction & Timeline
   - Challenges & Risks
   - Long-term Vision
Only ask one question at a time. Be curious but friendly.
When you think you have all the information, say: '✅ I'm ready to summarize your startup now.'
"""
    
    # Initialize conversation history
    conversation = f"System: {system_prompt}\nUser: My startup idea: {user_idea}\n"
    
    # First response from AI
    response = query_model(f"You are a helpful assistant. Respond to this startup idea: {user_idea}")
    print(f"\n🤖 {response}")
    conversation += f"Assistant: {response}\n"
    
    # Chat loop
    while True:
        if "✅ I'm ready to summarize" in response:
            break
            
        user_reply = input("💬 You: ").strip()
        conversation += f"User: {user_reply}\n"
        
        response = query_model(f"Continue this conversation about a startup idea. Remember to ask good questions and eventually say you're ready to summarize when you have enough information.", conversation)
        print(f"\n🤖 {response}")
        conversation += f"Assistant: {response}\n"
    
    return user_idea, conversation

# Generate a proper summary from conversation
def summarize_startup(user_idea, conversation):
    summary_prompt = f"""
You are IdeaGPT, an AI startup idea analyzer.

User's Idea: {user_idea}

Your task is to:
1. Understand the idea (even if it's short or unclear).
2. Ask smart, context-aware follow-up questions to fill in gaps.
3. Only when you have enough info, summarize the idea clearly and output it in this JSON format:

{{
  "title": "One-line Title",
  "description": "A clear explanation of the startup idea",
  "target_users": [],
  "problem": "",
  "solution": "",
  "tech_stack": [],
  "business_model": "",
  "monetization": "",
  "competition": "",
  "differentiator": "",
  "risks": [],
  "vision": ""
}}

If the input is too vague, ask your first clarifying question: "Can you tell me more about what the startup does, who it helps, and how it works?"
"""

    response = query_model(summary_prompt)

    # Try to extract just the JSON part if there's extra text
    if "```json" in response:
        json_part = response.split("```json")[1].split("```")[0].strip()
        return json_part
    elif "```" in response:
        json_part = response.split("```")[1].split("```")[0].strip()
        return json_part
    else:
        return response

# Main run
if __name__ == "__main__":
    idea, conversation = interactive_idea_extractor()
    print("\n📦 Generating your startup summary...\n")
    summary = summarize_startup(idea, conversation)
    print(summary)