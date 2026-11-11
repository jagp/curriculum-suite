"""Render a validated capability tree's leaf_order as a numbered leaf list.

Usage: python render_leaves.py <tree.json> [<out.md>]
Default output: skills-list.md next to the tree file. Always writes UTF-8.
"""
import json
import os
import sys


def main(tree_path, out_path):
    with open(tree_path, encoding="utf-8") as f:
        tree = json.load(f)
    nodes = {n["id"]: n for n in tree["nodes"]}

    lines = ["# Skills list", "", "Goal: " + tree["goal"], "",
             "Leaves of the capability tree, in an order where nothing a leaf needs comes after it.", ""]
    for i, nid in enumerate(tree["leaf_order"], 1):
        n = nodes[nid]
        lines.append(f"{i}. {n['skill']} ({nid})")
        if n["prereqs"]:
            lines.append(f"   - Needs first: {', '.join(n['prereqs'])}")
        fl = n.get("floor")
        if fl:
            lines.append(f"   - Floor ({fl['reason']}): {fl['detail']}")
        for d in n.get("data", []):
            lines.append(f"   - Data: {d['what']} [{d['source']}]")
        for c in n.get("claims", []):
            tag = "verify" if c.get("verify") else c.get("cite", "")
            lines.append(f"   - Claim ({tag}): {c['text']}")
    if tree["gaps"]:
        lines += ["", "## Gaps", ""]
        for g in tree["gaps"]:
            label = g.get("term") or g.get("node") or ""
            lines.append(f"- {g['kind']}{' — ' + label if label else ''}: {g['detail']}")
    if tree["set_aside"]:
        lines += ["", "## Set aside", ""]
        for s in tree["set_aside"]:
            lines.append(f"- \"{s['constraint']}\" — {s['reason']}")

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {out_path} ({len(tree['leaf_order'])} leaves)")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    tp = sys.argv[1]
    op = sys.argv[2] if len(sys.argv) == 3 else os.path.join(os.path.dirname(tp) or ".", "skills-list.md")
    main(tp, op)
