# VerifyIQ Community Guide

> Everything you need to contribute to, report issues on, and participate in the VerifyIQ project.

---

## Table of Contents

1. [Issue Templates](#1-issue-templates)
   - [Bug Report Template](#bug_reportmd)
   - [Feature Request Template](#feature_requestmd)
   - [config.yml](#configyml)
2. [Pull Request Template](#2-pull-request-template)
3. [Code of Conduct](#3-code-of-conduct)
4. [Security Policy](#4-security-policy)
5. [Maintenance Checklist](#5-maintenance-checklist)

---

## 1. Issue Templates

### Purpose

Issue templates guide users and contributors to report bugs, suggest features, or ask questions in a structured, consistent way. Well-formed issues save maintainers time, reduce back-and-forth, and make it easier to triage and prioritize work.

### Recommended Content

#### `BUG_REPORT.md`

```markdown
---
name: Bug Report
about: Report a reproducible bug or unexpected behavior
title: "[BUG] "
labels: bug
assignees: ''
---

## Summary
A clear, concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Run command '...'
3. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened (include full error output if applicable).

## Environment
- OS: [e.g. Ubuntu 22.04, macOS 14, Windows 11]
- Python version: [e.g. 3.10, 3.11, 3.12]
- VerifyIQ version: [e.g. 0.1.0, commit hash, or branch]
- Installation method: [pip install, source, Docker]

## Logs / Screenshots
If applicable, paste logs or attach screenshots. For long logs, use a gist or pastebin link.

## Possible Fix
Optional: suggest what might be causing the issue or how to fix it.

## Additional Context
Any other relevant context (pipeline stage, model used, dataset size, etc.).
```

#### `FEATURE_REQUEST.md`

```markdown
---
name: Feature Request
about: Propose a new feature or enhancement
title: "[FEATURE] "
labels: enhancement
assignees: ''
---

## Problem Statement
What problem does this feature solve? Who is the target user?

## Proposed Solution
Describe the feature in detail. How should it work from a user's perspective?

## Alternatives Considered
What other approaches have you considered and why are they insufficient?

## Implementation Ideas
Optional: high-level technical suggestions, relevant modules, or references to existing code.

## Impact Assessment
- **New dependencies:** Are any new libraries or tools required?
- **API changes:** Does this break or extend existing public APIs?
- **Performance:** Any expected impact on inference speed or memory?
- **Test coverage:** How can this be tested?

## Additional Context
Links to related issues, discussions, or external references.
```

#### `config.yml`

```yaml
blank_issues_enabled: false
contact_links:
  - name: VerifyIQ Discussions
    url: https://github.com/verifyiq/verifyiq/discussions
    about: Please ask and answer questions in GitHub Discussions before opening an issue.
  - name: VerifyIQ Documentation
    url: https://verifyiq.readthedocs.io/
    about: Check the official documentation for guides, API reference, and examples.
```

### Maintenance Requirements

| Aspect | Practice |
|---|---|
| Updates | Review templates when the project adds/removes major features or changes the tech stack. |
| Labels | Keep the label set in GitHub Issues aligned with the template `labels` field. |
| Testing | File a test issue on a fork every release cycle to verify templates render correctly. |
| Feedback | Watch for "template didn't fit my issue" comments and adjust accordingly. |

Location: Place `BUG_REPORT.md` and `FEATURE_REQUEST.md` under `.github/ISSUE_TEMPLATE/`. Place `config.yml` in the same directory to enforce template-only issue creation.

---

## 2. Pull Request Template

### Purpose

A pull request template ensures every contributor provides enough context for maintainers to review changes efficiently. It reduces the cognitive load of reviewing and helps catch missing tests, documentation, or formatting before CI runs.

### Recommended Content

#### `PULL_REQUEST_TEMPLATE.md`

```markdown
---
name: Pull Request
about: Submit changes to the VerifyIQ codebase
title: ""
labels: ""
assignees: ""
---

## Description
Please include a summary of the changes and the motivation behind them.

## Related Issues
Closes #(issue-number) | Related to #(issue-number)

## Type of Change
- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 📖 Documentation update
- [ ] ♻️ Refactor (no functional change)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test addition / improvement

## Testing Done
Describe the tests you ran and their outcomes.
- [ ] All existing tests pass (`pytest`)
- [ ] New tests cover the change
- [ ] Manual verification (describe steps)

## Checklist
- [ ] My code follows the project's style guidelines (`ruff` / `black`)
- [ ] I have added or updated docstrings for public APIs
- [ ] I have updated the documentation (README, docs/) if needed
- [ ] I have added type hints for new function signatures
- [ ] I have run `pytest` locally and all tests pass
- [ ] I have run `ruff check .` and `mypy .` with no new errors
- [ ] I have updated the changelog (if applicable)

## Screenshots
If the change affects CLI output or the dashboard UI, include before/after screenshots.

## Additional Notes
Any follow-up work or known limitations.
```

### Maintenance Requirements

| Aspect | Practice |
|---|---|
| Lint/type versions | Update checklist commands when the project changes linters or type checkers. |
| Test command | Update if the test runner or invocation changes (e.g., pytest → unittest, new flags). |
| Changelog location | Confirm the checklist links to the correct file path. |
| Branch protection | Ensure the PR template is the default for all PRs via GitHub repo settings. |

Location: `.github/PULL_REQUEST_TEMPLATE/pull_request_template.md` or `.github/PULL_REQUEST_TEMPLATE.md`.

---

## 3. Code of Conduct

### Purpose

A Code of Conduct sets the social rules of the project. It signals that the community is welcoming, inclusive, and professional. The Contributor Covenant is the most widely adopted standard across open-source projects (used by Kubernetes, VS Code, Rails, and thousands more).

### Recommended Content

#### `CODE_OF_CONDUCT.md`

```markdown
# Contributor Covenant Code of Conduct v2.1

## Our Pledge

We as members, contributors, and leaders pledge to make participation in the
VerifyIQ community a harassment-free experience for everyone, regardless of
age, body size, visible or invisible disability, ethnicity, sex characteristics,
gender identity and expression, level of experience, education, socioeconomic
status, nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment:

- Demonstrating empathy and kindness toward other people
- Being respectful of differing opinions, viewpoints, and experiences
- Giving and gracefully accepting constructive feedback
- Accepting responsibility and apologizing to those affected by our mistakes
- Focusing on what is best not just for us as individuals but for the overall community

Examples of unacceptable behavior:

- The use of sexualized language or imagery, and sexual attention or advances
- Trolling, insulting or derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

## Enforcement Responsibilities

Project maintainers are responsible for clarifying and enforcing our standards
and will take appropriate and fair corrective action in response to any
behavior that they deem inappropriate, threatening, offensive, or harmful.

Maintainers have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for
moderation decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies
when an individual is officially representing the community in public spaces.
Examples include using an official email address, posting via an official
social media account, or acting as an appointed representative at an event.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the project team at **conduct@verifyiq.dev**. All complaints will
be reviewed and investigated promptly and fairly.

All project maintainers are obligated to respect the privacy and security of
the reporter of any incident.

### Enforcement Guidelines

Project maintainers will follow these Community Impact Guidelines in determining
consequences for any action they deem in violation of this Code of Conduct:

**1. Correction**
- *Community Impact:* Use of inappropriate language or other behavior deemed unprofessional.
- *Consequence:* A private, written warning with clarity about why the behavior was inappropriate. A public apology may be requested.

**2. Warning**
- *Community Impact:* A violation through a single incident or series of actions.
- *Consequence:* A warning with consequences for continued behavior. No interaction with the people involved for a specified period, including unsolicited interaction with enforcement authorities. Violating these terms may lead to a temporary or permanent ban.

**3. Temporary Ban**
- *Community Impact:* A serious violation of community standards.
- *Consequence:* A temporary ban from any interaction or public communication with the community for a specified period. No public or private interaction with the people involved is permitted during this period.

**4. Permanent Ban**
- *Community Impact:* Demonstrating a pattern of violation, harassment, or aggression.
- *Consequence:* A permanent ban from any public interaction within the community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.1, available at
https://www.contributor-covenant.org/version/2/1/code_of_conduct.html.

Community Impact Guidelines were inspired by
[Mozilla's enforcement ladder](https://github.com/mozilla/diversity).

[homepage]: https://www.contributor-covenant.org

For answers to common questions about this Code of Conduct, see the FAQ at
https://www.contributor-covenant.org/faq. Translations are available at
https://www.contributor-covenant.org/translations.
```

### Maintenance Requirements

| Aspect | Practice |
|---|---|
| Contact info | Ensure the enforcement email (`conduct@verifyiq.dev`) is monitored by at least 2 maintainers. |
| Version | Check annually for Contributor Covenant updates (v2.1+). |
| Legal review | Have a lawyer or legal team review if the project is under a foundation. |

Location: `CODE_OF_CONDUCT.md` (repository root — GitHub auto-detects it).

---

## 4. Security Policy

### Purpose

A security policy tells researchers and users how to responsibly disclose vulnerabilities. Without one, reports may be filed publicly (risking exploitation before a fix is available) or not filed at all.

### Recommended Content

#### `SECURITY.md`

```markdown
# Security Policy

## Supported Versions

VerifyIQ follows semantic versioning. Security patches are provided for:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| 0.x     | :white_check_mark: (critical only) |
| < 0.1   | :x:                |

Older versions receive no security updates. We recommend always using the latest release.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, send an email to **security@verifyiq.dev** with the following details:

- Description of the vulnerability
- Steps to reproduce (PoC strongly preferred)
- Affected versions and components
- Any proposed fix or mitigation (optional)

You can optionally encrypt your report using our GPG key (fingerprint available on the project website).

### Response Timeline

| Timeframe | Action |
|-----------|--------|
| 24 hours  | Acknowledgment of receipt |
| 7 days    | Initial assessment and severity classification |
| 30 days   | Patch released (or detailed reason for delay communicated) |
| 90 days    | Public disclosure after fix is deployed (coordinated) |

### Disclosure Policy

We follow **coordinated disclosure**:

1. Reporter submits vulnerability privately via email.
2. Maintainers triage, assess impact, and develop a fix.
3. A patch is released, and a CVE is assigned (if applicable).
4. The reporter is credited (if they wish) in the release notes.
5. The vulnerability is publicly disclosed after the fix is available.

We aim to acknowledge and respond to every report within 24 hours. If you do
not receive a response, please escalate to the project lead at **lead@verifyiq.dev**.
```

### Maintenance Requirements

| Aspect | Practice |
|---|---|
| Email rotation | Update the security contact email when maintainers change. |
| GPG key | Rotate annually and publish the current fingerprint. |
| Version table | Update when branching or deprecating release lines. |
| Response SLA | Review quarterly to ensure staffing is adequate for the 24h SLA. |

Location: `SECURITY.md` (repository root — GitHub surfaces it under the "Security" tab automatically).

---

## 5. Maintenance Checklist

### Regular Cadence

| Frequency | Task | Owner |
|---|---|---|
| Every release | Verify all templates render correctly on a test repo | Release manager |
| Quarterly | Review template fields for relevance (remove stale fields, add new ones) | Project lead |
| Quarterly | Check security@ and conduct@ inboxes for missed messages | Project lead |
| Annually | Re-read Contributor Covenant for updates; update CODE_OF_CONDUCT if needed | Project lead |
| Annually | Rotate GPG key for security reports | Infrastructure lead |
| Ad-hoc | After community feedback (e.g., "this template confused me"), update within one week | Any maintainer |

### Feedback Collection

- Add a "Was this template helpful?" question at the bottom of each template (comment it out so the submittor sees it but it is stripped on submission, or use a closing question in the description).
- Review GitHub issue/PR comments quarterly for complaints about template structure.
- Survey active contributors annually (via GitHub Discussion poll) on contribution experience.

### Who Is Responsible

| Role | Community file responsibilities |
|---|---|
| **Project Lead** | Owns CODE_OF_CONDUCT.md, SECURITY.md; final decision on template changes |
| **Maintainer Team** | Owns ISSUE_TEMPLATE/, PULL_REQUEST_TEMPLATE.md; reviews quarterly |
| **Community Manager** (if one exists) | Monitors conduct reports, template feedback, and contributor surveys |

---

*Maintainers: Update this guide when the project structure, tooling, or governance changes.*
