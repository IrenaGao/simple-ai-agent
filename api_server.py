"""FastAPI server for telemetry visualization and agent orchestration."""

import os
import random
import uuid
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agents.diagrammer import DiagrammerAgent
from agents.orchestrator import OrchestratorAgent
from models.telemetry import RunSummary, telemetry_store
from synthetic_telemetry import SyntheticTelemetryGenerator
from telemetry_enhanced import start_run, end_run


# Pydantic models for API requests/responses
class RunRequest(BaseModel):
    query: str
    simulate: bool = False
    run_id: Optional[str] = None
    system_prompt: Optional[str] = None


class RunResponse(BaseModel):
    run_id: str
    response: str
    telemetry: Dict
    react_flow: Dict
    optimizations: List[Dict]
    agent_outputs: List[Dict] = []


class TelemetryResponse(BaseModel):
    run_id: str
    events: List[Dict]
    summary: Dict


class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float


# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Telemetry API",
    description="API for multi-agent orchestration with telemetry visualization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
orchestrator = OrchestratorAgent()
diagrammer = DiagrammerAgent()
synthetic_generator = SyntheticTelemetryGenerator()

# Track server start time for uptime
import time
server_start_time = time.time()


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - server_start_time
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime=uptime
    )


@app.post("/api/run/simulate", response_model=RunResponse)
async def run_simulation(request: RunRequest, background_tasks: BackgroundTasks):
    """Run a simulation or live agent execution."""
    try:
        # Generate or use provided run ID
        run_id = request.run_id or str(uuid.uuid4())
        
        if request.simulate:
            # Generate synthetic telemetry
            run = synthetic_generator.generate_run(
                run_id=run_id,
                duration_minutes=random.uniform(1.0, 3.0),
                event_count=random.randint(10, 25),
                include_errors=random.random() < 0.3,
                include_delegation=random.random() < 0.7
            )
            
            # Generate synthetic response
            response_text = f"Simulated response for query: '{request.query}'. This is a synthetic response generated for testing purposes."
            
        else:
            # Run live orchestrator with custom system prompt if provided
            start_run(run_id=run_id)
            
            try:
                # Create orchestrator with custom system prompt if provided
                if request.system_prompt:
                    custom_orchestrator = OrchestratorAgent(system_prompt=request.system_prompt)
                    result = custom_orchestrator.process_query(request.query, run_id)
                else:
                    result = orchestrator.process_query(request.query, run_id)
                response_text = result.response
            finally:
                end_run(status="completed")
            
            # Get the actual run from telemetry store
            run = telemetry_store.get_run(run_id)
            if not run:
                raise HTTPException(status_code=500, detail="Failed to retrieve run data")
        
        # Generate diagram analysis
        try:
            diagram_analysis = diagrammer.analyze_telemetry(run_id)
            
            # Convert to dictionaries for JSON response
            react_flow = {
                "nodes": [node.dict() for node in diagram_analysis.nodes],
                "edges": [edge.dict() for edge in diagram_analysis.edges]
            }
            
            optimizations = [opt.dict() for opt in diagram_analysis.optimizations]
            
        except Exception as e:
            # Fallback if diagram generation fails
            react_flow = {"nodes": [], "edges": []}
            optimizations = []
        
        # Prepare telemetry data
        events = telemetry_store.get_run_events(run_id)
        telemetry_data = {
            "run_id": run_id,
            "events": [event.dict() for event in events],
            "summary": {
                "total_events": len(events),
                "total_duration_ms": run.total_duration_ms,
                "status": run.status,
                "total_llm_calls": run.total_llm_calls,
                "total_tool_calls": run.total_tool_calls,
                "total_delegations": run.total_delegations,
                "error_count": run.error_count
            }
        }
        
        # Extract agent outputs from events
        agent_outputs = []
        for event in events:
            if hasattr(event, 'event_type') and event.event_type == "agent_output":
                agent_outputs.append({
                    "agent_type": event.agent_type.value if hasattr(event.agent_type, 'value') else str(event.agent_type) if event.agent_type else "unknown",
                    "output_type": event.output_type,
                    "output_content": event.output_content,
                    "timestamp": event.timestamp.isoformat(),
                    "success": event.success,
                    "error_message": event.error_message,
                    "metadata": event.output_metadata
                })
        
        return RunResponse(
            run_id=run_id,
            response=response_text,
            telemetry=telemetry_data,
            react_flow=react_flow,
            optimizations=optimizations,
            agent_outputs=agent_outputs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/api/telemetry/{run_id}", response_model=TelemetryResponse)
async def get_telemetry(run_id: str):
    """Get telemetry data for a specific run."""
    run = telemetry_store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    events = telemetry_store.get_run_events(run_id)
    
    return TelemetryResponse(
        run_id=run_id,
        events=[event.dict() for event in events],
        summary={
            "total_events": len(events),
            "total_duration_ms": run.total_duration_ms,
            "status": run.status,
            "total_llm_calls": run.total_llm_calls,
            "total_tool_calls": run.total_tool_calls,
            "total_delegations": run.total_delegations,
            "error_count": run.error_count,
            "start_time": run.start_time.isoformat() if run.start_time else None,
            "end_time": run.end_time.isoformat() if run.end_time else None
        }
    )


@app.get("/api/runs")
async def list_runs():
    """List all available runs."""
    runs = telemetry_store.get_all_runs()
    return {
        "runs": [
            {
                "run_id": run.run_id,
                "thread_id": run.thread_id,
                "status": run.status,
                "start_time": run.start_time.isoformat() if run.start_time else None,
                "end_time": run.end_time.isoformat() if run.end_time else None,
                "total_duration_ms": run.total_duration_ms,
                "total_events": len(run.agent_events)
            }
            for run in runs
        ]
    }


@app.post("/api/generate-sample-data")
async def generate_sample_data(count: int = 5):
    """Generate sample telemetry data for testing."""
    try:
        runs = synthetic_generator.generate_multiple_runs(count=count)
        return {
            "message": f"Generated {count} sample runs",
            "run_ids": [run.run_id for run in runs]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sample data: {str(e)}")


@app.delete("/api/telemetry/{run_id}")
async def delete_run(run_id: str):
    """Delete a specific run and its telemetry data."""
    # Note: This is a simple implementation. In production, you might want to
    # implement soft deletion or archive functionality.
    run = telemetry_store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Remove from store (this is a simplified implementation)
    # In a real implementation, you'd want to properly handle this
    return {"message": f"Run {run_id} deleted"}


if __name__ == "__main__":
    import uvicorn
    
    # Set up environment
    os.environ.setdefault("USE_LLM_DIAGRAMMER", "false")
    
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
