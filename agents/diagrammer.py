"""Agent D: Diagrammer/Analyst agent that converts telemetry to React Flow diagrams."""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel

from models.telemetry import (
    AgentType, DiagramAnalysis, OptimizationPoint, ReactFlowEdge, 
    ReactFlowNode, TelemetryEvent, telemetry_store
)
from telemetry_enhanced import log_agent_output, log_llm_call, log_step, set_current_agent


class DiagrammerAgent:
    """Agent D: Converts telemetry to React Flow diagrams and optimization suggestions."""
    
    def __init__(self, model_name: str = "anthropic:claude-3-7-sonnet-latest"):
        self.model = init_chat_model(model_name, temperature=0.1)
        self.agent_type = AgentType.DIAGRAMMER
        self.model_name = model_name
        self.use_llm = os.getenv("USE_LLM_DIAGRAMMER", "false").lower() == "true"
        
        self.system_prompt = """You are a specialized AI agent that analyzes telemetry data and creates React Flow diagrams. Your tasks include:

1. **Flow Analysis**: Convert telemetry events into nodes and edges for React Flow
2. **Optimization Detection**: Identify performance bottlenecks, inefficiencies, and improvement opportunities
3. **Visualization**: Create clear, informative diagrams that show agent interactions and data flow
4. **Insights**: Provide actionable recommendations for system optimization

When analyzing telemetry:
- Focus on agent interactions, tool calls, and delegation patterns
- Identify timing issues, error patterns, and resource usage
- Look for opportunities to optimize performance and reduce costs
- Consider both technical and business impact of optimizations

Your analysis should be thorough, accurate, and actionable."""
    
    def _get_model_name(self) -> str:
        """Extract model name from the LangChain model."""
        try:
            # Try different ways to get the model name
            if hasattr(self.model, 'model_name'):
                return self.model.model_name
            elif hasattr(self.model, 'model'):
                return str(self.model.model)
            elif hasattr(self.model, 'model_id'):
                return str(self.model.model_id)
            elif hasattr(self.model, '_model_name'):
                return str(self.model._model_name)
            else:
                # Fallback to the model_name parameter we passed in
                return self.model_name
        except:
            return self.model_name
    
    def analyze_telemetry(self, run_id: str) -> DiagramAnalysis:
        """Analyze telemetry data and create React Flow diagram."""
        set_current_agent(self.agent_type)
        
        log_step("analysis_start", f"Starting telemetry analysis for run {run_id}")
        
        # Get telemetry data
        run = telemetry_store.get_run(run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found")
        
        events = telemetry_store.get_run_events(run_id)
        log_step("data_retrieved", f"Retrieved {len(events)} events for analysis")
        
        if self.use_llm:
            return self._analyze_with_llm(events, run)
        else:
            return self._analyze_deterministic(events, run)
    
    def _analyze_deterministic(self, events: List[TelemetryEvent], run) -> DiagramAnalysis:
        """Deterministic analysis without LLM."""
        log_step("deterministic_analysis", "Using deterministic analysis method")
        
        nodes = []
        edges = []
        optimizations = []
        
        # Create nodes for each agent and tool
        agent_nodes = {}
        tool_nodes = {}
        event_nodes = {}
        
        # Track agent interactions
        agent_sequence = []
        tool_calls = []
        delegations = []
        
        for i, event in enumerate(events):
            # Create event node
            event_id = f"event_{i}"
            event_nodes[event_id] = event
            
            # Create agent node if not exists
            if event.agent_type:
                agent_type_value = event.agent_type.value if hasattr(event.agent_type, 'value') else str(event.agent_type)
                agent_id = f"agent_{agent_type_value}"
                if agent_id not in agent_nodes:
                    agent_nodes[agent_id] = {
                        "id": agent_id,
                        "type": "agent",
                        "agent_type": agent_type_value,
                        "events": []
                    }
                agent_nodes[agent_id]["events"].append(event)
                agent_sequence.append((event.timestamp, agent_type_value))
            
            # Track tool calls
            if hasattr(event, 'tool_name'):
                tool_id = f"tool_{event.tool_name}"
                if tool_id not in tool_nodes:
                    tool_nodes[tool_id] = {
                        "id": tool_id,
                        "type": "tool",
                        "tool_name": event.tool_name,
                        "calls": []
                    }
                tool_nodes[tool_id]["calls"].append(event)
                tool_calls.append(event)
            
            # Track delegations
            if hasattr(event, 'from_agent') and hasattr(event, 'to_agent'):
                delegations.append(event)
        
        # Create React Flow nodes with proper spacing
        # Agent nodes - top row
        agent_x = 0
        agent_spacing = 350  # Increased spacing for agent nodes
        
        for agent_id, agent_data in agent_nodes.items():
            # Get event details for this agent
            event_details = []
            for event in agent_data["events"]:
                event_info = {
                    "type": event.event_type,
                    "step": event.step_name or f"{event.event_type}_step",
                    "timestamp": event.timestamp.isoformat(),
                    "duration_ms": event.duration_ms
                }
                if hasattr(event, 'tool_name'):
                    event_info["tool"] = event.tool_name
                if hasattr(event, 'model'):
                    event_info["model"] = event.model or "claude-3-7-sonnet-latest"
                if hasattr(event, 'success'):
                    event_info["success"] = event.success
                event_details.append(event_info)
            
            nodes.append(ReactFlowNode(
                id=agent_id,
                type="agent",
                position={"x": agent_x, "y": 0},
                data={
                    "label": agent_data["agent_type"].title(),
                    "event_count": len(agent_data["events"]),
                    "agent_type": agent_data["agent_type"],
                    "events": event_details
                },
                style={"background": "#e1f5fe", "border": "2px solid #01579b"}
            ))
            agent_x += agent_spacing
        
        # Tool nodes - middle row
        tool_x = 0
        tool_spacing = 350  # Increased spacing for tool nodes
        
        for tool_id, tool_data in tool_nodes.items():
            # Get call details for this tool
            call_details = []
            for call in tool_data["calls"]:
                call_info = {
                    "timestamp": call.timestamp.isoformat(),
                    "duration_ms": call.duration_ms,
                    "success": call.success,
                    "agent": call.agent_type.value if hasattr(call.agent_type, 'value') else str(call.agent_type) if call.agent_type else "orchestrator"
                }
                if hasattr(call, 'error_message') and call.error_message:
                    call_info["error"] = call.error_message
                call_details.append(call_info)
            
            nodes.append(ReactFlowNode(
                id=tool_id,
                type="tool",
                position={"x": tool_x, "y": 200},  # Increased vertical spacing
                data={
                    "label": tool_data["tool_name"],
                    "call_count": len(tool_data["calls"]),
                    "tool_name": tool_data["tool_name"],
                    "calls": call_details
                },
                style={"background": "#f3e5f5", "border": "2px solid #4a148c"}
            ))
            tool_x += tool_spacing
        
        # Event nodes - bottom rows with better spacing
        events_per_row = 6  # Increased from 5
        event_spacing_x = 200  # Increased horizontal spacing
        event_spacing_y = 120  # Increased vertical spacing
        start_y = 400  # Increased starting Y position
        
        for i, event in enumerate(events):
            event_id = f"event_{i}"
            event_data = {
                "label": f"{event.event_type}",
                "event_type": event.event_type,
                "step_name": event.step_name or f"{event.event_type}_step",
                "timestamp": event.timestamp.isoformat(),
                "duration_ms": event.duration_ms,
                "agent_type": event.agent_type.value if hasattr(event.agent_type, 'value') else str(event.agent_type) if event.agent_type else "orchestrator"
            }
            
            # Add specific event details
            if hasattr(event, 'tool_name'):
                event_data["tool_name"] = event.tool_name
            if hasattr(event, 'model'):
                event_data["model"] = event.model or "claude-3-7-sonnet-latest"
            if hasattr(event, 'success'):
                event_data["success"] = event.success
            if hasattr(event, 'error_message'):
                event_data["error_message"] = event.error_message
            if hasattr(event, 'from_agent'):
                event_data["from_agent"] = event.from_agent.value if hasattr(event.from_agent, 'value') else str(event.from_agent) if event.from_agent else "orchestrator"
            if hasattr(event, 'to_agent'):
                event_data["to_agent"] = event.to_agent.value if hasattr(event.to_agent, 'value') else str(event.to_agent) if event.to_agent else "summarizer"
            
            # Position events in a grid with proper spacing
            row = i // events_per_row
            col = i % events_per_row
            x_pos = col * event_spacing_x
            y_pos = start_y + row * event_spacing_y
            
            nodes.append(ReactFlowNode(
                id=event_id,
                type="event",
                position={"x": x_pos, "y": y_pos},
                data=event_data,
                style={
                    "background": "#e8f5e8" if not hasattr(event, 'success') or event.success else "#ffebee",
                    "border": "2px solid #2e7d32" if not hasattr(event, 'success') or event.success else "2px solid #f44336",
                    "minWidth": "120px"
                }
            ))
        
        # Create edges based on agent sequence and delegations
        edge_id = 0
        for i in range(len(agent_sequence) - 1):
            current_agent = agent_sequence[i][1]
            next_agent = agent_sequence[i + 1][1]
            
            if current_agent != next_agent:
                edges.append(ReactFlowEdge(
                    id=f"edge_{edge_id}",
                    source=f"agent_{current_agent}",
                    target=f"agent_{next_agent}",
                    type="smoothstep",
                    data={"type": "agent_transition"}
                ))
                edge_id += 1
        
        # Add tool usage edges
        for tool_call in tool_calls:
            if tool_call.agent_type:
                agent_type_value = tool_call.agent_type.value if hasattr(tool_call.agent_type, 'value') else str(tool_call.agent_type)
                edges.append(ReactFlowEdge(
                    id=f"edge_{edge_id}",
                    source=f"agent_{agent_type_value}",
                    target=f"tool_{tool_call.tool_name}",
                    type="straight",
                    data={"type": "tool_usage"}
                ))
                edge_id += 1
        
        # Add edges from events to their agents
        for i, event in enumerate(events):
            event_id = f"event_{i}"
            if event.agent_type:
                agent_type_value = event.agent_type.value if hasattr(event.agent_type, 'value') else str(event.agent_type)
                agent_id = f"agent_{agent_type_value}"
                edges.append(ReactFlowEdge(
                    id=f"edge_{edge_id}",
                    source=agent_id,
                    target=event_id,
                    type="straight",
                    data={"type": "event_flow"}
                ))
                edge_id += 1
            
            # Add edges from events to tools if it's a tool call
            if hasattr(event, 'tool_name'):
                tool_id = f"tool_{event.tool_name}"
                edges.append(ReactFlowEdge(
                    id=f"edge_{edge_id}",
                    source=event_id,
                    target=tool_id,
                    type="straight",
                    data={"type": "event_tool"}
                ))
                edge_id += 1
        
        # Generate optimizations
        optimizations = self._generate_deterministic_optimizations(events, run)
        
        log_step("analysis_complete", "Deterministic analysis completed")
        
        # Create the analysis result
        analysis = DiagramAnalysis(
            nodes=nodes,
            edges=edges,
            optimizations=optimizations,
            summary=f"Analyzed {len(events)} events across {len(agent_nodes)} agents and {len(tool_nodes)} tools",
            total_events=len(events)
        )
        
        # Log diagrammer output
        log_agent_output(
            output_type="diagram_analysis",
            output_content=f"Generated diagram with {len(nodes)} nodes and {len(edges)} edges. {len(optimizations)} optimizations found.",
            success=True,
            metadata={
                "node_count": len(nodes),
                "edge_count": len(edges),
                "optimization_count": len(optimizations),
                "event_count": len(events),
                "agent_count": len(agent_nodes),
                "tool_count": len(tool_nodes)
            }
        )
        
        return analysis
    
    def _analyze_with_llm(self, events: List[TelemetryEvent], run) -> DiagramAnalysis:
        """Analysis using LLM for more sophisticated insights."""
        log_step("llm_analysis", "Using LLM-based analysis method")
        
        # Prepare telemetry data for LLM
        telemetry_data = self._prepare_telemetry_for_llm(events, run)
        
        prompt = f"""
        Analyze the following telemetry data and create a React Flow diagram representation.

        Telemetry Data:
        {json.dumps(telemetry_data, indent=2, default=str)}

        Please provide:
        1. A list of nodes (agents, tools, events) with positions and styling
        2. A list of edges showing relationships and flow
        3. Optimization recommendations based on the data
        4. A summary of the analysis

        Format your response as JSON:
        {{
            "nodes": [
                {{
                    "id": "agent_orchestrator",
                    "type": "agent",
                    "position": {{"x": 0, "y": 0}},
                    "data": {{"label": "Orchestrator", "agent_type": "orchestrator"}},
                    "style": {{"background": "#e1f5fe"}}
                }}
            ],
            "edges": [
                {{
                    "id": "edge_1",
                    "source": "agent_orchestrator",
                    "target": "agent_summarizer",
                    "type": "smoothstep",
                    "data": {{"type": "delegation"}}
                }}
            ],
            "optimizations": [
                {{
                    "category": "performance",
                    "severity": "medium",
                    "title": "Optimization Title",
                    "description": "Description of the issue",
                    "suggestion": "Specific recommendation",
                    "impact_estimate": "Expected impact"
                }}
            ],
            "summary": "Analysis summary"
        }}
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self._call_llm(messages, analysis_type="telemetry_analysis")
        
        # Parse LLM response
        try:
            analysis_data = json.loads(response)
            
            # Convert to Pydantic models
            nodes = [ReactFlowNode(**node) for node in analysis_data.get("nodes", [])]
            edges = [ReactFlowEdge(**edge) for edge in analysis_data.get("edges", [])]
            optimizations = [OptimizationPoint(**opt) for opt in analysis_data.get("optimizations", [])]
            
            analysis = DiagramAnalysis(
                nodes=nodes,
                edges=edges,
                optimizations=optimizations,
                summary=analysis_data.get("summary", "LLM analysis completed"),
                total_events=len(events)
            )
            
            # Log diagrammer output
            log_agent_output(
                output_type="diagram_analysis",
                output_content=f"Generated diagram with {len(nodes)} nodes and {len(edges)} edges. {len(optimizations)} optimizations found.",
                success=True,
                metadata={
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                    "optimization_count": len(optimizations),
                    "event_count": len(events),
                    "analysis_method": "llm"
                }
            )
            
            return analysis
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            log_step("llm_parse_error", f"Failed to parse LLM response: {str(e)}")
            # Fallback to deterministic analysis
            return self._analyze_deterministic(events, run)
    
    def _prepare_telemetry_for_llm(self, events: List[TelemetryEvent], run) -> Dict[str, Any]:
        """Prepare telemetry data for LLM analysis."""
        return {
            "run_id": run.run_id,
            "start_time": run.start_time.isoformat() if run.start_time else None,
            "end_time": run.end_time.isoformat() if run.end_time else None,
            "status": run.status,
            "total_duration_ms": run.total_duration_ms,
            "events": [
                {
                    "event_type": event.event_type,
                    "timestamp": event.timestamp.isoformat(),
                    "agent_type": event.agent_type.value if hasattr(event.agent_type, 'value') else str(event.agent_type) if event.agent_type else None,
                    "step_name": event.step_name,
                    "duration_ms": event.duration_ms,
                    "metadata": event.metadata
                }
                for event in events
            ],
            "summary": {
                "total_llm_calls": run.total_llm_calls,
                "total_tool_calls": run.total_tool_calls,
                "total_delegations": run.total_delegations,
                "error_count": run.error_count
            }
        }
    
    def _generate_deterministic_optimizations(self, events: List[TelemetryEvent], run) -> List[OptimizationPoint]:
        """Generate optimization suggestions deterministically."""
        optimizations = []
        
        # Check for long-running events
        long_events = [e for e in events if e.duration_ms and e.duration_ms > 5000]
        if long_events:
            optimizations.append(OptimizationPoint(
                category="performance",
                severity="medium",
                title="Long-running Operations Detected",
                description=f"Found {len(long_events)} events taking longer than 5 seconds",
                suggestion="Consider optimizing these operations or adding progress indicators",
                impact_estimate="Improved user experience and system responsiveness"
            ))
        
        # Check for high error rate
        error_events = [e for e in events if hasattr(e, 'success') and not e.success]
        if error_events and len(error_events) / len(events) > 0.1:
            optimizations.append(OptimizationPoint(
                category="reliability",
                severity="high",
                title="High Error Rate",
                description=f"Error rate is {len(error_events)/len(events)*100:.1f}%",
                suggestion="Investigate and fix error sources, add better error handling",
                impact_estimate="Improved system reliability and user satisfaction"
            ))
        
        # Check for frequent tool calls
        tool_events = [e for e in events if e.event_type == "tool_call"]
        if len(tool_events) > 10:
            optimizations.append(OptimizationPoint(
                category="efficiency",
                severity="low",
                title="High Tool Usage",
                description=f"System made {len(tool_events)} tool calls",
                suggestion="Consider caching or batching tool calls to reduce overhead",
                impact_estimate="Reduced latency and resource usage"
            ))
        
        # Check for delegation patterns
        delegation_events = [e for e in events if e.event_type == "delegation"]
        if len(delegation_events) > 3:
            optimizations.append(OptimizationPoint(
                category="architecture",
                severity="low",
                title="Complex Delegation Chain",
                description=f"System made {len(delegation_events)} delegations",
                suggestion="Consider simplifying the agent architecture or optimizing delegation logic",
                impact_estimate="Simplified maintenance and improved performance"
            ))
        
        return optimizations
    
    def _call_llm(self, messages: List[Any], **kwargs) -> str:
        """Call LLM with telemetry."""
        start_time = time.perf_counter()
        
        try:
            response = self.model.invoke(messages)
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)
            
            # Log LLM call
            log_llm_call(
                model=self._get_model_name(),
                prompt=str(messages),
                response=content,
                duration_ms=duration_ms,
                **kwargs
            )
            
            return content
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_llm_call(
                model=self._get_model_name(),
                prompt=str(messages),
                response=f"Error: {str(e)}",
                duration_ms=duration_ms,
                error=str(e)
            )
            raise
