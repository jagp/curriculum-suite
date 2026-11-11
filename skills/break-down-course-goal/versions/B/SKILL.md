---
name: break-down-course-goal
description: Use when a course goal, its weekly goals and its success criteria (an h0 inputs.json) must be broken into a capability tree of what participants must DO with Claude (h1 tree.json). Builds evidence-up: starts from what must be observably true and works back to the goal. Writes three gate-passing versions (A/B/C), pitches, and a rendered leaf list.
---

# break-down-course-goal

Turn one client's `inputs.json` into `tree.json`: a tree rooted at the course goal, where every edge means **"the child is something the participant must be able to DO, with Claude, for its parent to happen."**

**Design choice of this skill: evidence-up.** The method does not decompose the goal from the top. It starts from the criteria and weekly goals, asks what must be *observably true* when each is met and what the participant must *do* to produce that evidence, and works back from those actions toward the goal. The goal is the last thing joined, not the first thing split. The edge meaning is the same either way; only the build order differs.

## Inputs and outputs
- **Run folder:** given by the user. Everything is read from and written to it.
- **Reads:** `<run>/inputs.json` (schema `h0-inputs/1`). Client facts come only from this file. Read nothing else about the client.
- **Writes:** `tree-A.json`, `tree-B.json`, `tree-C.json`, `tree-pitches.md`; after the pick, `tree.json`, `skills-list.md` and a line in `decisions.md`.
- **Gate:** from the folder that holds `schemas/`, run
  `python schemas/validate.py h1 <run>/tree-X.json --inputs <run>/inputs.json`
  It must print `PASS`. Fix and re-run until it does. If it cannot reach `PASS`, stop and report the remaining errors; never hand on a failing file.
- **Scripts** (in this skill's `scripts/`, all write UTF-8):
  - `order_leaves.py <tree.json>`: computes `leaf_order` from the nodes and writes it into the file. Never hand-write `leaf_order`.
  - `render_leaves.py <tree.json> [<out.md>]`: renders `leaf_order` as the numbered leaf list `skills-list.md`. Never hand-write the list.
  - `pick.py <run> <A|B|C> ["reason"]`: copies the pick to `tree.json` and appends to `decisions.md`.

## Method (version A: evidence-up)

Work in this order. Keep a scratch list as you go; only the tree is written.

### Step 0. Sort the inputs
1. Copy `goal` exactly into the tree's `goal`.
2. Sort every `constraints` entry into one of two piles:
   - **Binds the tree**: about data (where it comes from, read/write) or scope (what is in or out). Use it in Steps 2–4.
   - **Delivery**: about time, length, number of sessions, format, scheduling. Put it in `set_aside` with the constraint copied exactly and a one-line reason ("delivery constraint; the tree is about capability only"). It never shapes, sizes, splits or merges a node.
3. Read `presenter_owned` (if any) as context. These are never nodes, and no node may require the participant to do them.
4. List glossary trouble now, before building:
   - every glossary value that starts with `UNRESOLVED` or `PROVISIONAL` → an `undefined_term` gap, even if the goal does not use the term;
   - every term in the goal, weekly goals, criteria or constraints that the glossary does not define and that the tree depends on (what counts as a unit to be checked, what form a data file takes) → an `undefined_term` gap.
   Do not define any of them yourself. Where a node depends on one, word the node so it works without the definition and name the gap.

### Step 1. Write down the evidence
For **each criterion**: the evidence is its `pass_if`, read literally. Write one line: "Observable: <pass_if>, produced by <who>, from <what>."
For **each weekly goal**: write what someone else could see if it were met (a product, a record, a visible change). If the goal is about comfort or confidence and has no product, name the smallest visible behaviour that shows it (for example, "a revised version exists after the participant's own follow-up request").

### Step 2. Name the action that produces each piece of evidence
For each evidence line, ask: **"What does the participant do, with Claude, that leaves this evidence behind?"** Write it as an imperative action with an object ("Produce …", "Flag …", "Ask Claude to …"), never a topic ("Prompting", "Data literacy").
- If two evidence lines are produced by the same action, they share one action.
- Each distinct action becomes a **top-level node** (a child of the root) and gets `serves` listing every weekly goal and criterion id whose evidence it produces.
- Coverage check: every `W` and `C` id in the inputs appears in at least one top-level `serves`. If a weekly goal's evidence is really produced inside another action (a smaller version of it), that top-level action serves it too and the smaller action becomes a descendant.
- If two top-level actions depend on each other (one needs the other's product), link them with `prereqs`, not by nesting.

### Step 3. Work back from each action
For each node, ask: **"What must they be able to do, with Claude, before this can happen?"** Each new answer becomes a child.
- Only actions done **with Claude** are children. Asking Claude counts, and so does judging, checking or acting on Claude's output (that is the participant's half of the work). A step that touches neither Claude nor its output (operating another tool, sending something) is not a node: either it is covered by the profile or domain knowledge, or it is a gap ("inputs do not say who/how …").
- If the answer is **already a node** elsewhere, link it in `prereqs` instead of duplicating it.
- A prerequisite that several siblings need sits under their lowest common parent, not inside one sibling's branch; otherwise a sibling's `prereqs` can point back into a branch that needs it, which `order_leaves.py` reports as a cycle.
- Split only by this question. Never split, merge or size a node to fit sessions, labs, time or any way of teaching it.

### Step 4. Stop at the floor, and record it
Stop splitting a node when the question in Step 3 gives no new answer. The node is then a leaf and gets `floor`:
- `profile`: the participant profile already covers what comes before (quote or paraphrase which profile field).
- `domain_knowledge`: it is ordinary knowledge of the participant's own work, stated in the inputs (say where).
- `inputs_stop`: the inputs say nothing that would let you go further (say what is missing, and add a gap if it matters).
When the only remaining prerequisites are existing nodes, they are in `prereqs`; pick the reason that explains why nothing *new* is left, and say "remaining prerequisites are already nodes: …" in `detail`.

### Step 5. Data and Claude claims
- **Data.** Any node that needs data gets a `data` entry: `what`, and `source` taken from the inputs: `live`, `read-only` (real data that is read and never written back; never invented), `sample`, or `own` (the participant's own). Put the inputs sentence that states the source in `quote`, copied exactly. If the inputs do not say where the data comes from, use `UNRESOLVED`, omit `quote`, and add a `data_provenance` gap naming the node.
- **Claims.** Any node that assumes something a Claude product can do (read an attached file, revise on request, point to a source row) gets a `claims` entry with `verify: true`, unless you cite a current doc URL that states it (then `cite` instead of `verify`). Never both.

### Step 6. Join the goal
Create the root last: `parent: null`, `skill` = the goal restated as the participant's action, no `serves`, no `floor`. Point every top-level node at it. Number nodes `N1` (root) upward. Check:
- every node except the root has a parent; leaves have `floor`, non-leaves do not; only root children have `serves`;
- no time, format or scheduling words in any `skill`.

### Step 7. Order, gate, render
1. `python <skill>/scripts/order_leaves.py <run>/tree-A.json` (sets `leaf_order`; fails on a cycle, which means a `prereqs` loop to fix).
2. Gate `tree-A.json` until `PASS`.
3. Fill `gaps` with everything from Steps 0, 3, 4 and 5. Gaps are reported, never filled.

## Three versions
Every run writes three gate-passing trees from the same `inputs.json` and the same schema. B and C come from **separate fresh subagents** (never forks), each given only its brief below, the run folder path, this skill's `scripts/` path and the gate command. If the platform has no subagents, write B and C yourself and put this sentence at the top of `tree-pitches.md`: *"B and C are role-played by the same model, not independent runs."*

**Brief for B (alternate design choice: goal-down decomposition).**
"Read `<run>/inputs.json` only. Build `<run>/tree-B.json` (schema h1-tree/1) by decomposing the goal from the top: split the root goal into the actions it consists of, then split each until asking 'what must they do, with Claude, before this?' gives no new answer (then record `floor`). Edge meaning: the child is something the participant must be able to DO, with Claude, for its parent to happen. Each root child declares `serves`; every W and C id must be served. Skills are actions, not topics. Delivery constraints (time, length, format) go in `set_aside` with a reason; data constraints bind the tree; presenter-owned items are never nodes. Data sources come only from the inputs, with the inputs sentence quoted exactly, or `UNRESOLVED` plus a gap. Report every UNRESOLVED/PROVISIONAL glossary term and every undefined term as a gap; never define one. Claude product claims carry `verify: true`. Run `scripts/order_leaves.py` to set `leaf_order`, then the gate, until it prints PASS. Return one sentence arguing for your version, naming the design choice."

**Brief for C (contrarian / fact-checker).**
"Read `<run>/inputs.json` and `<run>/tree-A.json` only. Attack A's premises: for every node ask whether it is really something done *with Claude*, whether it is needed for its parent, and whether its evidence could be checked by someone other than its author. Fact-check every claim about Claude products against current docs (docs.claude.com, support.claude.com); keep `verify: true` on anything you cannot confirm, and cite the URL on anything you can. Remove what cannot be verified or measured, merge duplicates into `prereqs`, and propose the leaner or safer tree. Keep the same schema, edge meaning and rules: every W and C id served, actions not topics, floors on leaves, delivery constraints in `set_aside`, data sources quoted from the inputs or `UNRESOLVED` with a gap, undefined terms reported not defined. Write `<run>/tree-C.json`, run `scripts/order_leaves.py`, then the gate, until PASS. Return one sentence arguing for your version."

### Pitches, pick, log
1. Write `<run>/tree-pitches.md`: one line per version, `A — <one sentence>`, `B — …`, `C — …`, each naming its design choice. No version is marked recommended. You may point out a factual error in any version; you do not vote.
2. The presenter picks. Run `python <skill>/scripts/pick.py <run> <A|B|C> "<reason given, if any>"`. Before proposing, read `decisions.md` if it exists so you do not re-propose something already rejected.
3. Gate `tree.json` once more, then `python <skill>/scripts/render_leaves.py <run>/tree.json` → `<run>/skills-list.md`.

## Report (to the user, at the end of a run)
- the files written;
- the gate output for each version;
- every gap (undefined terms, data provenance, other), as listed in the tree;
- every constraint set aside, with its reason;
- whether B and C were independent subagents or role-played.

## Invented example (generic, not from any client)
Goal: "Each volunteer organiser uses Claude to turn the sign-up sheet into a shift rota and checks every slot against the sheet." Criterion: "pass_if: one corrected slot per organiser, with the sign-up row it was checked against."
- Step 1 evidence: "a corrected slot plus the row it was checked against exists for every organiser."
- Step 2 action (top-level, serves that criterion): "Check each rota slot against the sign-up sheet and correct any slot the sheet does not support, recording the row."
- Step 3 back-step: "Ask Claude to show, for each slot, the sheet row it came from" (with Claude) → child. "Open the sign-up sheet" (without Claude) → not a node; profile or gap.
- Step 4 floor on "Judge whether a row supports a slot": `domain_knowledge`, because organisers already run sign-ups.
