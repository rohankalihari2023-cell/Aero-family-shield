import uvicorn
import sys
import os

if __name__ == "__main__":
    # Ensure working directory is this file's folder
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("=" * 65)
    print("  🛡️  AeroFamily - Smog & Clean Air AI Guardian")
    print("=" * 65)
    print("  Web App URL: http://localhost:8000")
    print("  API Docs:    http://localhost:8000/docs")
    print("=" * 65)
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
