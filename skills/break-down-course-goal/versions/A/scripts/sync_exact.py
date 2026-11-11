"""Copy the goal into a tree file exactly, and check every copied-exactly field.

Usage: python sync_exact.py <tree.json> <inputs.json>

Sets tree.goal to inputs.goal byte for byte. Then checks that each
set_aside.constraint is one of inputs.constraints exactly, and that each
data[].quote appears verbatim somewhere in the inputs text. Prints every
mismatch and exits non-zero if there is one; it never rewrites a quote.
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def all_text(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from all_text(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from all_text(v)


def main(tree_path, inputs_path):
    with open(inputs_path, encoding="utf-8") as f:
        inputs = json.load(f)
    with open(tree_path, encoding="utf-8") as f:
        tree = json.load(f)
    tree["goal"] = inputs["goal"]
    texts = list(all_text(inputs))
    problems = []
    for s in tree.get("set_aside", []):
        if s["constraint"] not in inputs["constraints"]:
            problems.append(f"set_aside constraint not copied exactly: {s['constraint']!r}")
    for n in tree["nodes"]:
        for d in n.get("data", []):
            q = d.get("quote")
            if q is not None and not any(q in t for t in texts):
                problems.append(f"{n['id']} data quote not found verbatim in inputs: {q!r}")
    with open(tree_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)
        f.write("\n")
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print("goal synced; set_aside and quotes match inputs exactly")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
