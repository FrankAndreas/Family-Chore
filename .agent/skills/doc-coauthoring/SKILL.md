---
name: doc-coauthoring
description: This skill provides a structured workflow for guiding users through collaborative document creation.
---

# Doc Co-Authoring Workflow

This skill provides a structured workflow for guiding users through collaborative document creation. Act as an active guide, walking users through three stages: Context Gathering, Refinement & Structure, and Reader Testing.

## When to Offer This Workflow
**Trigger conditions:**
- User mentions writing documentation: "write a doc", "draft a proposal", "create a spec", "write up"
- User mentions specific doc types: "PRD", "design doc", "decision doc", "RFC"
- User seems to be starting a substantial writing task

**Initial offer:**
Offer the user a structured workflow for co-authoring the document. Explain the three stages:

1. **Context Gathering**: User provides all relevant context while Claude asks clarifying questions
2. **Refinement & Structure**: Iteratively build each section through brainstorming and editing
3. **Reader Testing**: Test the doc with a fresh Claude (no context) to catch blind spots before others read it

Explain that this approach helps ensure the doc works well when others read it (including when they paste it into Claude). Ask if they want to try this workflow or prefer to work freeform.

If user declines, work freeform. If user accepts, proceed to Stage 1.

## Stage 1: Context Gathering
**Goal:** Close the gap between what the user knows and what Claude knows, enabling smart guidance later.

### Initial Questions
Ask the user for:
- **Purpose**: What is this doc trying to achieve?
- **Audience**: Who will read it? What do they already know?
- **Key Points**: What are the main things to communicate?
- **Tone/Style**: Formal? Casual? Technical?

### Info Dumping
Ask the user to dump all relevant information they have. Encourage them to paste relevant code snippets, logs, or other context.

## Stage 2: Refinement & Structure
**Goal:** Build the document section by section, ensuring high quality and user alignment.

### Step 1: Clarifying Questions
Announce work will begin on the [SECTION NAME] section. Ask 5-10 clarifying questions about what should be included.

### Step 2: Brainstorming
For the [SECTION NAME] section, brainstorm [5-20] things that might be included.

### Step 3: Curation
Ask which points should be kept, removed, or combined. Request brief justifications to help learn priorities for the next sections.

### Step 4: Gap Check
Based on what they've selected, ask if there's anything important missing for the [SECTION NAME] section.

### Step 5: Drafting
Draft the section based on the curated points.

### Step 6: Iterative Refinement
Iterate until the user is satisfied with the section.
- Use `str_replace` to make edits (never reprint the whole doc)
- **If using artifacts:** Provide link to artifact after each edit
- **If using files:** Just confirm edits are complete

### Quality Checking
After 3 consecutive iterations with no substantial changes, ask if anything can be removed without losing important information.

When section is done, confirm [SECTION NAME] is complete. Ask if ready to move to the next section.

**Repeat for all sections.**

### Near Completion
As approaching completion (80%+ of sections done), announce intention to re-read the entire document and check for:
- Flow and consistency across sections
- Redundancy or contradictions
- Anything that feels like "slop" or generic filler
- Whether every sentence carries weight

Read entire document and provide feedback.

## Stage 3: Reader Testing
**Goal:** Validate the document's effectiveness with a simulated reader.

### Testing Approach
**If access to sub-agents is available (e.g., in Claude Code):**
Perform the testing directly without user involvement.

**If no access to sub-agents (e.g., claude.ai web interface):**
The user will need to do the testing manually.

### Step 1: Predict Reader Questions
Generate 5-10 questions that readers would realistically ask.

### Step 2: Test / Setup Testing
Test these questions against the document (using a sub-agent or manual test).

### Step 3: Run Additional Checks / Additional Checks
Check for ambiguity, false assumptions, contradictions.

### Step 4: Report and Fix / Iterate Based on Results
If issues found, report them and iterate on the problematic sections.

### Exit Condition (Both Approaches)
When Reader Claude consistently answers questions correctly and doesn't surface new gaps or ambiguities, the doc is ready.

## Final Review
When Reader Testing passes:
Announce the doc has passed Reader Claude testing. Before completion:

1. Recommend they do a final read-through themselves - they own this document and are responsible for its quality
2. Suggest double-checking any facts, links, or technical details
3. Ask them to verify it achieves the impact they wanted

Ask if they want one more review, or if the work is done.

**If user wants final review, provide it. Otherwise:**
Announce document completion. Provide a few final tips:
- Consider linking this conversation in an appendix so readers can see how the doc was developed
- Use appendices to provide depth without bloating the main doc
- Update the doc as feedback is received from real readers

## Tips for Effective Guidance
**Tone:**
- Be direct and procedural
- Explain rationale briefly when it affects user behavior
- Don't try to "sell" the approach - just execute it

**Handling Deviations:**
- If user wants to skip a stage: Ask if they want to skip this and write freeform
- If user seems frustrated: Acknowledge this is taking longer than expected. Suggest ways to move faster
- Always give user agency to adjust the process

**Context Management:**
- Throughout, if context is missing on something mentioned, proactively ask
- Don't let gaps accumulate - address them as they come up

**Artifact Management:**
- Use `create_file` for drafting full sections
- Use `str_replace` for all edits
- Provide artifact link after every change
- Never use artifacts for brainstorming lists - that's just conversation

**Quality over Speed:**
- Don't rush through stages
- Each iteration should make meaningful improvements
- The goal is a document that actually works for readers
