"""
Memory Manager for AI Company Builder

Handles persistent storage of user business information across sessions.
Stores answers to the 10-question onboarding flow.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional

# Memory file path
MEMORY_DIR = Path(__file__).parent
MEMORY_FILE = MEMORY_DIR / "user_memory.json"

# Define the 10 onboarding questions and their memory fields
ONBOARDING_QUESTIONS = [
    ("problem", "What problem are you solving?"),
    ("target_audience", "Who is your target audience?"),
    ("unique_value", "What is your unique value proposition?"),
    ("offer", "What exactly are you offering?"),
    ("business_model", "How will the business make money?"),
    ("systems_needed", "What systems do you need to run the business?"),
    ("marketing_plan", "How will customers discover your business?"),
    ("brand_identity", "What is your brand identity?"),
    ("trust_factors", "Why should people trust your business?"),
    ("scaling_vision", "What is your 1–3 year scaling vision?"),
]

# Default empty memory structure
DEFAULT_MEMORY = {
    "problem": "",
    "target_audience": "",
    "unique_value": "",
    "offer": "",
    "business_model": "",
    "systems_needed": "",
    "marketing_plan": "",
    "brand_identity": "",
    "trust_factors": "",
    "scaling_vision": "",
    "onboarding_complete": False,
    "current_question_index": 0,
}


def load_memory() -> Dict:
    """Load memory from JSON file. Creates file with defaults if it doesn't exist."""
    if not MEMORY_FILE.exists():
        # Create directory if it doesn't exist
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        # Create file with default structure
        save_memory(DEFAULT_MEMORY.copy())
        return DEFAULT_MEMORY.copy()
    
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8-sig") as f:
            memory = json.load(f)
        
        # Ensure all required fields exist (backward compatibility)
        for key, default_value in DEFAULT_MEMORY.items():
            if key not in memory:
                memory[key] = default_value
        
        return memory
    except (json.JSONDecodeError, IOError) as e:
        print(f"[WARN] Error loading memory: {e}. Using defaults.")
        return DEFAULT_MEMORY.copy()


def save_memory(memory: Dict) -> bool:
    """Save memory to JSON file."""
    try:
        # Ensure directory exists
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        
        # Use UTF-8 without BOM for clean JSON files
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"[ERROR] Failed to save memory: {e}")
        return False


def update_memory(field: str, value: str) -> bool:
    """Update a specific memory field."""
    memory = load_memory()
    
    if field not in DEFAULT_MEMORY:
        print(f"[WARN] Unknown memory field: {field}")
        return False
    
    memory[field] = value
    return save_memory(memory)


def get_memory() -> Dict:
    """Get current memory (read-only)."""
    return load_memory()


def get_memory_field(field: str, default: str = "") -> str:
    """Get a specific memory field."""
    memory = load_memory()
    return memory.get(field, default)


def reset_memory() -> bool:
    """Reset all memory to defaults."""
    return save_memory(DEFAULT_MEMORY.copy())


def is_onboarding_complete() -> bool:
    """Check if onboarding is complete."""
    memory = load_memory()
    return memory.get("onboarding_complete", False)


def get_current_question_index() -> int:
    """Get the current question index (0-9)."""
    memory = load_memory()
    return memory.get("current_question_index", 0)


def get_current_question() -> Optional[tuple]:
    """Get the current question (field, question_text)."""
    index = get_current_question_index()
    if 0 <= index < len(ONBOARDING_QUESTIONS):
        return ONBOARDING_QUESTIONS[index]
    return None


def get_next_question_index() -> Optional[int]:
    """Get the index of the next unanswered question."""
    memory = load_memory()
    index = memory.get("current_question_index", 0)
    
    # Find first empty field
    for i, (field, _) in enumerate(ONBOARDING_QUESTIONS):
        if not memory.get(field, "").strip():
            return i
    
    # All questions answered
    return None


def save_answer(field: str, answer: str) -> bool:
    """Save an answer and update question index."""
    memory = load_memory()
    
    if field not in DEFAULT_MEMORY:
        print(f"[ERROR] Unknown field: {field}")
        return False
    
    # Update the answer
    memory[field] = answer.strip()
    print(f"[DEBUG] Saved answer to '{field}'")
    
    # Find next unanswered question by checking all fields
    next_index = None
    for i, (field_name, _) in enumerate(ONBOARDING_QUESTIONS):
        if not memory.get(field_name, "").strip():
            next_index = i
            break
    
    print(f"[DEBUG] Next unanswered question index: {next_index}")
    
    if next_index is not None:
        memory["current_question_index"] = next_index
        memory["onboarding_complete"] = False
        print(f"[DEBUG] Moving to question index {next_index}")
    else:
        # All questions answered!
        memory["onboarding_complete"] = True
        memory["current_question_index"] = len(ONBOARDING_QUESTIONS)
        print("[DEBUG] All questions answered!")
    
    success = save_memory(memory)
    print(f"[DEBUG] Memory saved successfully: {success}")
    return success


def get_business_summary() -> str:
    """Generate a formatted summary of all business information."""
    memory = get_memory()
    
    if not is_onboarding_complete():
        return "Onboarding is not yet complete. Please finish answering all questions."
    
    summary_parts = []
    for field, question in ONBOARDING_QUESTIONS:
        answer = memory.get(field, "").strip()
        if answer:
            summary_parts.append(f"**{question}**\n{answer}\n")
    
    if summary_parts:
        return "\n".join(summary_parts)
    return "No business information stored yet."

