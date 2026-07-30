from google.genai import types
from tools.files.read_file import read_file
from tools.files.write_file import write_file
from tools.files.delete_file import delete_file
from tools.files.list_files import list_files
from tools.skill.read_skill import read_skill
from tools.get_current_datetime import get_current_datetime
from lib.genai_client import get_client

def create_function_schema(callable):
    schema = types.FunctionDeclaration.from_callable(
    callable = callable,
    client = get_client()._api_client
).to_json_dict()

    if "parameters" not in schema:
        schema["parameters"] = {"type": "object", "properties": {}, "required": []}

    return schema 
   

write_file_schema = create_function_schema(write_file)
read_file_schema = create_function_schema(read_file)
delete_file_schema = create_function_schema(delete_file)
list_files_schema = create_function_schema(list_files)
read_skill_schema = create_function_schema(read_skill)
get_current_datetime_schema = create_function_schema(get_current_datetime)


tool_schemas = [write_file_schema, read_file_schema, delete_file_schema, list_files_schema, read_skill_schema, get_current_datetime_schema]

TOOL_MAP = { "read_file": read_file,"write_file": write_file, "delete_file": delete_file, "list_files": list_files, "read_skill": read_skill, "get_current_datetime": get_current_datetime}
