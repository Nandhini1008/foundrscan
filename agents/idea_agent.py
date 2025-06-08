from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import json
import logging
from pathlib import Path
import os
from together import Together
from dotenv import load_dotenv
import re
import asyncio
import aiohttp
import pyaudio
from deepgram import Deepgram
"""try:
    return response.choices[0].message.content.strip()
except (AttributeError, IndexError, KeyError):
    logger.error("Unexpected response format from Together AI")
    return "❌ Unexpected response format from the AI."
"""
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(_name_)

# Audio parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

@dataclass
class StartupSummary:
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

    def _init_(self):
        """Initialize the analyzer with Together AI client"""
        try:
            # Load environment variables from .env file
            load_dotenv(override=True)
            
            # Get API keys from environment variables
            together_api_key = os.getenv("TOGETHER_API_KEY")
            self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
            
            if not together_api_key:
                raise ValueError("TOGETHER_API_KEY environment variable is not set")
            if not self.deepgram_api_key:
                raise ValueError("DEEPGRAM_API_KEY environment variable is not set")
                
            self.client = Together(api_key=together_api_key)
            logger.info("Successfully initialized Together AI client")
            
        except Exception as e:
            logger.error(f"Failed to initialize: {str(e)}")
            raise

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI assistant"""
        return """You are an expert startup advisor and business analyst. Your role is to:
1. Ask insightful questions about the startup idea
2. Help clarify the business model, target market, and value proposition
3. Identify potential challenges and opportunities
4. Guide the conversation to gather all necessary information
5. When you have enough information, say "✅ I'm ready to summarize"

Be professional but conversational. Focus on understanding the core aspects of the business."""

    def query_model(self, prompt: str, conversation: Optional[str] = None) -> str:
        """Query the Together AI model with the given prompt"""
        try:
            full_prompt = prompt
            if conversation:
                full_prompt = f"{conversation}\n{prompt}"

            response = self.client.chat.completions.create(
                model="togethercomputer/llama-3-70b-chat",  # You can change to the model you prefer
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that helps clarify startup ideas."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Together AI query failed: {str(e)}")
            return "❌ Failed to get a response from the AI."

    async def transcribe_live(self) -> str:
        """Get voice input using Deepgram"""
        deepgram = Deepgram(self.deepgram_api_key)
        transcript = ""
        finished = False

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)

        print("🎤 Speak your startup idea...")

        # Create Deepgram connection with options
        dg_connection = await deepgram.transcription.live({
            'punctuate': True,
            'model': 'nova',
            'language': 'en-US',
            'encoding': 'linear16',
            'sample_rate': RATE,
            'channels': CHANNELS
        })

        async def process_audio():
            nonlocal finished
            try:
                while not finished:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    await dg_connection.send(data)
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error during audio processing: {str(e)}")
            finally:
                await dg_connection.finish()

        async def process_transcript():
            nonlocal transcript, finished
            try:
                async for event in dg_connection.events():
                    if event.type == 'Results':
                        transcript = event.channel.alternatives[0].transcript
                        if transcript:
                            print(f"You said: {transcript}")
                            finished = True
                            break
            except Exception as e:
                logger.error(f"Error during transcript processing: {str(e)}")

        # Start both tasks
        await dg_connection._start()
        audio_task = asyncio.create_task(process_audio())
        transcript_task = asyncio.create_task(process_transcript())

        try:
            # Wait for transcript task to complete
            await transcript_task
        finally:
            # Clean up
            finished = True
            await audio_task
            stream.stop_stream()
            stream.close()
            p.terminate()

        return transcript

    def interactive_session(self) -> Tuple[str, str]:
        """Run an interactive session to gather startup information"""
        try:
            print("🧠 Tell me your startup idea (type or speak):")
            print("Press Enter to start speaking, or type your idea and press Enter")
            
            user_input = input("> ").strip()
            if not user_input:  # If user pressed Enter without typing
                user_idea = asyncio.run(self.transcribe_live())
            else:
                user_idea = user_input
            
            conversation = f"System: {self._get_system_prompt()}\nUser: My startup idea: {user_idea}\n"
            
            # First response from AI
            response = self.query_model(f"You are a helpful assistant. Respond to this startup idea: {user_idea}")
            print(f"\n🤖 {response}")
            conversation += f"Assistant: {response}\n"
            
            while True:
                if "✅ I'm ready to summarize" in response:
                    break
                    
                print("\n💬 Your response (type or speak):")
                user_input = input("> ").strip()
                if not user_input:  # If user pressed Enter without typing
                    user_reply = asyncio.run(self.transcribe_live())
                else:
                    user_reply = user_input
                
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
        """Generate a structured summary of the startup idea"""
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
            if "" in json_str:
                # Try to find JSON block
                if "json" in json_str:
                    json_str = json_str.split("json")[1].split("")[0].strip()
                else:
                    json_str = json_str.split("")[1].split("")[0].strip()
            
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

if _name_ == "_main_":
    main()