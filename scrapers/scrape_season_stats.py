"""
Scrapes regular-season team stats for comeback and comparison teams
from Hockey Reference, for the season entering the playoff series.
"""

import time
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup, Comment

RAW_DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

REQUEST_DELAY = 4.0

# Season summary pages for each relevant year.
# We'll pull the full team stats table and filter to our teams of interest.
SEASON_URLS = {
    1942: "https://www.hockey-reference.com/leagues/NHL_1942.html",
    1975: "https://www.hockey-reference.com/leagues/NHL_1975.html",
    2010: "https://www.hockey-reference.com/leagues/NHL_2010.html",
    2014: "https://www.hockey-reference.com/leagues/NHL_2014.html",
    2013: "https://www.hockey-reference.com/leagues/NHL_2013.html",
    2019: "https://www.hockey-reference.com/leagues/NHL_2019.html",
}

# Teams we need stats for, keyed by (year, abbr)
TEAMS_OF_INTEREST = {
    (1942, "TOR"), (1942, "DET"),
    (1975, "NYI"), (1975, "PIT"),
    (2010, "PHI"), (2010, "BOS"),
    (2014, "LAK"), (2014, "SJS"),
    (2013, "DET"), (2013, "CHI"),
    (2014, "MIN"), (2014, "COL"),
    (2019, "CAR"), (2019, "WSH"),
}


def fetch_page(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.text


def extract_stats_table(html: str):
    """
    The stats table on HR season pages is wrapped in an HTML comment.
    Parse comments to find it, then return as a BeautifulSoup table element.
    """
    soup = BeautifulSoup(html, "lxml")
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if 'id="stats"' in str(comment):
            inner = BeautifulSoup(str(comment), "lxml")
            table = inner.find("table", {"id": "stats"})
            if table:
                return table
    return None


def parse_team_stats_table(html: str, year: int) -> list[dict]:
    table = extract_stats_table(html)
    if table is None:
        print(f"  [warn] No stats table found for {year}")
        return []

    # HR uses two header rows: row 0 has section labels, row 1 has real column names.
    # The team name column has no label in row 1 — we name it 'team'.
    header_rows = table.select("thead tr")
    raw_headers = [th.get_text(strip=True) for th in header_rows[-1].find_all("th")]
    # Second column is always team name but has empty header
    headers = []
    seen_empty = False
    for h in raw_headers:
        if h == "" and not seen_empty:
            headers.append("team")
            seen_empty = True
        else:
            headers.append(h)

    rows = []
    for row in table.select("tbody tr"):
        classes = row.get("class", [])
        if "thead" in classes or "partial_table" in classes:
            continue
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(min(len(headers), len(cells)))}
        # Strip playoff marker (*) from team names
        if "team" in row_data:
            row_data["team"] = row_data["team"].rstrip("*")
        row_data["year"] = year
        rows.append(row_data)
    return rows


def scrape_season(year: int, url: str) -> list[dict]:
    print(f"Fetching {year} season stats from {url}")
    html = fetch_page(url)
    time.sleep(REQUEST_DELAY)
    rows = parse_team_stats_table(html, year)
    print(f"  Found {len(rows)} team rows for {year}")
    return rows


def scrape_all_seasons() -> None:
    all_rows = []
    for year, url in sorted(SEASON_URLS.items()):
        rows = scrape_season(year, url)
        all_rows.extend(rows)

    out_path = RAW_DATA_DIR / "season_team_stats.json"
    with open(out_path, "w") as f:
        json.dump(all_rows, f, indent=2)
    print(f"\nSaved {len(all_rows)} total rows → {out_path}")


if __name__ == "__main__":
    scrape_all_seasons()
