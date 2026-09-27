"""
FastAPI backend for human interview web interface.
Deployed as Vercel serverless function.
"""
import os
import uuid
import time
import json
import logging
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import redis

# Import from src (project root is two levels up: web/api/index.py -> project root)
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from web_interview.web_interrogation_env import WebInterrogationEnv
from picon.agents.agent_factory import get_agent
from picon.tools.web_search import SerperSearch, TavilySearch
from picon.tools.address_locator import GoogleGeocodeValidate
from picon.utils import write_json, upload_to_github 

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Human Interview API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (primary) + Redis backup for recovery
sessions: Dict[str, WebInterrogationEnv] = {}

# Redis connection (optional - gracefully degrade if not available)
redis_client: Optional[redis.Redis] = None
REDIS_SESSION_TTL = 7200  # 2 hours

def get_redis_client() -> Optional[redis.Redis]:
    """Get or create Redis client."""
    global redis_client
    if redis_client is not None:
        return redis_client
    
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        logger.warning("REDIS_URL not set - session recovery disabled")
        return None
    
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()  # Test connection
        logger.info("Redis connected successfully")
        return redis_client
    except Exception as e:
        logger.warning(f"Redis connection failed: {e} - session recovery disabled")
        return None

def save_session_to_redis(session_id: str, env: WebInterrogationEnv) -> bool:
    """Save session state to Redis. Returns True on success."""
    client = get_redis_client()
    if not client:
        return False
    
    try:
        data = env.serialize_for_redis()
        client.setex(f"session:{session_id}", REDIS_SESSION_TTL, json.dumps(data))
        logger.info(f"[REDIS] Saved session {session_id} (phase={data['current_phase']}, turn={data['state_current_turn']})")
        return True
    except Exception as e:
        logger.warning(f"[REDIS] Failed to save session {session_id}: {e}")
        return False

def restore_session_from_redis(session_id: str) -> Optional[WebInterrogationEnv]:
    """Restore session from Redis. Returns None if not found or failed."""
    client = get_redis_client()
    if not client:
        return None
    
    try:
        data_str = client.get(f"session:{session_id}")
        if not data_str:
            return None
        
        data = json.loads(data_str)
        
        # Create new env with same name
        env = create_env(data["name"])
        env.restore_from_redis(data)
        
        logger.info(f"[REDIS] Restored session {session_id}")
        return env
    except Exception as e:
        logger.warning(f"[REDIS] Failed to restore session {session_id}: {e}")
        return None

def delete_session_from_redis(session_id: str) -> bool:
    """Delete session from Redis. Returns True on success."""
    client = get_redis_client()
    if not client:
        return False
    
    try:
        client.delete(f"session:{session_id}")
        logger.info(f"[REDIS] Deleted session {session_id}")
        return True
    except Exception as e:
        logger.warning(f"[REDIS] Failed to delete session {session_id}: {e}")
        return False

# Fixed parameters for human interview
Q_MODEL = "azure/gpt-5"
W_MODEL = "azure/gpt-5"
E_MODEL = "azure/gpt-5.1"
NHD_MODEL = "azure/gpt-5-nano"
NUM_TURNS = 40
NUM_SESSIONS = 1

# Request/Response models
class StartInterviewRequest(BaseModel):
    name: str
    question_seed: Optional[int] = 42

class StartInterviewResponse(BaseModel):
    session_id: str
    instruction: str
    first_question: str
    phase: str
    progress: dict

class RespondRequest(BaseModel):
    session_id: str
    response: str
    is_confirmation: Optional[bool] = False

class RespondResponse(BaseModel):
    next_question: Optional[str]
    phase: str
    progress: dict
    is_complete: bool
    confirmation_question: Optional[str] = None

class ResultsResponse(BaseModel):
    session_id: str
    results: dict

class ConversationMessage(BaseModel):
    question: str
    answer: str

class RecoverResponse(BaseModel):
    session_id: str
    recovered: bool
    current_question: Optional[str] = None
    phase: str
    progress: dict
    is_complete: bool = False
    message: str
    conversation_history: list[ConversationMessage] = []
    name: Optional[str] = None


def extract_conversation_history(env: WebInterrogationEnv, exclude_incomplete_turn: bool = True) -> list[dict]:
    """
    Extract Q&A pairs from environment state history.
    
    Args:
        env: The interview environment
        exclude_incomplete_turn: If True and there are pending confirmations,
            exclude the last turn since it's incomplete (user needs to re-answer)
    """
    history = []
    turns_to_process = env.state.history
    
    # If there are pending confirmations, the current turn is incomplete
    # Exclude it so user doesn't see duplicate Q&A
    if exclude_incomplete_turn and env.pending_confirmations:
        turns_to_process = env.state.history[:-1] if env.state.history else []
    
    for turn in turns_to_process:
        # Each turn has environment_observation which may contain interviewee responses
        for obs in turn.environment_observation:
            if obs.observation_type == "interviewee_response" and obs.response:
                history.append({
                    "question": obs.response.question,
                    "answer": obs.response.content
                })
    return history


def create_env(name: str, question_seed: int = 42) -> WebInterrogationEnv:
    """Create a new WebInterrogationEnv with fixed parameters."""
    tools = {
        "serper_search": SerperSearch(api_key=os.getenv('SERPER_API_KEY')),
        # "tavily_search": TavilySearch(api_key=os.getenv('TAVILY_API_KEY')),
        "google_geocode_validate": GoogleGeocodeValidate(
            api_key=os.getenv('GOOGLE_GEOCODE')
        )
    }
    
    agents = {
        "questioner": get_agent("questioner", f"{project_root}/src/agents/prompts/questioner.txt", model=Q_MODEL),
        "extractor": get_agent("entity_extractor", f"{project_root}/src/agents/prompts/entity_extractor.txt", model=E_MODEL),
        "web_search": get_agent("web_search", f"{project_root}/src/agents/prompts/websearch_prompt.txt", model=W_MODEL),
        "evaluator": get_agent("evaluator", f"{project_root}/src/agents/prompts/evaluator_prompt.txt", model=E_MODEL),
    }
    
    env = WebInterrogationEnv(
        questioner_model=Q_MODEL,
        web_search_model=W_MODEL,
        extractor_model=E_MODEL,
        evaluator_model=E_MODEL,
        agents=agents,
        tools=tools,
        max_turns=NUM_TURNS,
        baseline_name="human_interview",
        name=name,
        nhd_model=NHD_MODEL,
        question_seed=question_seed,
        question_path=f"{project_root}/src/env/wvs_orthogonal_questions.json",
        instruction_path=f"{project_root}/src/env/interrogation_instruct.txt"
    )
    
    return env


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": time.time()}


@app.post("/api/start", response_model=StartInterviewResponse)
def start_interview(request: StartInterviewRequest):
    """Start a new interview session."""
    try:
        session_id = str(uuid.uuid4())
        env = create_env(request.name, request.question_seed)
        
        # Initialize the interview
        instruction, first_question = env.initialize()
        
        sessions[session_id] = env
        
        # Save initial state to Redis for recovery
        save_session_to_redis(session_id, env)
        
        return StartInterviewResponse(
            session_id=session_id,
            instruction=instruction,
            first_question=first_question,
            phase=env.current_phase,
            progress=env.get_progress()
        )
    except Exception as e:
        logger.exception(f"Error starting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/respond", response_model=RespondResponse)
def submit_response(request: RespondRequest):
    """Submit a response and get the next question."""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        env = sessions[request.session_id]
        
        # Process response and get next question
        result = env.process_response(request.response, is_confirmation=request.is_confirmation)
        
        # Save to Redis after complete turns (when returning next_question, not confirmation_question)
        # A turn is complete when: next_question is set OR is_complete is True
        is_turn_complete = result.get("next_question") is not None or result.get("is_complete", False)
        if is_turn_complete:
            save_session_to_redis(request.session_id, env)
        
        return RespondResponse(
            next_question=result.get("next_question"),
            phase=result.get("phase", env.current_phase),
            progress=result.get("progress", env.get_progress()),
            is_complete=result.get("is_complete", False),
            confirmation_question=result.get("confirmation_question")
        )
    except Exception as e:
        logger.exception(f"Error processing response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/results/{session_id}", response_model=ResultsResponse)
def get_results(session_id: str):
    """Get the final results for a completed interview (without evaluation phase)."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found. It may have already been processed.")
    
    env = None
    try:
        env = sessions[session_id]
        
        if not env.is_complete:
            raise HTTPException(status_code=400, detail="Interview not yet complete")
        
        # Save state (without running evaluation to avoid LLM API issues)
        logger.info(f"[{session_id}] Starting save_state...")
        results = env.save_state()
        logger.info(f"[{session_id}] save_state completed.")
        
        # Save to file - do this BEFORE preparing response
        result_path = f"interview_results/human_interview/{env.interviewee.name.replace(' ', '_')}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.json"
        logger.info(f"[{session_id}] Uploading to GitHub: {result_path}")
        upload_to_github(result_path, results)
        logger.info(f"[{session_id}] Upload successful.")
        
        # Prepare response BEFORE deleting session
        response = ResultsResponse(session_id=session_id, results=results)
        
        # Clean up session from memory and Redis
        del sessions[session_id]
        delete_session_from_redis(session_id)
        logger.info(f"[{session_id}] Session cleaned up, returning response.")
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[{session_id}] Error getting results: {e}")
        # If upload succeeded but we failed later, still try to clean up
        if session_id in sessions:
            try:
                del sessions[session_id]
                delete_session_from_redis(session_id)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing results: {str(e)}")


@app.get("/api/recover/{session_id}", response_model=RecoverResponse)
def recover_session(session_id: str):
    """Attempt to recover a session from Redis backup."""
    # Check if already in memory
    if session_id in sessions:
        env = sessions[session_id]
        return RecoverResponse(
            session_id=session_id,
            recovered=True,
            current_question=env.pending_question,
            phase=env.current_phase,
            progress=env.get_progress(),
            is_complete=env.is_complete,
            message="Session found in memory",
            conversation_history=extract_conversation_history(env),
            name=env.interviewee.name
        )
    
    # Try to restore from Redis
    env = restore_session_from_redis(session_id)
    if env:
        sessions[session_id] = env
        return RecoverResponse(
            session_id=session_id,
            recovered=True,
            current_question=env.pending_question,
            phase=env.current_phase,
            progress=env.get_progress(),
            is_complete=env.is_complete,
            message=f"Session recovered from backup (turn {env.state.current_turn})",
            conversation_history=extract_conversation_history(env),
            name=env.interviewee.name
        )
    
    # Session not found
    return RecoverResponse(
        session_id=session_id,
        recovered=False,
        current_question=None,
        phase="unknown",
        progress={},
        is_complete=False,
        message="Session not found or expired",
        conversation_history=[],
        name=None
    )


@app.delete("/api/session/{session_id}")
def cancel_session(session_id: str):
    """Cancel and cleanup a session."""
    if session_id in sessions:
        env = sessions[session_id]
        # Save partial results
        try:
            results = env.save_state(termination_status="Cancelled by user")
            result_path = f"interview_results/human_interview/temp/{env.interviewee.name.replace(' ', '_')}_cancelled_{time.strftime('%Y-%m-%d_%H-%M-%S')}.json"
            # write_json(results, result_path)
            upload_to_github(result_path, results)
        except Exception as e:
            logger.warning(f"Could not save partial results: {e}")
        del sessions[session_id]
    
    # Also delete from Redis
    delete_session_from_redis(session_id)
    
    return {"status": "ok"}
