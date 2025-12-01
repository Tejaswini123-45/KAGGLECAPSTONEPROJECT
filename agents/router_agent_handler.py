"""Router Agent - Handles chatbot conversation."""
from memory import memory_manager as mem
from llm.gemini_llm import GeminiLLM

llm = GeminiLLM()
router_agent = type("RA", (), {"llm": llm})()

FRIENDLY_QUESTIONS = [
    "Let's start! 🎯 What problem does your business solve?",
    "Great! Who is your ideal customer or target audience?",
    "Nice! What makes your solution unique or better than others?",
    "What products or services do you offer?",
    "How will your business make money? (pricing model)",
    "What tools or systems do you need to run your business?",
    "How will customers discover your business? (marketing channels)",
    "Why should people trust your business? (testimonials, experience, etc.)",
    "What is your brand name or identity?",
    "Last one! 🚀 What's your launch goal or next milestone?"
]

def process_message_with_memory(message):
    msg = (message or "").strip()
    
    if msg.lower() in ["reset", "restart", "start over"]:
        mem.reset()
        return f"🔄 Starting fresh!\n\n{FRIENDLY_QUESTIONS[0]}"
    
    if msg in ["__CHECK__", "__CHECK_ONBOARDING__"]:
        if mem.is_complete():
            return f"✅ Onboarding complete!\n\n{mem.get_summary()}\n\n🚀 Go to Website Builder to create your site!"
        idx, _ = mem.get_question()
        return FRIENDLY_QUESTIONS[idx] if idx < len(FRIENDLY_QUESTIONS) else "All done!"
    
    if mem.is_complete():
        return handle_post_chat(msg)
    
    return handle_answer(msg)

def handle_answer(user_input):
    idx, _ = mem.get_question()
    
    greetings = ["hi", "hello", "hey", "hii"]
    if user_input.lower() in greetings:
        return f"👋 Welcome to Growth Hub!\n\n{FRIENDLY_QUESTIONS[idx]}"
    
    if len(user_input) < 2:
        return f"Please provide more detail.\n\n{FRIENDLY_QUESTIONS[idx]}"
    
    mem.save_answer(user_input)
    
    if mem.is_complete():
        return f"✅ Got it!\n\n🎉 All done!\n\n{mem.get_summary()}\n\n🚀 Go to Website Builder to create your site!"
    
    new_idx, _ = mem.get_question()
    return f"✅ Saved!\n\n{FRIENDLY_QUESTIONS[new_idx]}"

def handle_post_chat(message):
    if any(w in message.lower() for w in ["summary", "answers", "info"]):
        return mem.get_summary()
    if any(w in message.lower() for w in ["build", "website", "create"]):
        return f"🚀 Go to Website Builder to create your site!\n\n{mem.get_summary()}"
    return f"Your business is ready!\n\n{mem.get_summary()}\n\n👉 Go to Website Builder!"

def process_message_stream(message):
    yield process_message_with_memory(message)
