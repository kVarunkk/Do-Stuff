from pathlib import Path
from helpers.agent.constants import SKILLS_ROOT, WORKSPACE_ROOT

def read_file(path: str, is_skill: bool = False) -> str:
    """Read a file from the workspace or skills directory.

    Args:
        path: Path to the file. Can be relative to the respective root 
              or an absolute path pointing within the allowed directory.
        is_skill: If True, resolves relative to SKILLS_ROOT; otherwise WORKSPACE_ROOT.

    Returns:
        The file contents decoded as UTF-8.
    """
    # 1. Resolve base directory as an absolute Path object
    base_root = Path(SKILLS_ROOT if is_skill else WORKSPACE_ROOT).resolve()
    
    input_path = Path(path)

    # 2. Handle absolute vs relative input
    if input_path.is_absolute():
        target_path = input_path.resolve()
    else:
        # If relative, strip potential redundant prefixes (e.g., 'skills/...' when is_skill=True)
        clean_path_str = path.replace("\\", "/").lstrip("./")
        if is_skill and clean_path_str.startswith("skills/"):
            clean_path_str = clean_path_str[7:]  # Strip 'skills/'
            
        target_path = (base_root / clean_path_str).resolve()

    # 3. Security containment check (ensure target is strictly inside base_root)
    try:
        target_path.relative_to(base_root)
    except ValueError:
        raise ValueError(f"Access denied: Path '{target_path}' is outside allowed root '{base_root}'")

    # 4. Existence and type verification
    if not target_path.exists():
        raise FileNotFoundError(f"File not found at absolute path: {target_path}")

    if not target_path.is_file():
        raise IsADirectoryError(f"Target path is a directory, not a file: {target_path}")

    return target_path.read_text(encoding="utf-8")