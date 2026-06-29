from platform import system
from google.genai import client
import os
from dotenv import load_dotenv
from google import genai
import sys

from google.genai import types
from functions.write_file import write_file,schema_write_file
from functions.get_file_content import get_file_content,schema_get_file_content
from functions.run_python import run_python_file,schema_run_python_file
from functions.get_files_info import get_files_info,schema_get_files_info

from call_function import call_function
def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client=genai.Client(api_key=api_key)
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
    if len(sys.argv) <2:
        print("Usage: python main.py <prompt>")
        sys.exit(1)
    verbose_flag=False
    if len(sys.argv)==3 and sys.argv[2]=="--verbose":
        verbose_flag=True
    prompt=sys.argv[1]
    messages=[
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]


    available_functions = types.Tool(
        function_declarations=[schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file],
    )
    
    config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt)
    max_iter=10
    for i in range(max_iter):
        response =client.models.generate_content(
            model='gemini-2.5-flash',
            contents=messages,
            config=config
        )
        if response.function_calls:
            for func_c in response.function_calls:
                result=call_function(func_c,verbose=verbose_flag)
                # print(result)
        if response is None or response.usage_metadata is None:
            print("Response  is malformed")
            return
        if verbose_flag:
            print(f"Prompt Token: {response.usage_metadata.prompt_token_count}")
            print(f"Generated Token: {response.usage_metadata.candidates_token_count}")
            print(f"Total Token: {response.usage_metadata.total_token_count}")
        
        if response.candidates:
            for candidate in response.candidates:
                if candidate is None or candidate.content is None or candidate.content.parts is None:
                    continue
                messages.append(candidate.content)
                
        if response.function_calls:
            for func_c in response.function_calls:
                result=call_function(func_c,verbose=verbose_flag)
                messages.append(result)
        else:
            print(response.text)
            return
   
if __name__ == "__main__":
    main()
