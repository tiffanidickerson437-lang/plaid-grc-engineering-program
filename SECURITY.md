# Security policy

This repository ships compliance tooling. A defect in a checker here is not a normal bug — a
validator that silently stops validating reports "clean" forever after, and anyone relying on
it inherits that silence. Please report problems rather than filing them as feature requests.

## Reporting a vulnerability

**Use GitHub's private vulnerability reporting** — the *Report a vulnerability* button under the
repository's Security tab. That opens a private advisory only maintainers can see.

Please do not open a public issue for a security defect until it has been fixed.

If private reporting is unavailable to you, email **tiffanidickerson437@gmail.com** with
`SECURITY` in the subject line.

**What to expect:** an acknowledgement within 5 business days, an assessment within 10, and
credit in the advisory unless you ask otherwise. This is a personal project, not a funded
program — these are best-effort targets, stated as such rather than dressed up as an SLA.

## What counts as a security issue here

Beyond the usual, these are specifically in scope because of what this repository is:

| Class | Why it matters |
|---|---|
| **A validator that passes invalid input** | The whole repository's claim rests on the checkers failing closed. A false negative is the highest-severity defect class here. |
| **A validator that can be neutered without turning its own suite red** | Every checker carries a mutation guard for exactly this reason. A gap in that guard is a real finding. |
| **A path where a draft mapping is counted as approved coverage** | `strm_coverage.py` refuses this deliberately. A bypass would let unreviewed work be reported as satisfied coverage. |
| **A path where model-generated content could be recorded as evidence** | The upstream engine rejects `ai_generated: true` at schema, hook and CI layers. Any route around that is a security issue, not a style issue. |
| **Dependency or workflow supply-chain issues** | Actions are pinned to full commit SHAs; a tag-based reference slipping in is a finding. |

## What is out of scope

- **Anything about Plaid's actual security posture.** This repository contains no Plaid evidence,
  no credentials, and no non-public information. `evidence_in_repo: none` in the config is
  load-bearing and enforced by `.gitignore`. If you believe something here discloses non-public
  Plaid information, that is very much in scope — report it and it will be removed immediately.
- Findings in the upstream engine, which has its own policy.
- The accuracy of the ISO 27701 requirement text, which is documented as drawn from secondary
  sources and marked `DRAFT_PENDING_HUMAN_APPROVAL`. Corrections are welcome as issues.

## Hardening in place

- Every GitHub Action pinned to a full commit SHA, never a mutable tag
- Workflow `permissions:` scoped to `contents: read`
- No workflow step may swallow a failure — no `|| true`, no `continue-on-error`
- Secret scanning and push protection enabled
- Dependabot alerts and security updates enabled
- `main` protected: pull request required, status checks must pass, force-push and deletion blocked
- CodeQL analysis on every push and pull request
- One runtime dependency, pinned
