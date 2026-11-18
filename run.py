"""
run.py
Application bootstrapper for AeroFamily Smog & Clean Air AI Guardian.
Loads runtime environment configuration and initializes the Uvicorn ASGI server.
"""

import sys
import os
import uvicorn
from core.config import settings

if __name__ == "__main__":
    # Ensure current working directory is the project directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print("=" * 65)
    print(f"  🛡️  {settings.APP_NAME}")
    print(f"  Version:     {settings.APP_VERSION}")
    print("=" * 65)
    print(f"  Web Dashboard: http://{settings.HOST}:{settings.PORT}")
    print(f"  API Docs:      http://{settings.HOST}:{settings.PORT}/docs")
    print(f"  ReDoc:         http://{settings.HOST}:{settings.PORT}/redoc")
    print("=" * 65)

    uvicorn.run(
        "server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
