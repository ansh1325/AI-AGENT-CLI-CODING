# Gemini Sandbox Developer: Autonomous CLI AI Coding Agent

An elegant, production-grade CLI AI software engineering agent built using Python and the official Google GenAI SDK. Powered by the **Gemini 2.5 Flash** model, this agent operates within a multi-turn ReAct (Reasoning and Acting) execution loop, featuring sandboxed local file system analysis, autonomous code writing, and subprocess code verification.

---

## 📺 Project Demo Video

> [!IMPORTANT]
> **Insert your video link here!** Paste your published video link inside the brackets below.
> 
> 👇 **Paste Link Here** 👇
> 
> [![Watch the Demo Video](https://img.youtube.com/vi/YOUR_VIDEO_ID_HERE/0.jpg)](PASTE_YOUR_VIDEO_LINK_HERE)
> 
> *(Click above to watch the agent analyze, modify, compile, and run tests on the sandbox codebase entirely on its own.)*

---

## 🚀 Key Capabilities

*   **Multi-Turn Agentic Reasoning:** Employs an iterative execution loop (up to 10 iterations) to discover directories, read files, plan implementations, write modifications, and run unit tests.
*   **Secure Directory Sandboxing:** Prevents path traversal vulnerabilities and system corruption. All file modifications and subprocess executions are structurally confined to the [Calculator](./Calculator) sandbox.
*   **Structured Tool Integration:** Utilizes native Gemini function-calling schemas (`types.FunctionDeclaration`) rather than fragile regex-parsing of raw text.
*   **Real-time Diagnostics:** Supports a `--verbose` logging mode to track prompt token metrics, candidate token metrics, and active tool calls.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User([User Prompt]) --> Main[main.py Orchestrator]
    Main --> Gemini{Gemini 2.5 Flash}
    
    subgraph Tool Call Evaluation Loop (Max 10 iterations)
        Gemini -- Returns Tool Calls --> Router[call_function.py Router]
        Router -- Safe Path Resolving --> Tools[Tools API]
        Tools -- Executes inside Sandbox --> Sandbox[(Calculator Sandbox)]
        Sandbox -- Output/Error --> Tools
        Tools -- Formatted Response --> Main
        Main -- Appends Context --> Gemini
    end
    
    Gemini -- Final Answer --> User
```

The system runs a **ReAct loop**:
1. The user launches [main.py](./main.py) with a task.
2. The orchestrator prepares the system instructions and starts a generating session using Gemini 2.5 Flash.
3. The model reviews its available tools and decides what tools to call (e.g. `get_files_info` or `get_file_content`).
4. [call_function.py](./call_function.py) routes and executes these actions within the isolated [Calculator](./Calculator) directory.
5. The result is returned to the model as a `tool` role message.
6. This cycle repeats until the agent determines the task is complete and outputs the final solution.

---

## 📂 Repository Tour

This repository is designed with modularity, separating agent-execution logic from the target workspace sandbox:

*   [main.py](./main.py): The primary orchestrator. Configures the system instructions, initializes the Gemini client, registers schemas, and controls the execution loop.
*   [call_function.py](./call_function.py): The routing hub that maps the agent's function-calling requests to concrete Python tools while enforcing the sandbox directory scope.
*   [tests.py](./tests.py): A test script to verify functions are resolving files and catching out-of-bounds traversal requests.
*   [pyproject.toml](./pyproject.toml): Configures project metadata and locks dependencies (`google-genai` and `python-dotenv`).

### 🛠️ Agent Tools (Sub-modules)
The core agent features are modularized within the `functions/` directory:
*   [functions/get_files_info.py](./functions/get_files_info.py): Lists files in a given directory, returning file sizes and directory statuses.
*   [functions/get_file_content.py](./functions/get_file_content.py): Reads and returns the content of files (safely truncating output to `10,000` characters to protect context length).
*   [functions/run_python.py](./functions/run_python.py): Spawns a subprocess to execute Python files, capturing stdout and stderr. Includes a `30-second` safety timeout.
*   [functions/write_file.py](./functions/write_file.py): Writes source code modifications, automatically creating intermediate directories if they do not exist.

### 🧪 Target Sandbox (`Calculator/`)
The agent is restricted to working in this environment. It contains a mini-application:
*   [Calculator/main.py](./Calculator/main.py): Entry point for the calculator, displaying JSON outputs.
*   [Calculator/pkg/calculator.py](./Calculator/pkg/calculator.py): Evaluates mathematical expression strings using Dijkstra's Shunting-yard algorithm.
*   [Calculator/pkg/render.py](./Calculator/pkg/render.py): Formats computation results into standardized JSON outputs.
*   [Calculator/tests.py](./Calculator/tests.py): Standard suite of unit tests for verifying arithmetic capabilities.

---

## ⚙️ Getting Started

### 📋 Prerequisites
*   Python 3.12 or newer
*   A Gemini API Key (obtained from [Google AI Studio](https://aistudio.google.com/))
*   [uv](https://github.com/astral-sh/uv) (recommended) or `pip`

### 🔧 Installation
Clone the repository and install dependencies:

```bash
# Install dependencies using uv
uv sync

# Or using standard pip
pip install -r requirements.txt
```

### 🔑 Environment Setup
Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🚀 Execution & Usage

Run the agent by executing [main.py](./main.py) with a description of the task:

```bash
# Example: Ask the agent to find and fix a bug in the calculator
python main.py "Locate the calculator implementation, run tests.py to verify it works, then add power '**' support to calculator.py and update the tests to verify it works."
```

### 🔍 Verbose Mode
Use the `--verbose` flag to monitor the model's function calls and detailed token counts:

```bash
python main.py "Run the tests and tell me if they pass" --verbose
```

---

## 💡Architectural Choices

### 1. Robust Path Resolution & Traversals Prevention
**Q: How does the agent prevent write operations or commands on the host machine?**
Every tool resolves pathways using `os.path.abspath`. The path resolver checks if the targeted resource resides within the absolute path of the sandbox directory:
```python
abs_working_dir = os.path.abspath(working_directory)
abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))

if not abs_file_path.startswith(abs_working_dir):
    return f"Error: '{file_path}' is not in working directory"
```
If a path escapes the boundary (e.g. `../etc/passwd`), the operation halts and returns an error immediately.

### 2. High-Performance Context Management
**Q: How do you handle large files that could bloat the LLM's context window?**
In [functions/get_file_content.py](./functions/get_file_content.py), file content retrieval is capped at `10,000` characters. If a file is exceptionally large, the tool yields a truncated response with `[...truncated...]`. This keeps the API response compact, saving prompt costs and keeping response speeds fast.

### 3. Iteration Limits and Self-Correction
**Q: What prevents the agent from running indefinitely if it encounters a persistent bug?**
The execution loop in [main.py](./main.py) features a hard limit of `max_iter = 10`. If the agent cannot solve a issue within 10 turns, the loop terminates. If a script fails during execution, the stderr output is piped back to the Gemini model in the next message, allowing the agent to read the error stack trace, correct its own code, write a fix, and run the tests again.
