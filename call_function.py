from google.genai import types
from functions.get_file_content import get_file_content
from functions.run_python import run_python_file
from functions.write_file import write_file
from functions.get_files_info import get_files_info


working_directory="Calculator"

def call_function(
    function_call: types.FunctionCall, verbose: bool = False
) -> types.Content:
    if verbose:
        print(f"function call: {function_call.name}({function_call.args})")
    else:
        print(f"Calling function {function_call.name}......")
    result=' '
    if function_call.name=="get_files_info":
        result = get_files_info(working_directory,**(function_call.args or {}))
    elif function_call.name=="get_file_content":
        result = get_file_content(working_directory=working_directory,**(function_call.args or {}))
    elif function_call.name=="run_python_file":
        result = run_python_file(working_directory=working_directory,**(function_call.args or {}))
    elif function_call.name=="write_file":
        result = write_file(working_directory=working_directory,**(function_call.args or {}))
    
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
