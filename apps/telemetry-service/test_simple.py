#!/usr/bin/env python3
"""
Simple test script to run a minimal FastAPI app
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/test")
async def test():
    return {"message": "simple test works"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)
