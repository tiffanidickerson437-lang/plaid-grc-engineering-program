# Governance — what the public record says

Three files, and a discipline.

| File | What it is |
|---|---|
| [`regulatory-clock.md`](regulatory-clock.md) | Every governing date, verified from primary sources — and the finding that **no Section 1033 compliance deadline currently survives** |
| [`open-questions.md`](open-questions.md) | What the public record cannot answer, **and the seven claims that were refuted during research** |
| [`plaid-github-map.md`](plaid-github-map.md) | Plaid's public engineering surface, read for GRC relevance |

## The findings, from the public record

Six things visible from outside. Each is a springboard, not an accusation — if it is visible
to me it is visible to an auditor, a customer's security team, and a competitor.

| # | Finding | Source | Turns into |
|---|---|---|---|
| 01 | **The trust center lists six items under "Certifications," but only three are certifications.** TruSight is a third-party risk assessment utility (acquired by S&P Global in January 2023 and folded into Market Intelligence KY3P), Doyensec is an application-security firm, and AWS Foundational Technical Review is a partner review. | [security.plaid.com](https://security.plaid.com/) | Precision in every reference to them in this repo. Never "TruSight-certified." |
| 02 | **ISO 27701 is held but its scope is unknowable from outside** — and the controller/processor determination that drives it is unstated. | trust center | [The ISO 27701 mapping](../mappings/iso27701.draft.yaml), shipped as a draft with that as blocking question OQ-01 |
| 03 | **No FedRAMP authorization, and the posting says new authorizations are coming.** | trust center + the posting | [All 46 CR26 KSIs mapped](../04-evidence-and-audit/data/fedramp-20x-ksi-mapping.yaml) |
| 04 | **The Section 1033 deadline does not exist** — enjoined since 2025-10-29, no replacement proposal as of the CFPB's 2026-08-14 Unified Agenda. | Federal Register + the dockets | [`regulatory-clock.md`](regulatory-clock.md), and the argument for continuous over deadline-driven compliance |
| 05 | **The agent authorization enforcement point is built and public; the control over it is not.** Identity-aware proxy, call-time tool restrictions, short-lived DPoP tokens, dozens of internal agents. | [engineering blog](https://engineering.plaid.com/the-plaid-internal-mcp-server-8eff08bb6bdb) | [`AAT-01` as hero control](../02-ai-governance/) |
| 06 | **Security is already shared infrastructure; compliance is not.** CI templates and Terraform modules enforce security checks across every repo by default — and the posting says compliance work is still "manual and point-in-time." | [security-as-a-platform](https://plaid.com/blog/security-as-a-platform/) + the posting | The thesis of this whole repository: run the same play for compliance evidence |

**Finding 06 is the application.** Everything else supports it.

## The discipline

Every value in [`plaid.config.yaml`](../generated/companies/plaid/plaid.config.yaml) carries an
inline marker: **VERIFIED**, **NAMED IN POSTING**, **INFERRED**, or **DELIBERATELY UNSET**.

The last one matters most. `identity`, `docs`, `comms` and `grc-tool` are empty because Plaid
has never publicly named those systems. The engineering blog says "an identity-aware proxy"
and "identity provider authentication" without naming the IdP. Writing `okta` there would have
been a guess dressed as a system of record — and an invented evidence source is worse than a
blank one, because it looks finished.

`evidence_in_repo: none` is load-bearing. No Plaid evidence exists here and none is claimed.
