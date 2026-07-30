import os
import re

SKILLS_DIR = "./skills"

def discover_skills() -> list[dict]:
    skills = []
    if not os.path.isdir(SKILLS_DIR):
        return skills

    for entry in os.listdir(SKILLS_DIR):
        skill_md_path = os.path.join(SKILLS_DIR, entry, "SKILL.md")
        if not os.path.isfile(skill_md_path):
            continue

        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract YAML frontmatter (between --- markers)
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            continue

        frontmatter = match.group(1)
        name_match = re.search(r"name:\s*(.+)", frontmatter)
        desc_match = re.search(r"description:\s*(.+)", frontmatter)

        skills.append({
            "name": name_match.group(1).strip() if name_match else entry,
            "description": desc_match.group(1).strip() if desc_match else "",
            "location": skill_md_path,
        })

    return skills