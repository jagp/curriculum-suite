---
name: break-down-course-goal
description: Use when a course goal must be broken into a tree of what participants must be able to DO with Claude, rooted at the goal, split down to a prerequisite floor, with every weekly goal and success criterion bound to a branch. Reads inputs.json from a run folder, writes three gate-passing tree versions (tree-A/B/C.json) plus pitches, and renders the picked tree as a numbered skills list.
---

# Break down a course goal

Turns one client's `inputs.json` into `tree.json`: a capability tree whose root is the course goal and whose every edge means "the child is something the participant must be able to DO, with Claude, for the parent to happen". The tree is about capability only. It holds no time, format, scheduling or delivery decisions.

## Runtime contract
- **Run folder:** the folder the user names. Everything below is relative to it.
- **Reads:** `inputs.json` (schema `h0-inputs/1`), and `decisions.md` if it exists (to avoid re-proposing a version the presenter already rejected). Client facts come only from `inputs.json`. Do not look anywhere else for missing facts, and do not use any prior topic list, outline or planner export. If one is offered, stop and ask.
- **Writes:** `tree-A.json`, `tree-B.json`, `tree-C.json`, `tree-pitches.md`; after the pick, `tree.json`, `skills-list.md`, and one appended line in `decisions.md`.
- **Gate:** `python <schemas>/validate.py h1 <file> --inputs inputs.json`, where `<schemas>` is the folder holding `validate.py` and the `*.schema.json` files. Run it from the run folder on every version. A file that does not print `PASS` is never handed on.
- **Scripts** (in this skill's `scripts/`; all read and write UTF-8):
  - `sync_exact.py <tree> inputs.json` copies `goal` byte for byte and checks every copied-exactly field.
  - `order_leaves.py <tree>` computes `leaf_order`. Never hand-write it.
  - `render_skills_list.py tree.json` renders `skills-list.md` from `leaf_order`.
  - `pick_version.py <run folder> <A|B|C> "<reason>"` copies the pick to `tree.json` and logs it.

## Method (version A: top-down from the goal, by prerequisite floor)

Work in this order. Each step names what to read in `inputs.json`.

1. **Sort the inputs before building.**
   - `constraints`: put each one in exactly one bucket. *Data or scope* constraints (where data comes from, what may be written, what is in or out of scope) bind the tree. *Delivery* constraints (time, length, number of meetings, format, venue) go to `set_aside`, copied exactly, with a reason such as "Delivery constraint (time); it does not shape capability."
   - `presenter_owned`: read as context only. Never make a node from it. If a participant action depends on something the presenter supplies, the presenter's part stays out of the tree; the participant's use of it may be a node.
   - `glossary` vs. `goal`, `weekly_goals`, `constraints`: list every term those texts use that the glossary does not define, or defines with a value starting `UNRESOLVED` or `PROVISIONAL`. Also list any glossary entry marked `UNRESOLVED`/`PROVISIONAL` that a node will depend on. Each becomes a `gaps` entry of kind `undefined_term` with `term` set. Never write a definition yourself.

2. **Root.** One node, `parent: null`, `prereqs: []`, no `serves`, no `floor`. Its `skill` restates the goal as one action the participant performs with Claude. Top-level `goal` is copied exactly (run `sync_exact.py`).

3. **Top-level branches: one per distinct action the goal and weekly goals demand.** Read the goal clause by clause and each weekly goal. Each top-level node is an action (verb first, a thing done, not a topic), and declares `serves`: the `W` and `C` ids it delivers. Then check coverage: every weekly goal id and every criterion id must appear in at least one top-level `serves`. If an id fits no branch, the branch set is wrong; add or re-scope a branch. Do not drop the id.

4. **Split each node by the prerequisite-floor question only.** Ask: "What must the participant do, with Claude, before they can do this?" For each answer:
   - It is already in `participant_profile`, or it is common knowledge in the domain → no child. If this was the last answer, the node is a leaf: set `floor.reason` to `profile` or `domain_knowledge`, and quote or name the profile key in `floor.detail`.
   - It is already a node elsewhere → add that node's id to `prereqs`. Do not duplicate it.
   - The inputs say nothing that lets you go further (for example, the step happens outside Claude, or depends on facts the inputs lack) → leaf with `floor.reason: inputs_stop`, and add a matching `gaps` entry (kind `other` unless a more specific kind fits).
   - Otherwise → a new child node.
   Things participants do without Claude (opening another tool, fetching a file by hand) are not children. They are below the floor, and if the inputs do not say who does them, that is a gap.
   Never split, merge or size a node to fit a way of teaching it, a session, or a time slot. The only reason to split is the floor question.

5. **Data provenance.** For every node that needs data, add `data` entries: `what` it is, and `source` from the inputs: `live`, `read-only` (real data that is read and not written back; never invented), `sample`, or `own` (the participant's own). Put the exact inputs sentence that states the source in `quote`. If the inputs do not say where that data comes from, set `source: "UNRESOLVED"`, omit `quote`, and add a `gaps` entry of kind `data_provenance` with `node` set. A node may need two sources (for example real data for the job and sample data for practice); list both.

6. **Claude product claims.** Any node whose action assumes a Claude product can do something (accept a file, cite its input, keep a conversation's context, and so on) gets a `claims` entry. Each claim carries `verify: true` unless you cite a current doc by URL in `cite` (never both). Do not state which product, plan or surface participants use unless the inputs say so; if they don't, that is a gap.

7. **Field discipline.** `serves` only on the root's children. `floor` only on leaves. No time, length, session, format or scheduling words in any `skill`. Ids are `N1`, `N2`, ... with the root as `N1`. Write only schema fields.

8. **Order and gate.** Run, from the run folder:
   ```
   python <skill>/scripts/sync_exact.py tree-A.json inputs.json
   python <skill>/scripts/order_leaves.py tree-A.json
   python <schemas>/validate.py h1 tree-A.json --inputs inputs.json
   ```
   Fix what the gate reports and repeat until it prints `PASS`. Fix the tree, not the inputs. If it cannot reach `PASS`, stop and report the remaining errors verbatim.

### Invented illustration (not any client)
Goal: "Each volunteer coordinator uses Claude to build next month's shift roster from the sign-up sheet." One top-level branch is "Ask Claude to propose a roster that fills every shift from the sign-up sheet" (`serves` the roster weekly goal and criterion). Floor question on it: "Give Claude the sign-up sheet" is a new child; "read a roster" is in the profile, so it stops there (`floor.reason: profile`). If the inputs never say whether the sheet is real or a practice copy, its `data.source` is `UNRESOLVED` and a `data_provenance` gap is logged.

## Three versions
Every run writes three gate-passing trees from the same `inputs.json`, all in the `h1-tree/1` schema, so they compare side by side. No version is marked recommended. Before writing B or C, read `decisions.md` if present and do not re-propose a design the presenter rejected.

- **A (primary):** you, following the Method above. Output `tree-A.json`.
- **B (alternate seed):** spawn a fresh subagent (never a fork) with the brief below. Output `tree-B.json`.
- **C (contrarian / fact-checker):** spawn a second fresh subagent (never a fork) with the brief below. Output `tree-C.json`.

Give each subagent only: its brief, the run folder path, the path to this skill's `scripts/`, and the gate command. Do not give it A's tree.

### Brief for B
> You are writing version B of a capability tree for a course goal. Read `inputs.json` in the run folder (and `decisions.md` if present). Output `tree-B.json` in schema `h1-tree/1`, gated by `python <schemas>/validate.py h1 tree-B.json --inputs inputs.json` until it prints `PASS`.
> Your design choice, which must genuinely differ from the primary: **build bottom-up from the evidence.** Start from each success criterion (`criteria`) and ask "what observable action, done with Claude, produces this evidence?" Group those actions into top-level branches by the evidence they produce, then add only the parent actions the goal needs to connect them, and only then fill weekly goals that no evidence branch yet serves. The edge meaning does not change: a child is something the participant must be able to DO, with Claude, for its parent to happen.
> Rules you share with every version: root is the goal; every `skill` is an action, not a topic; split only by the prerequisite floor ("what must they do, with Claude, before this?"), linking an existing node through `prereqs` instead of duplicating it; every leaf has a `floor`; every root child has `serves`, and every W and C id is served; data sources come only from the inputs (`live`, `read-only`, `sample`, `own`), each with the exact quote, else `UNRESOLVED` plus a `data_provenance` gap; terms the glossary does not define (or marks UNRESOLVED/PROVISIONAL) go to `gaps`, never defined by you; delivery constraints (time, length, format) go to `set_aside` copied exactly with a reason; presenter-owned items are never nodes; Claude product claims carry `verify: true` unless a current doc URL is cited. No time, format or scheduling anywhere. Use only what `inputs.json` says.
> Run `scripts/sync_exact.py` and `scripts/order_leaves.py` on your file before the gate. Report: the file path, the gate output verbatim, your design choice in one line, and one sentence arguing for B.

### Brief for C
> You are version C, the contrarian and fact-checker, for a capability tree of a course goal. Read `inputs.json` in the run folder (and `decisions.md` if present). Output `tree-C.json` in schema `h1-tree/1`, gated by `python <schemas>/validate.py h1 tree-C.json --inputs inputs.json` until it prints `PASS`.
> Your stance is "prove it." Attack the premises a primary tree would make: (1) For every node, demand that it is truly needed for its parent; cut any node whose need you cannot show from the inputs, and prefer the leanest tree that still serves every W and C id. (2) Fact-check every claim about a Claude product against current official docs (docs.claude.com, support.claude.com, or the product-self-knowledge skill if available). Keep a claim only with a `cite` URL you actually checked, or with `verify: true` if you could not check it; drop any node that rests on a capability you found to be false, and say so in a `gaps` entry of kind `other`. (3) Refuse anything unmeasurable: if a node's action could not be observed by someone other than the participant, rewrite it as an observable action or remove it. (4) Treat every unstated data source, undefined term and unsaid assumption as a gap, not a fact.
> Rules you share with every version: root is the goal; every `skill` is an action; split only by the prerequisite floor, link instead of duplicating; every leaf has a `floor`; every root child has `serves`, and every W and C id is served; data sources only from the inputs with exact quotes, else `UNRESOLVED` plus a gap; never define a term yourself; delivery constraints go to `set_aside` copied exactly with a reason; presenter-owned items are never nodes. No time, format or scheduling anywhere. Use only what `inputs.json` says.
> Run `scripts/sync_exact.py` and `scripts/order_leaves.py` on your file before the gate. Report: the file path, the gate output verbatim, your design choice in one line, and one sentence arguing for C.

### If subagents can't be spawned
Write B and C yourself, each in a fresh pass from `inputs.json` following its brief, and put this line at the top of `tree-pitches.md`: *"B and C are role-played by the same model, not independent runs."*

### Pitches and the pick
1. Gate all three files. Any that fail are fixed or reported, never presented.
2. Write `tree-pitches.md`: a heading per version, its design choice in one line, and exactly one sentence arguing for it. No recommendation.
3. Show the presenter the pitches and each tree's gaps. The presenter picks.
4. Run `python <skill>/scripts/pick_version.py . <A|B|C> "<reason the presenter gave>"`, gate `tree.json`, then run `python <skill>/scripts/render_skills_list.py tree.json` to write `skills-list.md`.

## Report to the user
- Files written, and the gate output for each version and for `tree.json`.
- Every `gaps` entry, grouped by kind: undefined terms, unresolved data sources, other. These are questions for whoever owns the inputs; the skill did not answer them.
- Every `set_aside` constraint with its reason.
- Whether B and C were independent subagent runs or role-played.
