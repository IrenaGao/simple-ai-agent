"""Tests for synthetic telemetry generation."""

import pytest
from datetime import datetime, timedelta
from models.telemetry import telemetry_store
from synthetic_telemetry import SyntheticTelemetryGenerator, generate_sample_run


class TestSyntheticTelemetryGenerator:
    """Test cases for synthetic telemetry generation."""
    
    def setup_method(self):
        """Clear telemetry store before each test."""
        telemetry_store.clear()
    
    def test_generate_single_run(self):
        """Test generating a single synthetic run."""
        generator = SyntheticTelemetryGenerator()
        run = generator.generate_run(
            run_id="test-run-1",
            duration_minutes=1.0,
            event_count=10
        )
        
        assert run.run_id == "test-run-1"
        assert run.status == "completed"
        assert run.total_duration_ms is not None
        assert len(run.agent_events) > 0
        
        # Verify events were added to store
        events = telemetry_store.get_run_events("test-run-1")
        assert len(events) > 0
    
    def test_generate_multiple_runs(self):
        """Test generating multiple synthetic runs."""
        generator = SyntheticTelemetryGenerator()
        runs = generator.generate_multiple_runs(count=3)
        
        assert len(runs) == 3
        for run in runs:
            assert run.status == "completed"
            assert run.total_duration_ms is not None
    
    def test_event_types_generated(self):
        """Test that various event types are generated."""
        generator = SyntheticTelemetryGenerator()
        run = generator.generate_run(
            run_id="test-run-2",
            event_count=20,
            include_errors=True,
            include_delegation=True
        )
        
        events = telemetry_store.get_run_events("test-run-2")
        event_types = {event.event_type for event in events}
        
        # Should have multiple event types
        assert len(event_types) > 1
        assert "run_start" in event_types or "run_end" in event_types
    
    def test_error_inclusion(self):
        """Test that errors are included when requested."""
        generator = SyntheticTelemetryGenerator()
        run = generator.generate_run(
            run_id="test-run-3",
            include_errors=True
        )
        
        events = telemetry_store.get_run_events("test-run-3")
        error_events = [e for e in events if hasattr(e, 'success') and not e.success]
        
        # Should have some error events
        assert len(error_events) > 0
        assert run.error_count > 0
    
    def test_delegation_inclusion(self):
        """Test that delegations are included when requested."""
        generator = SyntheticTelemetryGenerator()
        run = generator.generate_run(
            run_id="test-run-4",
            include_delegation=True
        )
        
        events = telemetry_store.get_run_events("test-run-4")
        delegation_events = [e for e in events if e.event_type == "delegation"]
        
        # Should have some delegation events
        assert len(delegation_events) > 0
        assert run.total_delegations > 0
    
    def test_convenience_function(self):
        """Test the convenience function for generating sample runs."""
        run = generate_sample_run(run_id="test-run-5")
        
        assert run.run_id == "test-run-5"
        assert run.status == "completed"
        assert len(run.agent_events) > 0


class TestTelemetryStore:
    """Test cases for telemetry store functionality."""
    
    def setup_method(self):
        """Clear telemetry store before each test."""
        telemetry_store.clear()
    
    def test_start_end_run(self):
        """Test starting and ending a run."""
        run_id = "test-run-6"
        run = telemetry_store.start_run(run_id, "test-thread")
        
        assert run.run_id == run_id
        assert run.thread_id == "test-thread"
        assert run.status == "running"
        assert run.start_time is not None
        
        # End the run
        ended_run = telemetry_store.end_run(run_id, "completed")
        assert ended_run.status == "completed"
        assert ended_run.end_time is not None
        assert ended_run.total_duration_ms is not None
    
    def test_add_events(self):
        """Test adding events to a run."""
        run_id = "test-run-7"
        run = telemetry_store.start_run(run_id)
        
        # Add some events
        from models.telemetry import TelemetryEvent, EventType
        event1 = TelemetryEvent(
            event_type=EventType.STEP_LOG,
            run_id=run_id,
            step_name="test_step"
        )
        event2 = TelemetryEvent(
            event_type=EventType.TOOL_CALL,
            run_id=run_id,
            step_name="test_tool"
        )
        
        telemetry_store.add_event(event1)
        telemetry_store.add_event(event2)
        
        # Verify events were added
        events = telemetry_store.get_run_events(run_id)
        assert len(events) == 2
        
        # Verify run summary was updated
        updated_run = telemetry_store.get_run(run_id)
        assert len(updated_run.agent_events) == 2
    
    def test_get_all_runs(self):
        """Test getting all runs."""
        # Create multiple runs
        run1 = telemetry_store.start_run("run-1")
        run2 = telemetry_store.start_run("run-2")
        
        all_runs = telemetry_store.get_all_runs()
        assert len(all_runs) == 2
        
        run_ids = {run.run_id for run in all_runs}
        assert "run-1" in run_ids
        assert "run-2" in run_ids


if __name__ == "__main__":
    pytest.main([__file__])
