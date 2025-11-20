"""
Simple HTTP server to serve the website locally.
This serves index.html on http://localhost:5000
The FastAPI server (port 8000) handles the /chat API calls.
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# Change to project directory
os.chdir(Path(__file__).parent)

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for API calls
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        return super().do_GET()

if __name__ == '__main__':
    port = 5000
    server = HTTPServer(('localhost', port), MyHTTPRequestHandler)
    print(f"""
╔════════════════════════════════════════════════════════════╗
║         🌐 AI COMPANY BUILDER - WEBSITE SERVER            ║
╚════════════════════════════════════════════════════════════╝

✅ Website running on: http://localhost:{port}
✅ Open in browser: http://localhost:{port}

📊 Server Details:
  • Website: http://localhost:{port}
  • API: http://localhost:8000 (run: python main.py server)

⚙️ How to Use:
  1. Keep this server running
  2. In another terminal: python main.py server
  3. Open http://localhost:{port} in your browser
  4. Start chatting!

🛑 Stop server: Press Ctrl+C

════════════════════════════════════════════════════════════════
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped.")
        sys.exit(0)
