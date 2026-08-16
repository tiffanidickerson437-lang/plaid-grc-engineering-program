#!/usr/bin/env python3
"""Mutation tests for ksi_coverage.py.

Each test plants one defect and asserts the checker catches it. Gut the validator and this
suite goes red.

The two that carry the most weight:
  - test_02: the declared summary must not be allowed to drift from the computed rows.
             A hand-maintained tally sitting above rows that no longer agree with it is
             the most common way a coverage claim goes quietly wrong, and it is invisible
             to a reader who trusts the header.
  - test_07: no row may assert an implementation state. This mapping describes the
             ENGINE's control set. The moment a row says "met", the artifact has started
             making claims about a company it has no evidence for.

Run:  python3 04-evidence-and-audit/data/test_ksi_coverage.py
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ksi_coverage as kc  # noqa: E402

CONTROLS = {"SAT-02", "HRS-01", "CHG-02", "MON-01", "IAM-03", "BCD-01", "NET-01"}


def doc_of(*ksis, count=None, summary=None):
    ksis = list(ksis)
    return {
        "metadata": {
            "ksi_count": len(ksis) if count is None else count,
            "summary": summary or {
                "covered": sum(1 for k in ksis if k.get("coverage") == "covered"),
                "partial": sum(1 for k in ksis if k.get("coverage") == "partial"),
                "unaddressed": 0,
            },
        },
        "categories": [{"category": "Test", "ksis": ksis}],
    }


def ksi(kid="KSI-CED-RAT", coverage="covered", controls=("SAT-02",),
        basis="computed", note=None):
    k = {"id": kid, "title": "T", "coverage": coverage,
         "controls": list(controls), "basis": basis}
    if note is not None:
        k["note"] = note
    return k


class TestValidator(unittest.TestCase):

    def test_01_the_real_mapping_is_valid(self):
        problems = kc.validate(kc.load_mapping(), kc.in_scope_controls())
        self.assertEqual(problems, [], f"committed KSI mapping is invalid: {problems}")

    def test_02_declared_count_drift_is_caught(self):
        d = doc_of(ksi(), count=46)
        problems = kc.validate(d, CONTROLS)
        self.assertTrue(any("ksi_count" in p for p in problems),
                        "a declared ksi_count that disagrees with the rows must fail")

    def test_03_declared_summary_drift_is_caught(self):
        d = doc_of(ksi(coverage="covered"),
                   summary={"covered": 39, "partial": 7, "unaddressed": 0})
        problems = kc.validate(d, CONTROLS)
        self.assertTrue(any("summary" in p for p in problems),
                        "a summary that disagrees with the computed tally must fail")

    def test_04_malformed_ksi_id_is_caught(self):
        for bad in ("KSI-CED", "ksi-ced-rat", "CED-RAT", "KSI-CEDX-RAT", ""):
            with self.subTest(kid=bad):
                problems = kc.validate(doc_of(ksi(kid=bad)), CONTROLS)
                self.assertTrue(any("shape" in p for p in problems),
                                f"malformed id {bad!r} must fail")

    def test_05_duplicate_ksi_id_is_caught(self):
        d = doc_of(ksi(kid="KSI-CED-RAT"), ksi(kid="KSI-CED-RAT"))
        problems = kc.validate(d, CONTROLS)
        self.assertTrue(any("duplicate" in p for p in problems),
                        "a duplicated KSI id must fail")

    def test_06_unknown_coverage_value_is_caught(self):
        problems = kc.validate(doc_of(ksi(coverage="mostly")), CONTROLS)
        self.assertTrue(any("coverage" in p for p in problems))

    def test_07_a_row_may_never_assert_an_implementation_state(self):
        """The refusal that keeps this artifact honest about a real company."""
        for word in ("met", "compliant", "satisfied", "pass", "passed"):
            with self.subTest(word=word):
                problems = kc.validate(doc_of(ksi(coverage=word)), CONTROLS)
                self.assertTrue(
                    any("implementation state" in p for p in problems),
                    f"coverage {word!r} asserts a posture and must be rejected",
                )

    def test_08_unknown_basis_is_caught(self):
        problems = kc.validate(doc_of(ksi(basis="vibes")), CONTROLS)
        self.assertTrue(any("basis" in p for p in problems),
                        "a reader must be able to tell computed rows from judgment rows")

    def test_09_control_outside_scope_is_caught(self):
        problems = kc.validate(doc_of(ksi(controls=("NOT-A-CONTROL",))), CONTROLS)
        self.assertTrue(any("in-scope" in p for p in problems))

    def test_10_ksi_with_no_controls_is_caught(self):
        problems = kc.validate(doc_of(ksi(controls=())), CONTROLS)
        self.assertTrue(any("no controls" in p for p in problems))

    def test_11_partial_without_a_named_delta_is_caught(self):
        for note in (None, "", "this is a note but not a delta"):
            with self.subTest(note=note):
                d = doc_of(ksi(kid="KSI-CNA-OFA", coverage="partial",
                               controls=("BCD-01",), note=note))
                problems = kc.validate(d, CONTROLS)
                self.assertTrue(any("delta" in p for p in problems),
                                "a partial with no named gap must fail")

    def test_12_partial_with_a_named_delta_passes(self):
        d = doc_of(ksi(kid="KSI-CNA-OFA", coverage="partial", controls=("BCD-01",),
                       note="delta: availability engineering is a named extension"))
        self.assertEqual(kc.validate(d, CONTROLS), [])

    def test_13_empty_mapping_is_caught(self):
        problems = kc.validate(doc_of(), CONTROLS)
        self.assertTrue(problems, "an empty mapping must not validate clean")

    def test_14_control_test_clean_mapping_produces_no_findings(self):
        """A validator that fires on valid input gets muted, then guards nothing."""
        d = doc_of(
            ksi(kid="KSI-CED-RAT", controls=("SAT-02", "HRS-01")),
            ksi(kid="KSI-CMT-LMC", controls=("CHG-02", "MON-01")),
            ksi(kid="KSI-IAM-ELP", controls=("IAM-03",), basis="judgment"),
        )
        self.assertEqual(kc.validate(d, CONTROLS), [],
                         "a clean mapping must produce zero findings")

    def test_15_mutation_guard_validator_is_not_a_no_op(self):
        d = doc_of(ksi(kid="bad", coverage="met", controls=("NOPE",), basis="vibes"),
                   count=99, summary={"covered": 99, "partial": 99, "unaddressed": 7})
        problems = kc.validate(d, CONTROLS)
        self.assertGreaterEqual(
            len(problems), 5,
            "validate() appears to be a no-op — a mapping with many distinct defects "
            "produced almost no findings",
        )


class TestRender(unittest.TestCase):

    def test_01_render_states_the_authorization_status(self):
        """The map must never read as a readiness claim."""
        out = kc.render(kc.load_mapping())
        self.assertIn("no FedRAMP authorization", out,
                      "the rendered map must state that no authorization is held")

    def test_02_every_partial_delta_appears_in_the_render(self):
        doc = kc.load_mapping()
        out = kc.render(doc)
        partials = [k for _c, k in kc.iter_ksis(doc) if k.get("coverage") == "partial"]
        missing = [k["id"] for k in partials if f"`{k['id']}` delta" not in out]
        self.assertEqual(missing, [], f"partial deltas missing from the render: {missing}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
