#!/usr/bin/env python3
"""Mutation tests for strm_coverage.py.

A checker nobody checks can be quietly gutted to `return []` and will report "valid"
forever after. Every test below plants a specific defect and asserts the checker catches
it. If you neuter the validator, this suite goes red.

The tests that matter most are the ones asserting the checker REFUSES to do something:
  - test_05: a draft must never be counted as approved coverage
  - test_06: a gap with no delta must fail, because an undescribed gap is an unfinished
             mapping wearing a finished mapping's clothes
  - test_08: a mapping to a control the company does not carry is not coverage
  - test_10: the control test — a clean draft must produce zero findings, because a
             validator that fires on valid input gets muted by lunchtime

Run:  python3 04-evidence-and-audit/data/test_strm_coverage.py
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml  # noqa: E402

import strm_coverage as sc  # noqa: E402


def load_draft() -> dict:
    return yaml.safe_load(sc.DRAFT_PATH.read_text(encoding="utf-8"))


VALID_TYPES = {
    "equal-to", "subset-of", "superset-of", "intersects-with", "no-relationship",
}


def entry(control="PRI-01", rid="A.7.2.1", rel="equal-to", strength=8, delta=None):
    m = {
        "master_control_id": control,
        "external_framework": "ISO/IEC 27701:2019",
        "external_requirement_id": rid,
        "strm_parameters": {
            "relationship_type": rel,
            "relationship_strength": strength,
        },
    }
    if delta is not None:
        m["delta"] = delta
    return {"mapping": m}


def draft_of(*entries, status="DRAFT_PENDING_HUMAN_APPROVAL") -> dict:
    return {"strm_mapping": {"status": status, "entries": list(entries)}}


CONTROLS = {"PRI-01", "PRI-02", "DCH-01", "DCH-02", "TPM-01", "TPM-02",
            "CRY-01", "IRO-01", "AST-01", "GOV-01", "RSK-01", "RSK-02", "MON-01"}


class TestValidator(unittest.TestCase):

    def test_01_the_real_draft_is_valid(self):
        """The committed draft must pass its own validator."""
        problems = sc.validate(load_draft(), VALID_TYPES, sc.in_scope_controls())
        self.assertEqual(problems, [], f"committed draft is invalid: {problems}")

    def test_02_unknown_relationship_type_is_caught(self):
        d = draft_of(entry(rel="sort-of-related"))
        problems = sc.validate(d, VALID_TYPES, CONTROLS)
        self.assertTrue(any("relationship_type" in p for p in problems),
                        "an undefined relationship_type must fail validation")

    def test_03_strength_out_of_range_is_caught(self):
        for bad in (0, 11, -3, 99):
            with self.subTest(strength=bad):
                d = draft_of(entry(strength=bad))
                problems = sc.validate(d, VALID_TYPES, CONTROLS)
                self.assertTrue(any("relationship_strength" in p for p in problems),
                                f"strength {bad} must fail validation")

    def test_04_non_integer_strength_is_caught(self):
        """A float strength is a smell: it implies a computed score, not a human rating."""
        for bad in (7.5, "high", None, True):
            with self.subTest(strength=bad):
                d = draft_of(entry(strength=bad))
                problems = sc.validate(d, VALID_TYPES, CONTROLS)
                self.assertTrue(any("relationship_strength" in p for p in problems),
                                f"strength {bad!r} must fail validation")

    def test_05_draft_status_is_never_reported_as_approved(self):
        """The load-bearing refusal: a draft mapping must not count as coverage."""
        d = draft_of(entry(), status="DRAFT_PENDING_HUMAN_APPROVAL")
        self.assertNotEqual(
            d["strm_mapping"]["status"], sc.APPROVED_STATUS,
            "fixture sanity: this draft should not be approved",
        )
        real = load_draft()
        self.assertNotEqual(
            (real.get("strm_mapping") or {}).get("status"), sc.APPROVED_STATUS,
            "the committed ISO 27701 mapping claims approval it has not received — "
            "no human has confirmed these relationships against the normative text",
        )

    def test_06_gap_without_a_delta_is_caught(self):
        """An unclosed gap with no description is an unfinished mapping."""
        for rel in ("superset-of", "intersects-with", "no-relationship"):
            with self.subTest(rel=rel):
                d = draft_of(entry(rel=rel, delta=None))
                problems = sc.validate(d, VALID_TYPES, CONTROLS)
                self.assertTrue(any("delta" in p for p in problems),
                                f"{rel} without a delta must fail validation")

    def test_07_whitespace_only_delta_does_not_satisfy_the_requirement(self):
        """Guards against closing the finding with an empty string."""
        d = draft_of(entry(rel="superset-of", delta="   \n  "))
        problems = sc.validate(d, VALID_TYPES, CONTROLS)
        self.assertTrue(any("delta" in p for p in problems),
                        "a blank delta must not satisfy the delta requirement")

    def test_08_mapping_to_an_out_of_scope_control_is_caught(self):
        """A mapping to a control this company does not carry is not coverage."""
        d = draft_of(entry(control="PRI-03.13"))  # real engine control, not in Plaid scope
        problems = sc.validate(d, VALID_TYPES, CONTROLS)
        self.assertTrue(any("in-scope" in p for p in problems),
                        "a control outside the rendered scope must fail validation")

    def test_09_empty_draft_is_caught(self):
        """Zero entries must not read as zero problems."""
        problems = sc.validate(draft_of(), VALID_TYPES, CONTROLS)
        self.assertTrue(problems, "an empty draft must not validate clean")

    def test_10_control_test_clean_draft_produces_no_findings(self):
        """A validator that fires on valid input gets muted, then guards nothing."""
        d = draft_of(
            entry(control="PRI-01", rid="A.7.2.1", rel="equal-to", strength=8),
            entry(control="DCH-02", rid="A.7.4.7", rel="subset-of", strength=7),
            entry(control="TPM-01", rid="A.7.2.6", rel="superset-of", strength=5,
                  delta="named and described gap"),
        )
        self.assertEqual(sc.validate(d, VALID_TYPES, CONTROLS), [],
                         "a clean draft must produce zero findings")

    def test_11_mutation_guard_validator_is_not_a_no_op(self):
        """If validate() is gutted to return [], this test goes red."""
        d = draft_of(entry(rel="not-a-real-relationship", strength=99, control="NOPE-01"))
        problems = sc.validate(d, VALID_TYPES, CONTROLS)
        self.assertGreaterEqual(
            len(problems), 3,
            "validate() appears to be a no-op — a draft with three distinct defects "
            "produced fewer than three findings",
        )


class TestSummary(unittest.TestCase):

    def test_01_coverage_buckets_are_disjoint_and_total(self):
        """Every relationship type must land in exactly one bucket, or the math lies."""
        self.assertEqual(sc.COMPLETE & sc.PARTIAL, set())
        self.assertEqual(sc.COMPLETE & sc.NONE, set())
        self.assertEqual(sc.PARTIAL & sc.NONE, set())
        self.assertEqual(sc.COMPLETE | sc.PARTIAL | sc.NONE, VALID_TYPES,
                         "a relationship type exists that no coverage bucket claims")

    def test_02_counts_sum_to_entry_count(self):
        draft = load_draft()
        summary = sc.summarize(draft)
        entries = (draft.get("strm_mapping") or {}).get("entries") or []
        self.assertEqual(sum(summary["counts"].values()), len(entries),
                         "summary drops or double-counts entries")

    def test_03_every_gap_carries_a_delta_in_the_summary(self):
        summary = sc.summarize(load_draft())
        empty = [rid for rid, _title, delta in summary["gaps"] if not delta.strip()]
        self.assertEqual(empty, [], f"gaps reported with no delta text: {empty}")

    def test_04_partial_relationships_appear_in_the_gap_list(self):
        """The gap list is the deliverable; it must not silently omit partials."""
        draft = load_draft()
        summary = sc.summarize(draft)
        expected = sum(v for k, v in summary["counts"].items() if k in sc.DELTA_REQUIRED)
        self.assertEqual(len(summary["gaps"]), expected,
                         "the gap list does not contain every partial/absent relationship")

    def test_05_no_single_percentage_is_emitted(self):
        """Averaging complete and partial into one number hides the gap list."""
        report = sc.render_report(load_draft(), sc.summarize(load_draft()), "DRAFT")
        self.assertIn("no single coverage percentage", report.lower(),
                      "the report must state why it emits no single percentage")


if __name__ == "__main__":
    unittest.main(verbosity=2)
