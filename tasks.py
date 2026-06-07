"""
Executable tasks that the CAP agent can perform.
Replace these with your hackathon logic.
"""

import requests
from typing import Dict, Any


def summarise_news(params: Dict[str, Any]) -> str:
    """Fetch and summarise cryptocurrency news (example)."""
    query = params.get("query", "cryptocurrency news")
    # Using GNews free API – replace with your own API key or another source
    url = f"https://gnews.io/api/v4/search?q={query}&token=YOUR_API_KEY&lang=en"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])[:3]
            if not articles:
                return f"No news found for '{query}'."
            summary = "\n".join([f"• {a['title']}" for a in articles])
            return f"Latest {query}:\n{summary}"
        else:
            return f"Failed to fetch news (HTTP {response.status_code})"
    except Exception as e:
        return f"Error fetching news: {str(e)}"


def dummy_task(params: Dict[str, Any]) -> str:
    """Simple echo task for testing."""
    return f"Task executed with parameters: {params}"


# Registry of available tasks – the agent uses this to route jobs
TASK_REGISTRY = {
    "summarise_news": summarise_news,
    "dummy": dummy_task,
}
