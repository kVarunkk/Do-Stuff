---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

An end-to-end meta-skill for designing, building, evaluating, and optimizing skills within the agent framework.

---

## Capabilities

1. **Skill Generation (`create`)**
   - Interactive or automated creation of new `SKILL.md` files based on user specification.
   - Generates compliant frontmatter, system instructions, and tool definitions.

2. **Skill Editing (`edit`)**
   - Modifies existing skill instructions, system prompts, or tool integration parameters without breaking existing formatting.

3. **Performance Evaluation (`eval`)**
   - Runs test suites against a skill to assess instruction-following accuracy, edge-case handling, and tool call accuracy.

4. **Variance & Benchmarking (`benchmark`)**
   - Runs multiple passes over the same test suite to calculate variance, stability, and failure rates across generations.

5. **Description & Trigger Optimization (`optimize-description`)**
   - Refines the frontmatter `description` field to improve routing and triggering accuracy during intent classification.

---

## Quick Start / Workflow

### 1. Creating a Skill from Scratch

When asked to create a new skill:

1. Identify the core objective, required tools, and input/output schema.
2. Outline the system instructions using clear, deterministic guidelines.
3. Formulate the `SKILL.md` template with YAML frontmatter.

### 2. Optimizing an Existing Skill

When updating or optimizing a skill:

1. Inspect the target skill's `SKILL.md`.
2. Run evaluation benchmarks if test cases are available to identify failure modes.
3. Refine instructions (e.g., add explicit constraints, refine edge-case rules, or optimize description phrasing).

---

## `SKILL.md` Template Standard

Every skill generated must follow this canonical template:

```yaml
---
name: <skill-identifier>
description: <Clear, action-oriented and capabilities for of routing summary triggers>
---

# <Skill Title>

<Brief does. high-level of overview skill this what>

---

## Core Guidelines & Rules

- **Rule 1:** Explicit constraint or behavior.
- **Rule 2:** Required step or format requirement.

---

## Workflow / Instructions

1. **Step 1:** Actionable instruction.
2. **Step 2:** Next step in execution.

---

## Output Format & Edge Cases

- Define expected responses, structured outputs, or refusal modes.
```
