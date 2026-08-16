# Plaid's public engineering surface, read for GRC relevance

What `github.com/plaid` publishes, and what an operator can do with it. All repositories are
**MIT licensed**, which means a fix is openable as a real pull request rather than a mockup.

Observed 2026-08-15.

## The repositories that matter here

| Repo | Why a GRC engineer cares |
|---|---|
| **`plaid-openapi`** | The full machine-readable API specification (version 2020-09-14). Every endpoint that returns financial account data, identity, transactions, investments and liabilities is enumerated in a structured file. **This is a data-minimization control catalog that no compliance machine currently reads.** |
| **`core-exchange`** | The Core Exchange spec and generated server code — the open-banking data-sharing surface. Structured, versioned, and directly downstream of the Section 1033 conversation. |
| **`ai-coding-toolkit`** | A Python developer toolkit for building Plaid integrations. A live AI surface with a public artifact, updated within the last week of observation. |
| 9 client SDKs | node · python · ruby · java · go · react · react-native · iOS · Android |
| 7 quickstarts | quickstart · tiny-quickstart · pattern · income-sample · transfer-quickstart · layer-quickstart · idv-quickstart |

**Five of these are named as in-scope assets on Plaid's HackerOne program**:
`react-plaid-link`, `react-native-plaid-link-sdk`, `plaid-ruby`, `plaid-link-ios`,
`plaid-link-android`. That is a published, bounded attack surface with a paid disclosure
channel attached — and it is a stronger `VPM-01` evidence source than most companies have.

## The observation

A machine-readable API specification is a structured, authoritative statement of exactly what
data the platform can return. It is the closest thing to a computable purpose-and-minimization
inventory that exists for a data network, and it is already public.

Nothing currently reads it for compliance purposes.

That is the same shape as every other finding in this repository: **the structured surface is
already published — that is the hard part, and it is done — but nothing runs against it.**

## Why no instrument against it ships here yet

An honest scoping note rather than a silent omission.

A minimization checker over `plaid-openapi` is the obvious next instrument, and it was scoped.
It is not in this repository because the check that would matter — *does each endpoint return
only what its declared purpose requires* — needs a purpose declaration to compare against,
and **Plaid publishes the schema but not the purpose binding.** Building it without that would
produce a checker that counts fields and calls it minimization, which is exactly the kind of
metric that looks rigorous and measures nothing.

What *can* be computed from the spec alone, and would be the honest first version:

- the set of endpoints returning fields classifiable as consumer financial data, as a
  computed inventory rather than an asserted one
- schema drift between spec versions, as a change-detection signal on that inventory
- endpoints whose response schema grew between versions — a proportionality question worth a
  human's attention, stated as a question rather than a finding

That is a real instrument with a real limitation, and the limitation is the interesting part:
**the purpose binding is internal, so the useful version of this check cannot be built from
outside.** Building it is a first-week project in the seat, not a portfolio demo.

Saying that plainly is better than shipping a checker whose output looks like compliance and
isn't.

## Engineering blog — the three posts this repository leans on

| Post | Date | Load-bearing content |
|---|---|---|
| [Security as a Platform](https://plaid.com/blog/security-as-a-platform/) | 2026-01-15 | *"Treat security like infrastructure"* — CI templates, Terraform modules, checks enforced across every repo by default; incident-to-guardrail conversion; a pipeline that already includes *"privacy & compliance scanning"* |
| [Security at scale: Plaid's KMS](https://engineering.plaid.com/security-at-scale-b94475905810) | 2024-12-19 | AWS KMS as root of trust, envelope encryption, *"all sensitive data must be protected using Plaid KMS"*, hundreds of services across tens of thousands of pods. **Names no algorithms or key sizes** — which is why none are cited anywhere in this repo |
| [The Plaid Internal MCP Server](https://engineering.plaid.com/the-plaid-internal-mcp-server-8eff08bb6bdb) | 2025-07-29 | Identity-aware proxy, call-time tool restrictions, Device Authorization Grant with DPoP and short-lived bearer tokens, *"thousands of tool calls and dozens of agents"* |

The first of those is the most important document in this entire research file. It establishes
that Plaid has already built the architecture this role is meant to extend — for security
findings — and the posting establishes that compliance has not received the same treatment.
