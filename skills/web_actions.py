"""
skills/web_actions.py — Browser, YouTube, and web search
Migrated & extended from jarvis_groq.py
"""

import webbrowser


def open_browser(url: str = "https://www.google.com") -> str:
    webbrowser.open(url)
    return f"Opening {url}"


def open_youtube(query: str = "") -> str:
    if query:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Playing '{query}' on YouTube"
    webbrowser.open("https://www.youtube.com")
    return "Opening YouTube"


def google_search(query: str) -> str:
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching Google for '{query}'"


def open_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opening {url}"


def handle_web_intent(clean_text: str) -> str | None:
    """
    Parse web intents from natural text.
    Returns a response string if handled, None otherwise.
    """
    # Play X on YouTube
    if "play" in clean_text and "youtube" in clean_text:
        query = (clean_text
                 .replace("play", "")
                 .replace("on youtube", "")
                 .replace("youtube", "")
                 .strip())
        return open_youtube(query)

    # Just play X (assume YouTube)
    if clean_text.startswith("play "):
        query = clean_text.replace("play ", "", 1).strip()
        return open_youtube(query)

    # Open YouTube
    if "open youtube" in clean_text:
        return open_youtube()

    # Open browser / Google
    if "open browser" in clean_text or "open google" in clean_text:
        return open_browser()

    # Search for X
    if clean_text.startswith("search ") or clean_text.startswith("search for "):
        query = clean_text.replace("search for ", "").replace("search ", "").strip()
        return google_search(query)

    # Open a URL
    if "open " in clean_text and ("." in clean_text):
        possible_url = clean_text.replace("open ", "").strip()
        if "." in possible_url and " " not in possible_url:
            return open_url(possible_url)

    return None

METADATA = {
    "name": "web",
    "description": "Performs web searches, opens URLs, or plays YouTube videos.",
    "intents": ["google", "search", "lookup", "youtube", "browse", "url", "web"]
}

def execute(action: str, args: dict) -> str:
    if args is None: args = {}
    query = args.get("query", "")
    return handle_web_intent(query) or open_browser()
