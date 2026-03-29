"""
test_macro_evolution.py — Verify Vighna's self-learning macro capabilities
"""

import os
import json
from core.brain import Brain
from dotenv import load_dotenv

load_dotenv()

def test_evolution():
    print("🧬 Testing Vighna Self-Evolution...")
    brain = Brain()
    
    # We need to run the same sequence 3 times to trigger evolution
    # (MemoryAgent history is 10, check for last 3 matching prev 3)
    
    sequence = ["Open Calculator", "Open Notepad", "Open Explorer"]
    
    print("\n[Step 1] Running sequence 1/3...")
    for cmd in sequence: brain.process_text(cmd)
    
    print("\n[Step 2] Running sequence 2/3...")
    for cmd in sequence: brain.process_text(cmd)
    
    print("\n[Step 3] Running sequence 3/3 (Evolution should trigger!)")
    for cmd in sequence: brain.process_text(cmd)
    
    # Check knowledge.json for the new macro
    knowledge_path = os.path.join("memory", "knowledge.json")
    if os.path.exists(knowledge_path):
        with open(knowledge_path, "r") as f:
            knowledge = json.load(f)
            modes = knowledge.get("work_modes", {})
            learned = [m for m in modes if m.startswith("macro_")]
            if learned:
                print(f"✅ Success! Learned macros: {learned}")
                print(f"Macro content: {modes[learned[0]]}")
                
                # Test the macro
                print(f"\n[Step 4] Testing the learned macro: '{learned[0]}'")
                resp = brain.process_text(f"Run {learned[0]}")
                print(f"Response: {resp}")
            else:
                print("❌ Evolution failed: No macro learned.")
    else:
        print("❌ Evolution failed: knowledge.json not found.")

if __name__ == "__main__":
    test_evolution()
