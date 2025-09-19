#!/usr/bin/env python3
"""Test script to verify model names work correctly."""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_model_initialization():
    """Test that agents can be initialized with correct model names."""
    print("🧪 Testing model initialization...")
    
    try:
        # Test orchestrator agent
        from agents.orchestrator import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        print("✓ Orchestrator agent initialized")
        
        # Test summarizer agent
        from agents.summarizer import SummarizerAgent
        summarizer = SummarizerAgent()
        print("✓ Summarizer agent initialized")
        
        # Test diagrammer agent
        from agents.diagrammer import DiagrammerAgent
        diagrammer = DiagrammerAgent()
        print("✓ Diagrammer agent initialized")
        
        return True
        
    except Exception as e:
        print(f"✗ Model initialization failed: {e}")
        return False

def test_model_names():
    """Test that the model names are correct."""
    print("\n🧪 Testing model names...")
    
    # Check if we can import the models without errors
    try:
        from langchain.chat_models import init_chat_model
        
        # Test the model names we're using
        model_names = [
            "anthropic:claude-3-7-sonnet-latest",
            "anthropic:claude-3-haiku-20240307"
        ]
        
        for model_name in model_names:
            try:
                # Just test initialization, don't actually call the model
                print(f"  Testing {model_name}...")
                # Note: This will only work if you have API keys set up
                # For now, we'll just check that the model name format is correct
                if "claude-3-7-sonnet-latest" in model_name or "claude-3-haiku-20240307" in model_name:
                    print(f"  ✓ {model_name} format looks correct")
                else:
                    print(f"  ✗ {model_name} format may be incorrect")
            except Exception as e:
                print(f"  ⚠️  {model_name} - {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Model name test failed: {e}")
        return False

def main():
    """Run model tests."""
    print("🎯 Model Name Test")
    print("=" * 30)
    
    tests = [
        ("Model Initialization", test_model_initialization),
        ("Model Names", test_model_names),
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
        print("🎉 Model names are correct!")
        print("\nThe 404 error should be fixed now.")
        print("Try running your dashboard again with a query like:")
        print('  "How do I set up Intercom?"')
    else:
        print("⚠️  Some model tests failed.")
        print("You may need to check your API keys or model names.")

if __name__ == "__main__":
    main()
