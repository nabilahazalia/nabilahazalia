#!/usr/bin/env python3
"""Generate the profile's self-hosted performance card from public GitHub data."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

USERNAME = "nabilahazalia"
API_ROOT = "https://api.github.com"
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "performance-stats.svg"


def github_get(path: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-stats-generator",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"{API_ROOT}{path}", headers=headers)
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API returned {error.code}: {detail}") from error


def public_repositories():
    repositories = []
    page = 1
    while True:
        batch = github_get(
            f"/users/{USERNAME}/repos?type=public&sort=full_name&per_page=100&page={page}"
        )
        repositories.extend(batch)
        if len(batch) < 100:
            return repositories
        page += 1


def render_svg(repositories: list[dict], profile: dict) -> str:
    repository_count = len(repositories)
    star_count = sum(int(repository.get("stargazers_count", 0)) for repository in repositories)
    follower_count = int(profile["followers"])
    member_since = str(profile["created_at"])[0:7]
    year, month = member_since.split("-")
    month_name = (
        "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()[int(month) - 1]
    )
    joined = html.escape(f"{month_name} {year}")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="280" viewBox="0 0 900 280" role="img" aria-labelledby="title desc">
  <title id="title">Nabilah's public GitHub performance stats</title>
  <desc id="desc">{repository_count} public repositories, {star_count} stars across public repositories, {follower_count} followers, member since {joined}.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff8fb"/><stop offset="1" stop-color="#ffe3ec"/></linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#ff6f91"/><stop offset="1" stop-color="#ff9eaa"/></linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#d16b86" flood-opacity=".16"/></filter>
  </defs>
  <rect width="900" height="280" rx="24" fill="url(#bg)"/>
  <path d="M0 48C180 95 304 4 472 44s266 74 428 8V0H0Z" fill="#ffd1dc" opacity=".52"/>
  <circle cx="845" cy="44" r="22" fill="#fff" opacity=".55"/>
  <g fill="#ff8fa7" opacity=".7"><text x="36" y="44" font-size="20">&#10022;</text><text x="812" y="89" font-size="15">&#10022;</text><text x="863" y="222" font-size="21">&#10022;</text></g>
  <text x="450" y="53" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="22" font-weight="700" fill="#a94765">LIVE STAGE · PUBLIC PROFILE</text>
  <text x="450" y="78" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="12" letter-spacing="2" fill="#c66a82">AUTOMATICALLY REFRESHED</text>
  <g filter="url(#shadow)" font-family="Segoe UI,Arial,sans-serif">
    <g transform="translate(38 105)"><rect width="190" height="115" rx="18" fill="#fff"/><rect width="190" height="6" rx="3" fill="url(#accent)"/><text x="95" y="58" text-anchor="middle" font-size="34" font-weight="750" fill="#d65376">{repository_count}</text><text x="95" y="86" text-anchor="middle" font-size="13" font-weight="600" fill="#855366">PUBLIC REPOSITORIES</text></g>
    <g transform="translate(249 105)"><rect width="190" height="115" rx="18" fill="#fff"/><rect width="190" height="6" rx="3" fill="url(#accent)"/><text x="95" y="58" text-anchor="middle" font-size="34" font-weight="750" fill="#d65376">{star_count}</text><text x="95" y="86" text-anchor="middle" font-size="13" font-weight="600" fill="#855366">PUBLIC STARS</text></g>
    <g transform="translate(460 105)"><rect width="190" height="115" rx="18" fill="#fff"/><rect width="190" height="6" rx="3" fill="url(#accent)"/><text x="95" y="58" text-anchor="middle" font-size="34" font-weight="750" fill="#d65376">{follower_count}</text><text x="95" y="86" text-anchor="middle" font-size="13" font-weight="600" fill="#855366">FOLLOWERS</text></g>
    <g transform="translate(671 105)"><rect width="190" height="115" rx="18" fill="#fff"/><rect width="190" height="6" rx="3" fill="url(#accent)"/><text x="95" y="55" text-anchor="middle" font-size="23" font-weight="750" fill="#d65376">{joined}</text><text x="95" y="86" text-anchor="middle" font-size="13" font-weight="600" fill="#855366">MEMBER SINCE</text></g>
  </g>
  <text x="450" y="254" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="#9e6073">Public GitHub API data · private activity is not included</text>
</svg>
'''


def main() -> None:
    profile = github_get(f"/users/{USERNAME}")
    repositories = public_repositories()
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as output_file:
        output_file.write(render_svg(repositories, profile))
    print(f"Updated {OUTPUT} from {len(repositories)} public repositories")


if __name__ == "__main__":
    main()
