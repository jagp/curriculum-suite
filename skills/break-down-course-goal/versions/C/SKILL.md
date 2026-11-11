---
name: break-down-course-goal
description: Use when a course goal in an inputs.json (schema h0-inputs/1) must be broken down into a tree of what participants must be able to DO with Claude, written as tree.json (schema h1-tree/1). Builds a lean, prove-it tree - every node, split, data source and product claim must trace to the inputs or be cut or reported - then gates it, produces three competing versions, and renders the numbered leaf list.
---

# break-down-course-goal

Turns one course goal into a capability tree. Stance: **prove it.** A node, a split, a data source or a product claim stays only if someone other than you can check it against the inputs. Anything else is cut (and listed in your run report) or reported as a gap. When two trees both satisfy the inputs, keep the smaller one.

## Parameters (ask the user if any is missing; do not guess)
- `RUN` - the run folder. It holds `inputs.json`. All outputs go here.
- `SCHEMAS` - the folder holding `validate.py` and the `*.schema.json` files.
- `SKILL_DIR` - this skill's folder (for `scripts/`).

## Inputs
Read only `RUN/inputs.json`. Client facts come only from it. Read `RUN/decisions.md` if it exists: do not re-propose a design a logged pick already rejected.

## Outputs (this list is closed; write nothing else)
| File | What |
|---|---|
| `tree-A.json`, `tree-B.json`, `tree-C.json` | three gate-passing trees |
| `tree-pitches.md` | one sentence per version, plus the independence label |
| `tree.json` | copy of the presenter's pick |
| `decisions.md` | appended pick log |
| `skills-list.md` | rendered numbered leaf list (never hand-written) |

## Method (version A)

### 1. Inventory the inputs before building anything
Make a working list (in your head or the run report, not a file) of:
- every weekly goal id (`W*`) and criterion id (`C*`): each must end up in some top-level `serves`;
- each constraint, triaged:
  - **binds the tree** if it is about data or scope (where data comes from, what may be written, what is in or out);
  - **set aside** if it is about delivery (time, length, sessions, format). Copy it exactly into `set_aside` with the reason "Delivery constraint: ...; the tree is about capability only.";
- every data source the inputs state, with the exact sentence that states it;
- terms in the goal, weekly goals, criteria and constraints that the glossary does not define, or defines with a value starting `UNRESOLVED` or `PROVISIONAL`. Also every glossary value starting `UNRESOLVED`/`PROVISIONAL`, even if unused (say so in the gap detail);
- `presenter_owned` items: context only. They never become nodes.
- what the inputs do NOT say that a step would need (for example, which Claude product or surface participants use, or the format of a file). These become `gaps` of kind `other` and stop splitting (`floor.reason: inputs_stop`).

### 2. Root
`goal` is the inputs' goal, copied byte for byte. The root node (`parent: null`) restates it as one action the participant performs.

### 3. Top-level nodes: one per independently checkable outcome
Create a root child only for an outcome a requirement (`W*`/`C*`) names. Fold a weekly goal into an existing branch when it is a step of that branch rather than a separate outcome, and list its id in that branch's `serves` anyway. Every root child carries `serves` (ids only); no other node does.

### 4. Split by the prerequisite floor only
For each node ask: **"What must they do, with Claude, before this?"**
- No new answer, because the profile already covers it -> leaf, `floor.reason: profile`, `detail` quotes the profile line.
- No new answer, because it is common domain knowledge -> leaf, `floor.reason: domain_knowledge`, `detail` says what knowledge.
- The answer would need a fact the inputs do not give -> leaf, `floor.reason: inputs_stop`, `detail` names the missing fact; add a matching gap.
- The answer is already a node -> link it with `prereqs`; do not duplicate it.
- Otherwise -> add the child.

**Prove-it test for each proposed child** (all three must hold, or cut it):
1. The edge is true: the parent cannot happen without the child.
2. You can point to input text (goal, a `W*`, a `C*`, a binding constraint) that requires it.
3. It is an action (verb first), not a topic.

A child the inputs do not require, such as a step that makes Claude do something the inputs only ask the participant to do, is cut and listed in your run report with the reason. A checking step stays with the participant: Claude certifying its own output is not a check.

Never size, split or merge a node to fit sessions, labs or time. No time, format or schedule fields.

### 5. Data provenance
For every node that touches data, add a `data` entry per source the inputs state: `live`, `read-only`, `sample` or `own`. `quote` is the input sentence that states the source, copied exactly. `read-only` means real data read and not written back; it never means invented data. If the inputs state two sources for the same data (for example, real data for the work and a sample for practice), every node that touches that data carries both: each is a required data path. If no source is stated, use `UNRESOLVED` (no quote) and add a `data_provenance` gap naming the node.

### 6. Claude product claims
Any node whose action relies on Claude doing something (reading a file, drafting, revising) gets a `claims` entry stating that capability plainly, with `verify: true`. Use `cite` instead only if you have a current docs.claude.com / support.claude.com URL that you actually checked this run. Never cite from memory.

### 7. Leaf order
`leaf_order` lists every leaf exactly once, so that nothing a leaf needs (its prereqs, and the leaves under any prereq that is not a leaf) comes after it.

### 8. Gate
From any folder, run:

```
python SCHEMAS/validate.py h1 RUN/tree-A.json --inputs RUN/inputs.json
```

Fix the file from the error messages and re-run until it prints `PASS`. If it cannot reach `PASS`, stop and report the remaining errors; never hand on a failing file.

## Three versions
Write all three to the same schema; each must pass the same gate (substitute the file name).

- **A (primary):** the method above, done by you.
- **B (alternate seed):** spawn a fresh subagent (not a fork) with this brief:
  > You build `RUN/tree-B.json` (schema `SCHEMAS/h1-tree.schema.json`) from `RUN/inputs.json` only. Read `SKILL_DIR/SKILL.md` sections "Method", steps 1, 2 and 4-8, for the rules. Design choice that differs from A: **build evidence-up, not goal-down.** Start from each criterion's `pass_if` and each weekly goal, write the smallest action that produces that evidence as a leaf, then group leaves under parents until the root (the goal) is reached. Name this choice in your report. Do not read `tree-A.json`. Gate with `python SCHEMAS/validate.py h1 RUN/tree-B.json --inputs RUN/inputs.json` until it prints PASS. Report: the file, the gate output, and one sentence arguing for B.
- **C (contrarian / fact-checker):** spawn a separate fresh subagent with this brief:
  > You build `RUN/tree-C.json` (schema `SCHEMAS/h1-tree.schema.json`) from `RUN/inputs.json`, after reading `RUN/tree-A.json`. Attack A's premises. For every node, split, data entry and claim in A, ask "prove it": which input text requires it, and could someone other than A's author check it? Cut anything that fails, merge nodes whose split the floor does not justify, keep every node and data path the inputs require, mark every Claude product claim `verify: true` unless you checked a current doc URL this run, and report every undefined term or unstated source as a gap rather than resolving it. Prefer the leaner tree. Gate with `python SCHEMAS/validate.py h1 RUN/tree-C.json --inputs RUN/inputs.json` until it prints PASS. Report: the file, the gate output, a list of what you cut or changed from A and why, and one sentence arguing for C.

If the platform cannot spawn subagents, role-play B and C yourself and write in `tree-pitches.md`: *"B and C are role-played by the same model, not independent runs."*

## Pitches, pick, log, render
1. Write `RUN/tree-pitches.md`: one heading per version, one sentence each arguing for itself, no recommendation, then the independence label (independent subagents, or the role-play sentence above).
2. Show the presenter the three versions and pitches. Point out factual errors in any version if you see them; do not vote.
3. Copy the picked file to `RUN/tree.json` and log it:
   ```
   python SKILL_DIR/scripts/pick.py RUN <A|B|C> "<presenter's reason, or empty>"
   ```
   This re-runs nothing; it copies `tree-<X>.json` to `tree.json` and appends a dated line to `RUN/decisions.md`.
4. Gate `RUN/tree.json` once more (same command, file `tree.json`).
5. Render the leaf list:
   ```
   python SKILL_DIR/scripts/render_skills_list.py RUN/tree.json RUN/skills-list.md
   ```

## Run report (to the user, not a file)
- files written;
- gate output for each version and for `tree.json`, verbatim;
- **cut list**: each node, split or claim you considered and cut, with the input text it lacked;
- every gap from `gaps`, in plain words (undefined terms, unstated sources, missing facts).
