from helpers.tools.resolve_safe_path import resolve_safe_path

def read_file(path: str) -> str:
    """Read a file from the project directory.

    Args:
        path: Path relative to the project root, e.g. 'agent_workspace/data.json'
            or 'skills/job-postings-summarizer/scripts/summarize_postings.py'.
            Always include the top-level folder ('agent_workspace/' or 'skills/')
            as part of the path — do not omit it.

    Returns:
        The file contents decoded as UTF-8.
    """
    target_path = resolve_safe_path(path)

    if not target_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not target_path.is_file():
        raise IsADirectoryError(f"Path is a directory, not a file: {path}")

    content = target_path.read_text(encoding="utf-8", errors="replace")
    return content.replace("\xa0", " ")