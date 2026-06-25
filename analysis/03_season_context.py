import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'

season = pd.read_csv(DATA_DIR / 'season_team_stats.csv')

# ── Convert numeric columns ───────────────────────────────────────────────────
# Some columns come in as strings due to empty cells in older seasons
numeric_cols = ['Rk', 'GP', 'W', 'L', 'PTS', 'PTS%', 'GF', 'GA',
                'GF/G', 'GA/G', 'PP%', 'PK%', 'SRS']
for col in numeric_cols:
    if col in season.columns:
        season[col] = pd.to_numeric(season[col], errors='coerce')

# ── Teams of interest with their series role ──────────────────────────────────
# Maps (full team name, year) → (series_id, role)
TEAM_ROLES = {
    ('Toronto Maple Leafs',  1942): ('1942_tor_det', 'comeback'),
    ('Detroit Red Wings',    1942): ('1942_tor_det', 'opponent'),
    ('New York Islanders',   1975): ('1975_nyi_pit', 'comeback'),
    ('Pittsburgh Penguins',  1975): ('1975_nyi_pit', 'opponent'),
    ('Philadelphia Flyers',  2010): ('2010_phi_bos', 'comeback'),
    ('Boston Bruins',        2010): ('2010_phi_bos', 'opponent'),
    ('Los Angeles Kings',    2014): ('2014_lak_sjs', 'comeback'),
    ('San Jose Sharks',      2014): ('2014_lak_sjs', 'opponent'),
    ('Detroit Red Wings',    2013): ('2013_det_chi', 'trailing'),
    ('Chicago Blackhawks',   2013): ('2013_det_chi', 'leading'),
    ('Minnesota Wild',       2014): ('2014_col_min', 'trailing'),
    ('Colorado Avalanche',   2014): ('2014_col_min', 'leading'),
    ('Carolina Hurricanes',  2019): ('2019_car_wsh', 'trailing'),
    ('Washington Capitals',  2019): ('2019_car_wsh', 'leading'),
}

season['series_id'] = season.apply(
    lambda r: TEAM_ROLES.get((r['team'], r['year']), (None, None))[0], axis=1
)
season['role'] = season.apply(
    lambda r: TEAM_ROLES.get((r['team'], r['year']), (None, None))[1], axis=1
)

# Filter to only our teams of interest
teams = season[season['series_id'].notna()].copy()
teams = teams.reset_index(drop=True)

# Flag comeback series vs comparison
teams['is_comeback_series'] = teams['role'].isin(['comeback', 'opponent'])

# ── Seeding: points percentage rank within their season ──────────────────────
# Lower Rk = better team that season
teams['was_underdog'] = teams.apply(
    lambda r: (
        r['role'] in ('comeback', 'trailing') and
        r['Rk'] > season[(season['year'] == r['year']) &
                         (season['series_id'] == r['series_id']) &
                         (season['role'].isin(['opponent', 'leading']))]['Rk'].values[0]
    ) if r['role'] in ('comeback', 'trailing') else False,
    axis=1
)

# ── Goals for/against per game ────────────────────────────────────────────────
# Normalize to per-game to handle the short 1942/1975 seasons
teams['GF/G'] = pd.to_numeric(teams['GF/G'], errors='coerce')
teams['GA/G'] = pd.to_numeric(teams['GA/G'], errors='coerce')
teams['goal_diff_per_game'] = teams['GF/G'] - teams['GA/G']

# ── Summary: comeback teams vs comparison trailing teams ──────────────────────
comeback_teams = teams[teams['role'] == 'comeback'][['series_id', 'team', 'Rk', 'PTS%', 'GF/G', 'GA/G', 'goal_diff_per_game', 'PP%', 'PK%', 'SRS']]
opponent_teams = teams[teams['role'] == 'opponent'][['series_id', 'team', 'Rk', 'PTS%', 'GF/G', 'GA/G', 'goal_diff_per_game', 'PP%', 'PK%', 'SRS']]
trailing_teams = teams[teams['role'] == 'trailing'][['series_id', 'team', 'Rk', 'PTS%', 'GF/G', 'GA/G', 'goal_diff_per_game', 'PP%', 'PK%', 'SRS']]
leading_teams  = teams[teams['role'] == 'leading'][['series_id', 'team', 'Rk', 'PTS%', 'GF/G', 'GA/G', 'goal_diff_per_game', 'PP%', 'PK%', 'SRS']]

# ── Head-to-head comparison within each series ───────────────────────────────
merged = teams[teams['role'].isin(['comeback', 'opponent'])].merge(
    teams[teams['role'].isin(['comeback', 'opponent'])],
    on='series_id', suffixes=('_cb', '_op')
)
merged = merged[(merged['role_cb'] == 'comeback') & (merged['role_op'] == 'opponent')]
merged['pts_pct_diff'] = (merged['PTS%_cb'] - merged['PTS%_op']).round(3)
merged['srs_diff'] = (merged['SRS_cb'] - merged['SRS_op']).round(2)

# ── Print results ─────────────────────────────────────────────────────────────
pd.set_option('display.float_format', '{:.3f}'.format)

print("=== Comeback teams — regular season profile ===")
print(comeback_teams.to_string(index=False))

print("\n=== Their opponents — regular season profile ===")
print(opponent_teams.to_string(index=False))

print("\n=== Comparison: trailing teams (lost 0-4) ===")
print(trailing_teams.to_string(index=False))

print("\n=== Comparison: leading teams (won 4-0) ===")
print(leading_teams.to_string(index=False))

print("\n=== Head-to-head: comeback team vs opponent (pts% and SRS differential) ===")
print(merged[['series_id', 'team_cb', 'PTS%_cb', 'team_op', 'PTS%_op', 'pts_pct_diff', 'srs_diff']].to_string(index=False))

print("\n=== Average stats: comeback teams vs comparison trailing teams ===")
avg = teams[teams['role'].isin(['comeback', 'trailing'])].groupby('role')[['PTS%', 'GF/G', 'GA/G', 'goal_diff_per_game', 'PP%', 'PK%', 'SRS']].mean().round(3)
print(avg.to_string())
