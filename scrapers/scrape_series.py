"""
Scraper for Hockey Reference playoff series pages.
Pulls game-by-game logs and goalie stats for each series.
"""

import time
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

RAW_DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Hockey Reference rate limit — 20 requests/minute recommended
REQUEST_DELAY = 4.0


def fetch_page(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def parse_game_scores(soup: BeautifulSoup, series_id: str) -> list[dict]:
    """
    Parse per-game scores from the 'teams' tables on a series page.
    Each game has one table with three rows: date, road team, home team.
    """
    games = []
    teams_tables = soup.find_all("table", class_="teams")
    # The page includes bracket context tables; only take tables with 3 rows (one game each)
    game_tables = [t for t in teams_tables if len(t.find_all("tr")) == 3]

    for i, table in enumerate(game_tables):
        rows = table.find_all("tr")
        date_cells = rows[0].find_all(["td", "th"])
        team1_cells = rows[1].find_all(["td", "th"])
        team2_cells = rows[2].find_all(["td", "th"])

        date_text = date_cells[0].get_text(strip=True) if date_cells else ""
        ot_text = team2_cells[2].get_text(strip=True) if len(team2_cells) > 2 else ""

        games.append({
            "series_id": series_id,
            "game_num": i + 1,
            "date": date_text,
            "road_team": team1_cells[0].get_text(strip=True) if team1_cells else "",
            "road_score": team1_cells[1].get_text(strip=True) if len(team1_cells) > 1 else "",
            "home_team": team2_cells[0].get_text(strip=True) if team2_cells else "",
            "home_score": team2_cells[1].get_text(strip=True) if len(team2_cells) > 1 else "",
            "overtime": ot_text if ot_text not in ("Final", "") else "",
        })

    return games


def parse_skater_stats(soup: BeautifulSoup, series_id: str) -> list[dict]:
    """Parse per-player skater stats tables (one per team) for the full series."""
    skaters = []
    for table in soup.find_all("table"):
        table_id = table.get("id", "")
        if not table_id.startswith("series_stats_"):
            continue
        team_abbr = table_id.replace("series_stats_", "")
        headers_rows = table.select("thead tr")
        # Use the last header row for column names
        headers = [th.get_text(strip=True) for th in headers_rows[-1].find_all("th")] if headers_rows else []
        for row in table.select("tbody tr"):
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(min(len(headers), len(cells)))}
            row_data["series_id"] = series_id
            row_data["team"] = team_abbr
            skaters.append(row_data)
    return skaters


def parse_goalie_stats(soup: BeautifulSoup, series_id: str) -> list[dict]:
    """Parse goalie stats tables (one per team) from a series page."""
    goalies = []
    for table in soup.find_all("table"):
        table_id = table.get("id", "")
        if "goalies" not in table_id:
            continue
        team_abbr = table_id.replace("series_goalies_stats_", "").replace("goalies-", "")
        headers_rows = table.select("thead tr")
        headers = [th.get_text(strip=True) for th in headers_rows[-1].find_all("th")] if headers_rows else []
        for row in table.select("tbody tr"):
            cells = row.find_all(["td", "th"])
            if not cells:
                continue
            row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(min(len(headers), len(cells)))}
            row_data["series_id"] = series_id
            row_data["team"] = team_abbr
            row_data["table_id"] = table_id
            goalies.append(row_data)
    return goalies


def scrape_series(series: dict) -> dict:
    sid = series["id"]
    url = series["hr_url"]
    print(f"Fetching {sid} from {url}")

    soup = fetch_page(url)
    time.sleep(REQUEST_DELAY)

    games = parse_game_scores(soup, sid)
    skaters = parse_skater_stats(soup, sid)
    goalies = parse_goalie_stats(soup, sid)

    result = {
        "series_id": sid,
        "metadata": series,
        "games": games,
        "skaters": skaters,
        "goalies": goalies,
    }

    out_path = RAW_DATA_DIR / f"{sid}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"  Saved {len(games)} games, {len(skaters)} skater rows, {len(goalies)} goalie rows → {out_path}")
    return result


def scrape_all(series_list: list[dict]) -> None:
    for series in series_list:
        try:
            scrape_series(series)
        except Exception as e:
            print(f"  [error] {series['id']}: {e}")
        time.sleep(REQUEST_DELAY)


if __name__ == "__main__":
    from series_config import COMEBACK_SERIES, COMPARISON_SERIES

    print("=== Scraping comeback series ===")
    scrape_all(COMEBACK_SERIES)

    print("\n=== Scraping comparison series ===")
    scrape_all(COMPARISON_SERIES)

    print("\nDone.")
