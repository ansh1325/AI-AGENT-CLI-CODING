from google.genai import types
from functions.get_file_content import get_file_content
from functions.run_python import run_python_file
from functions.write_file import write_file
from functions.get_files_info import get_files_info


import os
import sys

def get_working_directory() -> str:
    # Accept target directory from CLI argument if provided, or default to Calculator/current directory
    for arg in sys.argv[1:]:
        if os.path.isdir(arg):
            return os.path.abspath(arg)
    if os.path.isdir("Calculator"):
        return os.path.abspath("Calculator")
    return os.getcwd()

working_directory = get_working_directory()

def call_function(
    function_call: types.FunctionCall, verbose: bool = False, target_directory: str = None
) -> types.Content:
    work_dir = target_directory or working_directory
    if verbose:
        print(f"⚡ function call: {function_call.name}({function_call.args}) [dir: {work_dir}]", flush=True)
    else:
        print(f"⚡ Executing {function_call.name}...", flush=True)
    result=' '
    if function_call.name=="get_files_info":
        result = get_files_info(work_dir,**(function_call.args or {}))
    elif function_call.name=="get_file_content":
        result = get_file_content(working_directory=work_dir,**(function_call.args or {}))
    elif function_call.name=="run_python_file":
        result = run_python_file(working_directory=work_dir,**(function_call.args or {}))
    elif function_call.name=="write_file":
        result = write_file(working_directory=work_dir,**(function_call.args or {}))
    
    if result==' ':
        return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call.name,
                response={"error": f"Unknown function: {function_call.name}"},
            )
        ],
    )
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": result},
                )
            ],
        )
