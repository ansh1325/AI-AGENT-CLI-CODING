import os
from google.genai import types
def write_file(working_directory: str, file_path: str, content: str) -> str:
    abs_working_directory=os.path.abspath(working_directory)
    abs_file_path=os.path.abspath(os.path.join(working_directory,file_path))
    if not abs_file_path.startswith(abs_working_directory):
        return f"Error: '{file_path}' is not in working directory"
    parent_dir=os.path.dirname(abs_file_path)
    if not os.path.isdir(parent_dir):
        try:
            os.makedirs(parent_dir)

        except Exception as e:
            return f"Could not Create a new Directory"
    try:
        with open(abs_file_path,"w") as file:
            file.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Failed to write to {file_path}:{e}"

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file. Creates the file and parent directory if they don't exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to write to, relative to the working directory",
            ),
            "content" : types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file",
            ),
        },
    ),
)