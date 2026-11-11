"""Compute leaf_order for a tree file and write it back in place.

Usage: python order_leaves.py <tree.json>

A leaf "needs" every node in its own prereqs and in its ancestors' prereqs,
transitively. A needed node that is not a leaf stands for all leaves under it.
The script orders leaves so nothing a leaf needs comes after it, keeping the
tree's own depth-first order wherever the needs allow. It exits non-zero on a
cycle or an unknown id; it never guesses.
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def main(path):
    with open(path, encoding="utf-8") as f:
        tree = json.load(f)
    nodes = {n["id"]: n for n in tree["nodes"]}
    children = {nid: [] for nid in nodes}
    for n in tree["nodes"]:
        p = n.get("parent")
        if p is not None:
            if p not in nodes:
                sys.exit(f"ERROR: {n['id']} has unknown parent {p}")
            children[p].append(n["id"])
        for q in n.get("prereqs", []):
            if q not in nodes:
                sys.exit(f"ERROR: {n['id']} has unknown prereq {q}")

    def leaves_under(nid):
        if not children[nid]:
            return [nid]
        out = []
        for c in children[nid]:
            out.extend(leaves_under(c))
        return out

    def ancestors(nid):
        out = []
        p = nodes[nid].get("parent")
        while p is not None:
            out.append(p)
            p = nodes[p].get("parent")
        return out

    def direct_needs(nid):
        """Leaves this leaf needs directly: prereqs of itself and its ancestors."""
        needed = set()
        for owner in [nid] + ancestors(nid):
            for q in nodes[owner].get("prereqs", []):
                needed.update(leaves_under(q))
        needed.discard(nid)
        return needed

    root = tree["root"]
    dfs_leaves = leaves_under(root)
    all_leaves = [nid for nid in nodes if not children[nid]]
    missing = set(all_leaves) - set(dfs_leaves)
    if missing:
        sys.exit(f"ERROR: leaves not under root {root}: {sorted(missing)}")

    order, state = [], {}

    def visit(nid, trail):
        if state.get(nid) == "done":
            return
        if state.get(nid) == "active":
            sys.exit("ERROR: prerequisite cycle: " + " -> ".join(trail + [nid]))
        state[nid] = "active"
        for need in sorted(direct_needs(nid), key=dfs_leaves.index):
            visit(need, trail + [nid])
        state[nid] = "done"
        order.append(nid)

    for leaf in dfs_leaves:
        visit(leaf, [])

    tree["leaf_order"] = order
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("leaf_order: " + ", ".join(order))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
