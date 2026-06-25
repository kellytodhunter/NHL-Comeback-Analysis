import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'

games   = pd.read_csv(DATA_DIR / 'game_logs.csv')
goalies = pd.read_csv(DATA_DIR / 'goalie_stats.csv')
season  = pd.read_csv(DATA_DIR / 'season_team_stats.csv')

pd.set_option('display.float_format', '{:.3f}'.format)

# ── 1. GAME MOMENTUM ─────────────────────────────────────────────────────────
games = games[games['date'].str.startswith('Game')].copy()
games = games.reset_index(drop=True)

def get_scores(row):
    if row['road_team'] == row['comeback_team']:
        return row['road_score'], row['home_score']
    else:
        return row['home_score'], row['road_score']

games[['comeback_score', 'opponent_score']] = games.apply(
    lambda row: pd.Series(get_scores(row)), axis=1
)
games['comeback_team_won']  = games['comeback_score'] > games['opponent_score']
games['score_differential'] = games['comeback_score'] - games['opponent_score']
games['overtime']           = games['overtime'].fillna('').astype(str)
games['is_overtime']        = games['overtime'].str.strip() != ''
games['phase']              = games['game_num'].apply(lambda g: 'games_1_3' if g <= 3 else 'games_4_7')

# Win % and avg goal diff per phase, grouped by comeback vs comparison
momentum = (
    games.groupby(['is_comeback_series', 'phase'])
    .agg(
        win_pct=('comeback_team_won', 'mean'),
        avg_goal_diff=('score_differential', 'mean'),
        ot_rate=('is_overtime', 'mean'),
    )
    .round(3)
    .reset_index()
)
momentum['series_type'] = momentum['is_comeback_series'].map(
    {True: 'comeback_series', False: 'comparison_series'}
)

# ── 2. GOALTENDING ───────────────────────────────────────────────────────────
series_goalies = goalies[goalies['table_id'].str.startswith('series_goalies')].copy()
series_goalies = series_goalies[series_goalies['GP'] > 0].copy()

# Identify which team abbreviation the comeback team uses
# (comeback_team column is the full name; team column is the abbr)
# We'll label each goalie row as playing for the trailing team or the leading team
# by checking whether the goalie's team appears in the series as the comeback/trailing team
SERIES_TRAILING_ABBR = {
    '1942_tor_det': 'TOR',
    '1975_nyi_pit': 'NYI',
    '2010_phi_bos': 'PHI',
    '2014_lak_sjs': 'LAK',
    '2013_det_chi': 'DET',
    '2014_col_min': 'MIN',
    '2019_car_wsh': 'CAR',
}
series_goalies['is_trailing_goalie'] = series_goalies.apply(
    lambda r: r['team'] == SERIES_TRAILING_ABBR.get(r['series_id'], ''), axis=1
)

# For each series, compute true SV% from raw totals for trailing and leading teams
goalie_sv = (
    series_goalies.groupby(['series_id', 'is_comeback_series', 'is_trailing_goalie'])
    .agg(total_ga=('GA', 'sum'), total_sa=('SA', 'sum'), goalies_used=('Player', 'count'))
    .reset_index()
)
goalie_sv['sv_pct'] = ((goalie_sv['total_sa'] - goalie_sv['total_ga']) / goalie_sv['total_sa']).round(4)
goalie_sv['role'] = goalie_sv['is_trailing_goalie'].map({True: 'trailing_team', False: 'leading_team'})

# Average SV% by series type and role
goalie_avg = (
    goalie_sv[goalie_sv['total_sa'] > 0]
    .groupby(['is_comeback_series', 'role'])['sv_pct']
    .mean()
    .round(4)
    .reset_index()
)
goalie_avg['series_type'] = goalie_avg['is_comeback_series'].map(
    {True: 'comeback_series', False: 'comparison_series'}
)

# Goalie changes: did trailing team change goalies?
goalie_changes = (
    series_goalies[series_goalies['is_trailing_goalie']]
    .groupby(['series_id', 'is_comeback_series'])['Player']
    .nunique()
    .reset_index()
    .rename(columns={'Player': 'unique_goalies_used'})
)
goalie_changes['made_change'] = goalie_changes['unique_goalies_used'] > 1

# ── 3. SEASON CONTEXT ────────────────────────────────────────────────────────
numeric_cols = ['Rk', 'PTS%', 'GF/G', 'GA/G', 'PP%', 'PK%', 'SRS']
for col in numeric_cols:
    if col in season.columns:
        season[col] = pd.to_numeric(season[col], errors='coerce')

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
season['series_id'] = season.apply(lambda r: TEAM_ROLES.get((r['team'], r['year']), (None, None))[0], axis=1)
season['role']      = season.apply(lambda r: TEAM_ROLES.get((r['team'], r['year']), (None, None))[1], axis=1)
teams = season[season['series_id'].notna()].copy()
teams['is_comeback_series'] = teams['role'].isin(['comeback', 'opponent'])

# Average regular-season stats for trailing teams (comeback) vs comparison trailing teams
trailing_avg = (
    teams[teams['role'].isin(['comeback', 'trailing'])]
    .groupby('role')[['PTS%', 'GF/G', 'GA/G', 'PP%', 'PK%', 'SRS']]
    .mean()
    .round(3)
)

# ── 4. PRINT COMPARATIVE SUMMARY ─────────────────────────────────────────────
print("=" * 65)
print("SECTION 1: GAME MOMENTUM — win % and goal differential by phase")
print("=" * 65)
print(momentum[['series_type', 'phase', 'win_pct', 'avg_goal_diff', 'ot_rate']].to_string(index=False))

print()
print("=" * 65)
print("SECTION 2A: GOALTENDING — avg SV% by team role and series type")
print("=" * 65)
print(goalie_avg[['series_type', 'role', 'sv_pct']].to_string(index=False))

print()
print("=" * 65)
print("SECTION 2B: GOALTENDING — did trailing team change goalies?")
print("=" * 65)
print(goalie_changes[['series_id', 'is_comeback_series', 'unique_goalies_used', 'made_change']].to_string(index=False))

print()
print("=" * 65)
print("SECTION 3: SEASON CONTEXT — trailing team profile (comeback vs comparison)")
print("=" * 65)
print(trailing_avg.to_string())

print()
print("=" * 65)
print("SECTION 4: COMBINED PROFILE — each series side by side")
print("=" * 65)

for sid in ['1942_tor_det', '1975_nyi_pit', '2010_phi_bos', '2014_lak_sjs',
            '2013_det_chi', '2014_col_min', '2019_car_wsh']:
    s_games   = games[games['series_id'] == sid]
    s_goalies = goalie_changes[goalie_changes['series_id'] == sid]
    s_season  = teams[teams['series_id'] == sid]

    is_comeback = s_games['is_comeback_series'].iloc[0] if len(s_games) else False
    label = 'COMEBACK' if is_comeback else 'COMPARISON'

    trailing_row = s_season[s_season['role'].isin(['comeback', 'trailing'])].iloc[0] if len(s_season) else None
    opponent_row = s_season[s_season['role'].isin(['opponent', 'leading'])].iloc[0] if len(s_season) else None

    g1_3_wins = s_games[s_games['phase'] == 'games_1_3']['comeback_team_won'].sum()
    g4_7_wins = s_games[s_games['phase'] == 'games_4_7']['comeback_team_won'].sum()
    g1_3_diff = s_games[s_games['phase'] == 'games_1_3']['score_differential'].mean()
    g4_7_diff = s_games[s_games['phase'] == 'games_4_7']['score_differential'].mean()

    goalie_change = s_goalies['made_change'].values[0] if len(s_goalies) else 'N/A'

    print(f"\n[{sid}]  {label}")
    if trailing_row is not None and opponent_row is not None:
        print(f"  Trailing: {trailing_row['team']:<28} PTS%={trailing_row['PTS%']:.3f}  SRS={trailing_row['SRS']:.2f}  PP%={trailing_row['PP%']:.1f}  PK%={trailing_row['PK%']:.1f}")
        print(f"  Leading:  {opponent_row['team']:<28} PTS%={opponent_row['PTS%']:.3f}  SRS={opponent_row['SRS']:.2f}  PP%={opponent_row['PP%']:.1f}  PK%={opponent_row['PK%']:.1f}")
    print(f"  Games 1-3: {g1_3_wins}-{3-int(g1_3_wins)} wins  avg goal diff {g1_3_diff:.2f}")
    print(f"  Games 4-7: {g4_7_wins}-{4-int(g4_7_wins)} wins  avg goal diff {g4_7_diff:.2f}")
    print(f"  Goalie change mid-series: {goalie_change}")
