#!/usr/bin/env python3
"""Scrape the public contribution calendar into data/contributions.json.

No GraphQL, no personal access token: GitHub serves the calendar as plain
HTML at /users/<user>/contributions and that page is public.
"""
import json
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_USER", "DiveshJ8766")
URL = f"https://github.com/users/{USER}/contributions"
OUT = Path(__file__).resolve().parents[1] / "data" / "contributions.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (profile-art bot; +https://github.com/%s)" % USER,
    "Accept": "text/html",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    days = []
    for td in soup.select("td[data-date]"):
        date = td.get("data-date")
        level = int(td.get("data-level") or 0)
        count = 0
        # The count lives in the <tool-tip for="cell-id"> that follows the grid.
        cell_id = td.get("id")
        if cell_id:
            tip = soup.find("tool-tip", attrs={"for": cell_id})
            if tip:
                m = re.search(r"(\d+)\s+contribution", tip.get_text())
                if m:
                    count = int(m.group(1))
        days.append({"date": date, "level": level, "count": count})

    days.sort(key=lambda d: d["date"])
    if not days:
        raise SystemExit("no contribution cells found - did the markup change?")
    return {
        "user": USER,
        "start": days[0]["date"],
        "end": days[-1]["date"],
        "total": sum(d["count"] for d in days),
        "days": days,
    }


def main():
    try:
        data = parse(fetch())
    except Exception as exc:  # noqa: BLE001 - keep yesterday's art rather than break the profile
        print(f"fetch failed: {exc}", file=sys.stderr)
        if OUT.exists():
            print("keeping existing data/contributions.json")
            return 0
        raise

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(f"wrote {OUT} - {len(data['days'])} days, {data['total']} contributions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
