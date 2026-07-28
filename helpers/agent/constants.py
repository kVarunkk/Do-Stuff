from tools.schedule_meeting import schedule_meeting

TOOL_MAP = {"schedule_meeting": schedule_meeting}
COMMANDS = {"/exit", "/history", "/clear", "/help"}
MAX_ITERATIONS = 15
SYSTEM_INSTRUCTIONS = 'You are a smart agent built by Varun. '
KEEP_RECENT_STEPS = 6  
