# curriculum-suite

A suite of reusable Claude skills that turn a stated course goal into a complete,
hands-on course design. Each skill reads and writes checkable files, and each stage
has a JSON schema plus a validator.

## Layout

| Path | Contents |
|---|---|
| `skills/` | The skills, one folder each (`SKILL.md`, `scripts/`, `versions/`) |
| `specs/` | Task specs handed to worker sessions |
| `schemas/` | Stage contracts (`*.schema.json`), extra checks, `validate.py`, tests |
| `gate/` | Term gate and sandbox builder for goal-blind worker runs |
| `references/` | Method references named by specs |

## Working rules

`CLAUDE.md` defines two session roles (coordinator and worker) and the rules each
follows. Read it before starting a session here.

## Client data stays out

This repo holds methods only. Client inputs, run fixtures and the client terms list
(`gate/client-terms.txt`, one term per line) are supplied locally and are ignored by git.
Before committing, check the tree with:

```bash
python gate/term_gate.py gate/client-terms.txt $(git ls-files)
```

## Tests

```bash
python schemas/tests/test_h0_h1.py
```

## Branching

GitFlow: `develop` is the integration branch, `main` holds signed-off releases.
Feature work branches `feature/<name>` off `develop`.
