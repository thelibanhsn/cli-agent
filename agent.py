import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from ddgs import DDGS

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY in .env")

API_URL = "https://api.groq.com/openai/v1/chat/completions"


# -------------------------
# Tools
# -------------------------

def web_search(query: str, max_results: int = 5) -> str:
    try:
        results = []

        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title"),
                    "url": r.get("href"),
                    "snippet": r.get("body")
                })

        if not results:
            return "No search results found."

        return json.dumps(results, indent=2)

    except Exception as e:
        return f"WEB_SEARCH_ERROR: {type(e).__name__}: {str(e)}"


def read_file(path: str) -> str:
    """Read a local text file."""
    file_path = Path(path).expanduser().resolve()

    if not file_path.exists():
        return f"File not found: {file_path}"

    if not file_path.is_file():
        return f"Path is not a file: {file_path}"

    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(errors="ignore")


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current or external information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of search results to return.",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a local text/code/markdown file and return its contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Local file path."
                    }
                },
                "required": ["path"]
            }
        }
    }
]

TOOL_MAP = {
    "web_search": web_search,
    "read_file": read_file
}


# -------------------------
# Groq API
# -------------------------

def call_groq(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
        "temperature": 0.2,
    }

    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )

    if response.status_code >= 400:
        print("\nGROQ ERROR:")
        print(response.status_code)
        print(response.text)
        raise RuntimeError("Groq request failed")

    return response.json()["choices"][0]["message"]


# -------------------------
# Agent loop
# -------------------------

SYSTEM_PROMPT = """
You are a command-line AI agent.

Rules:
- Use web_search for current or external information.
- If a tool returns an error, clearly tell the user the tool failed.
- Do not invent URLs, search results, or file contents.
- Only cite URLs that came from the tool result.
"""

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]


def run_agent(user_input: str) -> str:
    messages.append({"role": "user", "content": user_input})

    while True:
        assistant_msg = call_groq(messages)
        messages.append(assistant_msg)

        tool_calls = assistant_msg.get("tool_calls")

        if not tool_calls:
            return assistant_msg.get("content", "")

        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            tool_fn = TOOL_MAP.get(tool_name)

            if not tool_fn:
                tool_result = f"Unknown tool: {tool_name}"
            else:
                try:
                    tool_result = tool_fn(**tool_args)
                except Exception as e:
                    tool_result = f"Tool error: {str(e)}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "content": tool_result
            })


# -------------------------
# CLI
# -------------------------

def main():
    print("CLI Agent ready. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            break

        answer = run_agent(user_input)
        print(f"\nAgent: {answer}\n")


if __name__ == "__main__":
    main()