#!/usr/bin/env python3
"""Test script to verify the multi-agent telemetry system works correctly."""

import os
import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from models.telemetry import telemetry_store, AgentType, EventType
        print("✓ Telemetry models imported")
    except ImportError as e:
        print(f"✗ Failed to import telemetry models: {e}")
        return False
    
    try:
        from telemetry_enhanced import start_run, end_run, log_step
        print("✓ Enhanced telemetry imported")
    except ImportError as e:
        print(f"✗ Failed to import enhanced telemetry: {e}")
        return False
    
    try:
        from agents.orchestrator import OrchestratorAgent
        print("✓ Orchestrator agent imported")
    except ImportError as e:
        print(f"✗ Failed to import orchestrator: {e}")
        return False
    
    try:
        from agents.summarizer import SummarizerAgent
        print("✓ Summarizer agent imported")
    except ImportError as e:
        print(f"✗ Failed to import summarizer: {e}")
        return False
    
    try:
        from agents.diagrammer import DiagrammerAgent
        print("✓ Diagrammer agent imported")
    except ImportError as e:
        print(f"✗ Failed to import diagrammer: {e}")
        return False
    
    try:
        from synthetic_telemetry import SyntheticTelemetryGenerator, generate_sample_run
        print("✓ Synthetic telemetry imported")
    except ImportError as e:
        print(f"✗ Failed to import synthetic telemetry: {e}")
        return False
    
    return True

def test_synthetic_data():
    """Test synthetic data generation."""
    print("\n🧪 Testing synthetic data generation...")
    
    try:
        from synthetic_telemetry import generate_sample_run
        
        # Generate a sample run
        run = generate_sample_run(run_id="test-run-001")
        
        if run and run.run_id == "test-run-001":
            print("✓ Synthetic data generation works")
            print(f"  - Generated run with {len(run.agent_events)} events")
            print(f"  - Duration: {run.total_duration_ms:.1f}ms")
            print(f"  - Status: {run.status}")
            return True
        else:
            print("✗ Synthetic data generation failed")
            return False
            
    except Exception as e:
        print(f"✗ Synthetic data generation error: {e}")
        return False

def test_diagram_generation():
    """Test diagram generation."""
    print("\n🧪 Testing diagram generation...")
    
    try:
        from synthetic_telemetry import generate_sample_run
        from agents.diagrammer import DiagrammerAgent
        
        # Generate test data
        run = generate_sample_run(run_id="test-run-002")
        
        # Generate diagram
        diagrammer = DiagrammerAgent()
        analysis = diagrammer.analyze_telemetry("test-run-002")
        
        if analysis and len(analysis.nodes) > 0:
            print("✓ Diagram generation works")
            print(f"  - Generated {len(analysis.nodes)} nodes")
            print(f"  - Generated {len(analysis.edges)} edges")
            print(f"  - Found {len(analysis.optimizations)} optimizations")
            return True
        else:
            print("✗ Diagram generation failed")
            return False
            
    except Exception as e:
        print(f"✗ Diagram generation error: {e}")
        return False

def test_api_imports():
    """Test API server imports."""
    print("\n🧪 Testing API server imports...")
    
    try:
        # Set environment for testing
        os.environ.setdefault("USE_LLM_DIAGRAMMER", "false")
        
        from api_server import app
        print("✓ API server imported")
        
        # Test that we can create the app
        if app:
            print("✓ FastAPI app created successfully")
            return True
        else:
            print("✗ FastAPI app creation failed")
            return False
            
    except Exception as e:
        print(f"✗ API server import error: {e}")
        return False

def test_telemetry_store():
    """Test telemetry store functionality."""
    print("\n🧪 Testing telemetry store...")
    
    try:
        from models.telemetry import telemetry_store, TelemetryEvent, EventType
        
        # Clear store
        telemetry_store.clear()
        
        # Test basic operations
        run = telemetry_store.start_run("test-run-003")
        if not run:
            print("✗ Failed to start run")
            return False
        
        # Add an event
        event = TelemetryEvent(
            event_type=EventType.STEP_LOG,
            run_id="test-run-003",
            step_name="test_step"
        )
        telemetry_store.add_event(event)
        
        # End run
        ended_run = telemetry_store.end_run("test-run-003")
        if not ended_run:
            print("✗ Failed to end run")
            return False
        
        # Verify data
        events = telemetry_store.get_run_events("test-run-003")
        if len(events) == 1:
            print("✓ Telemetry store works")
            return True
        else:
            print(f"✗ Expected 1 event, got {len(events)}")
            return False
            
    except Exception as e:
        print(f"✗ Telemetry store error: {e}")
        return False

def main():
    """Run all tests."""
    print("🎯 Multi-Agent Telemetry System Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Synthetic Data Test", test_synthetic_data),
        ("Diagram Generation Test", test_diagram_generation),
        ("API Import Test", test_api_imports),
        ("Telemetry Store Test", test_telemetry_store),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Set up your .env file with API keys")
        print("2. Run: python start_server.py")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
