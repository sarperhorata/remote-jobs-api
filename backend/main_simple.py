from fastapi import FastAPI

app = FastAPI(title="Buzz2Remote API - Simple Test")

@app.get("/")
async def root():
    return {"message": "Hello from Render!", "status": "working"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "buzz2remote-api"}

@app.get("/test")
async def test():
    return {"test": "success", "deployed": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 