"""Smoke test for the h0 and h1 validators (coordinator-only; never copied into a worker sandbox).

1. The example inputs and a hand-written golden tree must PASS.
2. Each BREAK applies one edit to a copy of the golden tree; the validator must FAIL it,
   with an error containing the expected fragment (so we know the right rule fired).
Run:  python schemas/tests/test_h0_h1.py
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "schemas"))
from validate import validate  # noqa: E402  (path set just above)

INPUTS = json.loads((ROOT / "specs/examples/inputs.json").read_text(encoding="utf-8"))

GOLDEN = {
    "schema": "h1-tree/1",
    "goal": INPUTS["goal"],
    "root": "N0",
    "nodes": [
        {"id": "N0", "skill": "Draft and check the weekly report with Claude", "parent": None, "prereqs": []},
        {"id": "N1", "skill": "Ask Claude for a first draft and revise it", "parent": "N0", "prereqs": [], "serves": ["W1"]},
        {"id": "N2", "skill": "Write a request that states purpose, audience and format", "parent": "N1", "prereqs": [],
         "floor": {"reason": "profile", "detail": "leads already know the report's audience"},
         "claims": [{"text": "Claude can follow a stated output format", "verify": True}]},
        {"id": "N3", "skill": "Draft the report from a tracker export", "parent": "N0", "prereqs": ["N1"], "serves": ["W2", "C1"]},
        {"id": "N4", "skill": "Give Claude the tracker export as source material", "parent": "N3", "prereqs": ["N2"],
         "floor": {"reason": "domain_knowledge", "detail": "leads already export from the tracker"},
         "data": [{"what": "tracker export", "source": "read-only", "quote": "Tracker exports are read-only copies of real data"}]},
        {"id": "N5", "skill": "Check each line of a draft against the tracker", "parent": "N0", "prereqs": ["N3"], "serves": ["W3", "C2"],
         "floor": {"reason": "inputs_stop", "detail": "inputs name no finer step"}},
    ],
    "leaf_order": ["N2", "N4", "N5"],
    "gaps": [{"kind": "undefined_term", "term": "status code", "detail": "glossary marks it UNRESOLVED"}],
    "set_aside": [{"constraint": "Two 90-minute sessions.", "reason": "delivery constraint; does not shape capability"}],
}


def node(tree, node_id):
    return next(n for n in tree["nodes"] if n["id"] == node_id)


# (name, edit applied to a copy of GOLDEN, fragment the error must contain)
BREAKS = [
    ("goal changed", lambda t: t.update(goal="Something else"), "goal"),
    ("extra field (time)", lambda t: node(t, "N2").update(est_min=10), "est_min"),
    ("two roots", lambda t: node(t, "N5").update(parent=None), "exactly one node"),
    ("unknown prereq", lambda t: node(t, "N4").update(prereqs=["N9"]), "unknown node N9"),
    ("self prereq", lambda t: node(t, "N4").update(prereqs=["N4"]), "itself"),
    ("cycle via ancestor", lambda t: node(t, "N2").update(prereqs=["N1"]), "needs-cycle"),
    ("top-level missing serves", lambda t: node(t, "N1").pop("serves"), "must declare serves"),
    ("serves below top level", lambda t: node(t, "N2").update(serves=["W1"]), "only allowed on the root's children"),
    ("weekly goal unserved", lambda t: node(t, "N1").update(serves=["C1"]), "W1 is not served"),
    ("unknown serves id", lambda t: node(t, "N1").update(serves=["W1", "W9"]), "unknown id W9"),
    ("leaf without floor", lambda t: node(t, "N5").pop("floor"), "must state its floor"),
    ("floor on non-leaf", lambda t: node(t, "N1").update(floor={"reason": "profile", "detail": "x"}), "only allowed on leaves"),
    ("already_a_node without prereqs", lambda t: node(t, "N2").update(floor={"reason": "already_a_node", "detail": "x"}), "already_a_node needs"),
    ("leaf missing from order", lambda t: t.update(leaf_order=["N2", "N4"]), "every leaf exactly once"),
    ("order violates needs", lambda t: t.update(leaf_order=["N4", "N2", "N5"]), "N2 must come before N4"),
    ("time in skill", lambda t: node(t, "N5").update(skill="Check each line in 15 minutes"), "time estimate"),
    ("data quote invented", lambda t: node(t, "N4")["data"][0].update(quote="exports are mocked"), "not found in the inputs"),
    ("data without quote", lambda t: node(t, "N4")["data"][0].pop("quote"), "needs a quote"),
    ("UNRESOLVED data, no gap", lambda t: node(t, "N4")["data"][0].update(source="UNRESOLVED"), "no data_provenance gap"),
    ("unresolved term unreported", lambda t: t.update(gaps=[]), "status code"),
    ("set_aside not a constraint", lambda t: t["set_aside"][0].update(constraint="Three sessions."), "not an input constraint"),
    ("claim without verify or cite", lambda t: node(t, "N2")["claims"][0].pop("verify"), "claims"),
    ("bad cite", lambda t: node(t, "N2").update(claims=[{"text": "a claim", "cite": "docs.example"}]), "claims"),
]


def main():
    failures = []
    for label, kind, document, sources in [("inputs", "h0", INPUTS, {}), ("golden tree", "h1", GOLDEN, {"inputs": INPUTS})]:
        errors = validate(kind, document, sources)
        if errors:
            failures.append(f"golden {label} should PASS: {errors}")
    for name, edit, fragment in BREAKS:
        broken = copy.deepcopy(GOLDEN)
        edit(broken)
        errors = validate("h1", broken, {"inputs": INPUTS})
        if not any(fragment in e for e in errors):
            failures.append(f"break '{name}' should FAIL with '{fragment}', got {errors or 'PASS'}")
    print(f"2 golden checks, {len(BREAKS)} breaks, {len(failures)} failures")
    for failure in failures:
        print("  -", failure)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
