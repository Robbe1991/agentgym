"""
FastAPI Backend for AgentGym UI
Provides REST API endpoints and WebSocket support for real-time training updates.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import AgentGym components
# TODO: Enable these imports when integrating with actual AgentGym backend
# from agentgym.scenarios import ScenarioRegistry
# from agentgym.adapters.langchain_adapter import LangChainAdapter
# from agentgym.adapters.autogen_adapter import AutoGenAdapter
# from agentgym.adapters.crewai_adapter import CrewAIAdapter

# FastAPI app
app = FastAPI(
    title="AgentGym API",
    description="REST API and WebSocket interface for AgentGym training platform",
    version="1.0.0",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# Pydantic models
class FrameworkType(str, Enum):
    LANGCHAIN = "LangChain"
    AUTOGEN = "AutoGen"
    CREWAI = "CrewAI"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ScenarioResponse(BaseModel):
    id: str
    name: str
    description: str
    difficulty: DifficultyLevel
    duration: str
    rating: float
    tasks: int
    frameworks: List[str]
    metrics: List[str]
    features: List[str]

class TrainingSessionCreate(BaseModel):
    scenario_id: str
    framework: FrameworkType
    max_episodes: int = Field(default=200, ge=1, le=1000)
    learning_rate: float = Field(default=0.001, gt=0, le=1)

class TrainingSessionStatus(BaseModel):
    session_id: str
    scenario_id: str
    framework: str
    status: str  # "running", "paused", "completed", "failed"
    current_episode: int
    max_episodes: int
    accuracy: float
    avg_reward: float
    loss: float
    start_time: str
    elapsed_time: str

class ModelInfo(BaseModel):
    id: str
    name: str
    scenario: str
    framework: str
    accuracy: float
    episodes: int
    created_at: str
    size_mb: float

class SettingsUpdate(BaseModel):
    framework: Optional[str] = None
    llmProvider: Optional[str] = None
    maxEpisodes: Optional[int] = None
    learningRate: Optional[float] = None
    autoSave: Optional[bool] = None
    openaiKey: Optional[str] = None
    anthropicKey: Optional[str] = None

# In-memory storage (in production, use a database)
training_sessions: Dict[str, dict] = {}
models: List[dict] = []
settings: dict = {
    "framework": "LangChain",
    "llmProvider": "OpenAI",
    "maxEpisodes": 200,
    "learningRate": 0.001,
    "autoSave": True,
    "openaiKey": "",
    "anthropicKey": "",
}

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "AgentGym API",
        "version": "1.0.0",
        "endpoints": {
            "scenarios": "/api/scenarios",
            "training": "/api/training",
            "models": "/api/models",
            "settings": "/api/settings",
            "websocket": "/ws/training/{session_id}",
        },
    }

# Scenarios endpoints
@app.get("/api/scenarios", response_model=List[ScenarioResponse])
async def get_scenarios():
    """Get all available training scenarios"""
    scenarios_data = [
        {
            "id": "customer_support",
            "name": "Customer Support",
            "description": "Train agents to handle customer inquiries with high reliability. Focus on tool usage, escalation handling, and response quality.",
            "difficulty": DifficultyLevel.BEGINNER,
            "duration": "2-3 hours",
            "rating": 4.8,
            "tasks": 5,
            "frameworks": ["LangChain", "AutoGen", "CrewAI"],
            "metrics": ["Tool Reliability", "Response Quality", "Resolution Rate"],
            "features": ["5 sample customer issues", "8 support actions", "Real-time feedback"],
        },
        {
            "id": "code_review",
            "name": "Code Review",
            "description": "Train agents to perform thorough code reviews. Detect bugs, suggest improvements, and provide actionable feedback.",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "duration": "3-4 hours",
            "rating": 4.9,
            "tasks": 6,
            "frameworks": ["LangChain", "AutoGen", "CrewAI"],
            "metrics": ["Review Accuracy", "False Positive Rate", "Completeness"],
            "features": ["6 sample PRs", "11 review actions", "Severity-based rewards"],
        },
        {
            "id": "data_analysis",
            "name": "Data Analysis",
            "description": "Train agents to analyze data, generate insights, and create visualizations. Master statistical analysis and reporting.",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "duration": "3-4 hours",
            "rating": 4.7,
            "tasks": 6,
            "frameworks": ["LangChain", "AutoGen", "CrewAI"],
            "metrics": ["Analysis Accuracy", "Data Quality", "Insight Quality"],
            "features": ["6 analysis tasks", "15 analysis actions", "Visualization scoring"],
        },
    ]
    return scenarios_data

@app.get("/api/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(scenario_id: str):
    """Get details for a specific scenario"""
    scenarios = await get_scenarios()
    scenario = next((s for s in scenarios if s.id == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

# Training endpoints
@app.post("/api/training/start")
async def start_training(session: TrainingSessionCreate):
    """Start a new training session"""
    session_id = f"session_{len(training_sessions) + 1}_{datetime.now().timestamp()}"

    training_sessions[session_id] = {
        "session_id": session_id,
        "scenario_id": session.scenario_id,
        "framework": session.framework.value,
        "status": "running",
        "current_episode": 0,
        "max_episodes": session.max_episodes,
        "accuracy": 50.0,
        "avg_reward": 5.0,
        "loss": 2.5,
        "start_time": datetime.now().isoformat(),
        "elapsed_time": "0:00:00",
    }

    # Start background task to simulate training progress
    asyncio.create_task(simulate_training(session_id))

    return {"session_id": session_id, "status": "started"}

@app.get("/api/training/{session_id}", response_model=TrainingSessionStatus)
async def get_training_status(session_id: str):
    """Get status of a training session"""
    if session_id not in training_sessions:
        raise HTTPException(status_code=404, detail="Training session not found")
    return training_sessions[session_id]

@app.get("/api/training", response_model=List[TrainingSessionStatus])
async def get_all_training_sessions():
    """Get all training sessions"""
    return list(training_sessions.values())

@app.post("/api/training/{session_id}/pause")
async def pause_training(session_id: str):
    """Pause a training session"""
    if session_id not in training_sessions:
        raise HTTPException(status_code=404, detail="Training session not found")
    training_sessions[session_id]["status"] = "paused"
    return {"status": "paused"}

@app.post("/api/training/{session_id}/resume")
async def resume_training(session_id: str):
    """Resume a paused training session"""
    if session_id not in training_sessions:
        raise HTTPException(status_code=404, detail="Training session not found")
    training_sessions[session_id]["status"] = "running"
    asyncio.create_task(simulate_training(session_id))
    return {"status": "resumed"}

@app.post("/api/training/{session_id}/stop")
async def stop_training(session_id: str):
    """Stop a training session"""
    if session_id not in training_sessions:
        raise HTTPException(status_code=404, detail="Training session not found")
    training_sessions[session_id]["status"] = "completed"

    # Save as model
    models.append({
        "id": f"model_{len(models) + 1}",
        "name": f"{training_sessions[session_id]['scenario_id']}_model",
        "scenario": training_sessions[session_id]['scenario_id'],
        "framework": training_sessions[session_id]['framework'],
        "accuracy": training_sessions[session_id]['accuracy'],
        "episodes": training_sessions[session_id]['current_episode'],
        "created_at": datetime.now().isoformat(),
        "size_mb": 12.5,
    })

    return {"status": "stopped"}

# Models endpoints
@app.get("/api/models", response_model=List[ModelInfo])
async def get_models():
    """Get all trained models"""
    # Add some sample models if empty
    if not models:
        return [
            {
                "id": "model_1",
                "name": "customer_support_langchain",
                "scenario": "customer_support",
                "framework": "LangChain",
                "accuracy": 89.2,
                "episodes": 200,
                "created_at": "2024-01-15T10:30:00",
                "size_mb": 15.3,
            },
            {
                "id": "model_2",
                "name": "code_review_autogen",
                "scenario": "code_review",
                "framework": "AutoGen",
                "accuracy": 92.5,
                "episodes": 180,
                "created_at": "2024-01-14T14:20:00",
                "size_mb": 18.7,
            },
        ]
    return models

@app.get("/api/models/{model_id}", response_model=ModelInfo)
async def get_model(model_id: str):
    """Get details for a specific model"""
    model = next((m for m in models if m["id"] == model_id), None)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@app.delete("/api/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a trained model"""
    global models
    models = [m for m in models if m["id"] != model_id]
    return {"status": "deleted"}

# Settings endpoints
@app.get("/api/settings")
async def get_settings():
    """Get current settings"""
    return settings

@app.put("/api/settings")
async def update_settings(settings_update: SettingsUpdate):
    """Update settings"""
    for key, value in settings_update.dict(exclude_unset=True).items():
        if value is not None:
            settings[key] = value
    return settings

# WebSocket endpoint for real-time training updates
@app.websocket("/ws/training/{session_id}")
async def websocket_training(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time training updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send training updates
            if session_id in training_sessions:
                session_data = training_sessions[session_id]
                await websocket.send_json({
                    "type": "training_update",
                    "data": session_data,
                })
            await asyncio.sleep(1)  # Update every second
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task to simulate training progress
async def simulate_training(session_id: str):
    """Simulate training progress for demo purposes"""
    while session_id in training_sessions:
        session = training_sessions[session_id]

        if session["status"] != "running":
            await asyncio.sleep(1)
            continue

        if session["current_episode"] >= session["max_episodes"]:
            session["status"] = "completed"
            break

        # Update metrics
        session["current_episode"] += 1
        progress = session["current_episode"] / session["max_episodes"]

        session["accuracy"] = min(95, 50 + progress * 40 + (asyncio.get_event_loop().time() % 5))
        session["avg_reward"] = 5 + progress * 15 + (asyncio.get_event_loop().time() % 3)
        session["loss"] = max(0.1, 2.5 - progress * 2.3)

        # Calculate elapsed time
        start_time = datetime.fromisoformat(session["start_time"])
        elapsed = datetime.now() - start_time
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        session["elapsed_time"] = f"{hours}:{minutes:02d}:{seconds:02d}"

        # Broadcast update to all connected clients
        await manager.broadcast({
            "type": "training_update",
            "session_id": session_id,
            "data": session,
        })

        await asyncio.sleep(2)  # Update every 2 seconds

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
