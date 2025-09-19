"""Enhanced telemetry utilities for multi-agent orchestration."""

import functools
import logging
import time
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from models.telemetry import (
    AgentOutputEvent, AgentType, DelegationEvent, LLMCallEvent, StepLogEvent, 
    TelemetryEvent, ToolCallEvent, telemetry_store
)

# Context variables for tracking current run and thread
run_id_var = ContextVar("run_id", default=None)
thread_id_var = ContextVar("thread_id", default=None)
current_agent_var = ContextVar("current_agent", default=None)

logger = logging.getLogger(__name__)


def start_run(run_id: Optional[str] = None, thread_id: Optional[str] = None) -> str:
    """Start a new telemetry run."""
    if run_id is None:
        run_id = str(uuid.uuid4())
    
    run_id_var.set(run_id)
    if thread_id:
        thread_id_var.set(thread_id)
    
    # Create run in telemetry store
    telemetry_store.start_run(run_id, thread_id)
    
    # Log run start
    logger.info(f"Started run {run_id}", extra={"run_id": run_id, "thread_id": thread_id})
    
    return run_id


def end_run(status: str = "completed", **kwargs) -> None:
    """End the current telemetry run."""
    run_id = run_id_var.get()
    if run_id:
        telemetry_store.end_run(run_id, status)
        logger.info(f"Ended run {run_id} with status {status}", extra={"run_id": run_id, **kwargs})


def set_current_agent(agent_type: AgentType) -> None:
    """Set the current agent type for telemetry context."""
    current_agent_var.set(agent_type)


def log_step(step_name: str, description: str, data: Optional[Dict[str, Any]] = None) -> None:
    """Log a step in the current agent flow."""
    run_id = run_id_var.get()
    if not run_id:
        return
    
    event = StepLogEvent(
        run_id=run_id,
        thread_id=thread_id_var.get(),
        agent_type=current_agent_var.get(),
        step_name=step_name,
        step_description=description,
        step_data=data or {}
    )
    
    telemetry_store.add_event(event)
    logger.info(f"Step: {step_name} - {description}", extra={"run_id": run_id, "step_name": step_name})


def log_llm_call(
    model: str,
    prompt: str,
    response: str,
    duration_ms: float,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    **metadata
) -> None:
    """Log an LLM call."""
    run_id = run_id_var.get()
    if not run_id:
        return
    
    event = LLMCallEvent(
        run_id=run_id,
        thread_id=thread_id_var.get(),
        agent_type=current_agent_var.get(),
        step_name="llm_processing",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=(prompt_tokens or 0) + (completion_tokens or 0),
        temperature=temperature,
        response_time_ms=duration_ms,
        metadata={
            "prompt": prompt[:500] + "..." if len(prompt) > 500 else prompt,
            "response": response[:500] + "..." if len(response) > 500 else response,
            **metadata
        }
    )
    
    telemetry_store.add_event(event)
    logger.info(f"LLM call to {model} took {duration_ms:.1f}ms", extra={"run_id": run_id, "model": model})


def log_delegation(
    from_agent: AgentType,
    to_agent: AgentType,
    reason: str,
    input_data: Optional[Dict[str, Any]] = None,
    output_data: Optional[Dict[str, Any]] = None
) -> None:
    """Log agent delegation."""
    run_id = run_id_var.get()
    if not run_id:
        return
    
    event = DelegationEvent(
        run_id=run_id,
        thread_id=thread_id_var.get(),
        agent_type=from_agent,
        step_name="delegation_decision",
        from_agent=from_agent,
        to_agent=to_agent,
        delegation_reason=reason,
        input_data=input_data or {},
        output_data=output_data
    )
    
    telemetry_store.add_event(event)
    logger.info(f"Delegated from {from_agent} to {to_agent}: {reason}", extra={"run_id": run_id})


def log_agent_output(
    output_type: str,
    output_content: str,
    success: bool = True,
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Log an agent output."""
    run_id = run_id_var.get()
    if not run_id:
        return
    
    event = AgentOutputEvent(
        run_id=run_id,
        thread_id=thread_id_var.get(),
        agent_type=current_agent_var.get(),
        step_name=f"agent_{output_type}",
        output_type=output_type,
        output_content=output_content,
        output_metadata=metadata or {},
        success=success,
        error_message=error_message
    )
    
    telemetry_store.add_event(event)
    logger.info(f"Agent output: {output_type} - {'Success' if success else 'Failed'}", 
                extra={"run_id": run_id, "output_type": output_type})


def with_telemetry(
    tool_name: Optional[str] = None,
    agent_type: Optional[AgentType] = None
) -> Callable:
    """Enhanced decorator for tool telemetry with agent context."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            run_id = run_id_var.get()
            if not run_id:
                return func(*args, **kwargs)
            
            tool_name_final = tool_name or func.__name__
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000
                
                # Log successful tool call
                event = ToolCallEvent(
                    run_id=run_id,
                    thread_id=thread_id_var.get(),
                    agent_type=agent_type or current_agent_var.get(),
                    step_name=f"tool_{tool_name_final}",
                    tool_name=tool_name_final,
                    tool_input=_safe_repr_dict({"args": args, "kwargs": kwargs}),
                    tool_output=_safe_repr_dict({"result": result}),
                    success=True,
                    duration_ms=duration_ms
                )
                
                telemetry_store.add_event(event)
                logger.info(f"Tool {tool_name_final} succeeded in {duration_ms:.1f}ms", 
                           extra={"run_id": run_id, "tool_name": tool_name_final})
                
                return result
                
            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                
                # Log failed tool call
                event = ToolCallEvent(
                    run_id=run_id,
                    thread_id=thread_id_var.get(),
                    agent_type=agent_type or current_agent_var.get(),
                    step_name=f"tool_{tool_name_final}",
                    tool_name=tool_name_final,
                    tool_input=_safe_repr_dict({"args": args, "kwargs": kwargs}),
                    success=False,
                    error_message=str(e),
                    duration_ms=duration_ms
                )
                
                telemetry_store.add_event(event)
                logger.error(f"Tool {tool_name_final} failed in {duration_ms:.1f}ms: {e}", 
                            extra={"run_id": run_id, "tool_name": tool_name_final})
                
                raise
        
        return wrapper
    return decorator


def _safe_repr_dict(data: Dict[str, Any], max_length: int = 400) -> Dict[str, Any]:
    """Safely represent dictionary data for telemetry."""
    result = {}
    for key, value in data.items():
        try:
            repr_value = repr(value)
            if len(repr_value) > max_length:
                result[key] = repr_value[:max_length] + "..."
            else:
                result[key] = repr_value
        except Exception:
            result[key] = "<unrepr>"
    return result


def get_current_run_id() -> Optional[str]:
    """Get the current run ID."""
    return run_id_var.get()


def get_current_thread_id() -> Optional[str]:
    """Get the current thread ID."""
    return thread_id_var.get()


def get_current_agent() -> Optional[AgentType]:
    """Get the current agent type."""
    return current_agent_var.get()
