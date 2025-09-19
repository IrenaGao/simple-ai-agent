"""Tests for diagrammer agent functionality."""

import pytest
import os
from models.telemetry import telemetry_store, AgentType, EventType
from synthetic_telemetry import SyntheticTelemetryGenerator
from agents.diagrammer import DiagrammerAgent


class TestDiagrammerAgent:
    """Test cases for diagrammer agent."""
    
    def setup_method(self):
        """Clear telemetry store and set up test environment."""
        telemetry_store.clear()
        # Ensure deterministic mode for testing
        os.environ["USE_LLM_DIAGRAMMER"] = "false"
    
    def test_deterministic_analysis(self):
        """Test deterministic analysis without LLM."""
        # Generate test data
        generator = SyntheticTelemetryGenerator()
        run = generator.generate_run(
            run_id="test-run-1",
            duration_minutes=1.0,
            event_count=15,
            include_delegation=True
        )
        
        # Test diagrammer
        diagrammer = DiagrammerAgent()
        analysis = diagrammer.analyze_telemetry("test-run-1")
        
        # Verify analysis structure
        assert analysis is not None
        assert len(analysis.nodes) > 0
        assert len(analysis.edges) >= 0
        assert len(analysis.optimizations) >= 0
        assert analysis.summary is not None
        assert analysis.total_events > 0
        
        # Verify node structure
        for node in analysis.nodes:
            assert hasattr(node, 'id')
            assert hasattr(node, 'type')
            assert hasattr(node, 'position')
            assert hasattr(node, 'data')
        
        # Verify edge structure
        for edge in analysis.edges:
            assert hasattr(edge, 'id')
            assert hasattr(edge, 'source')
            assert hasattr(edge, 'target')
        
        # Verify optimization structure
        for opt in analysis.optimizations:
            assert hasattr(opt, 'category')
            assert hasattr(opt, 'severity')
            assert hasattr(opt, 'title')
            assert hasattr(opt, 'description')
            assert hasattr(opt, 'suggestion')
    
    def test_analysis_with_no_events(self):
        """Test analysis with empty telemetry data."""
        # Create empty run
        run = telemetry_store.start_run("empty-run")
        telemetry_store.end_run("empty-run", "completed")
        
        diagrammer = DiagrammerAgent()
        analysis = diagrammer.analyze_telemetry("empty-run")
        
        # Should still return valid analysis
        assert analysis is not None
        assert len(analysis.nodes) == 0
        assert len(analysis.edges) == 0
        assert len(analysis.optimizations) == 0
        assert analysis.total_events == 0
    
    def test_analysis_with_errors(self):
        """Test analysis with error events."""
        generator = SyntheticTelemetryGenerator()
        run = generator.generate_run(
            run_id="error-run",
            include_errors=True,
            event_count=10
        )
        
        diagrammer = DiagrammerAgent()
        analysis = diagrammer.analyze_telemetry("error-run")
        
        # Should detect error-related optimizations
        error_optimizations = [
            opt for opt in analysis.optimizations 
            if 'error' in opt.title.lower() or 'reliability' in opt.category.lower()
        ]
        assert len(error_optimizations) > 0
    
    def test_optimization_categories(self):
        """Test that different optimization categories are generated."""
        generator = SyntheticTelemetryGenerator()
        run = generator.generate_run(
            run_id="optimization-test",
            event_count=25,  # More events to trigger various optimizations
            include_errors=True,
            include_delegation=True
        )
        
        diagrammer = DiagrammerAgent()
        analysis = diagrammer.analyze_telemetry("optimization-test")
        
        categories = {opt.category for opt in analysis.optimizations}
        
        # Should have multiple categories
        assert len(categories) > 0
        # Common categories that should be detected
        expected_categories = ['performance', 'reliability', 'efficiency', 'architecture']
        assert any(cat in categories for cat in expected_categories)
    
    def test_react_flow_compatibility(self):
        """Test that generated data is compatible with React Flow."""
        generator = SyntheticTelemetryGenerator()
        run = generator.generate_run("react-flow-test")
        
        diagrammer = DiagrammerAgent()
        analysis = diagrammer.analyze_telemetry("react-flow-test")
        
        # Convert to dict format (as would be sent to frontend)
        nodes_dict = [node.dict() for node in analysis.nodes]
        edges_dict = [edge.dict() for edge in analysis.edges]
        
        # Verify required React Flow fields
        for node in nodes_dict:
            assert 'id' in node
            assert 'type' in node
            assert 'position' in node
            assert 'data' in node
            assert 'x' in node['position']
            assert 'y' in node['position']
        
        for edge in edges_dict:
            assert 'id' in edge
            assert 'source' in edge
            assert 'target' in edge
    
    def test_llm_mode_fallback(self):
        """Test that LLM mode falls back to deterministic on error."""
        # Set LLM mode but don't provide actual LLM (should fail)
        os.environ["USE_LLM_DIAGRAMMER"] = "true"
        
        generator = SyntheticTelemetryGenerator()
        run = generator.generate_run("llm-fallback-test")
        
        diagrammer = DiagrammerAgent()
        # This should not raise an exception, should fall back to deterministic
        analysis = diagrammer.analyze_telemetry("llm-fallback-test")
        
        assert analysis is not None
        assert len(analysis.nodes) > 0


if __name__ == "__main__":
    pytest.main([__file__])
