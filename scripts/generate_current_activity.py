#!/usr/bin/env python3
"""Build a self-hosted activity card from public GitHub repository data."""

from __future__ import annotations

import html
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

USERNAME = "nabilahazalia"
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "current-activity.svg"


def github_get(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-activity-generator",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urlopen(Request(url, headers=headers), timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API returned {error.code}: {detail}") from error


def render(repository: dict) -> str:
    name = html.escape(repository["name"])
    description = html.escape(repository.get("description") or "A public GitHub repository")
    language = html.escape(repository.get("language") or "Not specified")
    updated = datetime.fromisoformat(repository["pushed_at"].replace("Z", "+00:00"))
    updated_label = updated.strftime("%d %b %Y")
    accessible = f"Latest public repository: {name}. {description}. Primary language: {language}. Updated {updated_label}."
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="190" viewBox="0 0 900 190" role="img" aria-labelledby="title desc">
  <title id="title">Nabilah's current public GitHub activity</title>
  <desc id="desc">{accessible}</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff7fa"/><stop offset="1" stop-color="#ffe1ea"/></linearGradient>
  </defs>
  <rect width="900" height="190" rx="22" fill="url(#bg)" stroke="#e992ad"/>
  <circle cx="58" cy="52" r="20" fill="#d85f84"/><path d="m58 41 3 7 7 3-7 3-3 7-3-7-7-3 7-3 3-7Z" fill="#fff"/>
  <text x="92" y="48" font-family="Segoe UI,Arial,sans-serif" font-size="13" letter-spacing="2" fill="#9c4564">LATEST PUBLIC UPDATE</text>
  <text x="92" y="75" font-family="Segoe UI,Arial,sans-serif" font-size="24" font-weight="700" fill="#7d2e4c">{name}</text>
  <text x="44" y="112" font-family="Segoe UI,Arial,sans-serif" font-size="15" fill="#603b49">{description[:78]}</text>
  <rect x="44" y="136" width="190" height="31" rx="15" fill="#fff"/>
  <text x="139" y="157" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="#7d2e4c">Language · {language}</text>
  <text x="856" y="157" text-anchor="end" font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="#805566">Updated {updated_label}</text>
</svg>
'''


def main() -> None:
    repositories = github_get(
        f"https://api.github.com/users/{USERNAME}/repos?type=public&sort=pushed&per_page=100"
    )
    active = [repo for repo in repositories if not repo["fork"] and not repo["archived"]]
    if not active:
        raise RuntimeError("No active public repositories found; leaving the existing card unchanged")
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as output:
        output.write(render(active[0]))
    print(f"Updated {OUTPUT} from {active[0]['full_name']}")


if __name__ == "__main__":
    main()
