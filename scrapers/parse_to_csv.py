"""
Reads raw JSON files and outputs clean CSVs to data/processed/.
Run this after scraping is complete.
"""

import json
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def process_game_logs() -> None:
    all_games = []
    for json_file in RAW_DIR.glob("*.json"):
        if json_file.name == "season_team_stats.json":
            continue
        with open(json_file) as f:
            data = json.load(f)
        meta = data["metadata"]
        for game in data["games"]:
            game["year"] = meta["year"]
            game["round"] = meta["round"]
            game["comeback_team"] = meta.get("comeback_team") or meta.get("trailing_team")
            game["opponent"] = meta.get("opponent") or meta.get("leading_team")
            game["is_comeback_series"] = "comeback_team" in meta
            all_games.append(game)

    if all_games:
        df = pd.DataFrame(all_games)
        out = PROCESSED_DIR / "game_logs.csv"
        df.to_csv(out, index=False)
        print(f"Wrote {len(df)} game rows → {out}")
    else:
        print("No game data found — run scrapers first.")


def process_goalie_stats() -> None:
    all_goalies = []
    for json_file in RAW_DIR.glob("*.json"):
        if json_file.name == "season_team_stats.json":
            continue
        with open(json_file) as f:
            data = json.load(f)
        meta = data["metadata"]
        for row in data["goalies"]:
            row["year"] = meta["year"]
            row["comeback_team"] = meta.get("comeback_team") or meta.get("trailing_team")
            row["is_comeback_series"] = "comeback_team" in meta
            all_goalies.append(row)

    if all_goalies:
        df = pd.DataFrame(all_goalies)
        out = PROCESSED_DIR / "goalie_stats.csv"
        df.to_csv(out, index=False)
        print(f"Wrote {len(df)} goalie rows → {out}")


def process_season_stats() -> None:
    path = RAW_DIR / "season_team_stats.json"
    if not path.exists():
        print("No season stats file found — run scrape_season_stats.py first.")
        return
    with open(path) as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    out = PROCESSED_DIR / "season_team_stats.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} season stat rows → {out}")


if __name__ == "__main__":
    process_game_logs()
    process_goalie_stats()
    process_season_stats()
    print("Done.")
