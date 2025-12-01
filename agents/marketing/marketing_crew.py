import os
import yaml
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools.zapier_instagram_webhook import ZapierInstagramWebhookTool

# Placeholder for DALL-E since we don't have a key
from crewai.tools import BaseTool
class DummyDallETool(BaseTool):
    name: str = "dalle_tool"
    description: str = "Generates images using AI (Simulated)"
    def _run(self, query: str) -> str:
        return "https://via.placeholder.com/1080x1080.png?text=AI+Generated+Image"

@CrewBase
class SingleInstagramPostCreatorCrew:
    """SingleInstagramPostCreator crew"""
    
    def __init__(self):
        # Load configs manually since we are not using the full CLI structure
        base_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_path, "config", "agents.yaml"), "r") as f:
            self.agents_config = yaml.safe_load(f)
        with open(os.path.join(base_path, "config", "tasks.yaml"), "r") as f:
            self.tasks_config = yaml.safe_load(f)

    @agent
    def social_media_content_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["social_media_content_strategist"],
            tools=[], # Removed SerperDevTool
            verbose=True,
            llm=LLM(model="gemini/gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
        )
    
    @agent
    def content_publishing_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["content_publishing_manager"],
            tools=[ZapierInstagramWebhookTool()],
            verbose=True,
            llm=LLM(model="gemini/gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
        )
    
    @agent
    def visual_content_creator(self) -> Agent:
        return Agent(
            config=self.agents_config["visual_content_creator"],
            tools=[DummyDallETool()], # Replaced DallETool
            verbose=True,
            llm=LLM(model="gemini/gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
        )

    @task
    def generate_single_post_content_idea(self) -> Task:
        return Task(
            config=self.tasks_config["generate_single_post_content_idea"],
        )
    
    @task
    def create_single_instagram_image(self) -> Task:
        return Task(
            config=self.tasks_config["create_single_instagram_image"],
        )
    
    @task
    def send_content_to_zapier_webhook(self) -> Task:
        return Task(
            config=self.tasks_config["send_content_to_zapier_webhook"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
