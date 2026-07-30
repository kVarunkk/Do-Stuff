import os
from helpers.agent.constants import WORKSPACE_ROOT

def read_file(path: str) -> str:
    """Read a file from the workspace and return its text contents.

    Args:
        path: Relative path to the file within the workspace (for example
            'blog_post.md' or 'reports/summary.txt'). The path is resolved
            against the workspace root and must not escape that directory.

    Returns:
        The file contents decoded as UTF-8.

    Raises:
        ValueError: If the resolved path is outside the workspace root.
        FileNotFoundError: If the file does not exist.
    """
    safe_path = os.path.abspath(os.path.join(WORKSPACE_ROOT, path))

    if not safe_path.startswith(WORKSPACE_ROOT):
        raise ValueError(f"Invalid path: outside allowed directory ({path})")

    if not os.path.isfile(safe_path):
        raise FileNotFoundError(f"File not found: {path}")

    with open(safe_path, "r", encoding="utf-8") as f:
        return f.read()