#api/main.py
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid
import os
import json
from typing import Optional

from main_pipeline import ParallelFoundrScanPipeline
from agents.idea_agent import StartupIdeaAnalyzer

# In-memory job store for demo (use Redis/DB in production)
jobs = {}
sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    done: bool = False

class AnalysisRequest(BaseModel):
    startup_data: dict

class SummaryRequest(BaseModel):
    session_id: str

class SummaryResponse(BaseModel):
    summary: dict
    session_id: str

app = FastAPI()

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    if session_id not in sessions:
        analyzer = StartupIdeaAnalyzer()
        user_idea = req.message
        conversation = f"System: {analyzer._get_system_prompt()}\nUser: My startup idea: {user_idea}\n"
        # First response
        response = analyzer.query_model(
            "Continue this conversation about a startup idea. Ask ONE specific follow-up question about their business. Be brief and conversational. Only say you're ready to summarize if you have enough key information.",
            conversation
        )
        conversation += f"Assistant: {response}\n"
        ready = "✅ I'm ready to summarize" in response
        sessions[session_id] = {
            "conversation": conversation,
            "analyzer": analyzer,
            "ready": ready,
            "user_idea": user_idea,
            "turn_count": 1
        }
        return ChatResponse(
            response=response,
            session_id=session_id,
            done=ready
        )
    else:
        session = sessions[session_id]
        analyzer = session["analyzer"]
        conversation = session["conversation"]
        user_reply = req.message
        # Add user reply to conversation
        conversation += f"User: {user_reply}\n"
        # Get response with full conversation context
        response = analyzer.query_model(
            "Continue this conversation about a startup idea. Ask ONE specific follow-up question about their business. Be brief and conversational. Only say you're ready to summarize if you have enough key information.",
            conversation
        )
        conversation += f"Assistant: {response}\n"
        ready = "✅ I'm ready to summarize" in response
        # Update session with new conversation
        session["conversation"] = conversation
        session["ready"] = ready
        session["turn_count"] = session.get("turn_count", 0) + 1
        return ChatResponse(
            response=response,
            session_id=session_id,
            done=ready
        )
@app.post("/api/chat/summary", response_model=SummaryResponse)
def get_chat_summary(req: SummaryRequest):
    """Generate summary from completed chat session"""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.get("ready", False):
        raise HTTPException(status_code=400, detail="Chat session not ready for summary")
    
    analyzer = session["analyzer"]
    user_idea = session["user_idea"]
    conversation = session["conversation"]
    
    try:
        # Use the analyzer's existing generate_summary method
        summary = analyzer.generate_summary(user_idea, conversation)
        
        # Convert to dict using the built-in method
        summary_dict = summary.to_dict()
        
        # Store summary in session for potential reuse
        sessions[req.session_id]["summary"] = summary_dict
        
        return SummaryResponse(
            summary=summary_dict,
            session_id=req.session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@app.post("/api/analysis/start")
def start_analysis(req: AnalysisRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending"}
    background_tasks.add_task(run_analysis_job, job_id, req.startup_data)
    return {"job_id": job_id}

@app.post("/api/analysis/start_from_session")
def start_analysis_from_session(req: SummaryRequest, background_tasks: BackgroundTasks):
    """Start analysis directly from a chat session"""
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.get("ready", False):
        raise HTTPException(status_code=400, detail="Chat session not ready for analysis")
    
    # Generate summary if not already done
    if "summary" not in session:
        analyzer = session["analyzer"]
        user_idea = session["user_idea"]
        conversation = session["conversation"]
        summary = analyzer.generate_summary(user_idea, conversation)
        session["summary"] = summary.to_dict()
    
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending", "session_id": req.session_id}
    
    # Run analysis with the session summary
    background_tasks.add_task(run_analysis_job, job_id, session["summary"])
    return {"job_id": job_id}

@app.get("/api/analysis/{job_id}/status")
def get_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": job["status"]}

@app.get("/api/analysis/{job_id}/result")
def get_result(job_id: str):
    job = jobs.get(job_id)
    if not job or job["status"] != "complete":
        raise HTTPException(status_code=404, detail="Result not ready")
    return {"result": job["result"]}

@app.get("/api/sessions/{session_id}")
def get_session_info(session_id: str):
    """Get session information for debugging"""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "ready": session.get("ready", False),
        "turn_count": session.get("turn_count", 0),
        "user_idea": session.get("user_idea", ""),
        "has_summary": "summary" in session
    }

@app.delete("/api/sessions/{session_id}")
def clear_session(session_id: str):
    """Clear a session"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

def run_analysis_job(job_id, startup_data):
    pipeline = ParallelFoundrScanPipeline()
    try: 
        result = pipeline.run_pipeline(startup_data)
        jobs[job_id] = {"status": "complete", "result": result}
    except Exception as e:
        jobs[job_id] = {"status": "error", "error": str(e)}
        print(f"Analysis job {job_id} failed: {str(e)}")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "active_sessions": len(sessions), "active_jobs": len(jobs)}