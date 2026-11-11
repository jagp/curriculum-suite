"""Render a gate-passing tree file as a numbered leaf list.

Usage: python render_skills_list.py <tree.json> [out.md]

Writes skills-list.md (UTF-8) beside the tree file unless an output path is
given. Only run this on a file the gate has passed. The list follows
leaf_order exactly; nothing in it is typed by hand.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")


def main(path, out=None):
    with open(path, encoding="utf-8") as f:
        tree = json.load(f)
    nodes = {n["id"]: n for n in tree["nodes"]}
    out = out or os.path.join(os.path.dirname(os.path.abspath(path)), "skills-list.md")

    lines = ["# Skills list", "", f"Goal: {tree['goal']}", ""]
    for i, nid in enumerate(tree["leaf_order"], 1):
        n = nodes[nid]
        extra = []
        if n.get("prereqs"):
            extra.append("after " + ", ".join(n["prereqs"]))
        for d in n.get("data", []):
            extra.append(f"data: {d['what']} ({d['source']})")
        if n.get("claims"):
            extra.append("has product claims to verify" if any(c.get("verify") for c in n["claims"]) else "product claims cited")
        suffix = f" [{'; '.join(extra)}]" if extra else ""
        lines.append(f"{i}. {n['skill']} ({nid}, parent {n['parent']}){suffix}")
    lines.append("")
    if tree.get("gaps"):
        lines += ["## Open gaps", ""]
        for g in tree["gaps"]:
            tag = g.get("term") or g.get("node") or ""
            lines.append(f"- {g['kind']}{' ' + tag if tag else ''}: {g['detail']}")
        lines.append("")

    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"wrote {out} ({len(tree['leaf_order'])} leaves)")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(*sys.argv[1:])
