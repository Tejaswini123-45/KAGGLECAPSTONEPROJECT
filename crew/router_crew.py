# crew/router_crew.py
from crewai import Agent, Crew, Task

# A lightweight router agent (rule-based) — not heavy LLM
# Note: This file is legacy/unused. Main router uses GeminiLLM via agents/router_agent.py
class RouterAgent:
    def decide(self, text):
        text = text.lower()
        targets = []
        if "website" in text or "site" in text:
            targets.append("website")
        if "social" in text or "post" in text or "marketing" in text:
            targets.append("marketing")
        if "money" in text or "finance" in text or "profit" in text:
            targets.append("finance")
        if not targets:
            targets = ["website","marketing"]  # default
        return targets
