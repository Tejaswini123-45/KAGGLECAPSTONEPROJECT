"""
Router Agent Handler - Memory-Aware Message Processing

Handles onboarding flow, memory management, and personalized responses.
"""

from typing import Dict, Tuple, Optional
from memory.memory_manager import (
    load_memory,
    save_answer,
    is_onboarding_complete,
    get_current_question,
    get_next_question_index,
    get_business_summary,
    ONBOARDING_QUESTIONS,
    update_memory,
    get_memory_field,
)
from agents.router_agent import router_agent


def process_message_with_memory(user_message: str) -> str:
    """
    Process user message with memory awareness and onboarding flow.
    
    Returns:
        Agent response string
    """
    # IMPORTANT: Handle special check command FIRST - before ANY processing
    # This internal command should NEVER reach the LLM
    message_stripped = user_message.strip()
    if message_stripped == "__CHECK_ONBOARDING__":
        memory = load_memory()
        if not is_onboarding_complete():
            current_question_data = get_current_question()
            if current_question_data:
                field, question_text = current_question_data
                question_num = memory.get('current_question_index', 0) + 1
                response = generate_conversational_question(question_num, question_text, field, memory)
                print(f"[DEBUG] Auto-start onboarding - Question {question_num}")
                return response
            else:
                # Start from beginning
                first_question = ONBOARDING_QUESTIONS[0]
                response = generate_conversational_question(1, first_question[1], first_question[0], memory)
                print("[DEBUG] Auto-start onboarding - Starting from beginning")
                return response
        else:
            response = """Welcome back to The Growth Hub! 🎉

Your onboarding is complete. I have your business information and I'm ready to help you build your business!

How can I assist you today?"""
            print("[DEBUG] Auto-start check - Onboarding already complete")
            return response
    
    user_message_lower = user_message.lower().strip()
    memory = load_memory()
    
    # Handle special commands
    if "show my answers" in user_message_lower or "show my info" in user_message_lower:
        return get_business_summary()
    
    if "reset onboarding" in user_message_lower or "start over" in user_message_lower:
        from memory.memory_manager import reset_memory
        reset_memory()
        current_question = get_current_question()
        if current_question:
            return generate_conversational_question(1, current_question[1], current_question[0], load_memory())
        return "Onboarding reset. Ready to begin!"
    
    # Check if user wants to update a specific answer
    if "update" in user_message_lower or "change" in user_message_lower:
        # Try to detect which field they want to update
        for field, question in ONBOARDING_QUESTIONS:
            field_keywords = field.replace("_", " ").split()
            if any(keyword in user_message_lower for keyword in field_keywords):
                # Extract the new answer (after "update" keyword)
                parts = user_message_lower.split("update", 1) + user_message_lower.split("change", 1)
                if len(parts) > 1:
                    new_answer = parts[1].strip()
                    if new_answer:
                        update_memory(field, new_answer)
                        return f"✅ Updated your answer to '{question}': {new_answer}\n\nIs there anything else you'd like to update?"
        
        return "I can help you update any of your answers. Try saying 'update [field name] [new answer]' or just tell me what you'd like to change."
    
    # Check onboarding status
    if not is_onboarding_complete():
        # We're in onboarding mode - use conversational flow
        return handle_onboarding_conversation(user_message, memory)
    else:
        # Onboarding complete - normal chat mode with memory
        return process_normal_chat_with_memory(user_message, memory)


def generate_conversational_question(question_num: int, question_text: str, field: str, memory: Dict) -> str:
    """Generate a conversational, friendly question to ask the user."""
    # Build context of previous answers for natural conversation
    answered_fields = [f for f, q in ONBOARDING_QUESTIONS if memory.get(f, "").strip()]
    
    if question_num == 1:
        return f"""Welcome to The Growth Hub! 🚀

Before I can help you build your business, I need to understand your vision. Let's complete a quick onboarding - I'll ask you 10 questions about your business idea.

**Question 1:** What problem are you solving?

Think about what challenges or pain points your target customers face that you want to address."""
    
    # For subsequent questions, reference previous context naturally
    context_hint = ""
    if answered_fields:
        last_field = answered_fields[-1]
        if last_field == "problem" and memory.get("problem"):
            context_hint = f"Now that we know you're solving {memory['problem'][:50]}..."
        elif last_field == "target_audience" and memory.get("target_audience"):
            context_hint = f"Great! So your target audience is {memory['target_audience'][:50]}. "
    
    # Natural question phrasing based on question number - matches exact questions
    natural_phrases = {
        2: f"{context_hint}**Question 2:** Who is your target audience?",
        3: f"{context_hint}**Question 3:** What is your unique value proposition?",
        4: f"{context_hint}**Question 4:** What exactly are you offering?",
        5: f"{context_hint}**Question 5:** How will the business make money?",
        6: f"{context_hint}**Question 6:** What systems do you need to run the business smoothly?",
        7: f"{context_hint}**Question 7:** How will customers discover your business?",
        8: f"{context_hint}**Question 8:** What is your brand identity?",
        9: f"{context_hint}**Question 9:** Why should people trust your business?",
        10: f"{context_hint}**Question 10:** What is your 1–3 year scaling vision?",
    }
    
    return natural_phrases.get(question_num, f"{context_hint}**Question {question_num}:** {question_text}")


def validate_answer_relevance(question: str, answer: str, llm) -> Tuple[bool, str]:
    """
    Use LLM to validate if the answer is relevant to the question.
    Returns: (is_relevant: bool, feedback: str)
    """
    validation_prompt = f"""You are helping validate if a user's answer is relevant to a business onboarding question.

QUESTION: {question}

USER'S ANSWER: {answer}

Analyze if the answer is relevant and addresses the question. Consider:
1. Does the answer relate to the question topic?
2. Is it a reasonable business-related answer?
3. Is it specific enough (not too vague)?

Respond with ONLY one of these:
- "RELEVANT" - if the answer is good and relevant
- "VAGUE" - if the answer is too short or vague, provide a brief hint
- "IRRELEVANT" - if the answer doesn't address the question at all

Format: [STATUS] [Optional brief feedback]
"""
    
    try:
        response = llm.call(validation_prompt).strip()
        
        if "RELEVANT" in response.upper():
            return True, ""
        elif "VAGUE" in response.upper():
            feedback = response.replace("VAGUE", "").strip()
            if not feedback:
                feedback = "Could you provide a bit more detail? I'd love to understand better."
            return False, feedback
        elif "IRRELEVANT" in response.upper():
            feedback = response.replace("IRRELEVANT", "").strip()
            if not feedback:
                feedback = "That doesn't quite address this question. Let me rephrase..."
            return False, feedback
        else:
            # Default to accepting if unclear
            return True, ""
    except Exception as e:
        # If validation fails, default to accepting
        print(f"[WARN] Answer validation failed: {e}")
        return True, ""


def handle_onboarding_conversation(user_message: str, memory: Dict) -> str:
    """
    Handle FORCED onboarding conversation flow.
    User MUST answer questions sequentially - no other topics allowed.
    """
    current_question_data = get_current_question()
    
    if not current_question_data:
        # Start from beginning
        first_question = ONBOARDING_QUESTIONS[0]
        return generate_conversational_question(1, first_question[1], first_question[0], memory)
    
    field, question_text = current_question_data
    current_answer = memory.get(field, "").strip()
    question_num = memory.get('current_question_index', 0) + 1
    
    user_lower = user_message.lower().strip()
    
    # Handle special commands during onboarding
    if "show my answers" in user_lower or "show my info" in user_lower:
        summary = get_business_summary()
        return f"Here are your current answers:\n\n{summary}\n\n---\n\nLet's continue with your onboarding.\n\n**Question {question_num}:** {question_text}"
    
    if "restart onboarding" in user_lower or "start over" in user_lower:
        from memory.memory_manager import reset_memory
        reset_memory()
        first_question = ONBOARDING_QUESTIONS[0]
        return "Onboarding reset! Let's start fresh.\n\n" + generate_conversational_question(1, first_question[1], first_question[0], load_memory())
    
    # STRICT ENFORCEMENT: If user tries to ask unrelated questions, redirect them
    if not current_answer:
        # Check if this is an answer attempt or unrelated question
        is_likely_answer = check_if_answer_attempt(user_message, question_text, question_num)
        
        if not is_likely_answer:
            # User is trying to ask something else - redirect firmly but politely
            return f"""I'm currently helping you complete your business onboarding. Once we finish all 10 questions, I'll be happy to answer any questions you have!

Right now, let's focus on this question:

**Question {question_num}: {question_text}**

Please share your answer to this question. After we complete onboarding, I'll be ready to help with anything else! 😊"""
        
        # It's likely an answer - validate with LLM
        is_relevant, feedback = validate_answer_relevance(question_text, user_message, router_agent.llm)
        
        if not is_relevant:
            # Answer not relevant - guide user back firmly
            if feedback:
                return f"{feedback}\n\n**Please answer this question:** {question_text}"
            else:
                return f"I'd love to help with that after onboarding is complete! Right now, please answer:\n\n**Question {question_num}: {question_text}**"
        
        # Answer is relevant - check if detailed enough
        if len(user_message.strip()) < 10:
            return f"I'd appreciate a bit more detail to better understand your vision.\n\n**Question {question_num}: {question_text}**"
        
        # SAVE THE ANSWER - This is a valid answer
        save_answer(field, user_message)
        
        # Check if more questions
        next_index = get_next_question_index()
        if next_index is not None:
            next_question = ONBOARDING_QUESTIONS[next_index]
            next_question_num = next_index + 1
            # Auto-ask next question
            return f"Perfect! Thank you for that information. ✅\n\n**Question {next_question_num}:** {next_question[1]}"
        else:
            # All questions answered!
            return generate_onboarding_complete_response()
    else:
        # Field already answered, move to next automatically
        next_index = get_next_question_index()
        if next_index is not None:
            next_question = ONBOARDING_QUESTIONS[next_index]
            next_question_num = next_index + 1
            return generate_conversational_question(next_question_num, next_question[1], next_question[0], memory)
        else:
            # All answered but flag not set
            save_answer(field, current_answer)  # Ensure flag is set
            return generate_onboarding_complete_response()


def check_if_answer_attempt(user_message: str, current_question: str, question_num: int) -> bool:
    """
    Check if user message is likely an answer to the current question.
    Returns True if it seems like an answer, False if it's a different question/topic.
    """
    user_lower = user_message.lower().strip()
    
    # Common question indicators (user is asking something)
    question_indicators = [
        "how do i", "how can i", "what is", "what are", "why", "when", "where",
        "tell me", "explain", "help me", "can you", "i want to", "i need to",
        "i want", "i need", "how to", "what should", "what would"
    ]
    
    # If message starts with question indicators, likely not an answer
    if any(user_lower.startswith(indicator) for indicator in question_indicators):
        # Unless it's very short, might be answering with a question format
        if len(user_message) < 30:
            return True  # Could be a short answer
        return False  # Likely asking something else
    
    # Greetings - not answers
    greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
    if any(greeting in user_lower for greeting in greetings) and len(user_message) < 25:
        return False
    
    # If message is long enough and doesn't start with question words, likely an answer
    if len(user_message) > 15:
        return True
    
    # Default: assume it might be an answer (validation will catch it if not)
    return True


def generate_onboarding_complete_response() -> str:
    """Generate response after completing all onboarding questions."""
    summary = get_business_summary()
    
    completion_message = """🎉 **Great! Your onboarding is complete.**

I now have a complete understanding of your business vision. Here is your business foundation summary:

---
"""
    
    completion_message += summary
    
    completion_message += """
---

**You can now ask me anything!**

I'm ready to help you with:
• Website development strategies
• Marketing campaigns and content  
• Business systems and processes
• Scaling and growth plans
• Technical recommendations
• And much more!

You can also:
• Say "show my answers" to review your business blueprint anytime
• Say "restart onboarding" to start over
• Ask me specific questions about your business

What would you like to know? 🚀
"""
    
    return completion_message


def process_normal_chat_with_memory(user_message: str, memory: Dict) -> str:
    """
    Process normal chat messages with memory context.
    Agent uses memory to provide personalized responses.
    """
    # Build memory context for the agent
    memory_context = build_memory_context(memory)
    
    # Enhance the prompt with memory
    enhanced_prompt = f"""You are the CEO and smart chatbot of an AI-powered company builder platform.

USER'S BUSINESS INFORMATION (from previous onboarding):
{memory_context}

IMPORTANT: Use this business information to provide personalized, relevant advice. Reference their specific problem, audience, and goals when appropriate.

USER'S CURRENT MESSAGE:
{user_message}

Provide a helpful, personalized response that:
1. Uses the user's business information when relevant
2. Offers specific, actionable advice
3. Maintains a friendly, professional CEO tone
4. Focuses on helping them succeed

If the user asks to see their business info, redirect them to say "show my answers".
If they want to update information, help them do so.
"""
    
    # Get response from the agent's LLM
    try:
        response = router_agent.llm.call(enhanced_prompt)
        return response
    except Exception as e:
        return f"I encountered an error processing your message: {str(e)}\n\nPlease try again or say 'show my answers' to review your business information."


def build_memory_context(memory: Dict) -> str:
    """Build a formatted string of memory for agent context."""
    context_parts = []
    
    for field, question in ONBOARDING_QUESTIONS:
        answer = memory.get(field, "").strip()
        if answer:
            context_parts.append(f"• {question}\n  Answer: {answer}")
    
    if context_parts:
        return "\n".join(context_parts)
    return "No business information stored yet."


# For backward compatibility - direct access to handler
def get_agent_response(user_message: str) -> str:
    """Main entry point for getting agent responses."""
    return process_message_with_memory(user_message)

