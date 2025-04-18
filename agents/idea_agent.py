

from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import json
import logging
from pathlib import Path
import os
from together import Together
from dotenv import load_dotenv
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class StartupSummary:
    """Data class to store structured startup information"""
    title: str
    description: str
    target_users: List[str]
    problem: str
    solution: str
    tech_stack: List[str]
    business_model: str
    monetization: str
    competition: str
    differentiator: str
    risks: List[str]
    vision: str

    def to_dict(self) -> Dict:
        """Convert the summary to a dictionary"""
        return {
            "title": self.title,
            "description": self.description,
            "target_users": self.target_users,
            "problem": self.problem,
            "solution": self.solution,
            "tech_stack": self.tech_stack,
            "business_model": self.business_model,
            "monetization": self.monetization,
            "competition": self.competition,
            "differentiator": self.differentiator,
            "risks": self.risks,
            "vision": self.vision
        }

    def to_json(self) -> str:
        """Convert the summary to a JSON string"""
        return json.dumps(self.to_dict(), indent=2)

class StartupIdeaAnalyzer:
    """Main class for analyzing startup ideas using AI"""

    def __init__(self):
        """Initialize the analyzer with Together AI client"""
        try:
            self.client = Together()
            logger.info("Successfully initialized Together AI client")
        except Exception as e:
            logger.error(f"Failed to initialize Together AI client: {str(e)}")
            raise

    @staticmethod
    def _get_system_prompt() -> str:
        """Get the system prompt for the AI model"""
        return """You're a smart startup analyst and a startup coach helping understand a founder's idea. Your job is to: 
1. Understand their startup idea. 
2. Ask follow-up questions across these categories (if relevant): 
   - Technical Details 
   - Revenue
   - Business Viability 
   - Team 
   - Traction & Timeline 
   - Challenges & Risks 
   - Long-term Vision
   - Competition
   - Monetization
   - Differentiators
   - Risks



Only ask one question at a time. Be curious but friendly. Do not provide reasons or explanations for your questions. 
When you think you have all the information, say: '✅ I'm ready to summarize your startup now.'

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

    def query_model(self, prompt: str, conversation_history: str = "") -> str:
        """
        Query the AI model with proper error handling and retries
        
        Args:
            prompt: The user's input prompt
            conversation_history: Previous conversation context
            
        Returns:
            The model's response as a string
        """
        try:
            messages = [{"role": "system", "content": self._get_system_prompt()}]

            if conversation_history:
                for line in conversation_history.strip().split("\n"):
                    if line.startswith("User:"):
                        messages.append({
                            "role": "user",
                            "content": line.replace("User:", "").strip()
                        })
                    elif line.startswith(("Assistant:", "System:")):
                        messages.append({
                            "role": "assistant",
                            "content": line.replace("Assistant:", "").replace("System:", "").strip()
                        })

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=messages
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error querying model: {str(e)}")
            raise

    def interactive_session(self) -> Tuple[str, str]:
        """
        Run an interactive session to gather startup information
        
        Returns:
            Tuple of (user_idea, conversation_history)
        """
        try:
            print("🧠 Tell me your startup idea (ex: AI for diabetes care):")
            user_idea = input("> ").strip()
            
            conversation = f"System: {self._get_system_prompt()}\nUser: My startup idea: {user_idea}\n"
            
            # First response from AI
            response = self.query_model(f"You are a helpful assistant. Respond to this startup idea: {user_idea}")
            print(f"\n🤖 {response}")
            conversation += f"Assistant: {response}\n"
            
            while True:
                if "✅ I'm ready to summarize" in response:
                    break
                    
                user_reply = input("💬 You: ").strip()
                conversation += f"User: {user_reply}\n"
                
                response = self.query_model(
                    "Continue this conversation about a startup idea. Remember to ask good questions and eventually say you're ready to summarize when you have enough information.",
                    conversation
                )
                print(f"\n🤖 {response}")
                conversation += f"Assistant: {response}\n"
            
            return user_idea, conversation

        except KeyboardInterrupt:
            logger.info("Session interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Error in interactive session: {str(e)}")
            raise

    def generate_summary(self, user_idea: str, conversation: str) -> StartupSummary:
        """
        Generate a structured summary of the startup idea
        
        Args:
            user_idea: The initial startup idea
            conversation: The full conversation history
            
        Returns:
            StartupSummary object containing structured information
        """
        try:
            # Modified prompt to explicitly request JSON format
            prompt = f"""Based on this startup idea and conversation, generate a structured summary in valid JSON format:
Startup Idea: {user_idea}

Conversation:
{conversation}

Format the response EXACTLY like this, with no additional text:
{{
  "title": "One-line Title",
  "description": "A clear explanation of the startup idea",
  "target_users": ["user type 1", "user type 2"],
  "problem": "Problem statement",
  "solution": "Solution description",
  "tech_stack": ["technology 1", "technology 2"],
  "business_model": "Business model description",
  "monetization": "Monetization strategy",
  "competition": "Main competitors",
  "differentiator": "Key differentiators",
  "risks": ["risk 1", "risk 2"],
  "vision": "Long-term vision"
}}"""

            response = self.query_model(prompt)
            
            # Clean up the response to extract JSON
            json_str = response.strip()
            
            # Remove any markdown code block markers
            if "```" in json_str:
                # Try to find JSON block
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                else:
                    json_str = json_str.split("```")[1].split("```")[0].strip()
            
            # Additional cleanup for common issues
            json_str = json_str.replace('\n', ' ').replace('\r', '')
            json_str = re.sub(r'\\(?!["\\/bfnrt])', '', json_str)  # Remove invalid escapes
            
            try:
                summary_dict = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {json_str}")
                logger.error(f"JSON error: {str(e)}")
                
                # Fallback: Try to fix common JSON issues
                json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                
                try:
                    summary_dict = json.loads(json_str)
                except json.JSONDecodeError:
                    # If still failing, try to create a basic structure
                    logger.warning("Creating basic summary structure due to parsing failure")
                    summary_dict = {
                        "title": user_idea,
                        "description": "Failed to parse complete summary",
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
            
            # Ensure all required fields are present
            required_fields = [
                "title", "description", "target_users", "problem", "solution",
                "tech_stack", "business_model", "monetization", "competition",
                "differentiator", "risks", "vision"
            ]
            
            for field in required_fields:
                if field not in summary_dict:
                    summary_dict[field] = [] if field in ["target_users", "tech_stack", "risks"] else ""
                
                # Ensure list fields are actually lists
                if field in ["target_users", "tech_stack", "risks"] and not isinstance(summary_dict[field], list):
                    summary_dict[field] = [str(summary_dict[field])] if summary_dict[field] else []

            return StartupSummary(**summary_dict)

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            # Return a basic summary instead of raising an exception
            return StartupSummary(
                title=user_idea,
                description="Failed to generate complete summary",
                target_users=[],
                problem="",
                solution="",
                tech_stack=[],
                business_model="",
                monetization="",
                competition="",
                differentiator="",
                risks=[],
                vision=""
            )

def main():
    """Main entry point for the startup idea analyzer"""
    try:
        analyzer = StartupIdeaAnalyzer()
        idea, conversation = analyzer.interactive_session()
        
        print("\n📦 Generating your startup summary...\n")
        summary = analyzer.generate_summary(idea, conversation)
        
        # Print formatted JSON summary
        print(summary.to_json())
        
        # Optionally save to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "startup_summary.json", "w") as f:
            json.dump(summary.to_dict(), f, indent=2)
            
        logger.info("Summary saved to output/startup_summary.json")

    except KeyboardInterrupt:
        print("\n\nSession terminated by user.")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()