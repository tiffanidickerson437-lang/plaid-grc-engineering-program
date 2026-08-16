#!/usr/bin/env python3
"""Validate the FedRAMP 20x KSI mapping and render the KSI map.

WHAT IT CHECKS — and it fails closed on every one
-------------------------------------------------
  1. The declared ksi_count matches the number of KSIs actually present.
  2. The declared summary {covered, partial, unaddressed} matches the computed tallies.
     A hand-maintained summary that drifts from the rows beneath it is the single most
     common way a coverage claim goes quietly wrong.
  3. Every KSI id matches the CR26 shape KSI-XXX-YYY and is unique.
  4. Every `coverage` value is in the declared vocabulary.
  5. Every `basis` value is in {computed, mixed, judgment} — so a reader can always tell
     which rows are machine-derived from shared 800-53 anchors and which are the author's
     judgment. A mapping that hides that distinction is asking to be trusted blindly.
  6. Every referenced control resolves against the rendered in-scope control set.
     A KSI mapped to a control this company does not carry is not coverage.
  7. Every `partial` row states a delta beginning "delta:". Partial with no named gap is
     an unfinished row wearing a finished row's clothes.
  8. No row is scored "met" for any company. Coverage describes the ENGINE's control set.

Run:
    python3 04-evidence-and-audit/data/ksi_coverage.py
    python3 04-evidence-and-audit/data/ksi_coverage.py --check    # CI mode
    python3 04-evidence-and-audit/data/ksi_coverage.py --render   # write the .md

Exit codes:  0 valid  ·  1 validation failure  ·  2 could not read inputs
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("PyYAML is required. Install it with: pip install pyyaml\n")
    raise SystemExit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
MAPPING_PATH = Path(__file__).resolve().parent / "fedramp-20x-ksi-mapping.yaml"
PAYLOAD_PATH = REPO_ROOT / "generated" / "companies" / "plaid" / "data.json"
REPORT_PATH = REPO_ROOT / "04-evidence-and-audit" / "frameworks" / "fedramp-20x-ksi-map.md"

KSI_ID = re.compile(r"^KSI-[A-Z]{3}-[A-Z]{3}$")
COVERAGE_VOCAB = {"covered", "partial"}
BASIS_VOCAB = {"computed", "mixed", "judgment"}
FORBIDDEN_COVERAGE = {"met", "compliant", "satisfied", "pass", "passed"}


class CannotAssess(Exception):
    """Inputs unreadable. Never swallowed — the tool fails closed."""


def load_mapping() -> dict:
    if not MAPPING_PATH.exists():
        raise CannotAssess(f"mapping not found: {MAPPING_PATH}")
    return yaml.safe_load(MAPPING_PATH.read_text(encoding="utf-8"))


def in_scope_controls() -> set[str]:
    if not PAYLOAD_PATH.exists():
        raise CannotAssess(f"rendered payload not found: {PAYLOAD_PATH}")
    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    return {c["id"] for c in payload.get("controls", [])}


def iter_ksis(doc: dict):
    for cat in doc.get("categories") or []:
        name = cat.get("category", "<unnamed>")
        for k in cat.get("ksis") or []:
            yield name, k


def validate(doc: dict, controls: set[str]) -> list[str]:
    problems: list[str] = []
    meta = doc.get("metadata") or {}
    ksis = list(iter_ksis(doc))

    if not ksis:
        problems.append("mapping contains no KSIs")
        return problems

    # 1. declared count vs actual
    declared = meta.get("ksi_count")
    if declared != len(ksis):
        problems.append(
            f"metadata.ksi_count is {declared} but {len(ksis)} KSIs are present — "
            f"a declared count that drifts from the rows is how a coverage claim goes wrong"
        )

    seen: set[str] = set()
    tally = {"covered": 0, "partial": 0}

    for cat, k in ksis:
        kid = k.get("id", "<missing>")

        # 3. id shape and uniqueness
        if not KSI_ID.match(str(kid)):
            problems.append(f"{kid}: does not match the CR26 KSI id shape KSI-XXX-YYY")
        if kid in seen:
            problems.append(f"{kid}: duplicate KSI id")
        seen.add(kid)

        # 4. coverage vocabulary, and 8. nothing scored "met"
        cov = k.get("coverage")
        if str(cov).lower() in FORBIDDEN_COVERAGE:
            problems.append(
                f"{kid}: coverage {cov!r} asserts an implementation state. This mapping "
                f"describes the engine's control set, never a company's posture"
            )
        elif cov not in COVERAGE_VOCAB:
            problems.append(f"{kid}: coverage {cov!r} is not in {sorted(COVERAGE_VOCAB)}")
        else:
            tally[cov] += 1

        # 5. basis vocabulary
        basis = k.get("basis")
        if basis not in BASIS_VOCAB:
            problems.append(
                f"{kid}: basis {basis!r} is not in {sorted(BASIS_VOCAB)} — a reader must be "
                f"able to tell a computed row from a judgment row"
            )

        # 6. control resolution
        refs = k.get("controls") or []
        if not refs:
            problems.append(f"{kid}: no controls mapped")
        for cid in refs:
            if cid not in controls:
                problems.append(
                    f"{kid}: control {cid!r} is not in the in-scope control set — "
                    f"a KSI mapped to a control this company does not carry is not coverage"
                )

        # 7. partial rows must name the delta
        if cov == "partial":
            note = (k.get("note") or "").strip()
            if not note.lower().startswith("delta:"):
                problems.append(
                    f"{kid}: coverage 'partial' but the note does not begin 'delta:' — "
                    f"a partial with no named gap is an unfinished row"
                )

    # 2. declared summary vs computed
    summary = meta.get("summary") or {}
    for key in ("covered", "partial"):
        if summary.get(key) != tally[key]:
            problems.append(
                f"metadata.summary.{key} is {summary.get(key)} but {tally[key]} rows compute "
                f"as {key}"
            )
    if summary.get("unaddressed") not in (0, None):
        problems.append(
            f"metadata.summary.unaddressed is {summary.get('unaddressed')} but the coverage "
            f"vocabulary has no 'unaddressed' value to produce it"
        )

    return problems


def render(doc: dict) -> str:
    meta = doc.get("metadata") or {}
    ksis = list(iter_ksis(doc))
    covered = sum(1 for _c, k in ksis if k.get("coverage") == "covered")
    partial = sum(1 for _c, k in ksis if k.get("coverage") == "partial")

    out = [
        "# FedRAMP 20x Key Security Indicators — engine coverage",
        "",
        "<!-- GENERATED by 04-evidence-and-audit/data/ksi_coverage.py. Do not edit by hand. -->",
        "",
        f"**{meta.get('framework_name')}** · {len(ksis)} KSIs · "
        f"**{covered} covered · {partial} partial**",
        "",
        "> " + " ".join(str(meta.get("authorization_status", "")).split()),
        "",
        f"Source: `{meta.get('source')}` · basis checked {meta.get('basis_checked')}",
        "",
        "`covered` means the engine control's operating behavior satisfies the KSI's",
        "persistent-review intent. `partial` means a real control exists and a named",
        "modernization delta remains — the delta is the work, stated plainly.",
        "`basis` says whether the row was computed from the shared 800-53 anchor,",
        "curated by judgment, or mixed.",
        "",
    ]
    for cat in doc.get("categories") or []:
        rows = cat.get("ksis") or []
        out += [f"## {cat.get('category')}  ({len(rows)})", "",
                "| KSI | Title | Coverage | Controls | Basis |",
                "|---|---|---|---|---|"]
        for k in rows:
            mark = "covered" if k.get("coverage") == "covered" else "**partial**"
            out.append(
                f"| `{k.get('id')}` | {k.get('title')} | {mark} | "
                f"{', '.join(f'`{c}`' for c in k.get('controls') or [])} | {k.get('basis')} |"
            )
        out.append("")
        deltas = [k for k in rows if k.get("coverage") == "partial"]
        for k in deltas:
            out += [f"**`{k.get('id')}` delta** — {' '.join((k.get('note') or '')[6:].split())}", ""]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="CI mode: validate only")
    ap.add_argument("--render", action="store_true", help="write the markdown map")
    args = ap.parse_args(argv)

    try:
        doc = load_mapping()
        controls = in_scope_controls()
    except CannotAssess as exc:
        sys.stderr.write(f"cannot assess: {exc}\n")
        return 2

    ksis = list(iter_ksis(doc))
    problems = validate(doc, controls)
    covered = sum(1 for _c, k in ksis if k.get("coverage") == "covered")
    partial = sum(1 for _c, k in ksis if k.get("coverage") == "partial")

    print(f"FedRAMP 20x CR26 — {len(ksis)} KSIs across "
          f"{len(doc.get('categories') or [])} categories, "
          f"resolved against {len(controls)} in-scope controls")
    print(f"  covered: {covered}   partial: {partial}")

    if problems:
        print(f"\n{len(problems)} validation failure(s):")
        for p in problems:
            print(f"  [INVALID] {p}")
        return 1

    print("\nVALID — every KSI resolves, every partial names its delta, and no row "
          "asserts a company's implementation state.")

    if args.render and not args.check:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(render(doc), encoding="utf-8")
        print(f"map written to {REPORT_PATH.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
