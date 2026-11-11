"""Build a goal-blind worker sandbox for one skill, then gate it.

Usage:  python gate/make_sandbox.py <skill> <sandbox-folder>

A worker sees only what its sandbox holds, so blindness is structural, not an instruction:
  task-rules.md                 <- specs/_common.md
  spec.md                       <- the skill's spec in specs/
  schemas/                      <- only the schemas and check modules this skill's gate needs, plus validate.py
  references/competing-versions.md
  references/citations-*.md     <- only this skill's sections, cut out of references/citations.md
  examples/                     <- only the example inputs the spec names
  skill/                        <- empty; the worker builds here
Then two gates run on everything except examples/ (client-style inputs may legitimately say "sessions"):
  client terms (all files) and goal terms (method files; the skill's own name is allowed).
Exit 0 = sandbox ready, 1 = a gate failed (sandbox left in place for inspection).
"""
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "gate"))
from term_gate import files_under, load_patterns  # noqa: E402  (path set just above)

# What each skill's sandbox holds. Add a skill here when its spec exists.
SKILLS = {
    "break-down-course-goal": {
        "spec": "specs/1-break-down-course-goal.md",
        "checks": ["h0", "h1"],
        "schemas": ["common", "h0-inputs", "h1-tree"],
        "citations": {"cross-cutting": "Cross-cutting (all skills)", "break-down-course-goal": "1. break-down-course-goal"},
        "examples": ["inputs.json"],
    },
}

CITATION_PREAMBLE = (
    "**Access key:** FREE = full text open · PARTIAL = excerpts, summaries or an official overview · PAID = book or paywall only.\n"
    "Links were checked by web search on 2026-10-30. Re-verify before quoting.\n"
)


def citation_section(heading):
    """Return the body of '## <heading>' in references/citations.md, up to the next '## ' or '---' rule."""
    text = (REPO / "references/citations.md").read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |^---)", text, re.MULTILINE | re.DOTALL)
    if not match:
        sys.exit(f"citations.md has no section '## {heading}'")
    return match.group(1).strip() + "\n"


def build(skill, sandbox):
    """Copy only the allowed files into a fresh sandbox folder (pseudo-steps match the layout in the docstring)."""
    config = SKILLS[skill]
    if sandbox.exists():
        shutil.rmtree(sandbox)
    (sandbox / "schemas/checks").mkdir(parents=True)
    (sandbox / "references").mkdir()
    (sandbox / "examples").mkdir()
    (sandbox / "skill").mkdir()
    shutil.copy(REPO / "specs/_common.md", sandbox / "task-rules.md")
    shutil.copy(REPO / config["spec"], sandbox / "spec.md")
    shutil.copy(REPO / "schemas/validate.py", sandbox / "schemas/validate.py")
    for name in config["schemas"]:
        shutil.copy(REPO / f"schemas/{name}.schema.json", sandbox / f"schemas/{name}.schema.json")
    for name in config["checks"]:
        shutil.copy(REPO / f"schemas/checks/{name}.py", sandbox / f"schemas/checks/{name}.py")
    shutil.copy(REPO / "references/competing-versions.md", sandbox / "references/competing-versions.md")
    for slug, heading in config["citations"].items():
        body = citation_section(heading)
        (sandbox / f"references/citations-{slug}.md").write_text(f"# Citations: {slug}\n\n{CITATION_PREAMBLE}\n{body}", encoding="utf-8")
    for name in config["examples"]:
        shutil.copy(REPO / f"specs/examples/{name}", sandbox / f"examples/{name}")


def scan(terms_path, paths, allow=()):
    """Scan paths for a terms file's terms, ignoring allowed ones. Returns hit lines.

    terms_path is repo-relative: the client list is a run input (inputs/), the goal list ships in gate/.
    """
    terms_file = (REPO / terms_path).resolve()
    patterns = [(term, pattern) for term, pattern in load_patterns(terms_file) if term not in allow]
    hits = []
    for file in files_under(paths, terms_file):
        for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            hits += [f"{file}:{number}: '{term}'" for term, pattern in patterns if pattern.search(line)]
    return hits


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in SKILLS:
        sys.exit(__doc__ + f"\nKnown skills: {', '.join(SKILLS)}")
    skill, sandbox = sys.argv[1], Path(sys.argv[2]).resolve()
    build(skill, sandbox)
    method_files = [p for p in sandbox.iterdir() if p.name != "examples"]
    hits = scan("inputs/client-terms.txt", [sandbox]) + scan("gate/goal-terms.txt", method_files, allow={skill})
    if hits:
        print(f"FAIL sandbox {sandbox} ({len(hits)} hits)")
        print("\n".join(f"  - {hit}" for hit in hits))
        sys.exit(1)
    print(f"PASS sandbox {sandbox}")


if __name__ == "__main__":
    main()
