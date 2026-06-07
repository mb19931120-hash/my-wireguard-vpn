"""
FastAPI server that exposes the CAP agent endpoint.
"""

import os
from fastapi import FastAPI, HTTPException
from cap_protocol import JobRequest, JobResponse
from agent import process_job

app = FastAPI(title="CAP AI Agent", description="Crypto Agent Protocol compatible agent")


@app.post("/job", response_model=JobResponse)
async def handle_job(job: JobRequest):
    """
    CAP‑compatible endpoint that receives a job, processes it after payment,
    and returns a signed response.
    """
    try:
        response = process_job(job)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Simple health check for the agent."""
    return {"status": "healthy", "cap_version": "1.0"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
