"""
core/context_resolver.py — Follow-up phrase detection (unchanged from original)
"""

FOLLOW_UP_PHRASES = [
    "explain again",
    "repeat",
    "say that again",
    "tell me again",
    "continue",
    "what do you mean",
    "can you elaborate",
    "explain it again",
    "go on",
    "and then",
    "tell me more",
    "more details",
]


def is_follow_up(query: str) -> bool:
    query = query.lower()
    return any(phrase in query for phrase in FOLLOW_UP_PHRASES)
