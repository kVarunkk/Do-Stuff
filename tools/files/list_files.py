import os
from helpers.agent.constants import WORKSPACE_ROOT

def list_files(directory: str = ".") -> str:
    """Lists files and subdirectories inside a given directory within the agent's workspace.

    Use this before reading or writing files to see what already exists, or to check
    whether a specific file is present before creating/overwriting it.

    Args:
        directory: Relative path to the directory to list, relative to the workspace
            root. Defaults to the workspace root itself.

    Returns:
        A newline-separated list of entries, with directories marked by a trailing '/'.
        Returns "(empty directory)" if there are no entries.

    Raises:
        ValueError: If the resolved path is outside the workspace directory.
        NotADirectoryError: If the given path exists but is not a directory.
        FileNotFoundError: If the given directory does not exist.
    """
    safe_path = os.path.abspath(os.path.join(WORKSPACE_ROOT, directory))
    if not safe_path.startswith(WORKSPACE_ROOT):
        raise ValueError(f"Invalid path: outside workspace ({directory})")

    if not os.path.exists(safe_path):
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not os.path.isdir(safe_path):
        raise NotADirectoryError(f"Not a directory: {directory}")

    entries = sorted(os.listdir(safe_path))
    if not entries:
        return "(empty directory)"

    lines = []
    for entry in entries:
        full = os.path.join(safe_path, entry)
        lines.append(f"{entry}/" if os.path.isdir(full) else entry)

    return "\n".join(lines)