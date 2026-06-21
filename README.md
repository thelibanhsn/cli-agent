Agent: # 📟 CLI Agent – A Command‑Line AI Assistant with Tool Use

A minimal, extensible command‑line AI agent that can **read local files**, **search the web**, and **call a LLM** (via Groq) using the OpenAI‑compatible chat API.  
The agent demonstrates how to integrate **function calling** (tool use) into a conversational loop, making it a solid foundation for building more sophisticated autonomous agents.

---

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Extending the Agent](#extending-the-agent)
- [Testing & Debugging](#testing--debugging)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| ✅                                   | Description                                                                                                                   |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| **Tool‑enabled LLM**                 | The agent can invoke external functions (`web_search`, `read_file`) from within a chat, using Groq’s tool‑calling capability. |
| **Web search**                       | Powered by **DuckDuckGo Search (ddgs)** – returns JSON‑encoded results (title, URL, snippet).                                 |
| **Local file reading**               | Safely reads any text‑based file on the host machine (UTF‑8 with fallback).                                                   |
| **Environment‑driven configuration** | API keys and model selection are loaded from a `.env` file.                                                                   |
| **Simple CLI loop**                  | Interactive REPL (`python agent.py`) with `exit`/`quit` commands.                                                             |
| **Extensible tool registry**         | Adding new tools only requires a function definition and entry in the `TOOLS` list.                                           |

---

## Demo

bash
$ python agent.py
CLI Agent ready. Type 'exit' to quit.

You: read ./README.md
Agent: (contents of README.md printed here)

You: web search "latest python 3.12 features"
Agent: [
{
"title": "Python 3.12 Release Highlights",
"url": "https://docs.python.org/3.12/whatsnew/3.12.html",
"snippet": "Python 3.12 introduces pattern matching improvements, ..."
},
...
]

You: exit

---

## Installation

### 1️⃣ Clone the repository

git clone https://github.com/your‑username/cli-agent.git
cd cli-agent

### 2️⃣ Create a virtual environment (recommended)

python -m venv .venv
source .venv/bin/activate # Linux/macOS

# .venv\Scripts\activate # Windows PowerShell

### 3️⃣ Install dependencies

pip install -r requirements.txt

> **`requirements.txt`**

python-dotenv
requests
ddgs

### 4️⃣ Set up environment variables

Create a `.env` file in the project root:

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile # optional – defaults to this model

---

## Configuration

| Variable                       | Purpose                                              | Default                   |
| ------------------------------ | ---------------------------------------------------- | ------------------------- |
| `GROQ_API_KEY`                 | Authentication token for Groq’s API.                 | **Required**              |
| `GROQ_MODEL`                   | Model name to use (e.g., `llama-3.3-70b-versatile`). | `llama-3.3-70b-versatile` |
| `MAX_WEB_RESULTS` _(optional)_ | Max results returned by `web_search`.                | `5` (hard‑coded)          |

---

## Usage

Run the interactive REPL:

python agent.py

**Supported commands** (the agent decides which tool to call based on the user’s natural language):

- **Read a file** – e.g., `show me the contents of ./agent.py`
- **Search the web** – e.g., `what are the top 3 papers on reinforcement learning?`
- **General chat** – ask any question; the LLM will respond, possibly invoking tools automatically.

**Exit the REPL**:

exit
quit

---

## Project Structure

cli-agent/
│
├─ agent.py # Main entry point & core logic
├─ .env.example # Template for environment variables
├─ requirements.txt # Python dependencies
├─ README.md # ← you are reading this
└─ .gitignore # Excludes .env, **pycache**, etc.

---

## Extending the Agent

1. **Add a new tool function** (e.g., `weather_api`) in `agent.py`.
2. **Register it** in the `TOOLS` list with proper JSON schema for arguments.
3. **Update `TOOL_MAP`** to map the name to the Python callable.

The LLM will automatically discover the new tool via the `tools` field in the Groq request.

---

## Testing & Debugging

- **Tool errors** are returned as plain strings (e.g., `"File not found: …"`). The agent prints them verbatim, making failures obvious.
- To see the raw messages exchanged with Groq, temporarily set `print(response.text)` inside `call_groq`.
- Unit‑test individual tools by calling them directly:

python
from agent import read_file, web_search

assert "File not found" in read_file("nonexistent.txt")
assert isinstance(json.loads(web_search("python")), list)

---

## Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a feature branch (`git checkout -b my‑feature`).
3. Make your changes, add tests if applicable.
4. Submit a Pull Request with a clear description of the change.

Please follow the existing code style (PEP 8) and keep the **tool‑first** design principle intact.

---

## License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---

### Happy building! 🚀

If you run into any issues or have ideas for new tools, feel free to open an issue or start a discussion in the repository.
