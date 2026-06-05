# Stale GitHub Discussions Pin Examples

Use this page when GitHub Discussions pins, starter topics, category links, or launch-feedback discussion links may no longer reflect the current repository. Read it with `docs/github_discussions_launch_checklist.md`, `docs/discussion_to_issue_conversion_examples.md`, `docs/launch_feedback_collection_examples.md`, and `docs/post_publish_warning_examples.md`.

The core rule: GitHub Discussions setup, pinned topics, issue scope, launch feedback, private feedback, and roadmap acceptance prove different things. Do not claim Discussions are current until visible public evidence confirms the pins.

## Expected Evidence Split

Local source proof:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py launch-assets
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Public repository proof after push:

```bash
python -B scripts/dev.py github-readiness
python -B scripts/post_publish_check.py
```

Local docs can define intended categories, starter topics, routing, and moderation boundaries. They do not prove that the public Discussions page is enabled, pinned, unpinned, or refreshed.

Review global pins, category pins, starter topics, wrong-category links, and old launch-feedback discussion references as separate public evidence surfaces.

## Stale Global Pins

Use this when a globally pinned discussion still points to old launch wording, old screenshots, outdated commands, or an older release state.

Symptom:

- The global pin is visible from the Discussions landing page.
- The pin links old README wording, old launch copy, or old release evidence.
- Local docs or the current branch have moved on.

Wrong fix:

- Claim Discussions are current because the repository docs were updated locally.
- Leave the old pin visible as launch evidence.
- Edit README claims to match the stale pin.

Safe fix:

```bash
git status --short --branch
python -B scripts/dev.py launch-assets
python -B scripts/dev.py community-issues
```

After the push is visible, review the public Discussions page and update or unpin the stale global topic. Keep the pin claim manual until the visible public pin points to the current source docs.

## Stale Category Pins

Use this when a category-specific pin is current in one category but stale, misleading, or missing in another.

Symptom:

- Q&A, Ideas, Announcements, or General has a pinned topic from an older launch pass.
- The pinned topic routes users to an old issue template, release note, or support expectation.
- The category description and pinned topic disagree.

Wrong fix:

- Treat a correct global pin as proof that category pins are correct.
- Delete category boundaries from source docs to match stale public state.
- Promise response times or feature acceptance to reduce confusion.

Safe fix:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py safety
```

Compare each category against `docs/github_discussions_launch_checklist.md`. Update the public pin, remove the stale pin, or redirect users to the right channel without changing issue scope or support expectations.

## Outdated Starter Topics

Use this when the starter discussion text references an old quickstart, old command output, deprecated screenshots, or old roadmap language.

Symptom:

- Starter topics still ask users to run an old command.
- The topic links docs that no longer exist or have moved.
- The topic invites broad feature requests as if they are accepted roadmap items.

Wrong fix:

- Convert broad replies into issues just to keep activity visible.
- Ask users to paste private account screenshots, local paths, or full terminal history.
- Treat old setup replies as current docs evidence.

Safe fix:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py launch-assets
python -B scripts/dev.py quality
```

Refresh starter topics so they link current README sections, current troubleshooting docs, and `docs/discussion_to_issue_conversion_examples.md`. Keep setup Q&A, public issue scope, and private feedback separate.

## Wrong-Category Links

Use this when README, launch posts, issue replies, or public maintainer updates point users to the wrong discussion category.

Symptom:

- A setup question link opens Ideas instead of Q&A.
- A roadmap proposal is linked from Announcements as if it is accepted scope.
- A private feedback summary points to a public discussion that cannot safely contain the details.

Wrong fix:

- Move private details into the public thread.
- Open a broad issue to hide the category mismatch.
- Treat wrong-category traffic as evidence that the category is useful.

Safe fix:

```bash
python -B scripts/dev.py community-issues
python -B scripts/dev.py safety
python -B scripts/dev.py quality
```

Route setup questions to Q&A, proposals to Ideas, release notes to Announcements, and concrete bugs to issues only after the evidence is public and reproducible.

## Old Launch-Feedback Discussion References

Use this when a launch-feedback discussion was useful earlier but no longer proves current repository state.

Symptom:

- A launch note cites an old discussion as current feedback.
- A discussion references old stars, old screenshots, or old command output.
- The issue, PR, or doc that addressed the feedback has already changed.

Wrong fix:

- Quote the old discussion as a current endorsement.
- Count discussion volume as star-growth success, production proof, or roadmap acceptance.
- Copy private replies, account details, or screenshots into source docs.

Safe fix:

```bash
python -B scripts/dev.py launch-assets
python -B scripts/dev.py community-issues
python -B scripts/dev.py safety
```

Use `docs/launch_feedback_collection_examples.md` for current feedback handling. Use `docs/post_publish_warning_examples.md` when local and remote evidence disagree. Link the current issue, PR, or doc only when the follow-up is concrete and public.

## Review Checklist

- `docs/github_discussions_launch_checklist.md` remains the source for intended categories, starter topics, moderation, and channel routing.
- `docs/discussion_to_issue_conversion_examples.md` remains the source before a discussion becomes issue scope.
- `docs/launch_feedback_collection_examples.md` remains the source before discussion feedback becomes launch evidence.
- `docs/post_publish_warning_examples.md` remains the source when local docs and remote public evidence disagree.
- GitHub Discussions setup, pinned topics, issue scope, launch feedback, private feedback, and roadmap acceptance stay separate.
- Global pins, category pins, starter topics, wrong-category links, and old launch-feedback discussion references are reviewed against visible public evidence.
- Private messages, account analytics, personal account details, secrets, customer data, private screenshots, and local machine details are not committed.
- Do not claim Discussions are current until visible public evidence confirms the pins.
- `python -B scripts/dev.py community-issues`, `python -B scripts/dev.py launch-assets`, `python -B scripts/dev.py safety`, and `python -B scripts/dev.py quality` pass after changing Discussions pin wording.
