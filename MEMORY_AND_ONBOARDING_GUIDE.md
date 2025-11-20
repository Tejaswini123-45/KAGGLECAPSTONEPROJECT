# 🧠 Memory & Onboarding System - Complete Guide

## 📋 Overview

The AI Company Builder now includes:
1. **Long-term Memory System** - Stores user business information permanently
2. **10-Question Onboarding Flow** - Collects business blueprint before normal chat

## 🎯 How It Works

### **First Time User Flow:**

1. User opens chat → Router Agent detects onboarding incomplete
2. Agent asks **Question 1**: "What problem are you solving?"
3. User answers → Agent saves answer and asks **Question 2**
4. Process repeats for all 10 questions
5. After **Question 10** → Agent provides summary and switches to advisor mode
6. From then on → Agent uses memory for personalized responses

### **Returning User Flow:**

1. User opens chat → Router Agent loads existing memory
2. If onboarding complete → Normal personalized chat mode
3. If incomplete → Resumes from last unanswered question

## 📝 The 10 Questions

1. **What problem are you solving?**
2. **Who is your target audience?**
3. **What is your unique value proposition?**
4. **What exactly are you offering?**
5. **How will the business make money?**
6. **What systems do you need to run the business?**
7. **How will customers discover your business?**
8. **What is your brand identity?**
9. **Why should people trust your business?**
10. **What is your 1–3 year scaling vision?**

## 💾 Memory Storage

**Location**: `memory/user_memory.json`

**Structure**:
```json
{
  "problem": "User's answer",
  "target_audience": "User's answer",
  "unique_value": "User's answer",
  "offer": "User's answer",
  "business_model": "User's answer",
  "systems_needed": "User's answer",
  "marketing_plan": "User's answer",
  "brand_identity": "User's answer",
  "trust_factors": "User's answer",
  "scaling_vision": "User's answer",
  "onboarding_complete": true,
  "current_question_index": 10
}
```

**Features**:
- ✅ Persists across server restarts
- ✅ Automatically created if missing
- ✅ Updates in real-time
- ✅ Human-readable JSON format

## 🎮 Special Commands

Users can say:

### **"show my answers"** or **"show my info"**
- Displays complete business blueprint
- Shows all 10 answers formatted nicely

### **"update [field name]"** or **"change [field name]"**
- Updates any specific answer
- Example: "update problem" or "change target audience"

### **"reset onboarding"** or **"start over"**
- Clears all answers and starts fresh
- Useful for major business pivots

## 🔧 Technical Implementation

### **Files Created:**

1. **`memory/memory_manager.py`**
   - Handles all memory operations
   - Functions: `load_memory()`, `save_memory()`, `update_memory()`, `get_memory()`
   - Question management: `get_current_question()`, `save_answer()`
   - Status checks: `is_onboarding_complete()`, `get_next_question_index()`

2. **`agents/router_agent_handler.py`**
   - Main logic for onboarding flow
   - `process_message_with_memory()` - Routes messages correctly
   - `process_normal_chat_with_memory()` - Uses memory in responses
   - `generate_onboarding_complete_response()` - Completion summary

3. **`memory/user_memory.json`**
   - Auto-created on first use
   - Stores all business information

### **Files Modified:**

1. **`server.py`**
   - Now uses `router_agent_handler` instead of direct LLM call
   - Updated documentation

2. **`chatbot.html`**
   - Added onboarding progress indicator
   - Shows question number (e.g., "Question 3 of 10")
   - Progress bar visualization
   - Auto-hides when complete

## 🎨 UI Features

### **Progress Indicator:**
- Shows current question number
- Visual progress bar (0-100%)
- Auto-displays during onboarding
- Hides after completion

### **Visual Feedback:**
- ✅ Checkmark when answer saved
- 🎉 Celebration when onboarding complete
- Clear question numbering
- Formatted business summary

## 📊 Memory Usage in Normal Chat

Once onboarding is complete, the Router Agent:

1. **Loads memory** before every response
2. **Includes business context** in the prompt to Gemini
3. **Personalizes advice** based on stored information
4. **References specific details** when relevant

**Example**:
- User asks: "How should I market my business?"
- Agent uses memory about target audience, brand identity, etc.
- Provides personalized, relevant marketing advice

## 🔄 Memory Flow Diagram

```
User Message
    ↓
Check Onboarding Status
    ↓
    ├─→ Incomplete? → Ask Next Question
    │                   ↓
    │               Save Answer
    │                   ↓
    │               More Questions?
    │                   ├─→ Yes → Ask Next
    │                   └─→ No → Show Summary → Normal Mode
    │
    └─→ Complete? → Load Memory
                        ↓
                    Enhance Prompt with Memory
                        ↓
                    Generate Personalized Response
```

## 🧪 Testing

### **Test Onboarding Flow:**
1. Reset memory: `python -c "from memory.memory_manager import reset_memory; reset_memory()"`
2. Send "hello" to start
3. Answer all 10 questions
4. Verify completion message
5. Test "show my answers" command

### **Test Memory Persistence:**
1. Complete onboarding
2. Restart server
3. Verify memory still exists
4. Chat with agent - should use memory

### **Test Update Command:**
1. Say "show my answers"
2. Say "update problem" with new answer
3. Verify change saved
4. Check with "show my answers" again

## 🚀 Usage Examples

### **Starting Onboarding:**
```
User: hello
Agent: Hello! 👋 Welcome to AI Company Builder!
       Before I help you build your business, I need to understand your vision.
       Question 1: What problem are you solving?
```

### **Answering Questions:**
```
User: People struggle to manage their personal finances and overspend
Agent: ✅ Thank you! I've saved that.
       Question 2: Who is your target audience?
```

### **Viewing Answers:**
```
User: show my answers
Agent: [Displays formatted business blueprint with all 10 answers]
```

### **Normal Chat (After Onboarding):**
```
User: How should I market this?
Agent: Based on your target audience of [from memory] and your unique value 
       proposition of [from memory], I recommend...
```

## ✅ Features Summary

- ✅ Persistent memory across sessions
- ✅ 10-question onboarding flow
- ✅ Progress tracking in UI
- ✅ Special commands (show, update, reset)
- ✅ Personalized responses using memory
- ✅ Automatic question progression
- ✅ Graceful handling of greetings
- ✅ Business blueprint summary
- ✅ Clean, maintainable code

## 📚 API Reference

### **Memory Manager Functions:**

```python
from memory.memory_manager import *

# Load all memory
memory = load_memory()

# Get specific field
value = get_memory_field("problem")

# Update field
update_memory("problem", "New answer")

# Save answer (handles question progression)
save_answer("problem", "Answer text")

# Check status
is_complete = is_onboarding_complete()
current_q = get_current_question()

# Get summary
summary = get_business_summary()

# Reset all
reset_memory()
```

### **Router Agent Handler:**

```python
from agents.router_agent_handler import get_agent_response

# Process any message (handles onboarding + normal chat)
response = get_agent_response(user_message)
```

---

## 🎯 What's Next?

The system is now ready for:
- Enhanced personalization
- Multi-user support (separate memory files)
- Advanced analytics on stored data
- Integration with other agents (Website, Marketing)
- Export business blueprint to PDF/Word

**Everything is working and ready to use!** 🚀

