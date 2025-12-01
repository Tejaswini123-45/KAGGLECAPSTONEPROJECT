"""
Fallback handler for when AI safety filters are triggered.
Provides rule-based responses to keep the conversation flowing.
"""

def get_fallback_response(user_input: str, context: dict = None) -> str:
    """
    Generate a fallback response when AI is blocked.
    
    Args:
        user_input: The user's message
        context: Optional context dictionary with question info
        
    Returns:
        A helpful fallback response
    """
    user_input_lower = user_input.lower().strip()
    
    # Greetings
    if any(greeting in user_input_lower for greeting in ["hi", "hello", "hey", "good morning", "good afternoon"]):
        return "Hello! I'm here to help you build your business. Let's get started with some questions about your venture."
    
    # Thanks
    if any(thanks in user_input_lower for thanks in ["thank", "thanks", "appreciate"]):
        return "You're welcome! Let's continue building your business foundation."
    
    # Help requests
    if any(help_word in user_input_lower for help_word in ["help", "stuck", "confused", "don't understand"]):
        return "I'm here to help! Just answer the questions as best as you can. There are no wrong answers - I want to understand your business vision."
    
    # Short responses
    if len(user_input.split()) < 3:
        return "Could you tell me a bit more about that? I want to make sure I understand your business properly."
    
    # Default: Accept as answer
    return "Got it! That's helpful information. Let me save that and move on to the next question."


def sanitize_prompt(prompt: str) -> str:
    """
    Sanitize a prompt to reduce likelihood of safety filter triggers.
    
    Args:
        prompt: The original prompt
        
    Returns:
        Sanitized version of the prompt
    """
    # Remove potentially problematic phrases
    problematic_phrases = [
        "attack",
        "kill",
        "destroy",
        "harm",
        "weapon",
        "violence"
    ]
    
    sanitized = prompt
    for phrase in problematic_phrases:
        if phrase in sanitized.lower():
            # Replace with business-friendly alternatives
            replacements = {
                "attack": "approach",
                "kill": "eliminate",
                "destroy": "disrupt",
                "harm": "affect",
                "weapon": "tool",
                "violence": "intensity"
            }
            sanitized = sanitized.replace(phrase, replacements.get(phrase, "address"))
    
    return sanitized


def extract_answer_from_input(user_input: str, question: str) -> dict:
    """
    Simple rule-based answer extraction when AI is unavailable.
    
    Args:
        user_input: User's response
        question: The question being asked
        
    Returns:
        Dict with type, reply, and extracted answer
    """
    user_input_lower = user_input.lower().strip()
    
    # Check if it's a greeting
    if any(g in user_input_lower for g in ["hi", "hello", "hey"]) and len(user_input.split()) <= 3:
        return {
            "type": "CHAT",
            "reply": "Hello! Let's focus on the question at hand.",
            "extracted": ""
        }
    
    # Check if it's too short
    if len(user_input.split()) < 3:
        return {
            "type": "GIBBERISH",
            "reply": "Could you provide more details?",
            "extracted": ""
        }
    
    # Check if it's a question back
    if "?" in user_input:
        return {
            "type": "CHAT",
            "reply": "That's a good question! But first, let me understand your answer to my question.",
            "extracted": ""
        }
    
    # Default: treat as answer
    return {
        "type": "ANSWER",
        "reply": "Thank you for sharing that!",
        "extracted": user_input
    }
