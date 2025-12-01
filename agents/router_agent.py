from crewai import Agent, LLM
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini LLM for Router Agent using CrewAI's LLM class
# This ensures compatibility with the latest CrewAI version
print("[DEBUG] Initializing CrewAI LLM for Router Agent...")
llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)
print(f"[DEBUG] CrewAI LLM initialized: {llm.model}")

router_agent = Agent(
    name="RouterAgent",
    role="Smart Chatbot CEO / Project Manager / Orchestrator",
    goal=(
        "Be a friendly and engaging AI Advisor. Your primary goal is to ONBOARD the user by asking 10 key questions "
        "to understand their business idea deeply. Do not overwhelm them; ask 1-2 questions at a time. "
        "Once you have enough info, route them to specialized teams or provide a comprehensive plan."
    ),
    backstory=(
        "You are the AI Advisor and Onboarding Specialist for Growth Hub. "
        "You are friendly, enthusiastic, and curious. "
        "Your job is to guide new founders through a 10-step discovery process to uncover their vision, target audience, and needs. "
        "You keep the conversation flowing naturally. You are NOT just a router; you are a partner. "
        "Start by welcoming them and asking about their core business idea."
    ),
    llm=llm,
    verbose=True,
)
