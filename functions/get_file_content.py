import os
from google.genai import types
MAX_CHARS=10000
def get_file_content(working_directory: str, file_path: str) -> str:
    abs_working_directory=os.path.abspath(working_directory)
    abs_file_path=os.path.abspath(os.path.join(working_directory,file_path))
    if not abs_file_path.startswith(abs_working_directory):
        return f"Error: '{file_path}' is not in working directory"
    if not os.path.isfile(abs_file_path):
        return f"Error: '{file_path}' is not a file"
    file_content_string=''
    try:
            
        with open(abs_file_path,"r") as file:
            file_content_string=file.read(MAX_CHARS)
            if len(file_content_string) >= MAX_CHARS:
                file_content_string+="\n[...truncated...]" 
        return file_content_string
    except  Exception as  e:
        return f"Error: '{file_path}' could not be read: {e}"

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Returns the contents of a file in a specified directory relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The Path to file from Working Directory",
            ),
        },
    ),
)