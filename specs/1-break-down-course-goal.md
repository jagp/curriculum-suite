# Task spec: break-down-course-goal

Read `task-rules.md` first. Everything there applies.

## Input → output
| | File | Schema |
|---|---|---|
| In | `inputs.json` | `schemas/h0-inputs.schema.json` |
| Out | `tree.json` | `schemas/h1-tree.schema.json` |

**Gate:** `python schemas/validate.py h1 tree.json --inputs inputs.json` (paths relative to where you run it)
**Example input:** `examples/inputs.json`
**Citations:** `references/citations-cross-cutting.md`, `references/citations-break-down-course-goal.md`

## Method requirements
1. **Derive from the inputs, never from a prior topic list.** The root is the course goal. Every edge means: the child is something the participant must be able to DO, with Claude, for its parent to happen. Every node's `skill` is an action, not a topic. The order you build in (from the goal down, or from the evidence up) is a design choice; the meaning of the edges is not.
2. **Prerequisite floor.** Stop splitting a node when asking "what must they do, with Claude, before this?" gives no new answer: either it's already in the participant profile or common domain knowledge, or it's already a node. In that last case, link it with `prereqs` rather than duplicating it. Each leaf records its floor.
3. **Every requirement is bound.** Each top-level node declares `serves`, and every weekly goal and criterion id in the inputs is served by at least one top-level node.
4. **The tree is about capability only.** No time estimates, no format, no scheduling. Don't size, split or merge a node to fit any particular way of teaching it; split only by the prerequisite floor.
5. **Data provenance.** When a node needs data, take its source from the inputs: live, read-only, sample or the participant's own. Read-only means real data that is read and not written back. It never means invented data. If the inputs don't say where data comes from, mark it `UNRESOLVED` and report the gap.
6. **Undefined terms.** If the goal, weekly goals or constraints use a term the glossary doesn't define (or marks UNRESOLVED or PROVISIONAL), report it. Don't define it yourself.
7. **Constraints.** Constraints about data or scope bind the tree. Constraints about delivery (time, length, format) go in `set_aside` with the reason; they don't shape the tree.
8. **Presenter-owned items** in the inputs are context, never nodes.
9. **Deliverable view.** A script renders `leaf_order` as a numbered leaf list (`skills-list.md`) from `tree.json`.
