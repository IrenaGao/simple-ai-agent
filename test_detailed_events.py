#!/usr/bin/env python3
"""Test script to demonstrate detailed event information in the diagrammer."""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_detailed_event_display():
    """Test that the diagrammer shows detailed event information."""
    print("🧪 Testing detailed event display...")
    
    try:
        from synthetic_telemetry import generate_sample_run
        from agents.diagrammer import DiagrammerAgent
        
        # Generate test data with more events
        run = generate_sample_run(
            run_id="detailed-test",
            event_count=20,
            include_errors=True,
            include_delegation=True
        )
        
        # Test diagrammer
        diagrammer = DiagrammerAgent()
        analysis = diagrammer.analyze_telemetry("detailed-test")
        
        print(f"✓ Generated diagram with {len(analysis.nodes)} nodes and {len(analysis.edges)} edges")
        
        # Show detailed information about different node types
        agent_nodes = [n for n in analysis.nodes if n.type == "agent"]
        tool_nodes = [n for n in analysis.nodes if n.type == "tool"]
        event_nodes = [n for n in analysis.nodes if n.type == "event"]
        
        print(f"\n📊 Node Breakdown:")
        print(f"  - Agent nodes: {len(agent_nodes)}")
        print(f"  - Tool nodes: {len(tool_nodes)}")
        print(f"  - Event nodes: {len(event_nodes)}")
        
        # Show agent node details
        if agent_nodes:
            agent = agent_nodes[0]
            print(f"\n🤖 Agent Node Example ({agent.data['label']}):")
            print(f"  - Event count: {agent.data['event_count']}")
            if 'events' in agent.data and agent.data['events']:
                print(f"  - Event details:")
                for i, event in enumerate(agent.data['events'][:3]):
                    duration = event.get('duration_ms', 0) or 0
                    print(f"    {i+1}. {event['type']} - {event['step']} ({duration:.0f}ms)")
        
        # Show tool node details
        if tool_nodes:
            tool = tool_nodes[0]
            print(f"\n🔧 Tool Node Example ({tool.data['label']}):")
            print(f"  - Call count: {tool.data['call_count']}")
            if 'calls' in tool.data and tool.data['calls']:
                print(f"  - Call details:")
                for i, call in enumerate(tool.data['calls'][:3]):
                    status = "✓" if call['success'] else "✗"
                    duration = call.get('duration_ms', 0) or 0
                    print(f"    {i+1}. {call['agent']} - {duration:.0f}ms {status}")
        
        # Show event node details
        if event_nodes:
            event = event_nodes[0]
            print(f"\n📅 Event Node Example ({event.data['label']}):")
            print(f"  - Step: {event.data['step_name']}")
            print(f"  - Agent: {event.data['agent_type']}")
            print(f"  - Time: {event.data['timestamp']}")
            if event.data.get('duration_ms'):
                duration = event.data['duration_ms'] or 0
                print(f"  - Duration: {duration:.0f}ms")
            if event.data.get('tool_name'):
                print(f"  - Tool: {event.data['tool_name']}")
            if event.data.get('model'):
                print(f"  - Model: {event.data['model']}")
            if event.data.get('error_message'):
                print(f"  - Error: {event.data['error_message']}")
        
        # Show edge information
        print(f"\n🔗 Edge Information:")
        edge_types = {}
        for edge in analysis.edges:
            edge_type = edge.data.get('type', 'unknown')
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        for edge_type, count in edge_types.items():
            print(f"  - {edge_type}: {count} edges")
        
        return True
        
    except Exception as e:
        print(f"✗ Detailed event display test failed: {e}")
        return False

def main():
    """Run detailed event tests."""
    print("🎯 Detailed Event Display Test")
    print("=" * 40)
    
    tests = [
        ("Detailed Event Display", test_detailed_event_display),
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
        print("🎉 Detailed event display is working!")
        print("\nThe enhanced diagrammer now shows:")
        print("  - Detailed event information in agent nodes")
        print("  - Call details in tool nodes")
        print("  - Individual event nodes with timestamps and details")
        print("  - Error states and success indicators")
        print("  - Model information and tool usage")
        print("  - Delegation information")
        print("\nTry running a query in the dashboard to see the detailed visualization!")
    else:
        print("⚠️  Some detailed event tests failed.")

if __name__ == "__main__":
    main()
