# 30 · 60 · 90

What I would run in the seat. Written against the posting's own responsibilities, and honest
about which parts depend on access I do not have.

**The standing assumption:** Plaid's security organization already treats controls as shared
infrastructure — CI templates, Terraform modules, checks that enforce themselves across every
repository by default. This plan does not propose building that. It proposes **extending it
from security findings to compliance evidence**, which is a smaller and more tractable problem
than it sounds, because the hard part — the platform, the pipeline, the developer trust — is
already done.

---

## Days 0–30 — Baseline what is computable today

**Theme: find out what control state is already queryable, and write down the number nobody has written down.**

- Inventory the systems of record and mark, for each, whether control state is already exposed
  via API, exposed only via UI, or not exposed at all. The config in this repository leaves
  `identity`, `docs`, `comms` and `grc-tool` **deliberately unset** because Plaid has never
  named them publicly — filling those four fields is the first concrete deliverable.
- Establish the baseline that every automation claim will be measured against: **person-hours
  per audit cycle spent on evidence collection today**, broken down by control family. Most
  programs never write this down, which is why most automation ROI claims are unfalsifiable.
- Confirm the **ISO 27701 controller/processor determination** (blocking question OQ-01 on the
  mapping) and the certificate scope. Without it the ISO 27701 crosswalk cannot be approved.
- Walk the existing security platform with its owners. Understand where a compliance check
  would slot into the three-layer pipeline that already runs, rather than proposing a parallel one.
- Take the 7 `partial` FedRAMP KSI deltas and sort them into *already closed internally, needs
  evidence only* versus *genuinely needs build*. That ratio drives everything after.

**Exit criteria**

- [ ] Systems-of-record inventory complete; the four unset config fields filled with real values
- [ ] Evidence-collection baseline measured in hours, by control family
- [ ] ISO 27701 scope and role confirmed; OQ-01 and OQ-02 closed
- [ ] The 46 KSIs re-sorted against Plaid's actual posture rather than the engine's control set
- [ ] One control chosen for the first end-to-end continuous pipeline

---

## Days 31–60 — One control, end to end, computed

**Theme: prove the pattern on a single control before proposing it for forty-four.**

- Build the first **deterministic collector** against a real system of record — least
  privilege, hashed, timestamped output, no model in the path. Choose a control whose evidence
  is currently a screenshot, because that is the one FedRAMP RFC-0017 says an assessor must
  not accept.
- Write the pass/fail as **policy-as-code with paired allow and deny fixtures**, so the rule
  is unit-tested before it ever runs against production state.
- Wire it into the existing CI pattern rather than a new one. The check runs where the security
  checks already run, reports where they already report.
- Stand up the **drift signal**: when computed state diverges from baseline, an Issue opens
  carrying the control ID, owner, framework impact, and the evidence needed. The Issue is the
  record of due diligence.
- Approve the ISO 27701 mapping through pull request once OQ-01–03 are closed, and re-run the
  coverage report so the number is computed rather than drafted.

**Exit criteria**

- [ ] One control fully continuous: collected, tested, alerting, evidenced — with no manual step
- [ ] Its evidence regenerable on demand, satisfying RFC-0006's standard
- [ ] Policy tests running in CI with allow *and* deny fixtures
- [ ] ISO 27701 mapping approved by a human; coverage recomputed and published
- [ ] The person-hours baseline for that one control measured again, and the delta reported honestly

---

## Days 61–90 — Make it a pattern, and make risk legible

**Theme: turn one pipeline into a template, and turn control data into something leadership reads.**

- Generalize the collector into a **template** other control owners can instantiate — the same
  move the security platform made when it turned per-repo tooling into a Terraform declaration.
- Build the **SQL and dashboard layer**: control health, drift rate, mean time to remediate,
  evidence freshness. The posting names Mode; whatever the tool, the requirement is that a
  leader can answer "what is our posture" without asking a person.
- Recalibrate the **FAIR risk register** to Plaid's actual scenarios, replacing the engine's
  example archetype. This is where the honest limitation lives — see below.
- Run the framework crosswalk in anger: pick the next target regime and produce the gap list
  from existing mappings rather than a new assessment.

**Exit criteria**

- [ ] A second and third control onboarded by their owners using the template, not by me
- [ ] A dashboard leadership actually opens, with at least one metric that has changed a decision
- [ ] Risk register recalibrated to Plaid scenarios, with the quantification method documented
- [ ] A written answer to "what would it take to be FedRAMP 20x assessable," grounded in the KSI deltas

---

## What I will not do

- **Claim continuous evidence collection before it exists.** The instruments in this repository
  run against committed data and public surfaces. They do not read Plaid's systems, and nothing
  here pretends otherwise.
- **Put a model in the pass/fail path.** For the reasons in [02-ai-governance](../02-ai-governance/),
  with citations.
- **Propose a parallel platform.** Plaid has one. The work is extending it, not competing with it.
- **Report a coverage percentage that averages complete and partial coverage together.** It
  destroys the only number a reader needs.

## The honest limitation on day 91

Three of these exit criteria depend on access I cannot verify from outside: whether control
state is queryable at all, whether the security platform's pipeline can host a compliance
check without a rewrite, and whether the ISO 27701 certificate is scoped to controller,
processor or both.

If any of those three turns out badly, the 60-day milestone slips. Saying so now is better
than discovering it in week six — and the first 30 days are deliberately structured to find
out early.
