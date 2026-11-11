"""Render tree.json's leaf_order as a numbered leaf list (skills-list.md).

Usage: python render_skills_list.py <tree.json> <skills-list.md>
"""
import json
import sys


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: render_skills_list.py <tree.json> <skills-list.md>")
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        tree = json.load(f)
    nodes = {n["id"]: n for n in tree["nodes"]}

    lines = ["# Skills list", "", f"Goal: {tree['goal']}", ""]
    for i, nid in enumerate(tree["leaf_order"], 1):
        node = nodes[nid]
        line = f"{i}. {node['skill']} ({nid})"
        if node.get("prereqs"):
            line += f" - needs: {', '.join(node['prereqs'])}"
        lines.append(line)

    if tree.get("gaps"):
        lines += ["", "## Open gaps", ""]
        for g in tree["gaps"]:
            label = g.get("term") or g.get("node") or g["kind"]
            lines.append(f"- {g['kind']} - {label}: {g['detail']}")

    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(f"wrote {dst} ({len(tree['leaf_order'])} leaves)")


if __name__ == "__main__":
    main()
