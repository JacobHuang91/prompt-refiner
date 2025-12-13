"""
Shared data and tools for agent examples.

All examples use the same data to enable fair comparison of token usage.
"""

# System prompt
SYSTEM_PROMPT = "You are a helpful assistant that recommends books."

# Context documents (with HTML and extra whitespace for optimization demos)
CONTEXT_DOCUMENTS = [
    "<div><h1>Python Programming</h1><p>Python    is    a    high-level    programming    language.</p></div>",
    "<section><p>Popular    Python    books    include    'Python Crash Course'    and    'Fluent Python'.</p></section>",
    "<article>For   beginners,   focus   on   books   with   practical   examples.</article>",
]

# Message history
MESSAGE_HISTORY = [
    {"role": "user", "content": "Hi, I'm learning programming."},
    {"role": "assistant", "content": "Great! What language are you interested in?"},
    {"role": "user", "content": "I want to learn Python."},
    {"role": "assistant", "content": "Excellent choice! Python is beginner-friendly."},
]

# Current query
QUERY = "Can you recommend some Python books for beginners?"


def get_tool_schema() -> dict:
    """Get tool schema for search_books function."""
    return {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": "Search for books by query. This tool searches through our book database and returns detailed information about matching books including title, author, year, and more.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find books. Can include title, author, or topic keywords.",
                        "examples": ["Python programming", "machine learning", "Eric Matthes"],
                    }
                },
                "required": ["query"],
            },
        },
    }


def search_books(query: str) -> dict:
    """Search for books (mock implementation).

    Returns a large response with debug fields to demonstrate ResponseCompressor.
    """
    return {
        "results": [
            {
                "title": "Python Crash Course",
                "author": "Eric Matthes",
                "year": 2023,
                "description": "A hands-on, project-based introduction to programming",
                "publisher": "No Starch Press",
                "isbn": "978-1593279288",
                "pages": 544,
                "rating": 4.5,
            },
            {
                "title": "Fluent Python",
                "author": "Luciano Ramalho",
                "year": 2022,
                "description": "Clear, concise, and effective programming in Python",
                "publisher": "O'Reilly Media",
                "isbn": "978-1492056355",
                "pages": 792,
                "rating": 4.7,
            },
        ],
        "total_results": 2,
        "query_time": 0.05,
        "debug_info": "This is debug information that should be removed",
        "trace_id": "abc-123-def-456",
    }
