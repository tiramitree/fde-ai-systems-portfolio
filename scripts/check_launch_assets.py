from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "PROJECT_CONTENT_INDEX.md",
    "docs/launch_assets_hygiene.md",
    "docs/github_launch_plan.md",
    "docs/star_growth_plan.md",
    "docs/launch_copy_pack.md",
    "docs/launch_feedback_collection_examples.md",
    "docs/community_backlog.md",
    "docs/github_initial_issues.md",
    "docs/public_roadmap_issue_comment_examples.md",
    "docs/release_asset_upload_dry_run_examples.md",
    "docs/github_labels.json",
    "docs/demo_video_script.md",
    "docs/demo_recording_checklist.md",
    "docs/reviewer_perspective_checklist.md",
    "docs/differentiation_strategy.md",
    "docs/published_repository_status.md",
    "docs/post_publish_checklist.md",
    "docs/post_publish_warning_examples.md",
    "docs/dependabot_secret_scanning_verification_examples.md",
    "docs/github_authenticated_maintenance_troubleshooting_examples.md",
    "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
    "docs/github_api_rate_limit_troubleshooting_examples.md",
    "docs/github_repository_metadata_troubleshooting_examples.md",
    "docs/social_preview_verification_examples.md",
    "docs/profile_pin_verification_examples.md",
    "docs/github_actions_warning_examples.md",
    "docs/github_actions_badge_verification_examples.md",
    "docs/github_label_troubleshooting_examples.md",
    "docs/github_release_page_troubleshooting_examples.md",
    "docs/github_latest_release_troubleshooting_examples.md",
    "docs/release_attachment_verification_examples.md",
    "docs/github_release_attachment_screenshot_checklist.md",
    "docs/github_repository_settings.md",
    "docs/github_repository_settings_screenshot_checklist.md",
    "docs/final_readiness_report.md",
    "docs/portfolio_evidence_matrix.md",
]

REQUIRED_SECTIONS = {
    "docs/launch_copy_pack.md": [
        "# Launch Copy Pack",
        "## One-Line Pitch",
        "## Short Post",
        "## LinkedIn Post",
        "## X / Twitter Thread",
        "## Hacker News Show HN",
        "## Reddit / Community Post",
        "## Follow-Up Blog Outline",
    ],
    "docs/star_growth_plan.md": [
        "# Star Growth Plan",
        "## Audience",
        "## Core Message",
        "## Launch Channels",
        "## Content Pieces",
        "## First Issue Labels",
        "## Anti-Hype Rule",
    ],
    "docs/community_backlog.md": [
        "## Good First Issues",
        "## Intermediate Issues",
        "## Advanced Issues",
        "## Guardrails",
    ],
    "docs/github_initial_issues.md": [
        "# GitHub Community Issue Pack",
        "## Wave 1 Completed Issues",
        "## Issue 1",
        "## Issue 2",
        "## Issue 3",
        "## Issue 4",
        "## Issue 5",
    ],
    "docs/launch_assets_hygiene.md": [
        "# Launch Assets Hygiene",
        "## What It Checks",
        "## Anti-Hype Boundary",
        "## When To Run",
    ],
}

REQUIRED_PHRASES = {
    "docs/launch_copy_pack.md": [
        "without paid APIs",
        "Optional OpenAI Responses API integration points",
        "the model is not the security boundary",
        "docs/launch_feedback_collection_examples.md",
        "Repo: <repo-url>",
    ],
    "docs/star_growth_plan.md": [
        "GitHub profile pin",
        "LinkedIn technical post",
        "X / Twitter thread",
        "Hacker News Show HN",
        "Reddit communities",
        "Do not claim production readiness",
        "Claim practical reference value",
        "docs/launch_copy_pack.md",
        "docs/launch_feedback_collection_examples.md",
        "python -B scripts/dev.py launch-assets",
    ],
    "docs/community_backlog.md": [
        "Project 1 must not expose inaccessible evidence to the model",
        "Project 2 must not execute side-effect tools without application-level authorization",
        "Project 3 must block unsafe release rollout when high-risk incidents are linked to failed evals",
        "Eval gates must keep unsafe leak, unsafe direct side-effect, and unsafe release approval failures at zero",
    ],
    "docs/github_initial_issues.md": [
        "Do not create placeholder issues only for activity metrics",
        "Acceptance criteria",
        "python -B scripts/dev.py verify still passes",
    ],
    "README.md": [
        "python -B scripts/dev.py launch-assets",
        "Launch asset hygiene",
        "docs/launch_assets_hygiene.md",
        "docs/star_growth_plan.md",
        "docs/launch_copy_pack.md",
        "docs/launch_feedback_collection_examples.md",
        "docs/public_roadmap_issue_comment_examples.md",
        "docs/release_asset_upload_dry_run_examples.md",
        "docs/dependabot_secret_scanning_verification_examples.md",
        "docs/release_attachment_verification_examples.md",
        "docs/github_authenticated_maintenance_troubleshooting_examples.md",
        "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/github_release_page_troubleshooting_examples.md",
        "docs/github_latest_release_troubleshooting_examples.md",
        "docs/github_release_attachment_screenshot_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_api_rate_limit_troubleshooting_examples.md",
        "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/github_repository_settings_screenshot_checklist.md",
        "docs/launch_feedback_collection_examples.md",
        "docs/social_preview_verification_examples.md",
        "docs/profile_pin_verification_examples.md",
        "docs/github_actions_warning_examples.md",
        "docs/github_actions_badge_verification_examples.md",
        "docs/github_label_troubleshooting_examples.md",
    ],
    "PROJECT_CONTENT_INDEX.md": [
        "launch-assets",
        "scripts/check_launch_assets.py",
        "docs/launch_assets_hygiene.md",
        "docs/launch_feedback_collection_examples.md",
        "docs/public_roadmap_issue_comment_examples.md",
        "docs/release_asset_upload_dry_run_examples.md",
        "docs/dependabot_secret_scanning_verification_examples.md",
        "docs/release_attachment_verification_examples.md",
        "docs/github_authenticated_maintenance_troubleshooting_examples.md",
        "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/github_release_page_troubleshooting_examples.md",
        "docs/github_latest_release_troubleshooting_examples.md",
        "docs/github_release_attachment_screenshot_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_api_rate_limit_troubleshooting_examples.md",
        "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/github_repository_settings_screenshot_checklist.md",
        "docs/public_roadmap_issue_comment_examples.md",
        "docs/release_asset_upload_dry_run_examples.md",
        "docs/dependabot_secret_scanning_verification_examples.md",
        "docs/social_preview_verification_examples.md",
        "docs/profile_pin_verification_examples.md",
        "docs/github_actions_warning_examples.md",
        "docs/github_actions_badge_verification_examples.md",
        "docs/github_label_troubleshooting_examples.md",
    ],
    "docs/portfolio_evidence_matrix.md": [
        "Launch materials are complete without overclaiming",
        "python -B scripts/dev.py launch-assets",
    ],
    "docs/supply_chain_security.md": [
        "docs/dependabot_secret_scanning_verification_examples.md",
        "Dependabot alerts, Dependabot security updates, secret scanning, or push protection",
        "python -B scripts/dev.py dependency-surface",
    ],
    "docs/github_repository_settings.md": [
        "docs/dependabot_secret_scanning_verification_examples.md",
        "Dependabot alerts",
        "Dependabot security updates",
        "secret scanning and push protection",
    ],
    "docs/published_repository_status.md": [
        "Launch asset hygiene: passed",
        "launch copy and star-growth materials",
        "docs/dependabot_secret_scanning_verification_examples.md",
        "Collect launch feedback and star-growth evidence using `docs/launch_feedback_collection_examples.md`",
    ],
    "docs/post_publish_checklist.md": [
        "the launch asset hygiene script and documentation are published",
        "the authenticated GitHub maintenance troubleshooting examples are published",
        "the GitHub public PR API fallback troubleshooting examples are published",
        "the GitHub repository settings screenshot checklist is published",
        "the public roadmap issue comment examples are published",
        "the Dependabot and secret-scanning verification examples are published",
        "GitHub API rate-limit troubleshooting examples are published",
        "the GitHub repository metadata troubleshooting examples are published",
        "the release attachment verification examples are published",
        "the release asset upload dry-run examples are published",
        "the GitHub release attachment screenshot checklist is published",
        "the GitHub release page troubleshooting examples are published",
        "the GitHub latest release troubleshooting examples are published",
        "the social preview verification examples are published",
        "the profile pin verification examples are published",
        "the post-publish warning examples are published",
        "the GitHub Actions badge verification examples are published",
        "the launch feedback collection examples are published",
        "python -B scripts/dev.py launch-assets",
    ],
    "docs/final_readiness_report.md": [
        "python -B scripts/dev.py launch-assets",
        "Do not claim full launch completion",
        "Star growth: cannot be claimed as achieved",
    ],
    "docs/release_attachment_verification_examples.md": [
        "# Release Attachment Verification Examples",
        "docs/github_release_commands.md",
        "docs/release_asset_upload_dry_run_examples.md",
        "docs/github_release_attachment_screenshot_checklist.md",
        "docs/post_publish_checklist.md",
        "docs/command_output_troubleshooting_map.md",
        "docs/demo_replay_artifact.md",
        "Missing Replay Artifacts",
        "Stale Attachments",
        "Wrong Release Tag",
        "Generated out/ Handling",
        "Post-Publish Mismatch",
        "python -B scripts/dev.py replay-artifact",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/post_publish_check.py",
        "out/demo_replay_artifact.md",
        "out/demo_replay_artifact.json",
        "Do not commit",
    ],
    "docs/release_asset_upload_dry_run_examples.md": [
        "# Release Asset Upload Dry-Run Examples",
        "docs/release_attachment_verification_examples.md",
        "docs/github_release_commands.md",
        "docs/github_release_page_troubleshooting_examples.md",
        "docs/github_release_attachment_screenshot_checklist.md",
        "docs/post_publish_checklist.md",
        "Expected Evidence Split",
        "Missing Replay Artifacts",
        "Stale Local Artifacts",
        "Wrong Release Tag",
        "GitHub Release Page Not Found",
        "Generated out/ Handling",
        "Review Checklist",
        "dry-run plans, generated replay artifacts, source-controlled docs, and published GitHub release state prove different things",
        "Do not claim release assets were uploaded until public release evidence confirms it",
        "python -B scripts/dev.py replay-artifact",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/post_publish_check.py",
        "gh release upload v0.1.0 out/demo_replay_artifact.md out/demo_replay_artifact.json",
    ],
    "docs/github_release_attachment_screenshot_checklist.md": [
        "# GitHub Release Attachment Screenshot Checklist",
        "docs/release_attachment_verification_examples.md",
        "docs/release_asset_upload_dry_run_examples.md",
        "docs/github_release_page_troubleshooting_examples.md",
        "docs/github_latest_release_troubleshooting_examples.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Replay Artifact Attachment Screenshots",
        "Missing Attachment Screenshots",
        "Stale Attachment Screenshots",
        "Wrong Tag Screenshots",
        "Latest-Release Attachment Screenshots",
        "Screenshot Handling Rules",
        "Review Checklist",
        "upload-plan and generated-`out/` boundaries",
        "python -B scripts/dev.py replay-artifact",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py github-readiness",
        "generated local artifacts, release-page screenshots, and current public release evidence prove different things",
        "Do not commit private account screenshots, generated `out/` files, or release-attachment claims without matching public evidence",
    ],
    "docs/github_release_page_troubleshooting_examples.md": [
        "# GitHub Release Page Troubleshooting Examples",
        "docs/github_latest_release_troubleshooting_examples.md",
        "docs/github_release_commands.md",
        "docs/github_release_notes_v0.1.0.md",
        "docs/release_attachment_verification_examples.md",
        "docs/release_asset_upload_dry_run_examples.md",
        "docs/github_release_attachment_screenshot_checklist.md",
        "docs/post_publish_checklist.md",
        "Missing Release Page",
        "Wrong Tag",
        "Stale Release Notes",
        "Missing Replay Attachments",
        "Latest-Release Mismatch",
        "python -B scripts/dev.py replay-artifact",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/dev.py github-readiness",
        "local replay-artifact evidence and published release page evidence prove different things",
        "Do not claim the release page is current until the tag, release notes, and current replay attachments are visible on GitHub",
        "before treating an upload plan as applied release state",
        "Release attachment screenshots are compared with `docs/github_release_attachment_screenshot_checklist.md`",
    ],
    "docs/github_latest_release_troubleshooting_examples.md": [
        "# GitHub Latest Release Troubleshooting Examples",
        "docs/github_release_page_troubleshooting_examples.md",
        "docs/github_release_commands.md",
        "docs/release_attachment_verification_examples.md",
        "docs/github_release_attachment_screenshot_checklist.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing Latest Release",
        "Wrong Latest Tag",
        "Draft Or Prerelease Confusion",
        "Stale Release Page",
        "Attached Artifact Drift",
        "Review Checklist",
        "python -B scripts/dev.py replay-artifact",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/check_github_readiness.py --strict",
        "tag existence, release-page existence, and latest-release selection prove different things",
        "Do not claim the latest release is current until GitHub readiness or direct release-page evidence confirms it",
        "Latest-release attachment screenshots are compared with `docs/github_release_attachment_screenshot_checklist.md`",
    ],
    "docs/post_publish_warning_examples.md": [
        "# Post-Publish Warning Examples",
        "docs/post_publish_checklist.md",
        "docs/published_repository_status.md",
        "docs/github_release_commands.md",
        "docs/github_latest_release_troubleshooting_examples.md",
        "docs/github_release_attachment_screenshot_checklist.md",
        "docs/github_authenticated_maintenance_troubleshooting_examples.md",
        "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/github_api_rate_limit_troubleshooting_examples.md",
        "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/github_repository_settings_screenshot_checklist.md",
        "docs/social_preview_verification_examples.md",
        "docs/profile_pin_verification_examples.md",
        "docs/github_actions_badge_verification_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Remote File Lag",
        "Raw README Failures",
        "GitHub Actions Pending State",
        "Readiness Warning Rows",
        "Manual Account Settings",
        "README badge, Actions page, and current `github-readiness` output disagree",
        "Dependabot alerts, Dependabot security updates, secret scanning, push protection, or local safety-scan output",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py github-readiness",
        "local quality evidence and remote GitHub evidence prove different things",
        "Do not claim published evidence until the remote checks pass",
    ],
    "docs/launch_feedback_collection_examples.md": [
        "# Launch Feedback Collection Examples",
        "docs/launch_copy_pack.md",
        "docs/star_growth_plan.md",
        "docs/published_repository_status.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "GitHub Stars And Forks",
        "Issue Feedback",
        "Launch-Post Comments",
        "Private-Message Feedback",
        "Analytics Screenshots",
        "Review Checklist",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/post_publish_check.py",
        "public feedback, private messages, analytics screenshots, and source evidence prove different things",
        "Do not commit private DMs, account analytics, personal account details, or launch-feedback claims without matching evidence",
    ],
    "docs/github_authenticated_maintenance_troubleshooting_examples.md": [
        "# GitHub Authenticated Maintenance Troubleshooting Examples",
        "docs/github_repository_settings.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/pr_review_runbook.md",
        "docs/maintainer_review_policy.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing gh Auth",
        "Wrong Account Or Repository",
        "Dry-Run Versus Apply",
        "Branch Protection Or Release Side Effects",
        "PR Maintenance Safeguards",
        "Review Checklist",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/maintain_github_state.py --apply",
        "python -B scripts/dev.py pr-triage",
        "python -B scripts/dev.py pr-policy",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/review_open_prs.py --strict",
        "python -B scripts/maintain_github_state.py --apply --skip-release",
        "python -B scripts/maintain_github_state.py --apply --skip-launch --close-runtime-bump-prs",
        "dry-run planning, authenticated account permissions, repository metadata changes, and PR maintenance prove different things",
        "Do not claim remote maintenance applied until authenticated evidence confirms it",
    ],
    "docs/github_public_pr_api_fallback_troubleshooting_examples.md": [
        "# GitHub Public PR API Fallback Troubleshooting Examples",
        "docs/pr_review_runbook.md",
        "docs/pr_review_security.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_api_rate_limit_troubleshooting_examples.md",
        "docs/maintainer_review_policy.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Unauthenticated API Limits",
        "Public Pulls Page Fallback",
        "Missing File-Level Triage",
        "Strict-Mode Review",
        "Stale No-Open-PR State",
        "Review Checklist",
        "python -B scripts/dev.py pr-triage",
        "python -B scripts/review_open_prs.py --strict",
        "python -B scripts/dev.py pr-policy",
        "python -B scripts/dev.py governance",
        "python -B scripts/dev.py workflow-security",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/dev.py github-readiness",
        "public page visibility, API file-level triage, and strict review confidence prove different things",
        "Do not claim no risky PRs until API or authenticated evidence confirms it",
    ],
    "docs/github_api_rate_limit_troubleshooting_examples.md": [
        "# GitHub API Rate-Limit Troubleshooting Examples",
        "docs/published_repository_status.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
        "docs/github_actions_warning_examples.md",
        "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Unauthenticated Rate Limits",
        "Transient GitHub API Failures",
        "Pending Actions Lookups",
        "Stale Cached Status",
        "Strict-Mode Review",
        "Review Checklist",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py fresh-clone-local",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/check_github_readiness.py --strict",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "GitHub API availability and local project quality prove different things",
        "Do not claim remote readiness until the readiness command can verify the current repository state",
    ],
    "docs/github_repository_metadata_troubleshooting_examples.md": [
        "# GitHub Repository Metadata Troubleshooting Examples",
        "docs/github_repository_settings.md",
        "docs/published_repository_status.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing Description",
        "Missing Topics",
        "Wrong Repository URL",
        "Stale Public Status",
        "Unauthenticated Maintenance Output",
        "Review Checklist",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py fresh-clone",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "local launch docs and GitHub account-level repository metadata prove different things",
        "Do not claim metadata is current until GitHub readiness or authenticated maintenance confirms it",
    ],
    "docs/github_repository_settings_screenshot_checklist.md": [
        "# GitHub Repository Settings Screenshot Checklist",
        "docs/github_repository_settings.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_repository_metadata_troubleshooting_examples.md",
        "docs/branch_protection_verification_examples.md",
        "docs/github_release_page_troubleshooting_examples.md",
        "docs/github_release_attachment_screenshot_checklist.md",
        "docs/profile_pin_verification_examples.md",
        "docs/social_preview_verification_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Description And Topics Screenshots",
        "Branch Protection Screenshots",
        "Social Preview Screenshots",
        "Release Page Screenshots",
        "Profile Pin Screenshots",
        "Screenshot Handling Rules",
        "Review Checklist",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/post_publish_check.py",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/dev.py github-maintenance",
        "local docs, authenticated settings screenshots, and public repository evidence prove different things",
        "Do not commit private account screenshots or claim settings are current until public/account-level evidence confirms them",
    ],
    "docs/social_preview_verification_examples.md": [
        "# Social Preview Verification Examples",
        "docs/github_repository_settings.md",
        "docs/github_repository_settings_screenshot_checklist.md",
        "docs/assets/github-preview.png",
        "docs/profile_pin_verification_examples.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing Social Preview",
        "Stale Preview Image",
        "Wrong Uploaded Image",
        "Cache Delay",
        "Profile-Pin Confusion",
        "Review Checklist",
        "python -B scripts/dev.py assets",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "local image asset existence and GitHub account-level social preview setup prove different things",
        "Do not claim social preview setup until the GitHub UI or account-level evidence confirms it",
    ],
    "docs/profile_pin_verification_examples.md": [
        "# GitHub Profile Pin Verification Examples",
        "docs/github_repository_settings.md",
        "docs/github_repository_settings_screenshot_checklist.md",
        "docs/social_preview_verification_examples.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing Profile Pin",
        "Wrong Pinned Repository",
        "Stale Profile Cache",
        "Social-Preview Confusion",
        "Account Visibility",
        "Review Checklist",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/dev.py github-maintenance",
        "python -B scripts/dev.py launch-assets",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/post_publish_check.py",
        "repository readiness, social preview setup, and profile pin setup prove different things",
        "Do not claim the profile pin is configured until account-profile evidence confirms it",
    ],
    "docs/github_actions_warning_examples.md": [
        "# GitHub Actions Warning Examples",
        ".github/workflows/ci.yml",
        "docs/workflow_security.md",
        "docs/github_actions_badge_verification_examples.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_api_rate_limit_troubleshooting_examples.md",
        "Pending Quality Gate",
        "Missing Workflow Run",
        "Stale Badge",
        "Skipped Workflow",
        "Fork PR Permission Limits",
        "python -B scripts/dev.py workflow-security",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/check_github_readiness.py --strict",
        "local quality evidence and remote GitHub Actions evidence prove different things",
        "Do not claim a green workflow until the current remote `quality-gate` run passes",
        "README badge URL and link are reviewed with `docs/github_actions_badge_verification_examples.md`",
    ],
    "docs/github_actions_badge_verification_examples.md": [
        "# GitHub Actions Badge Verification Examples",
        ".github/workflows/ci.yml",
        "docs/github_actions_warning_examples.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/workflow_security.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing Badge",
        "Stale Badge",
        "Wrong Workflow Badge",
        "Skipped Workflow Badge",
        "Fork-PR Badge Confusion",
        "Review Checklist",
        "python -B scripts/dev.py workflow-security",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/dev.py fresh-clone",
        "https://github.com/tiramitree/fde-ai-systems-portfolio/actions/workflows/ci.yml/badge.svg",
        "local quality output, remote workflow status, skipped workflows, and README badge rendering prove different things",
        "Do not claim a green workflow badge until the current remote `quality-gate` run is public and current",
    ],
    "docs/dependabot_secret_scanning_verification_examples.md": [
        "# Dependabot And Secret-Scanning Verification Examples",
        ".github/dependabot.yml",
        "docs/supply_chain_security.md",
        "docs/post_publish_checklist.md",
        "docs/post_publish_warning_examples.md",
        "docs/github_repository_settings.md",
        "docs/command_output_troubleshooting_map.md",
        "Expected Evidence Split",
        "Missing Dependabot Config",
        "Stale Dependency Alerts",
        "Secret-Scanning Setting Confusion",
        "False Positive Secret Alerts",
        "Local Safety Scan Confusion",
        "Review Checklist",
        "python -B scripts/dev.py dependency-surface",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
        "python -B scripts/dev.py github-readiness",
        "python -B scripts/dev.py github-maintenance",
        "checked-in policy files, GitHub account-level security settings, generated alerts, and local safety scans prove different things",
        "Do not claim Dependabot or secret-scanning setup is complete until public/account-level evidence confirms it",
    ],
    "docs/public_roadmap_issue_comment_examples.md": [
        "# Public Roadmap Issue Comment Examples",
        "docs/github_initial_issues.md",
        "docs/community_backlog.md",
        "docs/issue_to_pr_handoff_flow.md",
        "docs/docs_only_review_comment_examples.md",
        "docs/maintainer_review_policy.md",
        "Comment Principles",
        "Accept Scoped Roadmap Issue",
        "Narrow Oversized Request",
        "Close Low-Signal Activity",
        "Redirect Unsafe Requests",
        "Link Useful PR",
        "Review Checklist",
        "accepted scope, backlog ideas, implementation promises, and low-signal activity",
        "do not promise delivery dates, external-account access, private data, or guaranteed roadmap acceptance",
        "python -B scripts/dev.py community-issues",
        "python -B scripts/dev.py pr-policy",
        "python -B scripts/dev.py safety",
        "python -B scripts/dev.py quality",
    ],
    "docs/github_label_troubleshooting_examples.md": [
        "# GitHub Label Troubleshooting Examples",
        "docs/github_labels.json",
        "docs/github_initial_issues.md",
        "docs/github_repository_settings.md",
        "docs/post_publish_checklist.md",
        "Missing Labels",
        "Color Drift",
        "Template Mismatch",
        "Dry-Run Output",
        "Issue-Pack Label Mismatch",
        "python -B scripts/dev.py community-issues",
        "python -B scripts/dev.py github-community",
        "python -B scripts/manage_community_issues.py --apply",
        "python -B scripts/manage_community_issues.py --apply --create-issues",
        "label sync and public roadmap issue creation are separate actions",
    ],
}

PUBLIC_POSITIONING_FILES = [
    "README.md",
    "docs/launch_assets_hygiene.md",
    "docs/launch_copy_pack.md",
    "docs/launch_feedback_collection_examples.md",
    "docs/star_growth_plan.md",
    "docs/community_backlog.md",
    "docs/github_initial_issues.md",
    "docs/github_launch_plan.md",
    "docs/published_repository_status.md",
    "docs/post_publish_checklist.md",
    "docs/post_publish_warning_examples.md",
    "docs/public_roadmap_issue_comment_examples.md",
    "docs/dependabot_secret_scanning_verification_examples.md",
    "docs/github_authenticated_maintenance_troubleshooting_examples.md",
    "docs/github_public_pr_api_fallback_troubleshooting_examples.md",
    "docs/github_api_rate_limit_troubleshooting_examples.md",
    "docs/github_repository_metadata_troubleshooting_examples.md",
    "docs/github_repository_settings_screenshot_checklist.md",
    "docs/social_preview_verification_examples.md",
    "docs/profile_pin_verification_examples.md",
    "docs/github_actions_warning_examples.md",
    "docs/github_actions_badge_verification_examples.md",
    "docs/github_label_troubleshooting_examples.md",
    "docs/github_release_page_troubleshooting_examples.md",
    "docs/github_latest_release_troubleshooting_examples.md",
    "docs/release_attachment_verification_examples.md",
    "docs/release_asset_upload_dry_run_examples.md",
    "docs/github_release_attachment_screenshot_checklist.md",
    "docs/final_readiness_report.md",
]

FORBIDDEN_HYPE_PATTERNS = {
    "production-ready claim": re.compile(r"\bproduction[- ]ready\b", re.IGNORECASE),
    "production-grade claim": re.compile(r"\bproduction[- ]grade\b", re.IGNORECASE),
    "completed launch claim": re.compile(r"\b(?:fully\s+)?launch(?:ed)?\s+complete\b", re.IGNORECASE),
    "Docker runtime verified claim": re.compile(r"\bdocker(?: compose)? runtime (?:is )?(?:verified|passed|complete)\b", re.IGNORECASE),
    "OpenAI live verified claim": re.compile(r"\bopenai live(?: mode)? (?:is )?(?:verified|passed|complete)\b", re.IGNORECASE),
    "branch protection enabled claim": re.compile(r"\bbranch protection (?:is )?(?:enabled|complete)\b", re.IGNORECASE),
    "release page created claim": re.compile(r"\brelease page (?:is )?(?:created|published|complete)\b", re.IGNORECASE),
    "star growth achieved claim": re.compile(r"\bstar[- ]growth (?:is )?(?:achieved|complete|proven)\b", re.IGNORECASE),
    "vanity activity framing": re.compile(r"\blook(?:s|ing)? (?:active|alive)\b", re.IGNORECASE),
    "fake activity framing": re.compile(r"\b(?:fake|placeholder) (?:activity|issues?)\b", re.IGNORECASE),
    "growth hack framing": re.compile(r"\bgrowth hack(?:ing)?\b", re.IGNORECASE),
}

SAFE_CONTEXT_MARKERS = [
    "not verified",
    "before claiming",
    "before claim",
    "do not claim",
    "not claim",
    "do not create",
    "cannot be claimed",
    "should not be claimed",
    "still manual",
    "missing",
    "manual",
    "not protected",
    "not yet",
]


def read_text(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def require_files() -> list[str]:
    failures = []
    for rel_path in REQUIRED_FILES:
        if not (ROOT / rel_path).exists():
            failures.append(f"missing required launch asset file: {rel_path}")
    return failures


def require_sections() -> list[str]:
    failures = []
    for rel_path, sections in REQUIRED_SECTIONS.items():
        if not (ROOT / rel_path).exists():
            continue
        text = read_text(rel_path)
        for section in sections:
            if section not in text:
                failures.append(f"{rel_path}: missing section {section!r}")
    return failures


def require_phrases() -> list[str]:
    failures = []
    for rel_path, phrases in REQUIRED_PHRASES.items():
        if not (ROOT / rel_path).exists():
            continue
        text = read_text(rel_path)
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{rel_path}: missing phrase {phrase!r}")
    return failures


def check_issue_pack() -> list[str]:
    rel_path = "docs/github_initial_issues.md"
    if not (ROOT / rel_path).exists():
        return []
    text = read_text(rel_path)
    failures = []
    issue_count = len(re.findall(r"^## Issue \d+\s*$", text, flags=re.MULTILINE))
    acceptance_count = text.count("Acceptance criteria:")
    label_count = text.count("Labels:")
    if issue_count < 5:
        failures.append(f"{rel_path}: expected at least 5 launch issues, found {issue_count}")
    if acceptance_count < issue_count:
        failures.append(f"{rel_path}: every launch issue should include acceptance criteria")
    if label_count < issue_count:
        failures.append(f"{rel_path}: every launch issue should include labels")
    return failures


def check_launch_copy_channels() -> list[str]:
    rel_path = "docs/launch_copy_pack.md"
    if not (ROOT / rel_path).exists():
        return []
    text = read_text(rel_path)
    channels = {
        "LinkedIn": "## LinkedIn Post",
        "X / Twitter": "## X / Twitter Thread",
        "Hacker News": "## Hacker News Show HN",
        "Reddit / Community": "## Reddit / Community Post",
        "blog follow-up": "## Follow-Up Blog Outline",
    }
    failures = []
    for name, marker in channels.items():
        if marker not in text:
            failures.append(f"{rel_path}: missing launch copy channel: {name}")
    if text.count("<repo-url>") < 2:
        failures.append(f"{rel_path}: launch posts should keep explicit <repo-url> placeholders")
    return failures


def check_no_unverified_claims() -> list[str]:
    failures = []
    for rel_path in PUBLIC_POSITIONING_FILES:
        if not (ROOT / rel_path).exists():
            continue
        for line_number, raw_line in enumerate(read_text(rel_path).splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            lower = line.lower()
            if any(marker in lower for marker in SAFE_CONTEXT_MARKERS):
                continue
            for name, pattern in FORBIDDEN_HYPE_PATTERNS.items():
                if pattern.search(line):
                    failures.append(f"{rel_path}:{line_number}: possible {name}: {line!r}")
    return failures


def main() -> int:
    failures = []
    failures.extend(require_files())
    failures.extend(require_sections())
    failures.extend(require_phrases())
    failures.extend(check_issue_pack())
    failures.extend(check_launch_copy_channels())
    failures.extend(check_no_unverified_claims())

    if failures:
        print("Launch asset hygiene check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Launch asset hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
