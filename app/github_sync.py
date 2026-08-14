
from __future__ import annotations

import base64
import json
from typing import Any

import httpx

from app.config import settings


class GitHubSyncError(RuntimeError):
    pass


def configured() -> bool:
    return bool(settings.github_token and settings.github_repo and settings.github_language_file)


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }


def _url(path: str) -> str:
    return f"https://api.github.com/repos/{settings.github_repo}/contents/{path.lstrip('/')}"


async def read_json_file() -> tuple[list[dict[str, Any]], str | None]:
    if not configured():
        raise GitHubSyncError("GitHub sync is not configured. Set GITHUB_TOKEN.")
    params = {"ref": settings.github_branch}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(_url(settings.github_language_file), headers=_headers(), params=params)
    if r.status_code == 404:
        return [], None
    if r.status_code in (401, 403):
        raise GitHubSyncError("GitHub authentication/permission failed. The token needs repository Contents write access.")
    if r.status_code != 200:
        raise GitHubSyncError(f"GitHub read failed: HTTP {r.status_code}")
    data = r.json()
    try:
        raw = base64.b64decode(data["content"].replace("\n", "")).decode("utf-8")
        parsed = json.loads(raw)
    except Exception as exc:
        raise GitHubSyncError("The GitHub language file is not valid JSON.") from exc
    if not isinstance(parsed, list):
        raise GitHubSyncError("The GitHub language file must contain a JSON list.")
    return [x for x in parsed if isinstance(x, dict)], data.get("sha")


async def commit_language_entry(entry: dict[str, Any]) -> dict[str, Any]:
    rows, sha = await read_json_file()
    source = str(entry.get("standard_or_source", "")).strip()
    if source:
        rows = [x for x in rows if str(x.get("standard_or_source", "")).strip() != source]
    rows.append(entry)
    content = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    payload: dict[str, Any] = {
        "message": f"Add Melimi word: {entry.get('melimi', '')}",
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": settings.github_branch,
    }
    if sha:
        payload["sha"] = sha
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.put(_url(settings.github_language_file), headers=_headers(), json=payload)
    if r.status_code not in (200, 201):
        if r.status_code in (401, 403):
            raise GitHubSyncError("GitHub rejected the write. Check token Contents: Read and write permission.")
        raise GitHubSyncError(f"GitHub write failed: HTTP {r.status_code}: {r.text[:300]}")
    data = r.json()
    return {
        "committed": True,
        "repository": settings.github_repo,
        "branch": settings.github_branch,
        "path": settings.github_language_file,
        "commit_url": data.get("commit", {}).get("html_url", ""),
        "blob_url": data.get("content", {}).get("html_url", ""),
    }


def status() -> dict[str, Any]:
    return {
        "configured": configured(),
        "repository": settings.github_repo,
        "branch": settings.github_branch,
        "path": settings.github_language_file,
        "auto_commit": settings.github_auto_commit,
    }
