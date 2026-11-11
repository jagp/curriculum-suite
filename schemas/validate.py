"""Validate a file against its schema and the files it depends on.

Usage:  python validate.py <kind> <file> [--<source-name> <path> ...]
        python validate.py <kind> --help     (lists the source files that file kind needs)

Two layers:
  1. Shape: the file (and each source file) must pass its JSON Schema in this folder.
  2. Cross-file: each file kind's checks/<kind>.py adds the rules JSON Schema can't express.
Exit 0 = PASS, 1 = FAIL, 2 = usage error.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy code page
HERE = Path(__file__).parent


def load_check(kind):
    """Load checks/<kind>.py. Each module defines SCHEMA, SOURCES ({name: kind}) and check(doc, sources)."""
    path = HERE / "checks" / f"{kind}.py"
    if not path.is_file():
        sys.exit(f"usage error: unknown file kind '{kind}'")
    spec = importlib.util.spec_from_file_location(f"checks_{kind}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def registry():
    """Every schema in this folder, addressable by file name, so $refs like common.schema.json resolve."""
    resources = [(p.name, Resource.from_contents(json.loads(p.read_text(encoding="utf-8")))) for p in HERE.glob("*.schema.json")]
    return Registry().with_resources(resources)


def shape_errors(schema_name, document, label):
    schema = json.loads((HERE / f"{schema_name}.schema.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, registry=registry())
    return [f"{label}: {'/'.join(map(str, e.absolute_path)) or '(top)'}: {e.message}" for e in validator.iter_errors(document)]


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        sys.exit(f"usage error: cannot read {path}: {error}")


def validate(kind, document, source_docs):
    """Return a list of error strings (empty = PASS). Source files are shape-checked first; cross-file checks run only on valid shapes."""
    module = load_check(kind)
    errors = shape_errors(module.SCHEMA, document, "file")
    for name, source_kind in module.SOURCES.items():
        errors += shape_errors(load_check(source_kind).SCHEMA, source_docs[name], f"--{name}")
    if errors:
        return errors
    return module.check(document, source_docs)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    module = load_check(sys.argv[1])
    parser = argparse.ArgumentParser(prog=f"validate.py {sys.argv[1]}")
    parser.add_argument("file")
    for name in module.SOURCES:
        parser.add_argument(f"--{name}", required=True)
    args = parser.parse_args(sys.argv[2:])
    document = load_json(args.file)
    source_docs = {name: load_json(getattr(args, name)) for name in module.SOURCES}
    errors = validate(sys.argv[1], document, source_docs)
    if errors:
        print(f"FAIL {sys.argv[1]} {args.file} ({len(errors)} errors)")
        print("\n".join(f"  - {e}" for e in errors))
        sys.exit(1)
    print(f"PASS {sys.argv[1]} {args.file}")


if __name__ == "__main__":
    main()
