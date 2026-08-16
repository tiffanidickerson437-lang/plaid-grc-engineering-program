# The regulatory clock — and the deadline that isn't

**All dates verified from primary sources as of 15 August 2026.** Docket entries were read
from the court records, not from secondary coverage.

---

## The short version

**Plaid has no Section 1033 compliance deadline.** Not a distant one — none.

The rule exists, codified at 12 CFR Part 1033. The CFPB is enjoined from enforcing it. Every
compliance date is stayed. The appeal is held in abeyance. And as of one day before this was
written, the Bureau has published no replacement proposal and no projected date for one.

A compliance program built around deadlines does nothing for two years and then panics. That
is the entire argument for continuous controls monitoring, and it is why this repository
counts *up* from the injunction rather than down to a date.

---

## What happened, in order

| Date | Event |
|---|---|
| 2024-10-22 | Final rule released. Challenged the **same day**. |
| 2024-11-18 | Published at **89 FR 90838**. Effective 2025-01-17. Codified at 12 CFR Part 1033. |
| 2025-07-29 | Case **stayed** pending the CFPB's new rulemaking (DE 83). All three summary-judgment motions denied without prejudice. |
| 2025-08-22 | **ANPR** published — *Personal Financial Data Rights Reconsideration*, 90 FR 40986. Comments closed 2025-10-21. |
| **2025-10-29** | **The CFPB is ENJOINED from enforcing the rule until it completes its reconsideration** (DE 90). |
| 2025-12-26 | Notices of appeal filed by both the CFPB and the Financial Technology Association. |
| 2026-02-12 | Sixth Circuit consolidates Nos. 25-6164 and 26-5005. |
| **2026-03-30** | **Briefing HELD IN ABEYANCE.** Schedule cancelled. Status reports every 60 days. |
| 2026-04-01 | **The first-tier compliance date passes without ever becoming binding.** |
| 2026-07-28 | Latest status report filed. Next due **2026-08-27**. |
| 2026-08-14 | The CFPB's **2026 Unified Agenda** (91 FR 53082) mentions 1033 once, as something it is "planning to pursue." **No timetable. No projected NPRM date. No rule stage.** |

The case is ***Forcht Bank, NA v. CFPB***, No. **5:24-cv-00304** (E.D. Ky.) — brought by Forcht
Bank, the Kentucky Bankers Association and the Bank Policy Institute. The **Financial
Technology Association intervened as a defendant**, defending the rule. That detail matters
for reading the landscape: the fintech trade body is in the case on the government's side.

The CFPB's own characterization, from its 2026-05-29 status report:

> "The Bureau is continuing to conduct the rulemaking to reconsider the Personal Financial
> Data Rights Rule (Rule), **with a view to substantially revising it**."

## The dates that were supposed to bind, and don't

12 CFR § 1033.121 as written. **Every one of these is stayed.**

| Date | Tier |
|---|---|
| ~~2026-04-01~~ | Depositories ≥$250B; nondepositories ≥$10B receipts |
| ~~2027-04-01~~ | Depositories ≥$10B and <$250B; **all other nondepositories** |
| ~~2028-04-01~~ | Depositories ≥$3B and <$10B |
| ~~2029-04-01~~ | Depositories ≥$1.5B and <$3B |
| ~~2030-04-01~~ | Depositories >$850M and <$1.5B |

> ⚠ **Do not build a countdown on 2027-04-01.** It is the tier a nondepository data network
> would fall into, it is stayed, and a fintech GRC audience knows it. Publishing that date as
> a live obligation would be the single most damaging error available in this material.

## What a GRC function actually tracks right now

One genuinely dated, forward-looking item exists on this file, and it is a **litigation**
milestone, not a compliance obligation:

**2026-08-27 — the next status report in the consolidated Sixth Circuit appeals**, recurring
every 60 days.

Tracking a docket rather than a deadline is precisely what a real GRC function does with a
suspended rule. Labelled honestly, it is a better signal than a fake countdown.

## The nearest real dated obligations

From the CPPA's approved regulation text (approved 2025-09-22, effective 2026-01-01), read
from the primary PDF:

| Date | Obligation | Cite |
|---|---|---|
| 2027-01-01 | ADMT compliance for significant decisions | 11 CCR § 7200(b) |
| 2027-12-31 | Risk assessment for processing that began before the effective date | 11 CCR § 7155(b) |
| **2028-04-01** | **First cybersecurity audit report** (>$100M 2026 revenue tier), covering 2027 | 11 CCR § 7121(a)(1) |
| 2028-04-01 | Submit 2026–2027 risk assessments to the Agency | 11 CCR § 7157(a)(1) |

> ⚠ **These are not asserted to bind Plaid.** The CCPA carries data-level exemptions for
> information collected or processed under **GLBA** and under the **FCRA**, and a
> consumer-permissioned financial data network plausibly sits inside both carve-outs. The
> exemption subsection numbers were **not** verified. Read this table as *a dated obligation
> in scope for a California-headquartered data business of this size*, never as a
> determination about Plaid. Making that determination requires counsel and internal facts.

## State open banking

**No enacted state open-banking statute with an effective date was found.**

New York Assembly Bill 10640 (introduced 2026-03-13) and Senate Bill 9483 (2026-03-17) would
go broader than the federal rule — covering all consumer financial products *and small
business accounts* — with penalties up to $10,000 per violation enforced by the Superintendent
of Financial Services. **Both remain in committee.** Single secondary source (Ballard Spahr,
Consumer Finance Monitor, 2026-06-26); verify on nysenate.gov before relying on it.

## Why this file is the argument, not the caveat

The posting says Plaid's compliance work today is "manual and point-in-time," and asks the
hire to make it "continuous, data-driven, and scalable."

A suspended rule is the cleanest possible case for that. There is no date to work backwards
from. There is no audit to sprint toward. The rule may return substantially revised, on a
timetable nobody controls, and the only posture that survives that is one where control state
is computed continuously and the question "are we ready" is answered by a query rather than a
project.

FedRAMP wrote the same conclusion into a standard for a different reason. **RFC-0017**:
assessors *"MUST NOT rely on screenshots, configuration dumps, or other point-in-time output
as evidence."* **RFC-0006**: packages *"must be in a machine-readable format that can be
regenerated on demand."*

Point-in-time evidence is exactly what a stayed deadline leaves you holding.

---

## Sources

- Federal Register 89 FR 90838 (2024-11-18); 90 FR 40986 (2025-08-22); 91 FR 53082 (2026-08-14)
- *Forcht Bank, NA v. CFPB*, No. 5:24-cv-00304 (E.D. Ky.) — docket entries 83, 90, 94, 95
- Sixth Circuit Nos. 25-6164 / 26-5005 — consolidation order, abeyance order, status reports
- 12 CFR § 1033.121 (compliance dates)
- CPPA approved regulation text, 11 CCR §§ 7121, 7155, 7157, 7200
- FedRAMP RFC-0006, RFC-0017

**Not verified, and therefore not stated as fact anywhere above:** PCI DSS 4.0.1 future-dated
requirements; NYDFS Part 500 phased deadlines *and whether Plaid is a covered entity at all*;
DORA applicability to Plaid B.V.; the PSD3/PSR timeline; FDX's status as a recognized
standard-setting body (note the trap — that framework hangs off the same enjoined rule).
