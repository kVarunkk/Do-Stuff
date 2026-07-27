from google.genai import types
from tools.schedule_meeting import schedule_meeting
from lib.genai_client import get_client

schedule_meeting_schema = types.FunctionDeclaration.from_callable(
    callable = schedule_meeting,
    client = get_client()._api_client
).to_json_dict()