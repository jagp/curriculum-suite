# General rules for your task

Read this file together with your own task spec. Nothing outside your task folder is part of your task, and inside it only the files listed at the bottom of this file.

## What you are building
A **skill**: a `SKILL.md` (with `name` and `description` frontmatter) plus any `scripts/` it needs, written into the folder your brief names. The skill is a reusable method. It must work for any client, so it contains no client, domain, people or system names. Any example you put in it is invented and generic.

## How the skill runs (runtime contract)
1. **Reads** the input files your spec lists, from a run folder the user gives it. Client facts come only from those files.
2. **Writes** its output file into the same run folder, under the file name your spec gives.
3. **Gates** itself: it runs the validator command in your spec and keeps fixing its output until the command prints `PASS`. A run that can't reach `PASS` stops and reports the remaining errors; it never hands on a failing file.
4. **Three versions** (see `references/competing-versions.md`): every run writes three gate-passing outputs, `<name>-A.json`, `<name>-B.json` and `<name>-C.json` (A primary, B a named alternate design choice, C contrarian/fact-checker). It also writes `<name>-pitches.md` with one sentence per version arguing for it. The presenter picks, the pick is copied to `<name>.json`, and the choice is appended to the run folder's `decisions.md`. B and C must come from separate subagents with their own briefs when the platform allows it; when it doesn't, the output says so.
5. **Lists are rendered, never hand-written.** Any human-readable view of the output (a list, a table, a document) is produced by a script in `scripts/` from the validated JSON. Scripts write UTF-8, whatever the console's default code page.
6. **Claude product claims** carry `verify: true` unless a current doc is cited by URL.
7. **Gaps are reported, not filled.** If an input is missing, ambiguous or undefined, the skill says so in its report. It doesn't invent data, look elsewhere, or guess client facts.
8. **Design only the output your spec names.** No time estimates, formats, scheduling or delivery decisions, unless your spec makes that its job.

## How you prove your skill works
Follow your own `SKILL.md`, cold, on the example input(s) your spec names in `examples/`, writing the output into `skill/test-run/`. Then run the gate command on it. Your task is done when the gate prints `PASS` for your test output. Copy the example inputs into `test-run/` first; don't edit them.

For this build test, produce **only the primary (A) output** and copy it to `<name>.json`. Don't spawn the B and C subagents: your `SKILL.md` must still contain their full briefs, but running them is for real runs, not for the build test.

## Your report (and nothing else)
1. The files you wrote.
2. The gate output for your test run, verbatim.
3. The design choice your version makes, in one line.
4. One sentence arguing for your version.
5. Any gap in your inputs or spec that you had to work around.

## Allowed to read (all inside your task folder)
- this file and your own spec (`spec.md`)
- the schema files in `schemas/` (`*.schema.json`)
- `references/competing-versions.md`
- the citation files your spec names in `references/`
- the example files your spec names in `examples/`

You may **run** `schemas/validate.py` (that is the gate), but don't read its source or `schemas/checks/`: the gate's error messages tell you what to fix.
