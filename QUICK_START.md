# 🚀 Quick Start Guide - AI Company Builder

## Launch Instructions

The system has **3 separate components** that need to run. Here's how to use them:

### Step 1: Open Terminal 1 - Start the API Server
```bash
python main.py server
```
Or double-click: `server_run.bat`

**Expected Output:**
```
✅ API Server started on http://localhost:8000
```

### Step 2: Open Terminal 2 - Start the Web Server
```bash
python web_server.py
```
Or double-click: `web_run.bat`

**Expected Output:**
```
✅ Website running on: http://localhost:5000
```

### Step 3: Open Your Browser
Navigate to: **http://localhost:5000**

You should see the AI Company Builder chatbot interface!

---

## What Each Component Does

| Component | Port | Purpose | Command |
|-----------|------|---------|---------|
| **API Server** | 8000 | Processes chat requests | `python main.py server` |
| **Web Server** | 5000 | Serves website UI | `python web_server.py` |
| **Chatbot UI** | Browser | User interface | Open `http://localhost:5000` |

---

## Testing the System

### Quick Test - Without Web UI
```bash
python main.py chat
```
Runs an interactive REPL with the RouterAgent.

### Full Workflow Test
```bash
python main.py
```
Runs the complete crew workflow once.

---

## Troubleshooting

### "Connection refused" error in browser?
- Make sure API server is running: `python main.py server` (Terminal 1)
- Make sure web server is running: `python web_server.py` (Terminal 2)

### "GEMINI_API_KEY error"?
- Check `.env` file has your Gemini API key
- If no key, system falls back to FakeLLM (offline mode)

### Port already in use?
- Port 8000 taken? Edit `server.py` line with `uvicorn.run(..., port=8001)`
- Port 5000 taken? Edit `web_server.py` line with `port = 5001`

---

## File Locations

```
CrewProject/
├── main.py              ← Start here!
├── server.py            ← API endpoints
├── web_server.py        ← Website server
├── index.html           ← Chatbot UI
├── server_run.bat       ← Double-click to start API
├── web_run.bat          ← Double-click to start website
├── .env                 ← Your Gemini API key
└── README.md            ← Full documentation
```

---

## Pro Tips

💡 **Faster Development:** Keep all 3 terminals open side-by-side
💡 **Testing:** Use suggestion buttons ("Start SaaS", "Build website", etc.) 
💡 **Debug:** Check console errors in browser (F12 → Console tab)
💡 **Offline Mode:** System works without Gemini key using FakeLLM

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  Browser (localhost:5000)                │
│                   index.html - Chatbot UI                │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP Fetch
                     ▼
        ┌────────────────────────────┐
        │  Web Server (port 5000)    │
        │   Serves index.html        │
        └────────────────────────────┘

        ┌────────────────────────────┐
        │  API Server (port 8000)    │
        │  /chat endpoint (FastAPI)  │
        └────────────┬───────────────┘
                     │
        ┌────────────▼───────────────┐
        │    Router Agent (CEO)      │
        │   ├─ Website Agent         │
        │   ├─ Marketing Agent       │
        │   └─ More agents...        │
        └────────────┬───────────────┘
                     │
        ┌────────────▼───────────────┐
        │  LLM Strategy             │
        │  ├─ Gemini (if available) │
        │  └─ FakeLLM (fallback)    │
        └────────────────────────────┘
```

---

## System Components Status

✅ **Backend Agents** - Multi-agent crew with Router, Website, Marketing agents
✅ **FastAPI Server** - REST API with /chat endpoint
✅ **Website UI** - Professional chatbot interface with suggestions
✅ **Gemini Integration** - Cloud LLM with offline fallback
✅ **Error Handling** - Graceful degradation if services unavailable

---

**Ready to go!** 🎉

Questions? Check `README.md` or `SYSTEM_STATUS.txt` for more details.
