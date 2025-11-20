# AI Company Builder - Smart Router Chatbot

A smart chatbot powered by Google Gemini API that helps founders build their businesses.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install google-generativeai python-dotenv
```

### 2. Get Gemini API Key
- Go to https://ai.google.dev/
- Click "Get API Key"
- Create a new API key (free tier available)

### 3. Configure API Key
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-pro
```

### 4. Run the Chatbot Server
```bash
python main.py server
```

Server will start on `http://localhost:8000`

## 💬 Usage

### Via API (Postman / cURL)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to start a bakery business, how do I begin?"}'
```

### Response
```json
{
  "response": "Great! Starting a bakery is an exciting venture...",
  "status": "success"
}
```

### Interactive Chat
```bash
python main.py chat
```

Then type your questions:
```
You: I want to build a SaaS platform
Router: That's a great idea! To help you better...
```

## 📁 Project Structure

```
CrewProject/
├── agents/
│   ├── router_agent.py       (Smart chatbot - uses Gemini)
│   ├── website_agent.py      (Website/Dev tasks)
│   └── marketing_agent.py    (Marketing/Social)
├── llm/
│   ├── gemini_llm.py         (Gemini API wrapper)
│   └── fake_llm.py           (Offline fallback)
├── crew/
│   └── crew_definition.py    (Crew + tasks)
├── server.py                 (FastAPI endpoint)
├── main.py                   (Entry point)
├── .env                      (Config - ADD YOUR API KEY HERE)
└── .env.example              (Config template)
```

## 🎯 Features

✅ **Smart Routing** - Understands business ideas and routes to right agents
✅ **Friendly Chatbot** - Warm, professional communication
✅ **Cloud-Powered** - Uses Google Gemini for intelligence
✅ **API Ready** - POST `/chat` endpoint for web integration
✅ **Scalable** - Build up to Finance, HR, DevOps agents

## 📝 Commands

```bash
# Run crew workflow
python main.py

# Interactive chat
python main.py chat

# Start API server
python main.py server
```

## 🔧 Switching LLMs

### Use Offline Mode (No API Key)
Edit `agents/router_agent.py`:
```python
from llm.fake_llm import FakeLLMWrapper
llm = FakeLLMWrapper()
```

### Use Gemini (Default)
Already configured in `router_agent.py`:
```python
from llm.gemini_llm import GeminiLLM
llm = GeminiLLM()
```

## 🌐 Website Frontend Integration

To use this chatbot on a website:

```javascript
// Example: Send message to router chatbot
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Help me start a business' })
});

const data = await response.json();
console.log(data.response);
```

## 📊 Next Steps

1. Deploy to cloud (Heroku, Railway, Render)
2. Add Finance Agent (budgeting, funding)
3. Add HR Agent (hiring, payroll)
4. Add Sales Agent (lead generation, CRM)
5. Build web frontend

## 🤝 Support

For API key issues: https://ai.google.dev/
For CrewAI docs: https://docs.crewai.com/

---

**Your AI-powered company builder is ready!** 🎉
