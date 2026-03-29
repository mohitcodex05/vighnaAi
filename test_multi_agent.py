"""
test_multi_agent.py — Manual verification of the Multi-Agent system
"""

import os
from core.brain import Brain
from dotenv import load_dotenv

load_dotenv()

def test_flow():
    print("🚀 Initializing Vighna Multi-Agent System...")
    brain = Brain()
    
    # Test 1: Simple Command
    print("\n[Test 1] Simple Command: 'Open Notepad'")
    resp1 = brain.process_text("Open Notepad")
    print(f"Response: {resp1}")
    
    # Test 2: Context Resolution
    print("\n[Test 2] Context Resolution: 'Close it'")
    resp2 = brain.process_text("Close it")
    print(f"Response: {resp2}")
    
    # Test 3: Complex Plan (Macro)
    print("\n[Test 3] Complex Plan: 'Start work'")
    # Note: 'start work' requires apps to be defined in knowledge.json
    resp3 = brain.process_text("Start work")
    print(f"Response: {resp3}")

if __name__ == "__main__":
    test_flow()
