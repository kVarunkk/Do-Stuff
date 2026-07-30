import os

SKILLS_ROOT = os.path.abspath("./skills")

def read_skill(skill_name: str, relative_path: str = "SKILL.md") -> str:
    """Reads SKILL.md or any auxiliary file (scripts, references, schemas) from a skill's directory.

    Args:
        skill_name: The name/folder of the skill (e.g., 'supabase-migration-checker').
        relative_path: Path to the specific file within the skill directory. 
                       Defaults to 'SKILL.md'. Examples: 'references/schema.sql', 
                       'scripts/check_indexes.py'.

    Returns:
        The text content of the requested file.
    """
    # safe_path = os.path.abspath(os.path.join(WORKSPACE_ROOT, path))
    skill_dir = os.path.abspath(os.path.join(SKILLS_ROOT, skill_name))
    target_path = os.path.abspath(os.path.join(skill_dir, relative_path))

    if not target_path.startswith(SKILLS_ROOT):
        raise ValueError(f"Invalid path traversal attempt: {relative_path}")

    if not os.path.isfile(target_path):
        raise FileNotFoundError(f"File '{relative_path}' not found in skill '{skill_name}'")

    with open(target_path, "r", encoding="utf-8") as f:
        return f.read()

    # if not safe_path.startswith(WORKSPACE_ROOT):
    #     raise ValueError(f"Invalid path: outside allowed directory ({path})")

    # if not os.path.isfile(safe_path):
    #     raise FileNotFoundError(f"File not found: {path}")

    # with open(safe_path, "r", encoding="utf-8") as f:
    #     return f.read()