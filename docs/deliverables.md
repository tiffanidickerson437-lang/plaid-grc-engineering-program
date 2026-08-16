# Deliverables

Everything in this repository, what it claims, and what it does not. Each entry says how to
hold it in your hand.

---

## 1. The Plaid configuration

**`generated/companies/plaid/plaid.config.yaml`** → **`generated/companies/plaid/data.json`**

One config file describing Plaid from public sources. Renders 44 in-scope controls across 6
framework views.

```bash
# from a checkout of the engine repo, with this config
python3 tools/onboard_company.py --config plaid.config.yaml --slug plaid --dry-run
```

**What it claims:** that these frameworks are in scope and these controls follow from them.
**What it does not claim:** anything about Plaid's implementation of any of them. Every value
is marked VERIFIED, NAMED IN POSTING, INFERRED, or DELIBERATELY UNSET, and
`evidence_in_repo: none`.

---

## 2. The FedRAMP 20x KSI mapping

**`04-evidence-and-audit/data/fedramp-20x-ksi-mapping.yaml`** → [`frameworks/fedramp-20x-ksi-map.md`](../04-evidence-and-audit/frameworks/fedramp-20x-ksi-map.md)

All 46 CR26 Key Security Indicators mapped to the control set. 39 covered, 7 partial with each
delta named, 0 unaddressed.

```bash
python3 04-evidence-and-audit/data/ksi_coverage.py --render
python3 04-evidence-and-audit/data/test_ksi_coverage.py    # 17 tests
```

**Ported, not regenerated.** The mapping is control-to-KSI and the controls are the engine's,
so it is company-agnostic by construction and carried over unchanged from a different
company's instance. Only the company-specific notes were rewritten. **That portability is
itself the argument**: adding a framework is a mapping, and a mapping that is genuinely
company-agnostic should not be re-derived per company.

**What it claims:** that the engine's control set addresses these KSIs.
**What it does not claim:** that Plaid is FedRAMP-ready, that an authorization is planned, or
that any KSI is "met." The validator rejects the word.

---

## 3. The ISO 27701 mapping — the one the engine was missing

**`mappings/iso27701.draft.yaml`** → [`frameworks/iso27701-coverage.md`](../04-evidence-and-audit/frameworks/iso27701-coverage.md)

26 requirements across Annex A (controllers) and Annex B (processors), in explicit STRM form.
9 complete, 16 partial with the gap named, 1 with no coverage at all.

```bash
python3 04-evidence-and-audit/data/strm_coverage.py --render
python3 04-evidence-and-audit/data/test_strm_coverage.py   # 16 tests
```

**Status: `DRAFT_PENDING_HUMAN_APPROVAL`, and the validator enforces it.** Three blocking open
questions must be answered before approval, the first being whether the certified role is PII
controller, processor, or both — which selects the annex and can invert the mapping.

**The limitation, stated plainly:** ISO/IEC 27701:2019 is paywalled. The requirement IDs and
short titles were assembled from secondary sources, **not from a purchased copy**. No
relationship type or strength has been confirmed against normative text. Standard text is
copyrighted and is deliberately not reproduced.

**The most useful single row** is `B.8.2.4` — the processor's duty to tell a customer that
their own instruction appears to breach applicable law — mapped `no-relationship`. Nothing in
the engine covers it. A new control is needed. Publishing that is the point.

---

## 4. Two defect fixes upstream, with regression tests

Found by using the engine, not by auditing it.

| Defect | Symptom | Fix |
|---|---|---|
| Framework token vocabulary mismatch | A 100%-covered framework silently absent from the payload — no error, no warning | Normalizer folds underscores and accepts the crosswalk's own spellings; HIPAA added to the renderer registry |
| Unencoded text I/O, 21 sites across 9 files | Crash on write under Windows cp1252; **silent mojibake on read**, which is worse | Explicit `encoding="utf-8"` everywhere |

The regression suite includes a **mutation guard**. Reverting either fix turns 3 tests red —
verified by actually reverting them, not asserted.

**Why the second one is the more serious bug:** a crash is loud. Reading `control-library.yaml`
— which carries both a middot and an em-dash — under cp1252 produced corrupted narratives with
no failure at all. Every control statement read on Windows was quietly wrong.

---

## 5. The research position

[`00-governance/regulatory-clock.md`](../00-governance/regulatory-clock.md) —
every governing date from primary sources, and the finding that **no Section 1033 compliance
deadline currently survives**.

[`00-governance/open-questions.md`](../00-governance/open-questions.md) —
15 unresolvable questions, **and the seven claims that were refuted during research.**
Publishing what was rejected is the only way a reader can distinguish research from recall.

[`02-ai-governance/README.md`](../02-ai-governance/README.md) —
why AI never renders the pass/fail, argued from PCAOB AS 1105.10, the batch-invariance
non-determinism finding, and FedRAMP RFC-0006/0017.

---

## The honest limitations

Six, in descending order of how much they constrain the claims above.

1. **No instrument here reads Plaid's systems.** They run against committed mappings and public
   surfaces. Nothing in this repository observes Plaid's actual control state, and no output
   should be read as if it did.
2. **The ISO 27701 requirement text is second-hand.** Paywalled standard; verify against a
   purchased copy before approval.
3. **The FAIR risk register is not recalibrated to Plaid.** The engine's Monte Carlo runs on an
   illustrative example register describing a different archetype entirely. The simulation is
   real and the method is sound, but **the dollar figures describe the example, not Plaid**, and
   are not reproduced anywhere in this repository for that reason. Recalibrating it needs
   internal loss data — a 60-day item, not a portfolio one.
4. **The KSI coverage describes the engine, not Plaid.** Whether Plaid's implementation
   satisfies any KSI is unknowable from outside and is never claimed.
5. **No OpenAPI minimization checker ships**, though the surface is public and the idea is
   obvious. The reason is in [`plaid-github-map.md`](../00-governance/plaid-github-map.md): the
   useful version needs a purpose binding Plaid does not publish, and the version buildable
   from outside would count fields and call it minimization.
6. **Four config fields are deliberately empty.** `identity`, `docs`, `comms`, `grc-tool` —
   because Plaid has never publicly named those systems. Filling them is a first-week task, not
   a research one.
