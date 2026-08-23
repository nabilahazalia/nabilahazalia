#!/usr/bin/env python3
"""Build self-hosted light and dark activity cards from public GitHub data."""

from __future__ import annotations

import html
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

USERNAME = "nabilahazalia"
ASSETS = Path(__file__).resolve().parents[1] / "assets"

THEMES = {
    "light": {"bg1": "#fff9fc", "bg2": "#ffe1ec", "panel": "#ffffff", "line": "#e88bad", "accent": "#c33f75", "title": "#752544", "text": "#58323f", "muted": "#805466", "beam": "#ffffff"},
    "dark": {"bg1": "#241622", "bg2": "#472139", "panel": "#34202f", "line": "#ef91b6", "accent": "#ff91bd", "title": "#ffd5e5", "text": "#f8e7ee", "muted": "#e6b8ca", "beam": "#ffdbeb"},
}


def github_get(url: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": f"{USERNAME}-profile-activity-generator", "X-GitHub-Api-Version": "2022-11-28"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urlopen(Request(url, headers=headers), timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API returned {error.code}: {detail}") from error


def render(repository: dict, theme_name: str) -> str:
    theme = THEMES[theme_name]
    name = html.escape(str(repository["name"])[:40])
    # Truncate raw text before escaping so an entity cannot expand beyond the layout budget.
    raw_description = str(repository.get("description") or "A public GitHub repository")[:76]
    description = html.escape(raw_description)
    language = html.escape(str(repository.get("language") or "Not specified")[:24])
    updated = datetime.fromisoformat(repository["pushed_at"].replace("Z", "+00:00"))
    updated_label = updated.strftime("%d %b %Y")
    accessible = html.escape(f"Latest public repository: {repository['name']}. {raw_description}. Primary language: {repository.get('language') or 'Not specified'}. Updated {updated_label}.")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="210" viewBox="0 0 900 210" role="img" aria-labelledby="title desc">
  <title id="title">Nabilah's current public GitHub activity</title><desc id="desc">{accessible}</desc>
  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{theme['bg1']}"/><stop offset="1" stop-color="{theme['bg2']}"/></linearGradient></defs>
  <rect x="1" y="1" width="898" height="208" rx="24" fill="url(#bg)" stroke="{theme['line']}" stroke-width="2"/>
  <path d="M85 1 185 178H30L85 1Zm730 0 55 177H715L815 1Z" fill="{theme['beam']}" opacity=".16"/>
  <g fill="{theme['accent']}" aria-hidden="true"><path d="m42 35 4 9 9 4-9 4-4 9-4-9-9-4 9-4 4-9Z"/><path d="m858 36 3 7 7 3-7 3-3 7-3-7-7-3 7-3 3-7Z"/></g>
  <text x="44" y="48" font-family="Segoe UI,Arial,sans-serif" font-size="13" font-weight="700" letter-spacing="2" fill="{theme['accent']}">NOW PERFORMING · LATEST PUBLIC UPDATE</text>
  <text x="44" y="83" font-family="Segoe UI,Arial,sans-serif" font-size="25" font-weight="700" fill="{theme['title']}">{name}</text>
  <text x="44" y="116" font-family="Segoe UI,Arial,sans-serif" font-size="15" fill="{theme['text']}">{description}</text>
  <rect x="44" y="142" width="210" height="36" rx="18" fill="{theme['panel']}" stroke="{theme['line']}"/>
  <text x="149" y="165" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="{theme['title']}">MIC CHECK · {language}</text>
  <text x="856" y="165" text-anchor="end" font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="{theme['muted']}">LAST REHEARSAL · {updated_label}</text>
  <g stroke="{theme['accent']}" stroke-width="4" stroke-linecap="round" opacity=".72" aria-hidden="true"><path d="m64 195 5-12"/><path d="m82 195-1-14"/><path d="m100 195-6-12"/><path d="m800 195-4-12"/><path d="m819 195 1-14"/><path d="m838 195 5-12"/></g>
</svg>\n'''


def main() -> None:
    repositories = github_get(f"https://api.github.com/users/{USERNAME}/repos?type=public&sort=pushed&per_page=100")
    active = [repo for repo in repositories if not repo["fork"] and not repo["archived"]]
    if not active:
        raise RuntimeError("No active public repositories found; leaving existing cards unchanged")
    for theme_name in THEMES:
        output = ASSETS / f"current-activity-{theme_name}.svg"
        with output.open("w", encoding="utf-8", newline="\n") as card:
            card.write(render(active[0], theme_name))
    print(f"Updated activity cards from {active[0]['full_name']}")


if __name__ == "__main__":
    main()
