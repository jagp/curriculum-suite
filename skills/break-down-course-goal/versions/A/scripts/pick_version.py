"""Copy the presenter's pick to tree.json and log it in decisions.md.

Usage: python pick_version.py <run_dir> <A|B|C> ["reason the presenter gave"]

Run only after the presenter has chosen. Appends one line to
<run_dir>/decisions.md; never rewrites earlier entries.
"""
import datetime
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")


def main(run_dir, version, reason=""):
    version = version.upper()
    if version not in ("A", "B", "C"):
        sys.exit("ERROR: version must be A, B or C")
    src = os.path.join(run_dir, f"tree-{version}.json")
    if not os.path.isfile(src):
        sys.exit(f"ERROR: {src} not found")
    shutil.copyfile(src, os.path.join(run_dir, "tree.json"))
    log = os.path.join(run_dir, "decisions.md")
    new = not os.path.exists(log)
    with open(log, "a", encoding="utf-8", newline="\n") as f:
        if new:
            f.write("# Decisions\n\n")
        stamp = datetime.date.today().isoformat()
        f.write(f"- {stamp} break-down-course-goal: picked tree-{version}.json"
                f" -> tree.json. Reason: {reason or '(none given)'}\n")
    print(f"tree-{version}.json -> tree.json; logged in {log}")


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    main(*sys.argv[1:])
