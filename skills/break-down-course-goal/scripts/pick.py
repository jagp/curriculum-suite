"""Record the presenter's pick: copy tree-<V>.json to tree.json and log it.

Usage: python pick.py <run-folder> <A|B|C> ["reason the presenter gave"]
Appends one line to <run-folder>/decisions.md (UTF-8).
"""
import datetime
import os
import shutil
import sys


def main(run, version, reason):
    version = version.upper()
    if version not in ("A", "B", "C"):
        print("version must be A, B or C", file=sys.stderr)
        return 2
    src = os.path.join(run, f"tree-{version}.json")
    if not os.path.exists(src):
        print(f"missing {src}", file=sys.stderr)
        return 1
    shutil.copyfile(src, os.path.join(run, "tree.json"))
    log = os.path.join(run, "decisions.md")
    new = not os.path.exists(log)
    with open(log, "a", encoding="utf-8", newline="\n") as f:
        if new:
            f.write("# Decisions\n\n")
        f.write(f"- {datetime.date.today().isoformat()} break-down-course-goal: picked {version}"
                f" — reason: {reason or 'none given'}\n")
    print(f"tree.json <- tree-{version}.json; logged in decisions.md")
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else ""))
