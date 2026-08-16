#!/usr/bin/env python3
"""Validate the ISO 27701 STRM draft and compute honest framework coverage.

WHAT THIS IS
------------
The Plaid GRC Engineering posting asks for "the ability to map controls to evidence and
crosswalk a single control across frameworks." A crosswalk is only worth anything if the
coverage number it produces is computed rather than asserted, and if it reports what it
does NOT cover as loudly as what it does.

This tool reads mappings/iso27701.draft.yaml, validates every entry against
mappings/strm-schema.yaml, resolves every referenced control against the rendered in-scope
control set, and prints coverage broken down by STRM relationship type.

IT FAILS CLOSED. Any of the following exits non-zero:
  - a relationship_type not defined in the STRM schema
  - a relationship_strength outside 1..10
  - a master_control_id that is not in the in-scope control set
  - a superset-of / intersects-with / no-relationship entry with no stated delta
  - a mapping still marked DRAFT being counted as approved coverage

That last rule is the point. A draft mapping that silently counts as coverage is how a
crosswalk lies. The tool refuses to report a draft as satisfied coverage; it reports it as
proposed, and says so in the exit banner.

WHY COVERAGE IS NOT A SINGLE PERCENTAGE
---------------------------------------
Per mappings/strm-schema.yaml, `equal-to` and `subset-of` give complete coverage and their
evidence is reusable as-is. `superset-of` and `intersects-with` are partial: real coverage
plus a named gap a human must design for. `no-relationship` is honest absence. Averaging
those into one number destroys the only information a reader needs, so this tool never
emits one. It emits the distribution and the gap list.

Run:
    python3 04-evidence-and-audit/data/strm_coverage.py
    python3 04-evidence-and-audit/data/strm_coverage.py --check     # CI mode, no report
    python3 04-evidence-and-audit/data/strm_coverage.py --render    # write the .md

Exit codes:  0 valid  ·  1 validation failure  ·  2 could not read inputs
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("PyYAML is required. Install it with: pip install pyyaml\n")
    raise SystemExit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "mappings" / "strm-schema.yaml"
DRAFT_PATH = REPO_ROOT / "mappings" / "iso27701.draft.yaml"
PAYLOAD_PATH = REPO_ROOT / "generated" / "companies" / "plaid" / "data.json"
REPORT_PATH = REPO_ROOT / "04-evidence-and-audit" / "frameworks" / "iso27701-coverage.md"

# Relationship types that deliver complete coverage of the focal requirement, per
# mappings/strm-schema.yaml. Everything else leaves a gap a human must close.
COMPLETE = {"equal-to", "subset-of"}
PARTIAL = {"superset-of", "intersects-with"}
NONE = {"no-relationship"}

# A partial or absent relationship without a stated delta is an unfinished mapping
# pretending to be a finished one.
DELTA_REQUIRED = PARTIAL | NONE

APPROVED_STATUS = "APPROVED"


class CannotAssess(Exception):
    """Raised when inputs cannot be read. Never swallowed — the tool fails closed."""


def load_yaml(path: Path):
    if not path.exists():
        raise CannotAssess(f"required input not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def in_scope_controls() -> set[str]:
    """Control IDs the engine actually rendered for this company."""
    if not PAYLOAD_PATH.exists():
        raise CannotAssess(f"rendered payload not found: {PAYLOAD_PATH}")
    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    return {c["id"] for c in payload.get("controls", [])}


def schema_relationship_types() -> set[str]:
    doc = load_yaml(SCHEMA_PATH)
    rels = (doc.get("strm_schema") or {}).get("relationship_types") or {}
    if not rels:
        raise CannotAssess("STRM schema declares no relationship_types")
    return set(rels)


def validate(draft: dict, valid_types: set[str], controls: set[str]) -> list[str]:
    """Return a list of validation failures. Empty list means valid."""
    problems: list[str] = []
    mapping = draft.get("strm_mapping") or {}
    entries = mapping.get("entries") or []

    if not entries:
        problems.append("draft contains no entries")

    for i, wrapper in enumerate(entries):
        m = (wrapper or {}).get("mapping") or {}
        rid = m.get("external_requirement_id", f"<entry {i}>")
        cid = m.get("master_control_id")
        params = m.get("strm_parameters") or {}
        rel = params.get("relationship_type")
        strength = params.get("relationship_strength")

        if cid not in controls:
            problems.append(
                f"{rid}: master_control_id {cid!r} is not in the in-scope control set "
                f"— a mapping to a control this company does not carry is not coverage"
            )
        if rel not in valid_types:
            problems.append(
                f"{rid}: relationship_type {rel!r} is not defined in {SCHEMA_PATH.name}"
            )
        # bool is a subclass of int in Python, and `1 <= True <= 10` is True, so a YAML
        # `relationship_strength: true` would sail through a naive isinstance check and be
        # counted as a strength of 1. Reject bools explicitly.
        if (
            isinstance(strength, bool)
            or not isinstance(strength, int)
            or not (1 <= strength <= 10)
        ):
            problems.append(
                f"{rid}: relationship_strength {strength!r} is not an integer in 1..10"
            )
        if rel in DELTA_REQUIRED and not (m.get("delta") or "").strip():
            problems.append(
                f"{rid}: relationship_type {rel!r} leaves a gap but states no delta "
                f"— an unclosed gap with no description is an unfinished mapping"
            )

    return problems


def summarize(draft: dict) -> dict:
    counts: dict[str, int] = {}
    gaps: list[tuple[str, str, str]] = []
    for wrapper in (draft.get("strm_mapping") or {}).get("entries") or []:
        m = (wrapper or {}).get("mapping") or {}
        rel = (m.get("strm_parameters") or {}).get("relationship_type", "<missing>")
        counts[rel] = counts.get(rel, 0) + 1
        if rel in DELTA_REQUIRED:
            gaps.append((
                m.get("external_requirement_id", "?"),
                m.get("external_requirement_title", ""),
                " ".join((m.get("delta") or "").split()),
            ))
    return {"counts": counts, "gaps": gaps}


def render_report(draft: dict, summary: dict, status: str) -> str:
    mapping = draft.get("strm_mapping") or {}
    total = sum(summary["counts"].values())
    complete = sum(v for k, v in summary["counts"].items() if k in COMPLETE)
    partial = sum(v for k, v in summary["counts"].items() if k in PARTIAL)
    absent = sum(v for k, v in summary["counts"].items() if k in NONE)

    lines = [
        "# ISO/IEC 27701 — computed coverage",
        "",
        "<!-- GENERATED by 04-evidence-and-audit/data/strm_coverage.py. Do not edit by hand. -->",
        "",
        f"**Status: `{status}`.** "
        + (
            "This mapping has NOT been approved by a human. Nothing below counts as "
            "satisfied coverage; every row is a proposal awaiting review."
            if status != APPROVED_STATUS
            else "Approved by pull request."
        ),
        "",
        f"- Framework: {mapping.get('framework_name', 'ISO/IEC 27701')}",
        f"- Requirements mapped: **{total}**",
        f"- Complete coverage (`equal-to`, `subset-of`): **{complete}**",
        f"- Partial, gap named (`superset-of`, `intersects-with`): **{partial}**",
        f"- No coverage (`no-relationship`): **{absent}**",
        "",
        "There is deliberately no single coverage percentage. Averaging complete and",
        "partial relationships into one number hides the only thing a reader needs: which",
        "requirements still need a human to design coverage.",
        "",
        "## Distribution by STRM relationship",
        "",
        "| Relationship | Count | Coverage meaning |",
        "|---|---:|---|",
    ]
    meaning = {
        "equal-to": "complete — reuse the control's evidence as-is",
        "subset-of": "complete plus extra — reuse the control's evidence",
        "superset-of": "partial — our control covers only part; design the delta",
        "intersects-with": "partial overlap — each covers ground the other does not",
        "no-relationship": "none — a new control is needed",
    }
    for rel in ("equal-to", "subset-of", "superset-of", "intersects-with", "no-relationship"):
        n = summary["counts"].get(rel, 0)
        if n:
            lines.append(f"| `{rel}` | {n} | {meaning[rel]} |")

    lines += ["", "## The gap list — what a human still has to design", ""]
    if not summary["gaps"]:
        lines.append("_None._")
    else:
        for rid, title, delta in summary["gaps"]:
            lines.append(f"**`{rid}` — {title}**")
            lines.append("")
            lines.append(f"> {delta}")
            lines.append("")

    oqs = mapping.get("open_questions") or []
    if oqs:
        lines += ["## Blocking questions before approval", ""]
        for q in oqs:
            flag = " **(blocking)**" if q.get("blocking") else ""
            lines.append(f"- `{q.get('id')}`{flag} {' '.join(str(q.get('question','')).split())}")
        lines.append("")

    lines += [
        "## Basis",
        "",
        f"- Requirements source: {' '.join(str(mapping.get('requirements_source','')).split())}",
        f"- Basis checked: {mapping.get('basis_checked')}",
        "",
        "No claim is made about any organization's ISO 27701 implementation, certificate",
        "scope, or audit outcome.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="CI mode: validate only, no report")
    ap.add_argument("--render", action="store_true", help="write the markdown report")
    args = ap.parse_args(argv)

    try:
        draft = load_yaml(DRAFT_PATH)
        valid_types = schema_relationship_types()
        controls = in_scope_controls()
    except CannotAssess as exc:
        sys.stderr.write(f"cannot assess: {exc}\n")
        return 2

    problems = validate(draft, valid_types, controls)
    summary = summarize(draft)
    status = (draft.get("strm_mapping") or {}).get("status", "UNKNOWN")

    total = sum(summary["counts"].values())
    complete = sum(v for k, v in summary["counts"].items() if k in COMPLETE)
    partial = sum(v for k, v in summary["counts"].items() if k in PARTIAL)
    absent = sum(v for k, v in summary["counts"].items() if k in NONE)

    print(f"ISO/IEC 27701 STRM draft — {total} requirements mapped "
          f"against {len(controls)} in-scope controls")
    print(f"  complete (equal-to, subset-of):        {complete}")
    print(f"  partial  (superset-of, intersects):    {partial}")
    print(f"  none     (no-relationship):            {absent}")
    print(f"  status:                                {status}")

    if problems:
        print(f"\n{len(problems)} validation failure(s):")
        for p in problems:
            print(f"  [INVALID] {p}")
        return 1

    if status != APPROVED_STATUS:
        print("\nVALID — and NOT approved. These are proposals, not coverage.")
        print("A human reviews and approves via pull request; the merge is the authorization.")
    else:
        print("\nVALID and approved.")

    if args.render and not args.check:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(render_report(draft, summary, status), encoding="utf-8")
        print(f"\nreport written to {REPORT_PATH.relative_to(REPO_ROOT).as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
