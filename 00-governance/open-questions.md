# Open questions, and the claims that were refuted

Two lists. The first is what the public record cannot answer. The second is what the public
record actively contradicted — claims that looked right, that a reasonable person would have
written, and that failed verification.

Publishing the second list is the point. Any portfolio piece can show what survived. Showing
what was rejected is the only way a reader can tell the difference between research and
recall.

---

## Part 1 — Refuted during research. None of this appears anywhere in this repo.

Each was extracted from a real source, checked adversarially, and killed. The vote is the
verification tally.

| # | The claim | Why it died |
|---|---|---|
| 1 | **"Plaid protects data in transit and at rest using AES-256 encryption and TLS."** | **0–3.** The EU safety page does not say this. Plaid's own KMS engineering post names **no algorithms and no key sizes** — only that they are *"secure by default."* Citing a cipher Plaid never published would be the single easiest error for a Plaid engineer to catch. |
| 2 | **"Plaid Link, not the third-party application, performs credential collection, validation and MFA, so the developer never handles end-user banking credentials."** | **0–3.** The most tempting sentence available for a GRC write-up, and it did not survive. The defensible version is OAuth-specific and narrower — see below. |
| 3 | The six-category product taxonomy (Payments / Fraud & risk / Personal finance insights / Credit underwriting / Open finance / Onboarding) as the authoritative structure. | **0–3.** |
| 4 | The enumerated 2026 product list including Protect, Cash Advance Index, LendScore, Enrich, Investments Move, App Directory, Permissions Manager. | **1–2.** Individual names may be real; the list as a whole is not verified. |
| 5 | Plaid Portal / Permissions Manager / App Directory as citable consent and data-subject-rights evidence. | **1–2.** *(Distinct from the Plaid Portal fact sourced to the 2022 settlement, which is solid.)* |
| 6 | The bug bounty launched November 2016. | **1–2.** HackerOne itself says **March 2018**. The 2016 date appears only in a later Plaid blog post. |
| 7 | "2 days average report acknowledgement, October 2021" as a bounty metric. | **0–3.** |

### What replaced claim #2

The narrow, sourced version, from Plaid's own OAuth documentation:

> "With OAuth, end users can grant third parties access to their data without sharing their
> credentials directly with the third party."

with the mandate that *"OAuth support is required in all Plaid integrations that connect to
financial institutions in the US, EU, and UK"* — and the limitation Plaid states itself: OAuth
is universal in the UK and EU, used by *"a number of"* US institutions, and **not currently
used in Canada.** The migration is explicitly incomplete, so nothing here implies otherwise.

Plaid's documentation never uses the phrase "screen scraping." Where that framing appears in
commentary, it belongs to the author, not to Plaid.

---

## Part 2 — What the public record cannot answer

Each of these is unresolvable from outside. Several are the first questions to ask in the seat.

### On the certifications

| # | Question | Public record | Unresolvable from outside |
|---|---|---|---|
| 1 | Which **ISO 27001 version** — :2013 or :2022? | The trust center lists "ISO-27001" with no year. | The certificate is behind the NDA gate. Given the October 2025 transition deadline the answer is almost certainly :2022, but *almost certainly* is not a citation, so no version is stated anywhere in this repo. |
| 2 | What is the **ISO 27701 certificate scope**? | Listed as held. | ISO 27701 is certifiable only as an extension to an ISO 27001 ISMS, so the PIMS scope inherits the ISMS boundary — which is not public. This is blocking question **OQ-02** on the mapping. |
| 3 | Is the certified role **PII controller, PII processor, or both**? | Not stated. | This selects Annex A, Annex B, or both, and therefore changes which mapping entries are in scope. Getting it wrong inverts the mapping. Blocking question **OQ-01**. |
| 4 | What **SOC 2 report period** and which auditor? | The document catalog names a "SOC 2 Type II with ISAE 3000 Combined Report." | Gated. Never stated. |
| 5 | What is in the **full NDA-gated document catalog**? | The 2023 launch blog named SOC 2, ISO certificates, penetration testing results, cyber insurance and policies — explicitly non-exhaustive ("such as … etc"). | The live catalog is a JavaScript application; the gated per-document list was never enumerated. More artifacts may exist. |
| 6 | **Penetration testing cadence** and scope? | Doyensec appears on the trust center, indicating an independent assessment. | Cadence, scope and findings are gated. |
| 7 | The **subprocessor list**. | Not located. | Directly material to `TPM-02` and to ISO 27701 B.8.5.6/B.8.5.8. |

### On the products and the regulatory position

| # | Question | Public record | Unresolvable from outside |
|---|---|---|---|
| 8 | Is **Plaid Consumer Reporting Agency, Inc. (dba Plaid Check)** also a *furnisher* under FCRA §623, as distinct from a CRA? | Plaid states FCRA and GLBA compliance in its CRA privacy policy, and the API requires a `consumer_report_permissible_purpose` parameter. | Furnisher status and whether it is a *nationwide specialty* CRA — which would trigger annual free file disclosure duties — are not stated. Neither is asserted here. |
| 9 | Does Plaid treat itself as a **GLBA "financial institution"**? | The End User Privacy Policy invokes the Regulation P exceptions at 12 C.F.R. §§ 1016.13, 1016.14 and 1016.15. | Plaid never uses the phrase about itself. The quote is published here; the inference is not. |
| 10 | Does the **FTC Safeguards Rule** (16 CFR Part 314) apply? | No Plaid statement found referencing it. | Structurally, a non-bank GLBA financial institution falls under Safeguards rather than the banking agencies' guidelines — but that is analysis, not a sourced fact. |
| 11 | Does Plaid have direct **BSA/AML** obligations? | Plaid positions Monitor as a *tool*, telling customers to *"consult with an AML professional."* | Whether Plaid itself is an obligated entity is not stated. Not speculated on. |
| 12 | Does **DORA** apply to Plaid B.V.? | Two regulated EU/UK entities are disclosed with named supervisors. | Unverified. Not asserted. |
| 13 | Current **bank data-access pricing**. | The JPMorgan Chase renewal (2025-09-16) states it *includes a pricing structure* and would not impact Plaid's current customer agreements and pricing. | The fee terms are not disclosed. Pricing at other banks is unverified. **No fee figure appears in this repo.** |

### On the settlement

| # | Question | Public record | Unresolvable from outside |
|---|---|---|---|
| 14 | What are the **durations and retention limits** in the settlement's non-monetary commitments? | Four commitments are public: minimize data stored going forward, delete certain previously retrieved data, maintain enhancements to Plaid Link, and provide Plaid Portal for connection management and deletion. | The specifics live in the settlement agreement itself, an exhibit to DE 156, which was not retrieved. Durations are not stated here. |

*In re Plaid Inc. Privacy Litigation*, No. **4:20-cv-03056** (N.D. Cal.), final approval
2022-07-20. **Plaid denied all allegations and any wrongdoing.** Note the citation trap: the
settlement website gives the number as `4:20-md-03056`, but court records show a consolidated
case, not an MDL. This repo uses the court's number.

### On enforcement

| # | Question | Public record | Unresolvable from outside |
|---|---|---|---|
| 15 | Has Plaid faced **FTC or CFPB enforcement**? | The CFPB enforcement database returns no Plaid results, and a federal docket party search found no case with the US, FTC or CFPB as plaintiff. | **Absence of evidence, not proof of absence.** The FTC case library returned HTTP 403, and administrative consent orders do not appear in court dockets. The phrasing used throughout is *"none publicly identified as of 2026-08-15"* — never "never." |

---

## Part 3 — Questions for the first week in the seat

Not answerable from outside, and not meant to be:

1. Which systems of record already expose an API that a collector could read today, and which
   would need one built? The config leaves `identity`, `docs`, `comms` and `grc-tool`
   **deliberately unset** because Plaid has never named them publicly. Guessing them would
   have meant inventing evidence sources.
2. Where does control state live today, and is any of it already queryable in SQL?
3. What does the current evidence pull actually cost in person-hours per audit cycle? That is
   the baseline every automation claim should be measured against, and it is the number most
   programs never write down.
4. Which of the 7 `partial` FedRAMP KSI deltas are already closed internally, and therefore
   only need evidence rather than build?
5. Is the ISO 27701 certificate scoped to controller, processor, or both — the question that
   unblocks the mapping.
