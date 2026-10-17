from platform import system
from google.genai import client
import os
import sys
import time
from dotenv import load_dotenv
from google import genai

from google.genai import types
from functions.write_file import write_file,schema_write_file
from functions.get_file_content import get_file_content,schema_get_file_content
from functions.run_python import run_python_file,schema_run_python_file
from functions.get_files_info import get_files_info,schema_get_files_info

from call_function import call_function, working_directory

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY is not set. Please set it via export GEMINI_API_KEY='...' or .env", flush=True)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    system_prompt = """You are an expert CLI-based AI coding assistant, code reviewer, and software architect.

Your primary responsibilities are:
1. **Code Review:** Analyze code for bugs, security vulnerabilities, performance bottlenecks, and stylistic improvements. Provide strict, constructive, and actionable feedback.
2. **Coding Assistance:** Write clean, modular, efficient, and well-documented code. Follow industry-standard best practices and idiomatic patterns for the requested language.
3. **Contextual Analysis:** You have access to the user's local filesystem context via tools. Proactively use these tools to inspect file contents, understand project structures, and read dependencies before suggesting architectural changes or deep refactors.

When a user asks a question or makes a request, make a function call to:
- List files and directories
- Read the content of a file
- Write to a file (create or update)
- Run a Python file with optional arguments

Communication Guidelines:
- **Be Concise and Terminal-Friendly:** You are operating in a CLI environment. Avoid unnecessary conversational filler, greetings, or lengthy conclusions.
- **Format Code Clearly:** Always use Markdown code blocks with the correct language tags.
- **Explain the "Why":** When suggesting a change or refactor, briefly explain the underlying reasoning (e.g., "Using a set here reduces lookup time from O(n) to O(1)").
- **Focus on Security and Edge Cases:** Always consider unexpected inputs, error handling, and potential failure points in the code you write or review.
"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <prompt> [target_directory]", flush=True)
        sys.exit(1)

    verbose_flag = False
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag = True

    prompt = sys.argv[1]
    print(f"\n🚀 AI Agent Started", flush=True)
    print(f"📁 Target Workspace: {working_directory}", flush=True)
    print(f"💬 Prompt: \"{prompt}\"\n", flush=True)

    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ],
    )
    
    config = types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt,
    )
    max_iter = 10

    FALLBACK_MODELS = [
        'gemini-3.6-flash',
        'gemini-3.5-flash',
        'gemini-3.1-flash-lite',
        'gemini-3.5-flash-lite',
        'gemini-flash-lite-latest',
        'gemini-3.8-flash',
        'gemini-3.7-flash',
    ]

    for i in range(max_iter):
        response = None
        for model_candidate in FALLBACK_MODELS:
            try:
                print(f"⏳ [Turn {i+1}/{max_iter}] Reasoning with {model_candidate}... ", end="", flush=True)
                response = client.models.generate_content(
                    model=model_candidate,
                    contents=messages,
                    config=config
                )
                if response:
                    print("✓ Received plan", flush=True)
                    break
            except Exception as e:
                err_str = str(e)
                print(f"\n⚠️  {model_candidate} overloaded/unavailable ({err_str[:70]}...). Cascading to next fallback...", flush=True)
                time.sleep(1)
                continue

        if response is None:
            print("\n❌ All Gemini fallback models are currently overloaded. Please try again in a few moments or export your own GEMINI_API_KEY.", flush=True)
            return

        if response.usage_metadata is None:
            print("Response is malformed", flush=True)
            return

        if verbose_flag:
            print(f"  [Tokens] Prompt: {response.usage_metadata.prompt_token_count} | Output: {response.usage_metadata.candidates_token_count} | Total: {response.usage_metadata.total_token_count}", flush=True)
        
        if response.candidates:
            for candidate in response.candidates:
                if candidate is None or candidate.content is None or candidate.content.parts is None:
                    continue
                messages.append(candidate.content)
                
        if response.function_calls:
            for func_c in response.function_calls:
                result = call_function(func_c, verbose=verbose_flag)
                messages.append(result)
        else:
            print(f"\n🏁 Solution Complete:\n{response.text}\n", flush=True)
            return
   
if __name__ == "__main__":
    main()
