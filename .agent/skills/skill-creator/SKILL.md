---
name: skill-creator
description: This skill provides guidance for creating effective skills.
---

# Skill Creator

This skill provides guidance for creating effective skills.

## Core Principles

### Concise is Key
Skills should be short and focused.
- **Why**: Large skills consume context window tokens and can confuse the model with irrelevant information.
- **Rule of thumb**: Keep SKILL.md under 1,000 words. Refactor large skills into multiple smaller, more specific skills, or move detailed reference material into `references/` files.

### Set Appropriate Degrees of Freedom
Define how much autonomy Claude has.
- **Low freedom**: For deterministic tasks (e.g., "Rotate this PDF"), use scripts or strict step-by-step instructions.
- **High freedom**: For creative or complex reasoning tasks (e.g., "Write a blog post"), provide guidelines, examples, and principles rather than rigid steps.

### Anatomy of a Skill
Every skill consists of a required SKILL.md file and optional bundled resources:

\`\`\`
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   ├── description: (required)
│   │   └── compatibility: (optional, rarely needed)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
\`\`\`

#### SKILL.md (required)
Every SKILL.md consists of:
- **Frontmatter** (YAML): Contains `name` and `description` fields (required). `description` dictates when the skill is triggered.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers.

#### Bundled Resources (optional)
- **scripts/**: Executable code for deterministic tasks.
- **references/**: Documentation loaded on-demand.
- **assets/**: Files used in final output (e.g., templates, images).

## Skill Creation Process

### Step 1: Understanding the Skill
Understand concrete examples of usage.
- "What functionality should this support?"
- "Can you give examples of usage?"

### Step 2: Planning Reusable Contents
Analyze examples to identify reusable scripts, references, and assets.

### Step 3: Initializing the Skill
Use `init_skill.py` (if available) or create the structure manually.

### Step 4: Edit the Skill
- **Frontmatter**: Define `name` and `description`. The description is Critical for correct triggering.
- **Body**: Write clear instructions.

### Step 5: Packaging (if applicable)
Ensure the skill is valid and packaged for distribution.

### Step 6: Iterate
Use the skill, observe performance, and refine instructions or resources.
