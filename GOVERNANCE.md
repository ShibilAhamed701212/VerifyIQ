# VerifyIQ Governance Model

**VerifyIQ is a production-oriented AI agent framework for multimodal claim verification. It performs reasoning, risk analysis, fraud detection, and decision-making using observations supplied by external vision providers (VLMs). Users configure their own VLM — Gemini, OpenRouter, local models, or custom providers. VerifyIQ does not contain a proprietary vision model.**

**Version:** 1.0  
**Status:** Target — this governance model will take effect as the project transitions from single-maintainer to community-driven development.  
**Last Updated:** June 2026

> **Current state:** VerifyIQ is a single-maintainer project. Sections below describe the target governance model for when the community grows. Until then, the lead maintainer makes all decisions, with input from contributors via GitHub Issues and Discussions.

> **Project identity:** As an agent framework (not a proprietary model), VerifyIQ's governance emphasizes provider neutrality, community contributions to the provider ecosystem, and maintaining a clear separation between the core reasoning engine and pluggable observation providers.

---

## 1. Maintainership Model

VerifyIQ uses a tiered maintainership model designed to balance bus factor, prevent decision deadlocks, and reduce maintainer burnout through clear role definitions and rotation policies.

### 1.1 Tiers

#### Lead Maintainer (1 person)

The Lead Maintainer holds final decision authority and is responsible for the project's strategic direction.

**Responsibilities:**
- Set the project vision and roadmap
- Manage version releases and the release calendar
- Break ties on contentious votes
- Approve new Core Maintainers
- Represent the project in community and press events
- Own security vulnerability response

**Privileges:**
- Final say on all decisions (tie-breaking vote, veto power on releases)
- Direct write access to the main branch
- Authority to freeze releases in case of critical issues
- Sole authority to designate LTS releases

**Advancing to Lead Maintainer:**
- Must be a Core Maintainer in good standing for at least 6 months
- Nominated by at least 2 Core Maintainers or the current Lead Maintainer
- Approved by a 2/3 majority vote of all Core Maintainers
- No term limit, but subject to annual confirmation vote by Core Maintainers

**Stepping Down:**
- Voluntary resignation with 1 month notice preferred
- Removal requires a 3/4 majority vote of Core Maintainers for cause (inactivity >6 months, Code of Conduct violations, gross negligence)
- On resignation, the Lead Maintainer may nominate a successor; Core Maintainers vote with 2/3 majority to confirm

#### Core Maintainers (2–5 people)

Core Maintainers own specific modules or cross-cutting concerns and drive day-to-day project maintenance.

**Responsibilities:**
- Own one or more modules (e.g., rule engine, VLM adapters, CLI, test infrastructure)
- Review and merge PRs in their owned modules
- Triage and respond to issues within 7 days
- Participate in release rotation (see Section 3)
- Mentor new Contributors
- Participate in roadmap discussions and votes
- Maintain module documentation and test coverage

**Privileges:**
- Write access to the repository
- Vote on RFCs, new Core Maintainers, and contentious decisions
- Authority to merge PRs in their owned modules (subject to CI passing)
- Access to private security issue trackers
- Participation in Core Maintainer discussions

**Advancing to Core Maintainer:**
- Consistent contribution history (>20 merged PRs or equivalent) over at least 3 months
- Demonstrated module expertise through quality reviews and issue resolution
- Sponsored by an existing Core Maintainer
- No objection from any Core Maintainer in a 7-day lazy-consensus period (see Section 6)
- If an objection is raised, a 2/3 majority vote of Core Maintainers is required

**Stepping Down:**
- Voluntary resignation at any time
- Automatic removal after 3 months of inactivity (no PRs reviews, issue comments, or commits)
- Removal for cause by Lead Maintainer with Core Maintainer majority support

#### Contributors

Anyone who submits a pull request, files a bug report, or contributes code, documentation, or tests.

**Responsibilities:**
- Follow the contribution guidelines
- Adhere to the Code of Conduct
- Respond to review feedback in a timely manner
- Ensure their contributions have passing tests and lint

**Privileges:**
- Ability to submit PRs and issues
- Access to GitHub Discussions
- Listed in release notes and/or CONTRIBUTORS.md on first merged PR
- Invitation to community calls

**Advancing to Contributor:**
- Simply submit a PR or issue. No formal process.

#### Community Members

Users, discussion participants, and anyone using VerifyIQ.

**Responsibilities:**
- Follow the Code of Conduct
- Provide constructive feedback

**Privileges:**
- Access to public repositories, documentation, and issue trackers
- Participation in GitHub Discussions and community calls
- Use of VerifyIQ under its license terms

### 1.2 Bus Factor Mitigation

- No single person may be the sole reviewer or owner of any critical path module
- Each module must have at least 2 Core Maintainers familiar with it
- The full release process must be documented and executable by any Core Maintainer
- Key secrets (PyPI credentials, signing keys) must be accessible via a secret-management system (e.g., 1Password teams, `sops`) with at least 3 Core Maintainers having access

### 1.3 Burnout Prevention

- Core Maintainers are expected to take at least 2 weeks of disconnection per year
- During absence periods, module ownership is covered by backup maintainers
- Release manager rotation prevents any single person from bearing release burden
- No Core Maintainer is expected to respond to issues or reviews outside their normal working hours
- A "no-blame" culture for delayed responses — life comes first

---

## 2. Versioning Strategy

VerifyIQ follows **Semantic Versioning 2.0.0** with the format `MAJOR.MINOR.PATCH[-pre-release]`.

### 2.1 What Each Bump Means

| Bump | VerifyIQ Meaning | Examples |
|------|-----------------|---------|
| **MAJOR** | Breaking API changes, pipeline architecture redesign, removal of deprecated features, large-scale configuration changes | Renaming public classes/functions, removing adapter interfaces, changing the pipeline execution model, dropping Python version support |
| **MINOR** | New backward-compatible features, new VLM providers, new detectors, new pipeline stages, dependency updates that add functionality | Adding a Gemini 2.5 adapter, adding a new claim type detector, expanding confidence scoring, new CLI flags |
| **PATCH** | Bug fixes, security patches, documentation improvements, performance optimizations, test additions | Fixing a parsing edge case, updating test fixtures, fixing CI, patching a dependency vulnerability |

### 2.2 Pre-Release Tags

| Tag | Purpose | Stability | Audience |
|-----|---------|-----------|----------|
| `alpha` | Active development; frequent breaking changes | Unstable | Core Maintainers and early adopters willing to track closely |
| `beta` | Feature-complete; stabilization phase | Mostly stable | Community testers |
| `rc` | Release candidate; final validation | Stable (if no regressions found) | All users for final testing |

Pre-release versions sort before the final release per SemVer precedence rules.

### 2.3 What Constitutes a Breaking Change in VerifyIQ

A change is **breaking** if it:

1. **Removes or renames any public API** — any function, class, method, or module exposed in the package's `__init__.py` or documented as public
2. **Changes the signature of a public API** — adding required parameters, reordering parameters, changing parameter types
3. **Changes the output format** — any structured output (JSON schemas, confidence score ranges, result dictionaries) that consumers may parse
4. **Removes or renames CLI commands or flags**
5. **Changes the pipeline execution model** — e.g., changing from synchronous to asynchronous execution, altering stage ordering semantics
6. **Drops support for a Python version** — follows Python end-of-life schedule
7. **Changes configuration file format** — breaking changes to `verifyiq.toml`, `verifyiq.json`, or environment variable names
8. **Changes the database schema** for any persisted storage
9. **Upgrades a major dependency version** that alters behavior (e.g., a VLM provider SDK major version)

**What is NOT breaking:**
- Adding new public APIs (non-breaking)
- Changing internal/private APIs (prefixed with `_`)
- Changing error messages (unless parsed by consumers)
- Performance improvements that don't change semantics
- Adding optional parameters with defaults

### 2.4 Communicating Breaking Changes

- All breaking changes must be documented in the **CHANGELOG.md** under a "Breaking Changes" sub-heading
- A deprecation warning must be issued at least 2 MINOR versions before the breaking change takes effect (see Section 5)
- The PR that introduces a breaking change must clearly label itself with a `[breaking]` tag in the title
- Breaking changes must be announced on GitHub Discussions with a dedicated post at least 2 weeks before the release
- A migration guide must accompany the release notes

### 2.5 Version Lifecycle

| Stage | Definition | Duration | Actions |
|-------|-----------|----------|---------|
| **Current** | Latest stable release | Until next release | Full support: bug fixes, security patches, feature backports (minor) |
| **Maintained** | Previous MINOR series | 3 months after next major/minor | Critical bug fixes and security patches only |
| **Deprecated** | Older releases | Indefinite | No active work; community PRs accepted |
| **End of Life (EOL)** | No longer supported | Permanent | No patches, no backports; users must upgrade |

---

## 3. Release Strategy

### 3.1 Release Cadence

| Release Type | Cadence | Process |
|-------------|---------|---------|
| **Minor** | Monthly (e.g., 1st Tuesday of each month) | Full release checklist |
| **Patch** | As needed (security fixes: within 72 hours; critical bugs: within 1 week; normal bugs: batched monthly) | Streamlined checklist |
| **Major** | No fixed schedule; when breaking changes accumulate | Full release checklist + migration guide + deprecation cleanup |
| **LTS** | Bi-annual (every 12 months from first stable release) | Extended support window (18 months) |

### 3.2 Release Manager Rotation

- The Release Manager role rotates among Core Maintainers on a monthly basis
- Release Manager is responsible for shepherding the month's minor release through the checklist
- The rotation schedule is maintained in `RELEASE_SCHEDULE.md`
- Each Release Manager serves as backup for the following month's manager
- New Core Maintainers are exempt from release rotation for their first 2 months

### 3.3 Release Checklist

For each release:

1. **Changelog**: Verify `CHANGELOG.md` is up-to-date with all merged PRs categorized (Breaking, Features, Fixes, Documentation, Internal)
2. **Version Bump**: Update version in `verifyiq/__version__.py`, `pyproject.toml`, and all relevant metadata
3. **Deprecation sweep**: Confirm any features scheduled for removal have had the required deprecation warnings in place for the correct number of versions
4. **Tag**: Create a signed git tag (`v{major}.{minor}.{patch}`)
5. **Build**: Build distribution packages (`sdist` and `wheel`)
6. **Test Suite**: Run the full test suite:
    - All unit tests pass
    - All integration tests pass (with live VLM providers if credentials available)
    - All code examples in documentation execute without error
7. **Publish**: Upload to PyPI via trusted publishing
8. **Announce**: Post release notes to GitHub Releases and GitHub Discussions

### 3.4 Long-Term Support (LTS)

- LTS releases are designated by the Lead Maintainer every 12 months from first stable release
- LTS releases receive backported security fixes for 18 months from the LTS designation date
- Patch releases for LTS are cut from a dedicated `lts/{version}` branch
- Only critical bug fixes and security patches are backported to LTS
- LTS users should pin their dependency to the exact LTS minor (e.g., `verifyiq==1.2.*`)

### 3.5 CHANGELOG Format

The `CHANGELOG.md` follows the [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

## [1.3.0] - 2026-06-01

### Breaking Changes
- Removed deprecated `verify()` function (was deprecated since 1.1.0)

### Added
- New Gemini 2.5 Flash adapter (`verifyiq.providers.gemini_flash`)
- New `--confidence-threshold` CLI flag

### Fixed
- Fixed race condition in pipeline stage scheduler

### Security
- Updated `httpx` dependency to 0.28.x to fix CVE-2026-XXXX

### Deprecated
- `v1_config` format — use `v2_config` instead; will be removed in 2.0.0

## [1.2.1] - 2026-05-15
...
```

---

## 4. Semantic Versioning for AI Projects

AI agent frameworks with pluggable provider architectures present unique versioning challenges. This section documents how VerifyIQ handles them.

### 4.1 Model Provider API Changes

- **New provider version** (e.g., Gemini 2.5 → 2.6): If the API change is backward-compatible (same inputs, same output shape), it's a PATCH or MINOR change in the adapter layer
- **Provider version that changes behavior**: If the same API call produces different results (confidence scores shift, output formatting changes), this is treated as a MINOR change with explicit documentation in the provider's adapter module
- **Provider version that breaks the adapter**: The adapter is patched (PATCH release) if the fix is straightforward; a MAJOR release is used if the adapter interface must change

### 4.2 VLM Provider Output Format Changes

- VLM providers may change the structure of their JSON responses. Each adapter normalizes responses into VerifyIQ's internal representation. Any change to the normalization layer is versioned as:
  - **PATCH**: Fixing a parsing bug or handling an edge case
  - **MINOR**: Adding support for a new field in the normalized output
  - **MAJOR**: Removing or renaming a field in the normalized output struct

### 4.3 Confidence Score Distribution Shifts

- Confidence scores are probabilistic. If a provider update causes scores to shift across the distribution, this is documented in the release notes
- Any change to the confidence score range (e.g., 0.0–1.0 → 0.0–100.0) is a **MAJOR** breaking change
- New confidence aggregation strategies are **MINOR** additions (backward-compatible)
- Changes to how confidence thresholds are applied or interpreted are documented as behavioral changes and require a MINOR bump

### 4.4 Security Vulnerability Response

| Severity | Response Time | Release Type | Process |
|----------|---------------|-------------|---------|
| **Critical** (remote code execution, credential leakage) | 48 hours | Emergency PATCH | Lead Maintainer notified directly via security@ alias; private fork; CVE requested; fix released |
| **High** (denial of service via crafted input, data corruption) | 1 week | Priority PATCH | Private issue tracker; fix coordinated with reporters |
| **Medium** (minor information disclosure, hard-to-exploit issues) | Next PATCH cycle | Normal PATCH | Public issue filed; fix in next patch |
| **Low** (best-practice violations, hardening) | Next MINOR | Normal MINOR | Public issue filed |

Security reports should be sent to `security@verifyiq.dev` (or equivalent private channel). Do NOT file security vulnerabilities as public GitHub Issues.

### 4.5 API Key / Service Dependency Changes

- **Adding a new provider**: Non-breaking (MINOR)
- **Removing a provider**: Breaking for users of that provider (MAJOR), with 2 MINOR versions of deprecation warning
- **Changing credential format**: Breaking (MAJOR), with migration path documented
- **Service deprecation** (e.g., Google shuts down a model): Emergency MINOR/PATCH with migration guidance; the adapter is marked as deprecated immediately

---

## 5. Deprecation Policy

### 5.1 Deprecation Window

- Any feature, API, or configuration option being removed must be announced **2 MINOR versions** before removal
- Example: A feature deprecated in `v1.3.0` may be removed in `v1.5.0` at the earliest
- Exception: Security-critical removals may be accelerated with a 1 PATCH version warning if the Lead Maintainer determines the feature poses an active risk

### 5.2 Deprecation Warning Mechanism

- Deprecated features emit a `DeprecationWarning` at runtime (visible when `PYTHONWARNINGS=default` or via `warnings.warn`)
- Each warning includes:
  - The feature or API name
  - The version in which deprecation took effect
  - The version in which it will be removed
  - The replacement API or migration path
- Warnings are shown only once per unique call site (using `warnings.warn(..., stacklevel=2)`)
- CLI deprecation: a deprecation message is printed to stderr when the deprecated CLI flag/command is used

### 5.3 Legacy Behavior Gate

- For high-impact breaking changes, a legacy behavior flag may be provided:
  ```python
  from verifyiq import config
  config.LEGACY_CONFIDENCE_SCORING = True  # Use old scoring until migration is complete
  ```
- Legacy flags are documented in the module they affect
- Legacy flags are removed in the same MAJOR version as the breaking change
- Legacy flags must be explicitly opt-in; they must never be on by default unless the feature is not yet deprecated

### 5.4 Migration Path Documentation

- Every deprecation must include documentation of the migration path in:
  1. The `CHANGELOG.md` entry's deprecation notice
  2. The module's docstring or a dedicated migration guide file under `docs/migrations/`
  3. The runtime warning text
- Migration guides must include code before/after examples

### 5.5 Tracking

- The `DEPRECATIONS.md` file tracks all currently-deprecated features, their deprecation version, and their scheduled removal version
- This file is checked as part of the release checklist to ensure timely removals

---

## 6. Decision-Making Process

### 6.1 Principles

VerifyIQ operates on a **lazy consensus** model by default. Decisions are considered approved unless an objection is raised within a reasonable period. This minimizes process overhead while ensuring all voices can be heard.

### 6.2 Decision Types and Processes

| Type | Process | Timeframe | Participants |
|------|---------|-----------|-------------|
| **Trivial** (typos, CI fixes, refactoring, test additions) | Self-merge or single Core Maintainer review | Immediate | Individual |
| **Normal** (feature additions, bug fixes, documentation) | PR review by 1 Core Maintainer with ownership of module | 2–7 days | Core Maintainer |
| **Contentious** (disagreement on approach, significant design decisions) | Vote of Core Maintainers | 7 days | All Core Maintainers |
| **Strategic** (roadmap changes, new module addition, new Core Maintainer nomination) | RFC process | 14 days minimum | Full community + Core Maintainer vote |
| **Governance** (changes to this document) | RFC process + Core Maintainer vote | 21 days minimum | Full community + 2/3 Core Maintainer vote |

### 6.3 Lazy Consensus

- For normal decisions, a PR is opened with a 7-day review period
- If no objections are raised within 7 days (with at least 1 approval), the decision is considered approved
- Any Core Maintainer may extend the review period by up to 7 additional days by posting a reasoned objection
- Explicit objections must include rationale; "veto" objections without justification are not accepted

### 6.4 Voting

- Voting is used for contentious decisions, new Core Maintainer nominations, and governance changes
- Each Core Maintainer has 1 vote; the Lead Maintainer has 2 votes (but abstains except in tie-breaking or strategic votes)
- Abstentions are counted as not voting (they do not count as "no" or "yes")
- Default passage threshold: simple majority (>50%) of votes cast
- Governance changes: 2/3 supermajority of all Core Maintainers
- Lead Maintainer removal: 3/4 supermajority of all Core Maintainers
- Votes are conducted via GitHub issue with a comment thread; anonymous voting is not used

### 6.5 RFC Process

- Significant changes start with a **Request for Comments** (RFC) document
- RFC template is available at `docs/rfc/TEMPLATE.md`
- An RFC is submitted as a PR to the `docs/rfc/` directory
- The RFC is open for community comment for a minimum of 14 days
- After the comment period, Core Maintainers vote on the RFC
- Approved RFCs are merged; rejected RFCs are closed with a summary of the decision rationale
- RFCs that require implementation tracking include link(s) to the implementation issue(s)

### 6.6 Escalation

- If a decision is deadlocked (tied vote or 7 days without resolution), it escalates to the Lead Maintainer
- The Lead Maintainer may break the tie, request additional discussion, or defer the decision to a future release
- If the Lead Maintainer is the source of the deadlock (e.g., a vote involving the Lead Maintainer), escalation goes to a 2/3 vote of the remaining Core Maintainers

---

## 7. Communication Channels

### 7.1 Current Channels

| Channel | Purpose | Moderation |
|---------|---------|-----------|
| **GitHub Issues** | Bug reports, feature requests, task tracking | Core Maintainers triage within 7 days |
| **GitHub Discussions** | Q&A, ideas, community support, RFC feedback | Community-managed with Core Maintainer oversight |
| **CHANGELOG.md** | Release notes and version history | Release Manager updates per release |
| **CONTRIBUTING.md** | Contribution guidelines | Lead Maintainer reviews |

### 7.2 Future Channels (Roadmap)

| Channel | Target | Purpose |
|---------|--------|---------|
| **Discord / Slack** | Post-v1.0.0 stable release | Real-time collaboration, quick Q&A, community bonding |
| **Monthly Community Calls** | After reaching 100+ GitHub stars | Public roadmap review, demo sessions, maintainer Q&A |
| **Mailing List / Newsletter** | Post-v1.0.0 stable release | Release announcements, security advisories, community highlights |
| **Official Documentation Site** | Post-v1.0.0 stable release | Full documentation with tutorials, API reference, migration guides |

### 7.3 Communication Norms

- **Be respectful**: All communication must follow the Code of Conduct
- **Public-by-default**: Prefer public channels (issues, discussions) over private messages. If you have a question, someone else likely has the same one
- **Search first**: Before filing a new issue or discussion, search existing conversations to avoid duplicates
- **One topic per thread**: Keep issues and discussions focused on a single topic for clarity and searchability
- **Responsiveness**: Core Maintainers strive to acknowledge issues within 7 days, even if a fix cannot be offered immediately

### 7.4 Editorial Control

- The `CHANGELOG.md`, `GOVERNANCE.md`, and `CONTRIBUTING.md` require PR approval from the Lead Maintainer
- All other documentation can be updated by any Core Maintainer
- GitHub Discussions and issue labels are managed by Core Maintainers
- Release announcements and social media posts are managed by the Release Manager
