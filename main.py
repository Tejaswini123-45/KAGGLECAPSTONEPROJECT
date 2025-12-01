# main.py
import sys
import uvicorn

def start_server():
    print("Starting AI Company Builder API Server...")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

def main():
    print("AI Setup Completed\n")
    if len(sys.argv) > 1 and sys.argv[1] in ("server", "run"):
        start_server()
    else:
        print("Usage: python main.py server")

if __name__ == "__main__":
    main()
