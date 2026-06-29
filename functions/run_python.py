from asyncio import timeout
from asyncio import subprocess
from time import time
from google.genai import types
import os
import subprocess
def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    abs_working_dir=os.path.abspath(working_directory)
    abs_file_path=os.path.abspath(os.path.join(working_directory,file_path))

    if not abs_file_path.startswith(abs_working_dir):
        return f"Error: '{file_path}' is not in working directory"
    if not os.path.isfile(abs_file_path):
        return f"Error: '{file_path}' is not a file"
    if not file_path.endswith(".py"):
        return f"Error: '{file_path}' is not a python file"
    try:
        f_arge=["python", file_path]
        f_arge.extend(args)
        output=subprocess.run(f_arge,cwd=abs_working_dir,capture_output=True,text=True,check=False,timeout=30)
        final_string=f"""
        STDOUT:{output.stdout}
        STDERR:{output.stderr}"""
        if output.stdout==' 'and output.stderr==' ':
            final_string='No  output produced'
        if  output.returncode != 0:
            final_string="Exited with code :"+str(output.returncode)
        return final_string
    except Exception as e:
        return f"Error executing python file {e} "



schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a python file with Python Interpreter. Accepts additional Command line Arguments as an array",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to run, relative to the working directory (default is the working directory itself)",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Command line arguments as an array",
                items=types.Schema(
                    type=types.Type.STRING,
                    description="An optional array of strings to be used as CLI arguments for the python file",
                ),
            ),
        },
    ),
)