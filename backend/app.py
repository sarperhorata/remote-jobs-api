"""
Main FastAPI application entry point.
This file imports the app from main.py to maintain compatibility.
"""

from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 