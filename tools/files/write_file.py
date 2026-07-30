import os
from lib.exceptions import ConfirmationRequired
from helpers.agent.constants import WORKSPACE_ROOT

def write_file(path: str, content: str, overwrite: bool = False) -> str:
    """Writes content to a file inside the agent's workspace directory. Creates one if the file does not exists. Use this when user asks to write to a file or create one.

    Args:
        path: Relative path (including filename) to write, e.g. 'blog_post.md' or
            'reports/summary.txt'. Must resolve inside the workspace directory.
        content: The text content to write to the file.
        overwrite: Internal flag used by the harness when resuming after user approval.
            Do not set this manually — leave it as the default (False); the harness will retry with this set to True only after the user has explicitly confirmed. 
    """
    safe_path = os.path.abspath(os.path.join(WORKSPACE_ROOT, path))

    if not safe_path.startswith(WORKSPACE_ROOT):
        raise ValueError(f"Invalid path: attempted write outside workspace ({path})")

    if os.path.isfile(safe_path) and not overwrite:
        raise ConfirmationRequired(
            f"File '{path}' already exists. Overwrite it?",
            resume_args={"overwrite": True},
        )

    os.makedirs(os.path.dirname(safe_path), exist_ok=True)

    with open(safe_path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"File written: {path}"    

   