from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECT_SRC = ROOT / "secure-enterprise-knowledge-copilot" / "src"
sys.path.insert(0, str(PROJECT_SRC))

from copilot.source_parsing import (  # noqa: E402
    PARSER_CONTRACT_VERSION,
    PARSER_QUALITY_SCHEMA_VERSION,
    parse_source_content,
)


CASES = {
    "text/plain": "Finance policy 2026\nEmployees submit receipts within five business days.",
    "text/markdown": (
        "# Expense Policy 2026\n\n"
        "[Receipt guide](https://example.invalid/receipt)\n\n"
        "```text\n"
        "approval: required\n"
        "```\n"
        "Managers review reports weekly."
    ),
    "text/csv": "vendor,owner,status\nNorthwind,Avery,approved\nContoso,Morgan,review",
    "text/html": (
        "<html><head><style>.hidden{display:none}</style></head>"
        "<body><h1>Benefits Notice 2026</h1><script>ignore()</script>"
        "<p>Enrollment opens June 10.</p></body></html>"
    ),
    "application/json": '{"policy":{"name":"Travel","rules":[{"window":"five days"}]}}',
}


def require(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def quality(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("quality")
    return value if isinstance(value, dict) else {}


def check_common_contract() -> list[str]:
    failures: list[str] = []
    for source_mime, content in CASES.items():
        parsed = parse_source_content(content, source_mime)
        metadata = parsed.metadata
        q = quality(metadata)
        require(metadata.get("source_mime") == source_mime, failures, f"{source_mime} missing source_mime")
        require(q.get("schema_version") == PARSER_QUALITY_SCHEMA_VERSION, failures, f"{source_mime} missing quality schema")
        require(q.get("contract_version") == PARSER_CONTRACT_VERSION, failures, f"{source_mime} missing parser contract")
        require(q.get("parser_name") == parsed.parser_name, failures, f"{source_mime} parser name mismatch")
        require(q.get("raw_character_count") == len(content), failures, f"{source_mime} raw count mismatch")
        require(q.get("normalized_character_count") == parsed.normalized_characters, failures, f"{source_mime} normalized count mismatch")
        require(q.get("normalized_non_empty_line_count", 0) >= 1, failures, f"{source_mime} empty quality line count")
        require(q.get("section_count", 0) >= 1, failures, f"{source_mime} missing section count")
    return failures


def check_format_details() -> list[str]:
    failures: list[str] = []

    markdown = parse_source_content(CASES["text/markdown"], "text/markdown")
    markdown_quality = quality(markdown.metadata)
    require(markdown_quality.get("markdown_heading_count") == 1, failures, "markdown heading count mismatch")
    require(markdown_quality.get("markdown_link_count") == 1, failures, "markdown link count mismatch")
    require(markdown_quality.get("markdown_code_block_count") == 1, failures, "markdown code block count mismatch")

    csv = parse_source_content(CASES["text/csv"], "text/csv")
    csv_quality = quality(csv.metadata)
    require(csv.metadata.get("row_count") == 2, failures, "csv row_count mismatch")
    require(csv.metadata.get("column_count") == 3, failures, "csv column_count mismatch")
    require(csv.metadata.get("has_header") is True, failures, "csv header detection mismatch")
    require(csv.metadata.get("ragged_row_count") == 0, failures, "csv ragged count mismatch")
    require(csv_quality.get("csv_data_row_count") == 2, failures, "csv quality row count mismatch")

    ragged_csv = parse_source_content("name,owner\nalpha,avery,extra\nbeta,morgan", "text/csv")
    require("ragged_csv_rows" in ragged_csv.warnings, failures, "ragged csv warning missing")
    require(ragged_csv.metadata.get("ragged_row_count", 0) >= 1, failures, "ragged csv metadata missing")
    require(quality(ragged_csv.metadata).get("csv_ragged_row_count", 0) >= 1, failures, "ragged csv quality missing")

    html = parse_source_content(CASES["text/html"], "text/html")
    html_quality = quality(html.metadata)
    require(html_quality.get("html_tag_count", 0) >= 6, failures, "html tag count missing")
    require(html_quality.get("html_script_style_block_count") == 2, failures, "html block count mismatch")
    require("ignore" not in html.text, failures, "html parser retained script content")

    json_payload = parse_source_content(CASES["application/json"], "application/json")
    json_quality = quality(json_payload.metadata)
    require(json_payload.metadata.get("json_root_type") == "dict", failures, "json root type mismatch")
    require(json_payload.metadata.get("field_count") == 2, failures, "json field count mismatch")
    require(json_payload.metadata.get("max_depth", 0) >= 5, failures, "json depth missing")
    require(json_quality.get("json_field_count") == json_payload.metadata.get("field_count"), failures, "json quality field mismatch")

    return failures


def main() -> int:
    failures = []
    failures.extend(check_common_contract())
    failures.extend(check_format_details())
    if failures:
        print("Project 1 parser quality contract failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Project 1 parser quality contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
