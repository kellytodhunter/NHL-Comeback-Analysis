"""
Scrapes per-game goalie stats from box scores for all four comeback series.
Extracts every goalie who played in each game so we can track starter vs
replacement performance before and after the 0-3 hole.
"""

import time
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

RAW_DATA_DIR = Path(__file__).parent.parent / 'data' / 'raw'
BASE_URL = 'https://www.hockey-reference.com'
REQUEST_DELAY = 4.0

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

# Only comeback series — that's what this analysis is about
COMEBACK_SERIES = [
    ('1942_tor_det',
     'https://www.hockey-reference.com/playoffs/1942-detroit-red-wings-vs-toronto-maple-leafs-stanley-cup-final.html',
     'TOR', 'DET'),
    ('1975_nyi_pit',
     'https://www.hockey-reference.com/playoffs/1975-new-york-islanders-vs-pittsburgh-penguins-quarter-finals.html',
     'NYI', 'PIT'),
    ('2010_phi_bos',
     'https://www.hockey-reference.com/playoffs/2010-boston-bruins-vs-philadelphia-flyers-eastern-conference-semi-finals.html',
     'PHI', 'BOS'),
    ('2014_lak_sjs',
     'https://www.hockey-reference.com/playoffs/2014-los-angeles-kings-vs-san-jose-sharks-western-first-round.html',
     'LAK', 'SJS'),
]


def fetch(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'lxml')


def get_boxscore_links(series_url: str) -> list[str]:
    soup = fetch(series_url)
    time.sleep(REQUEST_DELAY)
    links, seen = [], set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/boxscores/' in href and href != '/boxscores/' and href not in seen:
            slug = href.replace('/boxscores/', '').replace('.html', '')
            if len(slug) >= 8 and slug[:8].isdigit():
                links.append(BASE_URL + href)
                seen.add(href)
    return links[:7]  # playoff games only


def parse_goalie_table(soup: BeautifulSoup, team_abbr: str,
                       series_id: str, game_num: int) -> list[dict]:
    table = soup.find('table', {'id': f'{team_abbr}_goalies'})
    if table is None:
        return []

    # Use data-stat attributes for reliable extraction regardless of header layout
    STATS = ['player', 'decision', 'goals_against', 'shots_against',
             'saves', 'save_pct', 'shutouts', 'pen_min', 'time_on_ice']

    rows = []
    for row in table.select('tbody tr'):
        row_data = {}
        for stat in STATS:
            cell = row.find(['td', 'th'], {'data-stat': stat})
            row_data[stat] = cell.get_text(strip=True) if cell else None
        if not row_data.get('player'):
            continue
        row_data['team']      = team_abbr
        row_data['series_id'] = series_id
        row_data['game_num']  = game_num
        rows.append(row_data)
    return rows


def scrape_series_goalies(series_id: str, series_url: str,
                           cb_abbr: str, opp_abbr: str) -> list[dict]:
    print(f'\n=== {series_id} ===')
    links = get_boxscore_links(series_url)
    all_rows = []

    for game_num, url in enumerate(links, start=1):
        print(f'  Game {game_num}: {url}')
        soup = fetch(url)
        time.sleep(REQUEST_DELAY)

        for abbr in [cb_abbr, opp_abbr]:
            rows = parse_goalie_table(soup, abbr, series_id, game_num)
            for r in rows:
                r['is_comeback_team'] = (abbr == cb_abbr)
            all_rows.extend(rows)
            if rows:
                for r in rows:
                    print(f'    {abbr} — {r.get("Player","?")}  '
                          f'SV%={r.get("SV%","?")}  GA={r.get("GA","?")}  '
                          f'TOI={r.get("TOI","?")}')

    return all_rows


if __name__ == '__main__':
    all_game_goalies = []

    for series_id, series_url, cb_abbr, opp_abbr in COMEBACK_SERIES:
        rows = scrape_series_goalies(series_id, series_url, cb_abbr, opp_abbr)
        all_game_goalies.extend(rows)

    out_path = RAW_DATA_DIR / 'game_goalie_stats.json'
    with open(out_path, 'w') as f:
        json.dump(all_game_goalies, f, indent=2)
    print(f'\nSaved {len(all_game_goalies)} goalie-game rows → {out_path}')
