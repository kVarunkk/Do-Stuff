import json
from pathlib import Path
from typing import Dict, Any

def load_mcp_config(config_path: str = "mcp_config.json") -> Dict[str, Any]:
    """Loads MCP server configurations from a JSON file."""
    file_path = Path(config_path)
    
    if not file_path.exists():
        print(f"⚠️  Config file '{config_path}' not found. Starting without MCP servers.")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("mcpServers", {})
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing '{config_path}': {e}")
        return {}
    except Exception as e:
        print(f"❌ Failed to load '{config_path}': {e}")
        return {}