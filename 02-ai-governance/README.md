# AI governance — why AI never renders the pass/fail

**The one-line thesis: agents draft, compute and block. They never sign.**

The engine this repository is built on has always carried one hard rule — *AI drafts
narratives; AI never authors evidence*, enforced at three layers (a schema constant, a
pre-write hook, and a CI gate). This file is the argument for why that is an **engineering
constraint with citations**, not a stylistic preference, and why it is the right posture for
a role whose posting asks the hire to "scale agentic / AI-assisted workflows across the
function."

---

## 1. The doctrine: model output is Information Produced by the Entity

**PCAOB AS 1105.10**, verbatim:

> "When using information produced by the company as audit evidence, the auditor should
> evaluate whether the information is sufficient and appropriate for purposes of the audit by
> performing procedures to: **Test the accuracy and completeness of the information, or test
> the controls over the accuracy and completeness of that information.**"

Model output is IPE. AS 1105 offers exactly two routes to reliance — test the output, or test
the controls over the process that produced it.

**A generative model offers neither cleanly.** You cannot exhaustively test an open output
set. And the "control over the process" is a non-deterministic function.

AS 1105.08 separately ranks evidence obtained **directly** by the auditor above evidence
obtained indirectly, which is the same argument stated from the other end: a deterministic
collector reading a system of record beats a model narrating what it thinks the system says.

This is not a rule about AI. That is exactly why it is hard to argue around.

## 2. The part most people get wrong

The usual defence is: pin the model, set temperature to zero, fix the seed, and you have
reproducibility.

You do not.

**"Defeating Nondeterminism in LLM Inference"** (Horace He, Thinking Machines Lab,
2025-09-10) rejects the popular floating-point-and-GPU-concurrency explanation outright. The
actual cause is **batch-invariance failure**:

> "the primary reason nearly all LLM inference endpoints are nondeterministic is that the
> load (and thus batch-size) nondeterministically varies"

Stated precisely for an audit context: **at temperature 0, identical prompt, pinned model
snapshot, fixed seed, the output can still differ because of how many other customers hit the
endpoint at that millisecond.**

The irreproducibility is a function of a third party's traffic. It does not appear in your
audit log. It cannot be configured away on a shared endpoint. Batch-invariant kernels fix it
at roughly 1.6–2× slowdown — so it is solvable engineering that commercial endpoints do not
currently solve.

**Model version pinning is still a real and necessary control** — every Claude model ID is a
pinned dated snapshot, and alias entries are convenience pointers that resolve to one, so
*snapshot = control, alias = uncontrolled drift*. "No Model Version Pinning" is formally named
as a defect in the literature (Mahmoudi et al., ACM DOI 10.1145/3786582.3786835).

Pinning is necessary. Per the batch-invariance finding, it is **not sufficient**.

## 3. Why model confidence is not a safety signal

The failure mode that matters for control mapping is not the obvious hallucination. It is the
confident, plausible, wrong one.

- **arXiv:2607.11127** (2026-07-13) — bilingual legal-citation benchmark. GDPR retrieval
  94–100%. Saudi PDPL **60–77%**, highest fabrication rate **67%**. And the number that should
  end the debate: **91% of fabricated citations were asserted with model confidence ≥ 0.8.**
  Accuracy collapses on lower-resource corpora and the model's own confidence gives no
  warning that it has. **A bespoke internal control library is a low-resource corpus.** So is
  a customer's policy set. So is a framework crosswalk.
- **Stanford, arXiv:2405.20362** — purpose-built, RAG-grounded, commercially sold legal
  research tools hallucinated at **17–33%** despite vendor claims of elimination.
- **AI Hallucination Cases database** (Damien Charlotin), 1,890 cases as of 2026-08-15. Of
  5,652 tagged items: Fabricated 3,169, **Misrepresented 1,520**, False Quotes 928.
  **Misrepresentation — the source exists but does not say what the model claims — is the
  second-largest failure mode, and it survives a naive "does this citation exist?" check.**
  That is precisely the shape of a bad control mapping.
- **"Who judges the judges?" arXiv:2605.24737** — inter-judge agreement 51.5%–69.1%, and
  **reordering the questions degraded agreement by up to 25 percentage points.** A judge whose
  verdict moves 25 points on question order is not a control. LLM-as-judge does not rescue the
  design.

There is a further trap specific to crosswalking. **"LLM-based HSE Compliance Assessment"**
(arXiv:2505.22959) finds models *"largely rely on semantic matching rather than principled
reasoning."* An LLM doing a control crosswalk is computing semantic similarity while
presenting it as reasoning — which is exactly the failure **NIST IR 8477** guards against by
requiring a human rationale on every mapping relationship.

That is why [`mappings/iso27701.draft.yaml`](../mappings/iso27701.draft.yaml) ships as
`DRAFT_PENDING_HUMAN_APPROVAL` with three blocking open questions, and why
[`strm_coverage.py`](../04-evidence-and-audit/data/strm_coverage.py) refuses to count a draft
as satisfied coverage.

## 4. FedRAMP already wrote the deterministic version into a standard

- **RFC-0006** — KSIs are *"designed to produce final validations that are true or false,"*
  and packages *"must be in a machine-readable format that can be regenerated on demand."*
- **RFC-0017** — machine-based validation at least **every 3 days** at Moderate, human
  validation every 3 months. And the operative line: assessors **"MUST NOT rely on
  screenshots, configuration dumps, or other point-in-time output as evidence."**
- **`github.com/FedRAMP/rules`** ships the canonical JSON with an `AGENTS.md` titled
  *"Instructions For AI Agents."* Its best line, and the one this repository tries to live by:

  > **"Distinguish evidence found, evidence missing, and conclusions inferred from evidence.
  > Do not claim compliance from silence."**

All 32 FedRAMP RFCs were reviewed. **Not one is about AI.** The posture is *making the corpus
agent-legible while keeping validation deterministic and boolean* — a more accurate and more
useful reading than "FedRAMP is adopting AI."

## 5. Where the line lands

| Layer | Implementation | Justification |
|---|---|---|
| Evidence collection | Deterministic collectors, least-privilege, hashed, timestamped | AS 1105.08 (direct > indirect); RFC-0017 |
| **Pass/fail determination** | **Deterministic rules (Rego/SQL), versioned, unit-tested** | AS 1105.10; RFC-0006 (true or false) |
| Control-mapping *suggestion* | LLM proposes, human confirms, stored as draft | NIST IR 8477; the semantic-matching critique |
| Narrative from already-structured facts | LLM drafts, human owns | — |
| **Never** | LLM renders the pass/fail, or asserts an unreviewed mapping | §2 and §3 above |

Supporting practitioners, both from parties with every incentive to claim more:

- **Anton Chuvakin**, Google Cloud Office of the CISO (2025-12-03): *"'Do good security' is
  not a valid prompt. You need deterministic workflows that the probabilistic AI can follow,"*
  and *"the job is shifting from Operator to Reviewer."*
- **Anthropic**, "Building Effective AI Agents" (2024-12-19): *"workflows offer predictability
  and consistency for well-defined tasks, whereas agents are the better option when
  flexibility and model-driven decision-making are needed."* **Control evaluation is the
  definition of a well-defined task.**

Worth noting: **the GRC Engineering manifesto and the discipline's foundational writing do not
mention AI at all.** The value was always located in deterministic derivation.

## 6. Plaid has already built the enforcement point

Plaid's engineering blog describes an internal MCP server giving AI clients governed access to
20+ internal tools — JIRA, application logs, Prometheus metrics, gRPC services, data schemas.
The governance layer is the interesting part:

- an **identity-aware proxy** validating employee device and IdP authentication
- the **existing authorization server** controlling which employees reach which gRPC methods
- *"Controls on restrictions can be implemented at the tool level at call-time, ensuring
  policy compliance"*
- **Device Authorization Grant with DPoP and short-lived bearer tokens**
- operating at *"thousands of tool calls and dozens of agents across engineering, product, and
  support"*

That is a purpose-bound, time-boxed, centrally-authorized agent access model — which is
`AAT-01`'s control statement, built as infrastructure.

**Precision:** this is Plaid's **internal** agent estate. Plaid does not ship agentic AI to
consumers, and nothing here should be read as saying it does.

**What is not public is the control.** An enforcement point produces authorization decisions;
a control produces *evidence that those decisions were purpose-bound, reviewed, and
revocable*, on a cadence, in a form an assessor can test. `AAT-01` is the governing control
over the mechanism Plaid already runs — and the gap between the two is the work, not a
criticism of the build.

## 7. The reflexive point

An AI system that determines control pass/fail in a federal authorization pipeline is
plausibly *"high-impact"* under **OMB M-25-21** and plausibly Annex III high-risk under the
**EU AI Act**. The compliance robot is itself in scope.

*(The EU AI Act high-risk dates moved: the Digital Omnibus received final Council approval on
2026-06-29, pushing stand-alone Annex III high-risk to **2027-12-02** and embedded Annex I to
**2028-08-02**. Anything citing 2026-08-02 for high-risk is out of date — that date carried
Article 50 transparency obligations only.)*

## 8. The honest counterweight

The strongest citation against over-claiming here comes from a GRC vendor about its own
category. **Drata / Wakefield Research, "The State of GRC in the Age of AI"** (fielded
2026-03-12 to 03-27, n=300, MoE ±5.7pp):

- **71%** say AI has already led to a failed audit or a lapsed regulatory standard
- **86%** say GRC-focused AI tools are not enterprise-ready
- **90%** say at least some of their AI investments in GRC fell short

And the gap worth stating plainly: **there is no publicly documented case of an AI GRC tool
producing faulty evidence or a wrong control determination.** That is almost certainly
non-disclosure rather than non-occurrence — audit findings are not published, and there is no
CVE process for "the compliance robot passed a broken control." Saying so accurately is more
useful than implying the risk has been measured.
