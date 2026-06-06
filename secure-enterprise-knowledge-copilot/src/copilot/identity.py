from __future__ import annotations

from typing import Any


def string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        text = item.strip()
        if text and text not in normalized:
            normalized.append(text)
    return normalized


def user_group_ids(user: dict[str, Any]) -> list[str]:
    return string_list(user.get("group_ids"))


def user_source_principals(user: dict[str, Any]) -> list[str]:
    principals = string_list(user.get("source_principals"))
    for group_id in user_group_ids(user):
        principal = f"group:{group_id}"
        if principal not in principals:
            principals.append(principal)
    user_id = str(user.get("id", "")).strip()
    if user_id:
        principal = f"user:{user_id}"
        if principal not in principals:
            principals.append(principal)
    return principals


def row_allowed_groups(row: dict[str, Any]) -> list[str]:
    return string_list(row.get("allowed_groups"))


def row_source_acl_principals(row: dict[str, Any]) -> list[str]:
    return string_list(row.get("source_acl_principals"))


def has_group_access(row: dict[str, Any], user: dict[str, Any]) -> bool:
    user_groups = set(user_group_ids(user))
    if user_groups & set(row_allowed_groups(row)):
        return True
    return bool(set(user_source_principals(user)) & set(row_source_acl_principals(row)))


def has_identity_access(row: dict[str, Any], user: dict[str, Any]) -> bool:
    if row.get("tenant_id") != user.get("tenant_id"):
        return False
    allowed_roles = string_list(row.get("allowed_roles"))
    if str(user.get("role", "")).strip() in allowed_roles:
        return True
    return has_group_access(row, user)


def public_identity_context(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": user.get("role", ""),
        "tenant_id": user.get("tenant_id", ""),
        "group_ids": user_group_ids(user),
        "source_principals": user_source_principals(user),
    }
