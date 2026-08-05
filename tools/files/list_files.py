from helpers.tools.resolve_safe_path import resolve_safe_path

def list_files(directory: str = ".") -> str:
    """Lists files and subdirectories inside a given directory within the project.

    Use this before reading or writing files to see what already exists, or to check
    whether a specific file is present before creating/overwriting it.

    Args:
        directory: Path relative to the project root, e.g. 'agent_workspace' or
            'skills/job-postings-summarizer'. Defaults to the project root itself (".").
            Always include the top-level folder ('agent_workspace/' or 'skills/')
            when listing inside one of them — do not omit it.

    Returns:
        A newline-separated list of entries, with directories marked by a trailing '/'.
        Returns "(empty directory)" if there are no entries.

    Raises:
        ValueError: If the resolved path is outside the project root.
        NotADirectoryError: If the given path exists but is not a directory.
        FileNotFoundError: If the given directory does not exist.
    """
    safe_path = resolve_safe_path(directory)

    if not safe_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not safe_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    entries = sorted(safe_path.iterdir(), key=lambda p: p.name)
    if not entries:
        return "(empty directory)"

    lines = [f"{entry.name}/" if entry.is_dir() else entry.name for entry in entries]
    return "\n".join(lines)