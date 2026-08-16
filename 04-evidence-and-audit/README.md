# Evidence and audit — the instruments that run

Two mappings, two validators, 33 tests. Nothing here needs a network, an API key, or a model.

## The instruments

| Run it | What it does | Tests |
|---|---|---|
| `python3 data/ksi_coverage.py --render` | Validates all 46 FedRAMP 20x CR26 KSIs against the in-scope control set and renders [the map](frameworks/fedramp-20x-ksi-map.md) | [17](data/test_ksi_coverage.py) |
| `python3 data/strm_coverage.py --render` | Validates the ISO 27701 STRM draft and renders [computed coverage](frameworks/iso27701-coverage.md) | [16](data/test_strm_coverage.py) |

Both **fail closed**. Exit 0 valid, 1 validation failure, 2 could not read inputs. Neither has
a `|| true` anywhere, and neither swallows an error — a green check that cannot go red is
decoration.

## What they refuse to do

The refusals are the design. In rough order of how much they matter:

1. **A draft is never counted as coverage.** `strm_coverage.py` reads the mapping's `status`
   field and reports `DRAFT_PENDING_HUMAN_APPROVAL` as *proposals, not coverage*. A draft
   mapping that silently counts as coverage is how a crosswalk lies.
2. **No row may assert an implementation state.** `ksi_coverage.py` rejects the coverage values
   `met`, `compliant`, `satisfied`, `pass` and `passed` outright. This mapping describes the
   *engine's* control set. The moment a row says "met," the artifact has started making claims
   about a company it has no evidence for.
3. **A gap with no named delta fails.** Any `superset-of`, `intersects-with`,
   `no-relationship` or `partial` row must state what is missing. A partial with no described
   gap is an unfinished row wearing a finished row's clothes.
4. **A mapping to an out-of-scope control fails.** A KSI or requirement mapped to a control
   this company does not carry is not coverage, and would inflate the count.
5. **A declared summary that drifts from the rows fails.** `ksi_coverage.py` recomputes the
   `covered`/`partial` tallies and compares them to the hand-maintained header. A stale summary
   above rows that no longer agree with it is invisible to a reader who trusts the header.
6. **No single coverage percentage is emitted.** Averaging complete and partial relationships
   into one number destroys the only information a reader needs — the list of what a human
   still has to design.

## Why every checker is attacked

A checker nobody checks can be quietly gutted to `return []` and will report clean forever
after. So each suite plants defects and asserts they are caught, and each ends with a
**mutation guard** that fails if the validator becomes a no-op.

Each suite also carries a **control test** — a clean input that must produce *zero* findings.
A validator that fires on valid input gets muted by lunchtime, and then guards nothing.

Two real bugs were caught this way while building, both in my own work:

- `test_strm_coverage.py::test_04` found that `isinstance(True, int)` is `True` in Python, so
  a YAML `relationship_strength: true` would have passed validation as a strength of 1. Fixed
  by rejecting bools explicitly.
- `strm_coverage.py` itself caught a mapping entry (`B.8.2.6`) where I had written a partial
  relationship and never stated the delta.

## Reproducibility

Same config, same mappings, same output every run — no model in the pass/fail path, for the
reasons set out in [02-ai-governance](../02-ai-governance/).

That property is not decoration. **FedRAMP RFC-0006** requires packages *"in a machine-readable
format that can be regenerated on demand,"* and **RFC-0017** states that assessors *"MUST NOT
rely on screenshots, configuration dumps, or other point-in-time output as evidence."* A
regenerable artifact is the only kind that satisfies both.
