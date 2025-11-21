"""
Main entry point for the AI Company Builder.

Usage:
  python main.py              - Run the crew and execute tasks
  python main.py chat         - Interactive chat with router agent
  python main.py server       - Start FastAPI server on port 8000
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def interactive_chat():
    """Interactive REPL to chat with the router agent."""
    from agents.router_agent import router_agent
    llm = router_agent.llm
    
    print("\n" + "="*60)
    print("AI Company Builder - Interactive Chat with Router Agent")
    print("="*60)
    print("Ask about building a business. Type 'exit' or 'quit' to stop.\n")
    
    try:
        while True:
            try:
                msg = input("You: ").strip()
            except EOFError:
                break
            
            if not msg:
                continue
            
            if msg.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            
            try:
                response = llm.call(msg)
                print(f"Router: {response}\n")
            except Exception as e:
                print(f"Error: {e}\n")
    except KeyboardInterrupt:
        print("\n\nGoodbye!")


def run_crew():
    """Run the crew with all agents and tasks."""
    from crew.crew_definition import my_crew
    
    print("\n" + "="*60)
    print("AI Company Builder - Running Crew")
    print("="*60 + "\n")
    
    result = my_crew.kickoff(inputs={"request": "Build a comprehensive company builder system."})
    
    print("\n" + "="*60)
    print("Crew Execution Complete")
    print("="*60)
    print(f"\nFinal Output:\n{result}\n")


def start_server():
    """Start the FastAPI server."""
    print("\nStarting AI Company Builder API Server...")
    print("Server running on http://localhost:8000")
    print("Open in browser: http://localhost:8000\n")
    
    # Import here to avoid issues if fastapi not installed
    try:
        import uvicorn
        from server import app
        uvicorn.run(app, host="localhost", port=8000)
    except ImportError:
        print("FastAPI not installed. Install with: pip install fastapi uvicorn")


def main():
    args = [a.lower() for a in sys.argv[1:]]
    
    if not args or "run" in args:
        run_crew()
    elif "chat" in args:
        interactive_chat()
    elif "server" in args:
        start_server()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
