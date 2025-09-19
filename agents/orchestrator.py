"""Agent A: Orchestrator agent that can delegate to other agents."""

import time
from typing import Any, Dict, List, Optional

from langchain.chat_models import init_chat_model
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from models.telemetry import AgentType, telemetry_store
from telemetry_enhanced import (
    log_agent_output, log_delegation, log_llm_call, log_step, set_current_agent, 
    with_telemetry
)
from tools.pinecone_tool import search_kb


class OrchestrationResult(BaseModel):
    """Result from orchestrator agent."""
    response: str
    used_kb: bool = False
    delegated_to: Optional[str] = None
    confidence: float = 0.0


class OrchestratorAgent:
    """Agent A: Orchestrator that can delegate to other agents."""
    
    def __init__(self, model_name: str = "anthropic:claude-3-7-sonnet-latest", system_prompt: Optional[str] = None):
        self.model = init_chat_model(model_name, temperature=0.2)
        self.agent_type = AgentType.ORCHESTRATOR
        
        # Set system prompt
        self.system_prompt = system_prompt or """You are an intelligent orchestrator agent that coordinates multi-agent workflows. Your responsibilities include:

1. **Query Analysis**: Understand user queries and determine the best approach
2. **Knowledge Integration**: Search and utilize knowledge bases effectively
3. **Smart Delegation**: Decide when to delegate to specialized agents
4. **Response Synthesis**: Combine information from multiple sources
5. **Quality Assurance**: Ensure responses are accurate and helpful

When processing queries:
- Always search the knowledge base first for relevant context
- Delegate to specialized agents when analysis, summarization, or grading is needed
- Provide clear, comprehensive responses
- Maintain high quality and accuracy standards

Your goal is to provide the best possible response by intelligently coordinating available resources and agents."""
        
        # Initialize tools with telemetry
        self.tools = {
            "search_kb": with_telemetry("search_kb", self.agent_type)(search_kb)
        }
    
    def _should_delegate(self, query: str, kb_context: str) -> tuple[bool, str]:
        """Determine if we should delegate to Agent B (summarizer/grader)."""
        delegation_indicators = [
            "summarize", "summary", "grade", "evaluate", "assess", "review",
            "analyze", "compare", "rate", "score", "judge", "critique"
        ]
        
        query_lower = query.lower()
        kb_lower = kb_context.lower()
        
        # Check if query contains delegation keywords
        has_delegation_keywords = any(indicator in query_lower for indicator in delegation_indicators)
        
        # Check if we have substantial KB context that might need analysis
        has_substantial_context = len(kb_context) > 200 and kb_context != "No results found."
        
        # Check if query is asking for analysis of the KB content
        analysis_keywords = ["what does this mean", "explain this", "analyze this", "what can you tell me about"]
        is_analysis_query = any(keyword in query_lower for keyword in analysis_keywords)
        
        should_delegate = has_delegation_keywords or (has_substantial_context and is_analysis_query)
        reason = "delegation keywords" if has_delegation_keywords else "analysis of KB content"
        
        return should_delegate, reason
    
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
            model_name = self._get_model_name()
            log_llm_call(
                model=model_name,
                prompt=str(messages),
                response=content,
                duration_ms=duration_ms,
                **kwargs
            )
            
            return content
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            model_name = self._get_model_name()
            log_llm_call(
                model=model_name,
                prompt=str(messages),
                response=f"Error: {str(e)}",
                duration_ms=duration_ms,
                error=str(e)
            )
            raise
    
    def process_query(self, query: str, run_id: str) -> OrchestrationResult:
        """Process a user query with potential delegation."""
        set_current_agent(self.agent_type)
        
        log_step("query_received", f"Received query: {query[:100]}...")
        
        # Step 1: Plan the approach
        log_step("planning", "Planning approach to handle query")
        
        planning_prompt = f"""
        You are an orchestrator agent. Analyze this user query and determine the best approach:
        
        Query: {query}
        
        Consider:
        1. Does this query need knowledge base search?
        2. Does this query require analysis, summarization, or grading?
        3. What tools or agents might be needed?
        
        Respond with a brief plan (1-2 sentences).
        """
        
        plan = self._call_llm([HumanMessage(content=planning_prompt)])
        log_step("plan_created", f"Created plan: {plan}")
        
        # Step 2: Search knowledge base if needed
        kb_context = ""
        used_kb = False
        
        if any(keyword in query.lower() for keyword in ["how", "what", "where", "when", "why", "setup", "configure"]):
            log_step("kb_search", "Searching knowledge base")
            try:
                kb_context = self.tools["search_kb"](query)
                used_kb = True
                log_step("kb_search_complete", f"Found KB context: {len(kb_context)} characters")
            except Exception as e:
                log_step("kb_search_error", f"KB search failed: {str(e)}")
                kb_context = "No results found."
        
        # Step 3: Determine if delegation is needed
        should_delegate, delegation_reason = self._should_delegate(query, kb_context)
        
        if should_delegate:
            log_step("delegation_decision", f"Decided to delegate: {delegation_reason}")
            
            # Log delegation event
            log_delegation(
                from_agent=self.agent_type,
                to_agent=AgentType.SUMMARIZER,
                reason=delegation_reason,
                input_data={"query": query, "kb_context": kb_context}
            )
            
            # For now, we'll simulate delegation by calling a simplified summarizer
            # In a real implementation, this would call Agent B
            log_step("delegating", "Delegating to summarizer agent")
            
            # Simulate Agent B response
            summarizer_response = self._simulate_summarizer(query, kb_context)
            
            log_step("delegation_complete", "Received response from summarizer")
            
            # Log orchestrator output
            log_agent_output(
                output_type="orchestrator_response",
                output_content=summarizer_response,
                success=True,
                metadata={
                    "delegated_to": "summarizer",
                    "used_kb": used_kb,
                    "confidence": 0.8
                }
            )
            
            return OrchestrationResult(
                response=summarizer_response,
                used_kb=used_kb,
                delegated_to="summarizer",
                confidence=0.8
            )
        
        # Step 4: Handle directly without delegation
        log_step("direct_handling", "Handling query directly without delegation")
        
        response_prompt = f"""
        User Query: {query}
        
        Knowledge Base Context:
        {kb_context if kb_context else "No additional context available."}
        
        Provide a clear, helpful response based on the available information.
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=response_prompt)
        ]
        
        response = self._call_llm(messages)
        
        log_step("response_generated", "Generated final response")
        
        # Log orchestrator output
        log_agent_output(
            output_type="orchestrator_response",
            output_content=response,
            success=True,
            metadata={
                "delegated_to": None,
                "used_kb": used_kb,
                "confidence": 0.9
            }
        )
        
        return OrchestrationResult(
            response=response,
            used_kb=used_kb,
            delegated_to=None,
            confidence=0.9
        )
    
    def _simulate_summarizer(self, query: str, kb_context: str) -> str:
        """Simulate Agent B (summarizer) response."""
        # This is a placeholder - in a real implementation, this would call Agent B
        log_step("simulating_summarizer", "Simulating summarizer agent response")
        
        summarizer_prompt = f"""
        Query: {query}
        Context: {kb_context}
        
        Provide a comprehensive summary and analysis.
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=summarizer_prompt)
        ]
        
        response = self._call_llm(messages)
        
        log_step("summarizer_complete", "Summarizer simulation complete")
        
        return response
