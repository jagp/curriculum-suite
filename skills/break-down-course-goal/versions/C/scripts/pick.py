"""Copy the presenter's pick to tree.json and append it to decisions.md.

Usage: python pick.py <run-folder> <A|B|C> [reason]
"""
import datetime
import os
import shutil
import sys


def main():
    if len(sys.argv) not in (3, 4) or sys.argv[2] not in ("A", "B", "C"):
        sys.exit("usage: pick.py <run-folder> <A|B|C> [reason]")
    run, version = sys.argv[1], sys.argv[2]
    reason = sys.argv[3].strip() if len(sys.argv) == 4 else ""
    src = os.path.join(run, f"tree-{version}.json")
    if not os.path.isfile(src):
        sys.exit(f"missing {src}")
    shutil.copyfile(src, os.path.join(run, "tree.json"))
    entry = (f"- {datetime.date.today().isoformat()} break-down-course-goal: "
             f"picked {version} (tree-{version}.json -> tree.json). "
             f"Reason: {reason or 'none given'}\n")
    with open(os.path.join(run, "decisions.md"), "a", encoding="utf-8", newline="\n") as f:
        f.write(entry)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(entry.strip())


if __name__ == "__main__":
    main()
