from lib.exceptions import ConfirmationRequired
import os
from helpers.agent.constants import WORKSPACE_ROOT

def delete_file(path: str,  _confirmed: bool = False) -> str:
    """Deletes a file inside the agent's workspace. Always requires user confirmation
    before proceeding, since deletion is irreversible.

    Args:
        path: Relative path to the file to delete, relative to the workspace root.
        _confirmed: Internal flag used by the harness when resuming after user approval.
            Do not set this manually — leave it as the default (False) when initially
            requesting a deletion; the harness will retry with this set to True only
            after the user has explicitly confirmed. 
    Returns:
        A confirmation message once the file has been deleted.

    Raises:
        ValueError: If the resolved path is outside the workspace directory.
        FileNotFoundError: If the file does not exist.
        ConfirmationRequired: Always raised on first call (no prior approval) —
            the harness should catch this, prompt the user, and retry with
            resume_args merged in to actually perform the deletion.
    """
    safe_path = os.path.abspath(os.path.join(WORKSPACE_ROOT, path))
    if not safe_path.startswith(WORKSPACE_ROOT):
        raise ValueError(f"Invalid path: outside workspace ({path})")
    if not os.path.isfile(safe_path):
        raise FileNotFoundError(f"File not found: {path}")

    if not _confirmed:
        raise ConfirmationRequired(f"Delete file '{path}'? This cannot be undone.", resume_args={"_confirmed": True})

    os.remove(safe_path)
    return f"File deleted: {path}"