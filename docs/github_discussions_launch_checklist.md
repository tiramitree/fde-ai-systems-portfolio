# GitHub Discussions Launch Checklist

Use this page before enabling or announcing GitHub Discussions for the repository. Read it with `docs/community_backlog.md`, `docs/github_initial_issues.md`, `docs/launch_feedback_collection_examples.md`, `docs/issue_triage_sla_wording_examples.md`, `docs/discussion_to_issue_conversion_examples.md`, `docs/maintainer_review_policy.md`, and `docs/post_publish_checklist.md`.

The core rule: GitHub Discussions, issues, PRs, private feedback, and roadmap acceptance are different channels. Do not promise support SLAs, private account access, or guaranteed feature acceptance from a discussion thread.

## Evidence Boundaries

Local launch proof:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Remote repository proof after push:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

GitHub Discussions is an account-level repository feature. Local docs can define the launch plan, categories, moderation rules, and evidence boundaries, but they do not prove Discussions is enabled on GitHub.

## Suggested Categories

Use a small category set at launch:

| Category | Format | Purpose | Boundary |
| --- | --- | --- | --- |
| Announcements | Announcement | Maintainer updates, releases, and launch notes. | Not a support queue or roadmap commitment. |
| Q&A | Question and answer | Setup questions, command confusion, and docs clarification. | Answers are best-effort and do not replace issue triage. |
| Ideas | Open-ended discussion | Early proposals before they become scoped issues. | Ideas are not accepted roadmap work until triaged. |
| Show and tell | Open-ended discussion | Demos, adaptations, and implementation notes from users. | No private customer data, secrets, or proprietary screenshots. |
| General | Open-ended discussion | Broad feedback that does not fit the other categories. | Move concrete bugs or planned work to issues. |

Keep category descriptions explicit enough that users know whether to open a discussion, issue, or PR. Avoid creating many categories before there is real community traffic.

## Pinned Starter Topics

Create one or two starter discussions only after Discussions is intentionally enabled:

1. Announcement: "Welcome and project scope"
   - Link `README.md`, `docs/community_backlog.md`, and `docs/post_publish_checklist.md`.
   - State that Issues are for scoped work and Discussions are for questions, ideas, and feedback.
   - Avoid support-time promises, private account access, and roadmap guarantees.

2. Q&A: "Setup and local demo questions"
   - Link the quick start, command output expectations, and troubleshooting map.
   - Ask users to redact paths, usernames, tokens, private data, and customer details.
   - Move confirmed bugs to issues only after the problem is concrete and reproducible.

3. Ideas: "Future extensions"
   - Link `docs/community_backlog.md`.
   - Invite feature proposals without treating every idea as accepted scope.
   - Convert only narrow, safe, reviewable ideas into public issues.

GitHub supports pinned discussions, including global pins and category-specific pins. Keep pinned topics sparse so they guide the first visit instead of becoming stale navigation.

## Moderation Rules

Follow `docs/maintainer_review_policy.md` for unsafe or low-signal activity.

Close, lock, hide, or redirect discussion content when it:

- asks for secrets, tokens, account credentials, private files, local machine details, or personal data
- includes unrelated links, downloads, binaries, obfuscated snippets, or instructions to run unknown commands
- requests collaborator access, private account access, or paid-service access
- asks to weaken permission checks, approval gates, traces, audit logs, evals, workflow security, or PR review
- copies private messages, analytics screenshots, customer data, or proprietary screenshots into public threads
- repeatedly treats ideas as accepted roadmap work after maintainers narrow or decline scope

Use Q&A answer marking only for factual setup answers. Do not mark speculative roadmap opinions, support promises, or private-account guidance as accepted answers.

## Channel Routing

Use this routing table when replying:

| Incoming Content | Best Channel | Maintainer Response |
| --- | --- | --- |
| Reproducible bug with affected command or file | Issue | Ask for a minimal public repro and link the issue template. |
| Narrow implementation already tied to an issue | PR | Point to `docs/issue_to_pr_handoff_flow.md`. |
| Broad feature idea | Discussion first | Keep it in Ideas until scope, risk, and verification are clear. |
| Setup question | Q&A discussion | Answer with docs links and mark a factual answer when appropriate. |
| Private feedback or private analytics | Outside git | Summarize only the technical issue in neutral public wording. |
| Security concern | SECURITY.md path | Do not ask for exploit details in a public thread. |

## Launch Feedback Boundary

Discussions can provide launch feedback, but they do not prove adoption, production readiness, runtime correctness, star-growth success, or GitHub account setup.

Useful evidence:

- public discussion URL
- category name
- short maintainer summary of the technical point
- linked issue or PR only when concrete follow-up work exists

Wrong use:

- copying private account details or screenshots into source docs
- counting discussion volume as quality evidence
- claiming roadmap acceptance from an untriaged idea
- promising response times, support SLAs, or private help

Review with `docs/launch_feedback_collection_examples.md` before turning discussion feedback into public launch claims.

Use `docs/issue_triage_sla_wording_examples.md` before converting discussion replies into public issue response expectations.

Use `docs/discussion_to_issue_conversion_examples.md` before turning a discussion into a scoped issue.

## Review Checklist

- Discussions are enabled only when the repository is intentionally ready for public conversation.
- Categories separate announcements, Q&A, ideas, show-and-tell, and general feedback.
- Pinned starter topics link source docs and avoid support SLAs, private account access, and roadmap guarantees.
- Moderation rules follow `docs/maintainer_review_policy.md`.
- Issues, PRs, Discussions, private feedback, and roadmap acceptance stay separate.
- Discussion volume, untriaged ideas, private feedback, and accepted issue scope stay separate.
- No private messages, account analytics, personal account details, secrets, customer data, or private screenshots are committed.
- `python -B scripts/dev.py community-issues`, `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing Discussions launch wording.
