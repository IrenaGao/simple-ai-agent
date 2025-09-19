"""Agent B: Summarizer/Grader agent with specialized system prompt."""

import time
from typing import Any, Dict, List, Optional

from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel

from models.telemetry import AgentType
from telemetry_enhanced import log_agent_output, log_llm_call, log_step, set_current_agent


class SummarizationResult(BaseModel):
    """Result from summarizer agent."""
    summary: str
    grade: Optional[float] = None
    key_points: List[str] = []
    confidence: float = 0.0
    analysis_type: str = "summary"


class SummarizerAgent:
    """Agent B: Specialized summarizer and grader agent."""
    
    def __init__(self, model_name: str = "anthropic:claude-3-7-sonnet-latest"):
        self.model = init_chat_model(model_name, temperature=0.1)  # Lower temp for more consistent analysis
        self.agent_type = AgentType.SUMMARIZER
        
        # Specialized system prompt for summarization and grading
        self.system_prompt = """You are a specialized AI agent focused on summarization, analysis, and grading tasks. Your capabilities include:

1. **Summarization**: Create concise, accurate summaries of complex information
2. **Grading/Evaluation**: Assess content quality, accuracy, and completeness
3. **Analysis**: Break down complex topics into key components
4. **Critical Review**: Identify strengths, weaknesses, and areas for improvement

When processing information:
- Always maintain objectivity and accuracy
- Provide clear, structured analysis
- Include relevant metrics or scores when appropriate
- Highlight key insights and actionable recommendations
- Be specific and evidence-based in your assessments

Your responses should be professional, thorough, and actionable."""
    
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
    
    def summarize(self, content: str, query: str, run_id: str) -> SummarizationResult:
        """Summarize content based on a query."""
        set_current_agent(self.agent_type)
        
        log_step("summarization_start", f"Starting summarization for query: {query[:100]}...")
        
        # Determine the type of analysis needed
        analysis_type = self._determine_analysis_type(query)
        log_step("analysis_type", f"Determined analysis type: {analysis_type}")
        
        # Create specialized prompt based on analysis type
        if analysis_type == "grade":
            prompt = self._create_grading_prompt(content, query)
        elif analysis_type == "compare":
            prompt = self._create_comparison_prompt(content, query)
        else:
            prompt = self._create_summarization_prompt(content, query)
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self._call_llm(messages, analysis_type=analysis_type)
        
        # Parse the response to extract structured data
        result = self._parse_response(response, analysis_type)
        
        log_step("summarization_complete", f"Completed {analysis_type} analysis")
        
        # Log summarizer output
        log_agent_output(
            output_type="summarizer_response",
            output_content=result.summary,
            success=True,
            metadata={
                "analysis_type": analysis_type,
                "grade": result.grade,
                "key_points_count": len(result.key_points),
                "confidence": result.confidence
            }
        )
        
        return result
    
    def _determine_analysis_type(self, query: str) -> str:
        """Determine what type of analysis is needed."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["grade", "score", "rate", "evaluate", "assess"]):
            return "grade"
        elif any(word in query_lower for word in ["compare", "contrast", "versus", "vs"]):
            return "compare"
        elif any(word in query_lower for word in ["analyze", "break down", "examine"]):
            return "analyze"
        else:
            return "summary"
    
    def _create_summarization_prompt(self, content: str, query: str) -> str:
        """Create prompt for summarization tasks."""
        return f"""
        Please provide a comprehensive summary of the following content in response to the user's query.

        User Query: {query}

        Content to Summarize:
        {content}

        Please provide:
        1. A clear, concise summary (2-3 paragraphs)
        2. Key points and insights (bullet points)
        3. Any important details or recommendations
        4. Your confidence level in the analysis (0-1 scale)

        Format your response as:
        SUMMARY: [your summary]
        KEY POINTS: [bullet points]
        RECOMMENDATIONS: [any recommendations]
        CONFIDENCE: [0.0-1.0]
        """
    
    def _create_grading_prompt(self, content: str, query: str) -> str:
        """Create prompt for grading tasks."""
        return f"""
        Please evaluate and grade the following content based on the user's query.

        User Query: {query}

        Content to Evaluate:
        {content}

        Please provide:
        1. A numerical grade (0-100 scale)
        2. Detailed evaluation criteria
        3. Strengths and weaknesses
        4. Specific recommendations for improvement
        5. Your confidence in the evaluation

        Format your response as:
        GRADE: [0-100]
        CRITERIA: [evaluation criteria used]
        STRENGTHS: [what's good]
        WEAKNESSES: [what needs improvement]
        RECOMMENDATIONS: [specific suggestions]
        CONFIDENCE: [0.0-1.0]
        """
    
    def _create_comparison_prompt(self, content: str, query: str) -> str:
        """Create prompt for comparison tasks."""
        return f"""
        Please analyze and compare the following content based on the user's query.

        User Query: {query}

        Content to Compare:
        {content}

        Please provide:
        1. A structured comparison
        2. Key differences and similarities
        3. Pros and cons of each option
        4. A recommendation with justification
        5. Your confidence in the analysis

        Format your response as:
        COMPARISON: [structured comparison]
        DIFFERENCES: [key differences]
        SIMILARITIES: [key similarities]
        RECOMMENDATION: [your recommendation]
        CONFIDENCE: [0.0-1.0]
        """
    
    def _parse_response(self, response: str, analysis_type: str) -> SummarizationResult:
        """Parse the LLM response into structured data."""
        lines = response.split('\n')
        
        summary = ""
        grade = None
        key_points = []
        confidence = 0.5  # Default confidence
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("SUMMARY:"):
                current_section = "summary"
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("KEY POINTS:"):
                current_section = "key_points"
            elif line.startswith("GRADE:"):
                try:
                    grade = float(line.replace("GRADE:", "").strip())
                except ValueError:
                    pass
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.replace("CONFIDENCE:", "").strip())
                except ValueError:
                    pass
            elif current_section == "key_points" and line.startswith("-"):
                key_points.append(line[1:].strip())
            elif current_section == "summary" and not line.startswith(("KEY POINTS:", "GRADE:", "CONFIDENCE:")):
                if summary:
                    summary += " " + line
                else:
                    summary = line
        
        # If no structured sections found, use the whole response as summary
        if not summary:
            summary = response
        
        return SummarizationResult(
            summary=summary,
            grade=grade,
            key_points=key_points,
            confidence=confidence,
            analysis_type=analysis_type
        )
