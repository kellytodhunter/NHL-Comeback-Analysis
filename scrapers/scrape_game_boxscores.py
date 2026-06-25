"""
Scrapes per-game box scores for each series to extract:
  - PP goals by team
  - PP opportunities by team (derived from penalties against opponent)
  - Penalty minutes by team
"""

import time
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup

RAW_DATA_DIR = Path(__file__).parent.parent / 'data' / 'raw'
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}
REQUEST_DELAY = 4.0
BASE_URL = 'https://www.hockey-reference.com'


def fetch(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'lxml')


def get_boxscore_links(series_url: str) -> list[str]:
    """Return all playoff game boxscore links from a series page."""
    soup = fetch(series_url)
    time.sleep(REQUEST_DELAY)
    links = []
    seen = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/boxscores/' in href and href != '/boxscores/' and href not in seen:
            # Only take links that look like real game URLs (8-digit date prefix)
            slug = href.replace('/boxscores/', '').replace('.html', '')
            if len(slug) >= 8 and slug[:8].isdigit():
                links.append(BASE_URL + href)
                seen.add(href)
    return links


def parse_pp_goals(scoring_table, team_abbrs: list[str]) -> dict[str, int]:
    """Count PP goals per team from the scoring summary table."""
    pp_goals = {t: 0 for t in team_abbrs}
    for row in scoring_table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) < 3:
            continue
        team = cells[1].get_text(strip=True)
        goal_type = cells[2].get_text(strip=True)
        if team in pp_goals and goal_type == 'PP':
            pp_goals[team] += 1
    return pp_goals


def parse_penalties(penalty_table, team_abbrs: list[str]) -> dict[str, dict]:
    """
    Parse penalty table.
    A penalty AGAINST team X gives team Y a power play opportunity.
    So PP opportunities for team X = penalties taken by opponent.
    Also sum penalty minutes per team.
    """
    penalties = {t: {'pim': 0, 'penalties_taken': 0} for t in team_abbrs}
    for row in penalty_table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) < 5:
            continue
        team = cells[1].get_text(strip=True)
        if team not in penalties:
            continue
        # Penalty minutes: last cell, e.g. "2 min", "4 min", "10 min"
        min_text = cells[4].get_text(strip=True)
        try:
            minutes = int(min_text.replace(' min', '').strip())
        except ValueError:
            minutes = 0
        penalties[team]['pim'] += minutes
        penalties[team]['penalties_taken'] += 1

    # PP opportunities = opponent's penalties taken (standard minors only, approximation)
    result = {}
    for i, team in enumerate(team_abbrs):
        opponent = team_abbrs[1 - i]
        result[team] = {
            'ppo': penalties[opponent]['penalties_taken'],
            'pim': penalties[team]['pim'],
        }
    return result


def scrape_boxscore(url: str, series_id: str, game_num: int,
                    comeback_abbr: str, opponent_abbr: str) -> dict:
    soup = fetch(url)
    time.sleep(REQUEST_DELAY)

    team_abbrs = [comeback_abbr, opponent_abbr]
    result = {
        'series_id': series_id,
        'game_num': game_num,
        'url': url,
        'comeback_abbr': comeback_abbr,
        'opponent_abbr': opponent_abbr,
    }

    scoring = soup.find('table', {'id': 'scoring'})
    penalty = soup.find('table', {'id': 'penalty'})

    if scoring:
        pp_goals = parse_pp_goals(scoring, team_abbrs)
        result['comeback_pp_goals'] = pp_goals.get(comeback_abbr, 0)
        result['opponent_pp_goals'] = pp_goals.get(opponent_abbr, 0)
    else:
        result['comeback_pp_goals'] = None
        result['opponent_pp_goals'] = None

    if penalty:
        pen_data = parse_penalties(penalty, team_abbrs)
        result['comeback_ppo']  = pen_data[comeback_abbr]['ppo']
        result['comeback_pim']  = pen_data[comeback_abbr]['pim']
        result['opponent_ppo']  = pen_data[opponent_abbr]['ppo']
        result['opponent_pim']  = pen_data[opponent_abbr]['pim']
    else:
        result['comeback_ppo'] = result['comeback_pim'] = None
        result['opponent_ppo'] = result['opponent_pim'] = None

    return result


# Series config: (series_id, series_url, comeback_abbr, opponent_abbr)
SERIES = [
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
    ('2013_det_chi',
     'https://www.hockey-reference.com/playoffs/2013-chicago-blackhawks-vs-detroit-red-wings-western-conference-semi-finals.html',
     'DET', 'CHI'),
    ('2014_col_min',
     'https://www.hockey-reference.com/playoffs/2014-colorado-avalanche-vs-minnesota-wild-western-first-round.html',
     'MIN', 'COL'),
    ('2019_car_wsh',
     'https://www.hockey-reference.com/playoffs/2019-carolina-hurricanes-vs-washington-capitals-eastern-first-round.html',
     'CAR', 'WSH'),
]


if __name__ == '__main__':
    all_games = []

    for series_id, series_url, cb_abbr, opp_abbr in SERIES:
        print(f'\n=== {series_id} ===')
        links = get_boxscore_links(series_url)

        # Filter to playoff games only (regular season links also appear on series pages)
        # Playoff box scores for 2010 will have dates like 20100501, 20100503, etc.
        # We take only the first 7 (or fewer) that are clearly sequential
        print(f'  Found {len(links)} boxscore links — filtering to first 7')
        playoff_links = links[:7]

        for i, url in enumerate(playoff_links, start=1):
            print(f'  Scraping game {i}: {url}')
            try:
                game_data = scrape_boxscore(url, series_id, i, cb_abbr, opp_abbr)
                all_games.append(game_data)
                print(f'    CB PP: {game_data["comeback_pp_goals"]}/{game_data["comeback_ppo"]}  '
                      f'OPP PP: {game_data["opponent_pp_goals"]}/{game_data["opponent_ppo"]}')
            except Exception as e:
                print(f'    [error] {e}')
            time.sleep(REQUEST_DELAY)

    out_path = RAW_DATA_DIR / 'game_special_teams.json'
    with open(out_path, 'w') as f:
        json.dump(all_games, f, indent=2)
    print(f'\nSaved {len(all_games)} game rows → {out_path}')
