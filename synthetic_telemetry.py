"""Synthetic telemetry generator for testing and simulation."""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from models.telemetry import (
    AgentType, DelegationEvent, EventType, LLMCallEvent, 
    RunSummary, StepLogEvent, TelemetryEvent, ToolCallEvent, telemetry_store
)


class SyntheticTelemetryGenerator:
    """Generates synthetic telemetry data for testing and simulation."""
    
    def __init__(self):
        self.agent_types = [AgentType.ORCHESTRATOR, AgentType.SUMMARIZER, AgentType.DIAGRAMMER]
        self.tool_names = ["search_kb", "analyze_content", "generate_summary", "create_diagram"]
        self.step_names = [
            "query_received", "planning", "kb_search", "delegation_decision",
            "llm_processing", "response_generation", "analysis_complete"
        ]
    
    def generate_run(
        self, 
        run_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        duration_minutes: float = 2.0,
        event_count: Optional[int] = None,
        include_errors: bool = True,
        include_delegation: bool = True
    ) -> RunSummary:
        """Generate a complete synthetic run with events."""
        if run_id is None:
            run_id = str(uuid.uuid4())
        
        # Start the run
        run = telemetry_store.start_run(run_id, thread_id)
        start_time = run.start_time
        
        # Generate events
        if event_count is None:
            event_count = random.randint(8, 20)
        
        events = self._generate_events(
            run_id, thread_id, start_time, duration_minutes, 
            event_count, include_errors, include_delegation
        )
        
        # Add events to store
        for event in events:
            telemetry_store.add_event(event)
        
        # End the run
        end_time = start_time + timedelta(minutes=duration_minutes)
        run.end_time = end_time
        run.status = "completed"
        run.total_duration_ms = duration_minutes * 60 * 1000
        
        # Update counters
        run.total_llm_calls = len([e for e in events if e.event_type == EventType.LLM_CALL])
        run.total_tool_calls = len([e for e in events if e.event_type == EventType.TOOL_CALL])
        run.total_delegations = len([e for e in events if e.event_type == EventType.DELEGATION])
        run.error_count = len([e for e in events if hasattr(e, 'success') and not e.success])
        run.agent_events = events
        
        return run
    
    def _generate_events(
        self,
        run_id: str,
        thread_id: Optional[str],
        start_time: datetime,
        duration_minutes: float,
        event_count: int,
        include_errors: bool,
        include_delegation: bool
    ) -> List[TelemetryEvent]:
        """Generate a list of synthetic events."""
        events = []
        current_time = start_time
        duration_seconds = duration_minutes * 60
        time_step = duration_seconds / event_count
        
        # Track current agent for delegation logic
        current_agent = AgentType.ORCHESTRATOR
        delegation_occurred = False
        
        for i in range(event_count):
            # Advance time
            current_time += timedelta(seconds=time_step + random.uniform(-time_step/2, time_step/2))
            
            # Determine event type
            event_type = self._choose_event_type(i, event_count, include_delegation, delegation_occurred)
            
            # Generate event based on type
            if event_type == EventType.RUN_START:
                continue  # Already handled
            elif event_type == EventType.AGENT_START:
                event = self._generate_agent_start_event(run_id, thread_id, current_time, current_agent)
            elif event_type == EventType.LLM_CALL:
                event = self._generate_llm_call_event(run_id, thread_id, current_time, current_agent)
            elif event_type == EventType.TOOL_CALL:
                event = self._generate_tool_call_event(run_id, thread_id, current_time, current_agent, include_errors)
            elif event_type == EventType.DELEGATION:
                event, new_agent = self._generate_delegation_event(run_id, thread_id, current_time, current_agent)
                current_agent = new_agent
                delegation_occurred = True
            elif event_type == EventType.STEP_LOG:
                event = self._generate_step_log_event(run_id, thread_id, current_time, current_agent)
            else:
                continue
            
            events.append(event)
        
        # Add run end event
        events.append(self._generate_run_end_event(run_id, thread_id, start_time + timedelta(minutes=duration_minutes)))
        
        return events
    
    def _choose_event_type(
        self, 
        event_index: int, 
        total_events: int, 
        include_delegation: bool,
        delegation_occurred: bool
    ) -> EventType:
        """Choose event type based on position in sequence and configuration."""
        # Early events are more likely to be planning and setup
        if event_index < total_events * 0.2:
            return random.choice([EventType.AGENT_START, EventType.STEP_LOG])
        
        # Middle events are the main processing
        elif event_index < total_events * 0.8:
            choices = [EventType.LLM_CALL, EventType.TOOL_CALL, EventType.STEP_LOG]
            if include_delegation and not delegation_occurred and event_index > total_events * 0.3:
                choices.append(EventType.DELEGATION)
            return random.choice(choices)
        
        # Late events are cleanup and finalization
        else:
            return random.choice([EventType.STEP_LOG, EventType.TOOL_CALL])
    
    def _generate_agent_start_event(
        self, 
        run_id: str, 
        thread_id: Optional[str], 
        timestamp: datetime, 
        agent_type: AgentType
    ) -> TelemetryEvent:
        """Generate agent start event."""
        return TelemetryEvent(
            event_type=EventType.AGENT_START,
            run_id=run_id,
            thread_id=thread_id,
            timestamp=timestamp,
            agent_type=agent_type,
            step_name="agent_initialization",
            metadata={"agent_version": "1.0.0", "environment": "production"}
        )
    
    def _generate_llm_call_event(
        self, 
        run_id: str, 
        thread_id: Optional[str], 
        timestamp: datetime, 
        agent_type: AgentType
    ) -> LLMCallEvent:
        """Generate LLM call event."""
        models = [
            "anthropic:claude-3-7-sonnet-latest", 
            "anthropic:claude-3-haiku-20240307", 
            "openai:gpt-4o",
            "anthropic:claude-3-5-sonnet-20241022",
            "openai:gpt-4-turbo"
        ]
        model = random.choice(models)
        
        prompt_tokens = random.randint(50, 500)
        completion_tokens = random.randint(20, 200)
        response_time = random.uniform(500, 3000)  # 0.5-3 seconds
        
        return LLMCallEvent(
            run_id=run_id,
            thread_id=thread_id,
            timestamp=timestamp,
            agent_type=agent_type,
            step_name="llm_processing",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            temperature=random.uniform(0.1, 0.9),
            response_time_ms=response_time,
            duration_ms=response_time,
            metadata={
                "prompt_length": prompt_tokens,
                "response_length": completion_tokens,
                "model_version": "latest"
            }
        )
    
    def _generate_tool_call_event(
        self, 
        run_id: str, 
        thread_id: Optional[str], 
        timestamp: datetime, 
        agent_type: AgentType,
        include_errors: bool
    ) -> ToolCallEvent:
        """Generate tool call event."""
        tool_name = random.choice(self.tool_names)
        duration = random.uniform(100, 2000)  # 0.1-2 seconds
        success = True
        
        if include_errors and random.random() < 0.1:  # 10% error rate
            success = False
            duration *= 2  # Errors take longer
        
        return ToolCallEvent(
            run_id=run_id,
            thread_id=thread_id,
            timestamp=timestamp,
            agent_type=agent_type,
            step_name=f"tool_{tool_name}",
            tool_name=tool_name,
            tool_input={"query": f"test query {random.randint(1, 100)}", "params": {"limit": 10}},
            tool_output={"result": f"tool output {random.randint(1, 100)}"} if success else None,
            success=success,
            error_message="Tool execution failed" if not success else None,
            duration_ms=duration,
            metadata={"tool_version": "1.0.0", "retry_count": 0 if success else 1}
        )
    
    def _generate_delegation_event(
        self, 
        run_id: str, 
        thread_id: Optional[str], 
        timestamp: datetime, 
        from_agent: AgentType
    ) -> tuple[DelegationEvent, AgentType]:
        """Generate delegation event."""
        # Choose target agent (not the same as source)
        available_agents = [a for a in self.agent_types if a != from_agent]
        to_agent = random.choice(available_agents)
        
        reasons = [
            "Query requires specialized analysis",
            "Content needs summarization",
            "Complex task delegation",
            "Expertise required"
        ]
        
        return DelegationEvent(
            run_id=run_id,
            thread_id=thread_id,
            timestamp=timestamp,
            agent_type=from_agent,
            from_agent=from_agent,
            to_agent=to_agent,
            delegation_reason=random.choice(reasons),
            input_data={"query": f"delegated query {random.randint(1, 100)}"},
            output_data={"response": f"delegated response {random.randint(1, 100)}"},
            duration_ms=random.uniform(50, 200)
        ), to_agent
    
    def _generate_step_log_event(
        self, 
        run_id: str, 
        thread_id: Optional[str], 
        timestamp: datetime, 
        agent_type: AgentType
    ) -> StepLogEvent:
        """Generate step log event."""
        step_name = random.choice(self.step_names)
        
        return StepLogEvent(
            run_id=run_id,
            thread_id=thread_id,
            timestamp=timestamp,
            agent_type=agent_type,
            step_name=step_name,
            step_description=f"Executing {step_name}",
            step_data={
                "progress": random.randint(0, 100),
                "status": random.choice(["in_progress", "completed", "pending"]),
                "metadata": {"step_id": random.randint(1, 1000)}
            },
            duration_ms=random.uniform(10, 500)
        )
    
    def _generate_run_end_event(
        self, 
        run_id: str, 
        thread_id: Optional[str], 
        timestamp: datetime
    ) -> TelemetryEvent:
        """Generate run end event."""
        return TelemetryEvent(
            event_type=EventType.RUN_END,
            run_id=run_id,
            thread_id=thread_id,
            timestamp=timestamp,
            step_name="run_completion",
            metadata={"final_status": "completed", "total_events": "generated"}
        )
    
    def generate_multiple_runs(
        self, 
        count: int = 5,
        **kwargs
    ) -> List[RunSummary]:
        """Generate multiple synthetic runs."""
        runs = []
        for _ in range(count):
            run = self.generate_run(**kwargs)
            runs.append(run)
        return runs


# Convenience function for quick testing
def generate_sample_run(**kwargs) -> RunSummary:
    """Generate a single sample run for testing."""
    generator = SyntheticTelemetryGenerator()
    return generator.generate_run(**kwargs)
