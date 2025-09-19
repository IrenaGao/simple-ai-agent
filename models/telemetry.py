"""Structured telemetry models for multi-agent orchestration."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of telemetry events."""
    RUN_START = "run_start"
    RUN_END = "run_end"
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    LLM_CALL = "llm_call"
    TOOL_CALL = "tool_call"
    DELEGATION = "delegation"
    STEP_LOG = "step_log"
    AGENT_OUTPUT = "agent_output"


class AgentType(str, Enum):
    """Types of agents in the system."""
    ORCHESTRATOR = "orchestrator"  # Agent A
    SUMMARIZER = "summarizer"      # Agent B
    DIAGRAMMER = "diagrammer"      # Agent D


class TelemetryEvent(BaseModel):
    """Base telemetry event model."""
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    run_id: str
    thread_id: Optional[str] = None
    agent_type: Optional[AgentType] = None
    step_name: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class LLMCallEvent(TelemetryEvent):
    """Telemetry event for LLM calls."""
    event_type: EventType = EventType.LLM_CALL
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    temperature: Optional[float] = None
    response_time_ms: Optional[float] = None


class ToolCallEvent(TelemetryEvent):
    """Telemetry event for tool calls."""
    event_type: EventType = EventType.TOOL_CALL
    tool_name: str
    tool_input: Dict[str, Any] = Field(default_factory=dict)
    tool_output: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None


class DelegationEvent(TelemetryEvent):
    """Telemetry event for agent delegation."""
    event_type: EventType = EventType.DELEGATION
    from_agent: AgentType
    to_agent: AgentType
    delegation_reason: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None


class StepLogEvent(TelemetryEvent):
    """Telemetry event for step logging."""
    event_type: EventType = EventType.STEP_LOG
    step_description: str
    step_data: Dict[str, Any] = Field(default_factory=dict)


class AgentOutputEvent(TelemetryEvent):
    """Telemetry event for agent outputs."""
    event_type: EventType = EventType.AGENT_OUTPUT
    output_type: str  # response, summary, diagram, etc.
    output_content: str
    output_metadata: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None


class RunSummary(BaseModel):
    """Summary of a complete run."""
    run_id: str
    thread_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # running, completed, failed
    total_duration_ms: Optional[float] = None
    agent_events: List[TelemetryEvent] = Field(default_factory=list)
    total_llm_calls: int = 0
    total_tool_calls: int = 0
    total_delegations: int = 0
    error_count: int = 0


class ReactFlowNode(BaseModel):
    """React Flow node representation."""
    id: str
    type: str = "default"
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0})
    data: Dict[str, Any] = Field(default_factory=dict)
    style: Dict[str, Any] = Field(default_factory=dict)


class ReactFlowEdge(BaseModel):
    """React Flow edge representation."""
    id: str
    source: str
    target: str
    type: str = "default"
    data: Dict[str, Any] = Field(default_factory=dict)
    style: Dict[str, Any] = Field(default_factory=dict)


class OptimizationPoint(BaseModel):
    """Optimization suggestion."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    category: str  # performance, cost, reliability, etc.
    severity: str  # low, medium, high, critical
    title: str
    description: str
    suggestion: str
    impact_estimate: Optional[str] = None


class DiagramAnalysis(BaseModel):
    """Complete diagram analysis result."""
    nodes: List[ReactFlowNode]
    edges: List[ReactFlowEdge]
    optimizations: List[OptimizationPoint]
    summary: str
    total_events: int
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class TelemetryStore:
    """In-memory telemetry store."""
    
    def __init__(self):
        self._runs: Dict[str, RunSummary] = {}
        self._events: List[TelemetryEvent] = []
    
    def start_run(self, run_id: str, thread_id: Optional[str] = None) -> RunSummary:
        """Start a new run."""
        run = RunSummary(
            run_id=run_id,
            thread_id=thread_id,
            start_time=datetime.utcnow()
        )
        self._runs[run_id] = run
        return run
    
    def end_run(self, run_id: str, status: str = "completed") -> Optional[RunSummary]:
        """End a run."""
        if run_id not in self._runs:
            return None
        
        run = self._runs[run_id]
        run.end_time = datetime.utcnow()
        run.status = status
        if run.start_time:
            run.total_duration_ms = (run.end_time - run.start_time).total_seconds() * 1000
        
        return run
    
    def add_event(self, event: TelemetryEvent) -> None:
        """Add a telemetry event."""
        self._events.append(event)
        
        # Update run summary if it exists
        if event.run_id in self._runs:
            run = self._runs[event.run_id]
            run.agent_events.append(event)
            
            # Update counters
            if event.event_type == EventType.LLM_CALL:
                run.total_llm_calls += 1
            elif event.event_type == EventType.TOOL_CALL:
                run.total_tool_calls += 1
            elif event.event_type == EventType.DELEGATION:
                run.total_delegations += 1
            
            if hasattr(event, 'success') and not event.success:
                run.error_count += 1
    
    def get_run(self, run_id: str) -> Optional[RunSummary]:
        """Get a run by ID."""
        return self._runs.get(run_id)
    
    def get_run_events(self, run_id: str) -> List[TelemetryEvent]:
        """Get all events for a run."""
        return [event for event in self._events if event.run_id == run_id]
    
    def get_all_runs(self) -> List[RunSummary]:
        """Get all runs."""
        return list(self._runs.values())
    
    def clear(self) -> None:
        """Clear all data."""
        self._runs.clear()
        self._events.clear()


# Global telemetry store instance
telemetry_store = TelemetryStore()
