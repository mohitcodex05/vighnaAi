"""
skills/macro.py — Specialized skill for running learned action sequences.
"""

from skills.open_app import open_app

METADATA = {
    "name": "macro",
    "description": "Runs a sequence of learned or pre-defined actions.",
    "intents": ["macro", "workflow", "mode", "automated sequence"]
}

def execute(action: str, args: dict) -> str:
    """
    Executes a macro by its name. 
    Macros are currently stored as 'work modes' (list of apps).
    """
    apps = args.get("apps", [])
    if not apps:
        return "Macro sequence is empty."
    
    results = []
    for app in apps:
        msg = open_app(app)
        results.append(msg)
    
    return f"Macro '{action}' finished: " + ", ".join(results)
