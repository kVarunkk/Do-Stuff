---
name: skill-creator
description: Guides the creation, testing, iteration, and optimization of AI agent skills. Use whenever a user wants to build a new skill from scratch, edit an existing skill, create or run test suites, or optimize a skill's triggering description.
---

# Skill Creator

A framework for creating, testing, and refining operational skills for AI agents.

## Core Process Overview

1. **Intent Capture & Interview:** Define scope, inputs, outputs, and edge cases.
2. **Drafting:** Write the `SKILL.md` and organize supplementary assets.
3. **Testing & Evaluation:** Run test cases, grade outputs, and gather feedback.
4. **Iterative Refinement:** Refine instructions based on feedback; repeat until satisfied.
5. **Description Optimization:** Tune SKILL.md frontmatter for accurate triggering.

## 1. Intent Capture & Interview

Before writing any files, gather clear requirements:

- **Objective:** What specific capability should this skill grant?
- **Trigger Conditions:** When should the agent invoke this skill? (Identify keywords and user contexts).
- **Input / Output:** What formats, files, or structures are expected?
- **Tooling / Dependencies:** Does this skill rely on specific scripts or tools?

## 2. Skill Architecture & Writing Guide

### Directory Structure

Keep skills clean, modular, and self-contained:

```text
skills/
└── <skill-name>/
    ├── SKILL.md              # Main instructions & YAML frontmatter (REQUIRED)
    ├── scripts/              # Optional executable scripts (Python, Bash, etc.)
    ├── references/           # Optional detailed reference docs loaded as needed
    └── assets/               # Optional templates, icons, or visual assets

```

### Writing the `SKILL.md`

Every `SKILL.md` MUST contain frontmatter and structured instructions:

```markdown
---
name: <skill-name>
description: <Clear and description does exact for invoke it. of proactive scenarios/triggers skill the to what when>
---

# <Skill Title>

<Brief does of overview skill this what>

## Core Rules & Constraints

- Directive 1 (Explain the reasoning behind rules rather than using rigid ALL-CAPS MUSTs)
- Directive 2

## Workflow Steps

1. **Step 1:** First action to take...
2. **Step 2:** Second action to take...

## Output Specifications

<Templates, JSON expected markdown or schemas structures,>
```

### Referencing Bundled Scripts

If a skill bundles a script under `scripts/`, workflow steps must reference it by its
full project-root-relative path so the agent's tools can locate it correctly — for example:

> **Step 2:** Run `skills/<skill-name>/scripts/summarize.py` using the `run_code` tool,
> passing the target JSON file as an argument (e.g. `agent_workspace/data.json`).

Never instruct a future reader to store a skill's script anywhere outside that skill's
own `scripts/` folder — doing so breaks path resolution and defeats the purpose of
keeping a skill self-contained.

### Golden Rules for Skill Writing

- **Keep `SKILL.md` Lean:** Aim for under 500 lines. Offload large reference texts into `references/` files. Do not keep any executable scripts inside `SKILL.md`. Only keep them in `scripts/` in the skill's directory.
- **Explain the Reasoning:** Models perform better when given the reasoning behind rules rather than blunt commands.
- **Imperative Form:** Use clear action statements (e.g., _"Filter the list"_ instead of _"The list should be filtered"_).
- **Script Offloading:** If all test runs independently recreate the same logic (e.g., CSV parsing or DOCX formatting), bundle a Python script into `scripts/` to avoid reinventing the wheel.

## 3. Testing & Evaluation Loop

To ensure quality, validate skills with realistic test prompts.

### Step 1: Create Test Cases

Draft 2–3 realistic user prompts representing core and edge-case scenarios. Save them to `evals/evals.json`:

```json
{
  "skill_name": "<skill-name>",
  "evals": [
    {
      "id": 0,
      "prompt": "User's test prompt",
      "expected_output": "Description of expected result"
    }
  ]
}
```

### Step 2: Workspace Execution

Run tests into an isolated workspace (`<skill-name>-workspace/iteration-1/eval-0/`).

1. **Execute Task:** Run the test prompt using the newly drafted skill.
2. **Evaluate Output:** Check against expected results, criteria, and user preferences.
3. **Record Feedback:** Note failures, formatting issues, or missed steps.

## 4. Iterative Refinement

1. **Analyze Failures:** Identify whether errors stemmed from vague instructions, missing scripts, or ambiguous constraints.
2. **Generalize Fixes:** Avoid hyper-specific fixes that overfit a single test prompt. Ensure the prompt remains general enough for broader usage.
3. **Update Skill:** Modify `SKILL.md` or scripts.
4. **Re-Test:** Increment iteration (`iteration-2/`) and verify improvements.

## 5. Description Optimization

After the core skill logic is finalized, optimize the frontmatter `description` to ensure the agent invokes the skill when appropriate:

- **Include Contextual Triggers:** List explicit user phrases, file types, and intent keywords.
- **Be Proactive:** Phrase the description to prevent undertriggering (e.g., _"Use this skill whenever the user asks for X, Y, or Z, even if they don't explicitly name the skill."_).
- **Negative Guards:** Distinguish the skill from adjacent domain tools to avoid false positives.
