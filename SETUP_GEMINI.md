# 🚀 AI Company Builder - Smart Router Chatbot Setup

Your Gemini-powered smart chatbot is ready! Follow these steps to get it running.

## ✅ What's Been Set Up

- ✓ **GeminiLLM** - Cloud-powered LLM using Google's Gemini API
- ✓ **Smart RouterAgent** - Friendly chatbot that understands business ideas
- ✓ **FastAPI Server** - `/chat` endpoint for website integration
- ✓ **Interactive Chat** - Direct CLI chat with the router agent
- ✓ **All Dependencies** - Installed in `crew_venv`

## 📝 Step 1: Add Your Gemini API Key

1. Go to: **https://ai.google.dev/**
2. Click "Get API Key" (free tier available)
3. Create a new API key
4. Open `.env` file and replace:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

## 🎯 Step 2: Choose How to Run

### Option A: Interactive Chat (Easiest)
```bash
python main.py chat
```

Then ask questions like:
```
You: I want to start a bakery business
Router: [Gemini-powered response with guidance]
```

### Option B: Start API Server
```bash
python main.py server
```

Server starts on `http://localhost:8000`

**Test with cURL:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me start a SaaS business"}'
```

**Response:**
```json
{
  "response": "Great idea! Here's how to start a SaaS...",
  "status": "success"
}
```

### Option C: Run Full Crew
```bash
python main.py
```

## 🔗 Website Integration

Add this to your website to embed the chatbot:

```html
<!-- Simple chatbot embed -->
<div id="chatbot">
  <div id="messages" style="height: 400px; overflow-y: auto; border: 1px solid #ccc;"></div>
  <input id="input" type="text" placeholder="Ask about your business..." />
  <button onclick="sendMessage()">Send</button>
</div>

<script>
async function sendMessage() {
  const input = document.getElementById('input');
  const message = input.value;
  
  const response = await fetch('http://your-server:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  
  const data = await response.json();
  document.getElementById('messages').innerHTML += `
    <p><strong>You:</strong> ${message}</p>
    <p><strong>Router:</strong> ${data.response}</p>
  `;
  input.value = '';
}
</script>
```

## 📊 Project Structure

```
CrewProject/
├── agents/
│   ├── router_agent.py       ← Smart chatbot (uses Gemini)
│   ├── website_agent.py      ← Dev team (ready to extend)
│   └── marketing_agent.py    ← Marketing team (ready to extend)
├── llm/
│   ├── gemini_llm.py         ← Gemini API wrapper ⭐
│   └── fake_llm.py           ← Offline fallback
├── server.py                 ← FastAPI endpoint
├── main.py                   ← Entry point
├── .env                      ← Your API key goes here
└── requirements.txt          ← Dependencies
```

## 🔄 Switching LLMs

### Use Gemini (Current)
Already configured in `agents/router_agent.py`

### Use Offline Mode (No API)
Edit `agents/router_agent.py`:
```python
from llm.fake_llm import FakeLLMWrapper
llm = FakeLLMWrapper()  # Change this line
```

## 🚀 Next Steps

1. **Add your Gemini API key** to `.env`
2. **Test:** `python main.py chat`
3. **Deploy:** Use Heroku, Railway, or Render
4. **Extend:** Add more agents (Finance, HR, Sales)
5. **Scale:** Build web frontend

## 📚 Resources

- Gemini API: https://ai.google.dev/docs
- CrewAI Docs: https://docs.crewai.com/
- FastAPI Docs: https://fastapi.tiangolo.com/

---

**Your AI company builder with Gemini is ready to serve!** 🎉

Questions? Check `.env.example` or README.md
