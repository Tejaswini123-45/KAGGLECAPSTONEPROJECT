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

# Note: router_agent is imported lazily only when needed to speed up server startup
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
    if question_num == 1:
        return f"""Welcome to The Growth Hub! 🚀

Before I can help you build your business, I need to understand your vision. Let's complete a quick onboarding - I'll ask you 10 questions about your business idea.

**Question 1 of 10:** {question_text}

Think about what challenges or pain points your target customers face that you want to address."""
    
    # For subsequent questions, keep it simple and direct
    return f"**Question {question_num} of 10:** {question_text}"


def validate_answer_relevance(question: str, answer: str, llm) -> Tuple[bool, str]:
    """
    Use LLM to validate if the answer is relevant to the question.
    Returns: (is_relevant: bool, feedback: str)
    
    Quick validation - if answer is reasonably detailed, accept it.
    """
    # Quick pre-checks before calling LLM
    answer_lower = answer.lower().strip()
    
    # If answer is very short, reject immediately (increased from 15 to 25)
    if len(answer) < 25:
        return False, "Please provide more details (at least 25 characters). Think about your business vision."
    
    # Check for vague/generic answers
    vague_phrases = ['i dont know', "i'm not sure", 'maybe', 'probably', 'not sure yet', 'tbd', 'to be determined', 'idk', 'dunno']
    if any(phrase in answer_lower for phrase in vague_phrases) and len(answer) < 50:
        return False, "Please provide a more specific answer. Take your time to think about your business."
    
    # If answer looks completely off-topic (common spam words), reject
    spam_words = ['click here', 'buy now', 'free money', 'guaranteed', 'xyz', 'abc', 'test', 'hello world', 'lorem ipsum']
    if any(word in answer_lower for word in spam_words):
        return False, "Please provide a genuine business answer, not test or promotional text."
    
    # If answer addresses the question meaningfully, accept it
    # (Check for common business-related keywords)
    business_keywords = ['business', 'product', 'service', 'customer', 'market', 'money', 'sell', 'buy', 'need', 'want', 'problem', 'solution', 'make', 'create', 'build', 'help', 'support', 'provide', 'offer', 'have', 'use', 'platform', 'online', 'digital', 'brand', 'people', 'audience', 'sell', 'revenue', 'profit']
    
    has_business_keyword = any(keyword in answer_lower for keyword in business_keywords)
    
    if has_business_keyword and len(answer) > 20:
        # Likely a valid answer - accept it
        print(f"[DEBUG] Quick validation: ACCEPTED (has business context, {len(answer)} chars)")
        return True, ""
    
    # If unclear, try LLM validation (with timeout)
    try:
        validation_prompt = f"""Is this answer relevant to the business question? Answer with just YES or NO.

QUESTION: {question}
ANSWER: {answer}

Reply with one word only: YES or NO"""
        
        response = llm.call(validation_prompt).strip()[:20].upper()
        print(f"[DEBUG] LLM validation response: {response}")
        
        if "YES" in response:
            return True, ""
        else:
            return False, "Please address the question more directly."
    except Exception as e:
        # If LLM fails, be lenient (user experience matters more than perfect validation)
        print(f"[WARN] LLM validation failed: {str(e)[:50]}, accepting answer")
        return True, ""


def handle_onboarding_conversation(user_message: str, memory: Dict) -> str:
    """
    Handle FORCED onboarding conversation flow.
    User MUST answer questions sequentially - no other topics allowed.
    
    All answers are validated for relevance using LLM before being stored.
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
    
    # STRICT ENFORCEMENT: Save answer if it's detailed and relevant
    if not current_answer:
        # Answer is new - check if detailed enough (minimum 10 chars)
        if len(user_message.strip()) < 10:
            return f"I'd appreciate a bit more detail to better understand your vision.\n\n**Question {question_num} of 10:** {question_text}"
        
        # VALIDATE ANSWER RELEVANCE using LLM with timeout
        print(f"[DEBUG] Validating answer for field '{field}'...")
        try:
            from agents.router_agent import router_agent
            is_relevant, feedback = validate_answer_relevance(question_text, user_message, router_agent.llm)
            
            if not is_relevant:
                # Answer is not relevant - reject and ask again with feedback
                print(f"[DEBUG] Answer rejected for field '{field}': {feedback}")
                rejection_msg = f"That doesn't quite address the question. {feedback if feedback else ''}\n\n**Question {question_num} of 10:** {question_text}"
                return rejection_msg.strip()
        except Exception as e:
            # If validation fails or times out, be lenient and accept the answer
            print(f"[WARN] Validation error (being lenient): {str(e)[:100]}")
            # Continue to save the answer anyway
            pass
        
        # SAVE THE ANSWER - This is a relevant answer
        print(f"[DEBUG] Answer validated! Saving answer to field '{field}': {user_message[:50]}...")
        save_answer(field, user_message)
        
        # Check if more questions
        next_index = get_next_question_index()
        if next_index is not None:
            next_question = ONBOARDING_QUESTIONS[next_index]
            next_question_num = next_index + 1
            # Auto-ask next question
            print(f"[DEBUG] Moving to question {next_question_num}")
            return f"Perfect! Thank you for that information. ✅\n\n**Question {next_question_num} of 10:** {next_question[1]}"
        else:
            # All questions answered!
            print("[DEBUG] All questions answered, showing completion response")
            return generate_onboarding_complete_response()
    else:
        # Field already answered, move to next automatically
        next_index = get_next_question_index()
        if next_index is not None:
            next_question = ONBOARDING_QUESTIONS[next_index]
            next_question_num = next_index + 1
            print(f"[DEBUG] Field already answered, moving to question {next_question_num}")
            return generate_conversational_question(next_question_num, next_question[1], next_question[0], memory)
        else:
            # All answered but flag not set
            print("[DEBUG] All questions answered (already saved), showing completion")
            save_answer(field, current_answer)  # Ensure flag is set
            return generate_onboarding_complete_response()


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
        from agents.router_agent import router_agent
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

    return ChatResponse(response=get_agent_response(user_msg))
    