"""Compute leaf_order for a capability tree and write it back into the file.

Usage: python order_leaves.py <tree.json>

A leaf needs: its own prereqs, and the prereqs of every ancestor. A needed node
that is not a leaf stands for every leaf under it. The script orders leaves so
nothing a leaf needs comes after it. Ties keep the depth-first order of the tree
(children in the order they appear in `nodes`). Exits 1 on a cycle.
"""
import json
import sys


def main(path):
    with open(path, encoding="utf-8") as f:
        tree = json.load(f)
    nodes = {n["id"]: n for n in tree["nodes"]}
    children = {nid: [] for nid in nodes}
    for n in tree["nodes"]:
        if n["parent"] is not None:
            children[n["parent"]].append(n["id"])

    # depth-first order from the root, used for stable tie-breaking
    dfs = []
    stack = [tree["root"]]
    while stack:
        nid = stack.pop()
        dfs.append(nid)
        stack.extend(reversed(children[nid]))
    rank = {nid: i for i, nid in enumerate(dfs)}

    def leaves_under(nid):
        if not children[nid]:
            return {nid}
        out = set()
        for c in children[nid]:
            out |= leaves_under(c)
        return out

    leaves = [nid for nid in dfs if not children[nid]]
    needs = {}
    for leaf in leaves:
        req = set()
        cur = leaf
        while cur is not None:
            for p in nodes[cur]["prereqs"]:
                req |= leaves_under(p)
            cur = nodes[cur]["parent"]
        req.discard(leaf)
        needs[leaf] = req

    order, done = [], set()
    while len(order) < len(leaves):
        ready = [l for l in leaves if l not in done and needs[l] <= done]
        if not ready:
            stuck = [l for l in leaves if l not in done]
            print("CYCLE among leaves: " + ", ".join(stuck), file=sys.stderr)
            return 1
        nxt = min(ready, key=rank.get)
        order.append(nxt)
        done.add(nxt)

    tree["leaf_order"] = order
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("leaf_order: " + ", ".join(order))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
