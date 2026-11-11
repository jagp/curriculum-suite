"""Term gate: fail if any file under the given paths mentions a term from a terms file.

Usage:  python gate/term_gate.py <terms-file> <path> [<path> ...]
Exit 0 = clean, 1 = a term was found (one line per hit), 2 = usage error.

Two terms files, one script:
  client-terms.txt  client names, people, systems, domain nouns. Methods must stay client-agnostic:
                    client data reaches a skill only at runtime, through its inputs file.
  goal-terms.txt    the suite's shape (other skills, hand-offs, the course format). A worker must
                    see only its own skill's requirements, so its sandbox may not name these.
Terms files are coordinator-only and never enter a sandbox.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy code page
SCANNED_SUFFIXES = {".md", ".json", ".py", ".txt"}


def load_patterns(terms_file):
    """Each line -> a whole-word regex. Blank lines and # comments are skipped; a leading "=" means match case exactly."""
    patterns = []
    for line in terms_file.read_text(encoding="utf-8").splitlines():
        term = line.strip()
        if not term or term.startswith("#"):
            continue
        flags = 0 if term.startswith("=") else re.IGNORECASE
        term = term.lstrip("=")
        patterns.append((term, re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", flags)))
    return patterns


def files_under(paths, skip):
    """Expand each path to the text files it holds (a file stays itself; a folder is walked). The terms file is skipped."""
    for path in map(Path, paths):
        for candidate in [path] if path.is_file() else sorted(path.rglob("*")):
            if candidate.is_file() and candidate.suffix in SCANNED_SUFFIXES and candidate.resolve() != skip:
                yield candidate


def main():
    """1. Load the term patterns.  2. Scan every line of every file.  3. Print hits; exit 1 if any."""
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    terms_file = Path(sys.argv[1]).resolve()
    patterns = load_patterns(terms_file)
    hits = []
    for file in files_under(sys.argv[2:], terms_file):
        for line_number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            hits += [f"{file}:{line_number}: '{term}'" for term, pattern in patterns if pattern.search(line)]
    label = f"term gate {terms_file.name}"
    if hits:
        print(f"FAIL {label} ({len(hits)} hits)")
        print("\n".join(f"  - {hit}" for hit in hits))
        sys.exit(1)
    print(f"PASS {label} ({len(patterns)} terms)")


if __name__ == "__main__":
    main()
