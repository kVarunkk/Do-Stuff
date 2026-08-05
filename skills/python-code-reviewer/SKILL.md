---
name: python-code-reviewer
description: Reviews Python code by checking for type hints on all functions, Google-style docstrings, summarizing issues in a table, and refactoring with asyncio if applicable. Use this skill when the user asks to review Python code.
---

# Python Code Reviewer

This skill automates the process of reviewing Python code against a set of best practices, including type hinting, docstring standards, and potential for asynchronous refactoring.

---

## Core Guidelines & Rules

- **Type Hints:** Always check for type hints on all function definitions.
- **Docstrings:** Always check for docstrings and ensure they adhere to Google style.
- **Issue Summary:** Always output a table summarizing all identified issues.
- **Asyncio Refactoring:** Always end with a refactored version of the code using `asyncio` if applicable to the code's nature.

---

## Workflow / Instructions

1.  **Receive Code:** The model receives Python code from the user for review.
2.  **Type Hint Analysis:** Analyze all function definitions within the provided code to identify any missing or improperly used type hints.
3.  **Docstring Analysis:** Examine all function docstrings to ensure they are present and follow the Google docstring style guide.
4.  **Summarize Issues:** Compile all identified issues (missing type hints, incorrect docstring style, etc.) into a markdown table. The table should include columns for 'Function Name', 'Issue Type', and 'Description'.
5.  **Asyncio Refactoring:** Assess the code for sections that could benefit from asynchronous execution. If applicable, refactor these sections using Python's `asyncio` library. If not applicable, state that no asyncio refactoring was necessary.
6.  **Output Review:** Present the generated summary table of issues, followed by the refactored Python code (or the original code with a note if no refactoring occurred).

---

## Output Format & Edge Cases

- **Structured Output:** The output should clearly separate the issues table from the refactored code block.
- **No Refactoring:** If `asyncio` refactoring is not applicable, the model should clearly state this and present the original code (or just the issues table if no other changes were made).
- **No Issues:** If no issues are found, the table should indicate "No issues found." and the model should still provide the refactored code (or original if no refactoring).
