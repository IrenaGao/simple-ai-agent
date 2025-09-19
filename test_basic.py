#!/usr/bin/env python3
"""Basic test script that doesn't require external dependencies."""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_core_imports():
    """Test core module imports without external dependencies."""
    print("🧪 Testing core imports...")
    
    try:
        from models.telemetry import telemetry_store, AgentType, EventType, TelemetryEvent
        print("✓ Core telemetry models imported")
    except ImportError as e:
        print(f"✗ Failed to import core telemetry: {e}")
        return False
    
    try:
        from synthetic_telemetry import SyntheticTelemetryGenerator, generate_sample_run
        print("✓ Synthetic telemetry imported")
    except ImportError as e:
        print(f"✗ Failed to import synthetic telemetry: {e}")
        return False
    
    return True

def test_telemetry_models():
    """Test telemetry model functionality."""
    print("\n🧪 Testing telemetry models...")
    
    try:
        from models.telemetry import TelemetryEvent, EventType, AgentType, telemetry_store
        
        # Clear store
        telemetry_store.clear()
        
        # Test creating events
        event = TelemetryEvent(
            event_type=EventType.STEP_LOG,
            run_id="test-run",
            agent_type=AgentType.ORCHESTRATOR,
            step_name="test_step"
        )
        
        if event.event_type == EventType.STEP_LOG:
            print("✓ Telemetry event creation works")
        else:
            print("✗ Telemetry event creation failed")
            return False
        
        # Test store operations
        run = telemetry_store.start_run("test-run")
        telemetry_store.add_event(event)
        telemetry_store.end_run("test-run")
        
        events = telemetry_store.get_run_events("test-run")
        if len(events) == 1:
            print("✓ Telemetry store operations work")
            return True
        else:
            print(f"✗ Expected 1 event, got {len(events)}")
            return False
            
    except Exception as e:
        print(f"✗ Telemetry model error: {e}")
        return False

def test_synthetic_generation():
    """Test synthetic data generation."""
    print("\n🧪 Testing synthetic data generation...")
    
    try:
        from synthetic_telemetry import generate_sample_run
        
        # Generate sample data
        run = generate_sample_run(run_id="test-synthetic")
        
        if run and run.run_id == "test-synthetic":
            print(f"✓ Generated run with {len(run.agent_events)} events")
            print(f"  - Duration: {run.total_duration_ms:.1f}ms")
            print(f"  - Status: {run.status}")
            return True
        else:
            print("✗ Synthetic generation failed")
            return False
            
    except Exception as e:
        print(f"✗ Synthetic generation error: {e}")
        return False

def test_diagrammer_basic():
    """Test basic diagrammer functionality."""
    print("\n🧪 Testing basic diagrammer...")
    
    try:
        from synthetic_telemetry import generate_sample_run
        from agents.diagrammer import DiagrammerAgent
        
        # Generate test data
        run = generate_sample_run(run_id="test-diagram")
        
        # Test diagrammer (should work in deterministic mode)
        diagrammer = DiagrammerAgent()
        analysis = diagrammer.analyze_telemetry("test-diagram")
        
        if analysis and hasattr(analysis, 'nodes') and hasattr(analysis, 'edges'):
            print(f"✓ Generated diagram with {len(analysis.nodes)} nodes, {len(analysis.edges)} edges")
            print(f"  - Found {len(analysis.optimizations)} optimizations")
            return True
        else:
            print("✗ Diagram generation failed")
            return False
            
    except Exception as e:
        print(f"✗ Diagram generation error: {e}")
        return False

def main():
    """Run basic tests."""
    print("🎯 Basic Multi-Agent Telemetry System Test")
    print("=" * 45)
    
    tests = [
        ("Core Imports", test_core_imports),
        ("Telemetry Models", test_telemetry_models),
        ("Synthetic Generation", test_synthetic_generation),
        ("Basic Diagrammer", test_diagrammer_basic),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
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
        print("🎉 Core system is working! Ready for full setup.")
        print("\nTo run the full system:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up .env file with API keys")
        print("3. Run: python start_server.py")
    else:
        print("⚠️  Some core tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
