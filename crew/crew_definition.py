from crewai import Crew, Task
from agents.router_agent import router_agent
from agents.website_agent import website_agent
from agents.marketing_agent import marketing_agent

# Define tasks for each agent

# Router task: orchestrate based on user input
router_task = Task(
    description=(
        "Listen to the founder's business idea and request. "
        "Determine which teams (Website, Marketing, Finance, HR, etc.) should handle specific parts. "
        "Orchestrate their work and combine all outputs into a comprehensive action plan."
    ),
    expected_output="A strategic plan routing the request to the appropriate teams with clear action items.",
    agent=router_agent,
)

# Website team task
website_task = Task(
    description=(
        "Design and plan the website architecture for the business. "
        "Consider technical stack, hosting options, SEO requirements, and scalability."
    ),
    expected_output="A detailed website plan with technical recommendations and implementation steps.",
    agent=website_agent,
)

# Marketing team task
marketing_task = Task(
    description=(
        "Create a marketing strategy for the business including: "
        "audience analysis, content calendar, social media plan, and lead generation strategy."
    ),
    expected_output="A comprehensive marketing plan with daily content ideas and engagement strategies.",
    agent=marketing_agent,
)

# Create the crew
my_crew = Crew(
    agents=[router_agent, website_agent, marketing_agent],
    tasks=[router_task, website_task, marketing_task],
    verbose=True,
    process="sequential",  # Run tasks sequentially for now
)
