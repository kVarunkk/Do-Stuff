---
name: server-log-parser
description: Use whenever you are asked to parse, extract, or summarize server log files. This skill filters for ERROR/CRITICAL logs, parses timestamps/codes/modules, and groups them into a structured JSON summary.
---

# Server Log Parser

A utility to parse raw server log files and categorize critical errors.

## Core Rules & Constraints

- Filter logs exclusively for lines containing "ERROR" or "CRITICAL".
- Parse lines into three distinct fields: Timestamp, Error Code, and Module Name.
- Group the final output into a JSON object where keys are Error Codes and values are lists of associated log entries.
- Maintain data integrity; do not hallucinate information not present in the log line.

## Workflow Steps

1. **Read Log:** Locate the log file path provided by the user in the `agent_workspace/` directory.
2. **Parse Lines:** Run `skills/server-log-parser/scripts/parse_logs.py` using the `run_code` tool, passing the log file path as an argument.
3. **Report:** Return the resulting JSON summary to the user.

## Output Specification (JSON)

```json
{
  "ERR_CODE": [
    {
      "timestamp": "YYYY-MM-DD HH:MM:SS",
      "module": "ModuleName",
      "message": "Original log message"
    }
  ]
}
```
