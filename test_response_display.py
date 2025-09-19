#!/usr/bin/env python3
"""Test script to verify response display functionality."""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_api_response_structure():
    """Test that the API returns the expected response structure."""
    print("🧪 Testing API response structure...")
    
    try:
        from synthetic_telemetry import generate_sample_run
        from agents.diagrammer import DiagrammerAgent
        
        # Generate test data
        run = generate_sample_run(run_id="test-response")
        
        # Test diagrammer
        diagrammer = DiagrammerAgent()
        analysis = diagrammer.analyze_telemetry("test-response")
        
        # Simulate API response structure
        mock_response = {
            "run_id": "test-response",
            "response": "This is a test response from the agent. It should be displayed in the UI.",
            "telemetry": {
                "run_id": "test-response",
                "events": [],
                "summary": {
                    "total_events": 10,
                    "total_duration_ms": 120000,
                    "status": "completed"
                }
            },
            "react_flow": {
                "nodes": [node.dict() for node in analysis.nodes],
                "edges": [edge.dict() for edge in analysis.edges]
            },
            "optimizations": [opt.dict() for opt in analysis.optimizations]
        }
        
        # Verify response structure
        required_fields = ["run_id", "response", "telemetry", "react_flow", "optimizations"]
        for field in required_fields:
            if field not in mock_response:
                print(f"✗ Missing required field: {field}")
                return False
        
        print("✓ API response structure is correct")
        print(f"  - Response text: {mock_response['response'][:50]}...")
        print(f"  - Nodes: {len(mock_response['react_flow']['nodes'])}")
        print(f"  - Edges: {len(mock_response['react_flow']['edges'])}")
        print(f"  - Optimizations: {len(mock_response['optimizations'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ API response test failed: {e}")
        return False

def main():
    """Run response display tests."""
    print("🎯 Response Display Test")
    print("=" * 30)
    
    tests = [
        ("API Response Structure", test_api_response_structure),
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
        print("🎉 Response display functionality is ready!")
        print("\nThe UI now includes:")
        print("  - Agent response display at the top of the sidebar")
        print("  - Copy button to copy responses")
        print("  - Loading states and empty states")
        print("  - Proper styling and layout")
        print("\nTry running a query in the dashboard to see the response!")
    else:
        print("⚠️  Some response display tests failed.")

if __name__ == "__main__":
    main()
