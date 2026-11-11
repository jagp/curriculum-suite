"""h0 — inputs.json. Cross-file rules: ids are unique."""
SCHEMA = "h0-inputs"
SOURCES = {}


def check(inputs, sources):
    errors = []
    for key in ("weekly_goals", "criteria", "presenter_owned"):
        ids = [item["id"] for item in inputs.get(key, [])]
        errors += [f"{key}: duplicate id {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    return errors
