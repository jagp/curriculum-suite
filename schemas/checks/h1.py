"""h1 — tree.json, checked against inputs.json.

Rules JSON Schema can't express (each numbered block in check() below):
  1. The goal is the inputs' goal, copied exactly.
  2. One root (the only parentless node); ids unique; every parent and prereq id exists.
  3. "Needs" edges (parent -> child, node -> prereq) form no cycle.
  4. serves sits only on the root's children; every weekly goal and criterion id is served; no unknown ids.
  5. floor sits on every leaf and only on leaves; an already_a_node floor lists those nodes in prereqs.
  6. leaf_order holds every leaf once, and no leaf comes before a leaf it needs.
  7. No time estimates in a node's skill.
  8. Data sources quote the inputs; UNRESOLVED sources have a data_provenance gap for that node.
  9. Glossary terms marked UNRESOLVED/PROVISIONAL have an undefined_term gap; gap fields match their kind.
 10. set_aside constraints are copied exactly from the inputs.
"""
import re

SCHEMA = "h1-tree"
SOURCES = {"inputs": "h0"}

TIME_PATTERN = re.compile(r"\b\d+\s*(min|mins|minutes?|hours?|hrs?)\b", re.IGNORECASE)
NOT_YET_DEFINED = ("UNRESOLVED", "PROVISIONAL")


def squash(text):
    """Collapse runs of whitespace so a quote matches across line wraps."""
    return " ".join(text.split())


def inputs_text(inputs):
    """All client text a quote may come from, flattened into one searchable string."""
    parts = [inputs["goal"], *inputs["constraints"], *inputs["participant_profile"].values()]
    parts += [g["goal"] for g in inputs["weekly_goals"]]
    parts += [f"{c['check']} {c['pass_if']}" for c in inputs["criteria"]]
    parts += [f"{term}: {meaning}" for term, meaning in inputs["glossary"].items()]
    return squash("\n".join(parts))


def find_cycle(needs):
    """Depth-first search over the needs graph; return one cycle as a list of ids, or None.
    Colours: absent = unvisited, 1 = on the current path, 2 = finished."""
    colour = {}

    def visit(node, path):
        colour[node] = 1
        for nxt in needs.get(node, ()):
            if colour.get(nxt) == 1:
                return path[path.index(nxt):] + [nxt]
            if nxt not in colour:
                found = visit(nxt, path + [nxt])
                if found:
                    return found
        colour[node] = 2
        return None

    for start in needs:
        if start not in colour:
            found = visit(start, [start])
            if found:
                return found
    return None


def everything_needed(needs, start):
    """Every node reachable from start along needs edges (start itself excluded)."""
    seen, stack = set(), list(needs.get(start, ()))
    while stack:
        node = stack.pop()
        if node not in seen:
            seen.add(node)
            stack.extend(needs.get(node, ()))
    return seen


def check(tree, sources):
    inputs = sources["inputs"]
    errors = []
    nodes = {n["id"]: n for n in tree["nodes"]}

    # 1. goal copied exactly
    if squash(tree["goal"]) != squash(inputs["goal"]):
        errors.append("goal: must be the inputs' goal, copied exactly")

    # 2. ids unique, one root, references resolve
    ids = [n["id"] for n in tree["nodes"]]
    errors += [f"nodes: duplicate id {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    roots = [n["id"] for n in tree["nodes"] if n["parent"] is None]
    if roots != [tree["root"]]:
        errors.append(f"root: exactly one node may have parent null, and it must be root {tree['root']} (found {roots})")
    for node in tree["nodes"]:
        for ref in ([node["parent"]] if node["parent"] else []) + node["prereqs"]:
            if ref not in nodes:
                errors.append(f"{node['id']}: refers to unknown node {ref}")
        if node["id"] in node["prereqs"]:
            errors.append(f"{node['id']}: lists itself as a prereq")
    if errors:
        return errors  # later checks assume a well-formed graph

    # 3. needs graph: a parent needs its children; a node needs its prereqs
    children = {i: [] for i in nodes}
    for node in tree["nodes"]:
        if node["parent"]:
            children[node["parent"]].append(node["id"])
    needs = {i: children[i] + nodes[i]["prereqs"] for i in nodes}
    cycle = find_cycle(needs)
    if cycle:
        return errors + [f"nodes: needs-cycle {' -> '.join(cycle)} (a node can't need its own ancestor)"]
    unreachable = set(nodes) - {tree["root"]} - everything_needed({i: children[i] for i in nodes}, tree["root"])
    errors += [f"{i}: not under the root" for i in sorted(unreachable)]

    # 4. serves: only on the root's children; every W/C id served; no unknown ids
    top_level = set(children[tree["root"]])
    known = {g["id"] for g in inputs["weekly_goals"]} | {c["id"] for c in inputs["criteria"]}
    served = set()
    for node in tree["nodes"]:
        if node["id"] in top_level and not node.get("serves"):
            errors.append(f"{node['id']}: top-level node must declare serves")
        if node["id"] not in top_level and "serves" in node:
            errors.append(f"{node['id']}: serves is only allowed on the root's children")
        served |= set(node.get("serves", []))
    errors += [f"serves: unknown id {i}" for i in sorted(served - known)]
    errors += [f"serves: {i} is not served by any top-level node" for i in sorted(known - served)]

    # 5. floor on leaves only
    leaves = {i for i in nodes if not children[i]}
    for i, node in nodes.items():
        if i in leaves and "floor" not in node:
            errors.append(f"{i}: leaf must state its floor (why splitting stops)")
        if i not in leaves and "floor" in node:
            errors.append(f"{i}: floor is only allowed on leaves")
        if node.get("floor", {}).get("reason") == "already_a_node" and not node["prereqs"]:
            errors.append(f"{i}: floor already_a_node needs the nodes it relies on listed in prereqs")

    # 6. leaf_order: every leaf once, needs before needers
    order = tree["leaf_order"]
    if sorted(order) != sorted(leaves):
        missing, extra = leaves - set(order), set(order) - leaves
        errors.append(f"leaf_order: must list every leaf exactly once (missing {sorted(missing)}, not leaves {sorted(extra)}, length {len(order)} vs {len(leaves)})")
    else:
        position = {leaf: index for index, leaf in enumerate(order)}
        for leaf in order:
            for needed in everything_needed(needs, leaf) & leaves:
                if position[needed] > position[leaf]:
                    errors.append(f"leaf_order: {needed} must come before {leaf}, which needs it")

    # 7. no time estimates
    errors += [f"{i}: skill contains a time estimate" for i, n in nodes.items() if TIME_PATTERN.search(n["skill"])]

    # 8. data provenance
    source_text = inputs_text(inputs)
    provenance_gaps = {g.get("node") for g in tree["gaps"] if g["kind"] == "data_provenance"}
    for i, node in nodes.items():
        for item in node.get("data", []):
            if item["source"] == "UNRESOLVED":
                if i not in provenance_gaps:
                    errors.append(f"{i}: data '{item['what']}' is UNRESOLVED but no data_provenance gap names {i}")
            elif "quote" not in item:
                errors.append(f"{i}: data '{item['what']}' needs a quote from the inputs stating its source")
            elif squash(item["quote"]) not in source_text:
                errors.append(f"{i}: data quote not found in the inputs: '{item['quote']}'")

    # 9. gaps: field per kind; unresolved glossary terms reported
    for index, gap in enumerate(tree["gaps"]):
        if gap["kind"] == "undefined_term" and "term" not in gap:
            errors.append(f"gaps[{index}]: undefined_term needs a term")
        if gap["kind"] == "data_provenance" and "node" not in gap:
            errors.append(f"gaps[{index}]: data_provenance needs a node")
        if gap.get("node") and gap["node"] not in nodes:
            errors.append(f"gaps[{index}]: unknown node {gap['node']}")
    reported_terms = {squash(g["term"]).lower() for g in tree["gaps"] if g["kind"] == "undefined_term" and "term" in g}
    for term, meaning in inputs["glossary"].items():
        if meaning.strip().upper().startswith(NOT_YET_DEFINED) and squash(term).lower() not in reported_terms:
            errors.append(f"gaps: glossary term '{term}' is not yet defined in the inputs and must be reported as undefined_term")

    # 10. set_aside constraints copied exactly
    constraints = {squash(c) for c in inputs["constraints"]}
    errors += [f"set_aside: not an input constraint: '{s['constraint']}'" for s in tree["set_aside"] if squash(s["constraint"]) not in constraints]
    return errors
