import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'

goalies = pd.read_csv(DATA_DIR / 'goalie_stats.csv')

# ── Split into series stats vs regular season stats ───────────────────────────
# Hockey Reference includes two table types per series page:
#   series_goalies_stats_* — stats for this playoff series only
#   goalies-*              — full regular season stats
series_goalies = goalies[goalies['table_id'].str.startswith('series_goalies')].copy()
reg_season_goalies = goalies[goalies['table_id'].str.startswith('goalies-')].copy()

# ── Clean up series goalie stats ──────────────────────────────────────────────
# Keep only rows with an actual player name and games played
series_goalies = series_goalies[series_goalies['Player'].notna()].copy()
series_goalies = series_goalies[series_goalies['GP'] > 0].copy()
series_goalies = series_goalies.reset_index(drop=True)

# Flag whether each goalie played for the comeback team or the opponent
series_goalies['is_comeback_goalie'] = (
    series_goalies['team'] == series_goalies['comeback_team'].str[:3].str.upper()
)

# ── Save % by team role (comeback vs opponent) ────────────────────────────────
sv_summary = (
    series_goalies.groupby(['series_id', 'is_comeback_series', 'is_comeback_goalie'])
    .agg(
        goalies_used=('Player', 'count'),
        combined_sv_pct=('SV%', 'mean'),
        total_ga=('GA', 'sum'),
        total_sa=('SA', 'sum'),
    )
    .reset_index()
)
# Recalculate SV% from raw totals for accuracy
sv_summary['true_sv_pct'] = (
    (sv_summary['total_sa'] - sv_summary['total_ga']) / sv_summary['total_sa']
).round(4)

sv_summary['role'] = sv_summary['is_comeback_goalie'].map(
    {True: 'comeback_team', False: 'opponent'}
)

# ── Goalie changes: teams that used more than one goalie in series ─────────────
goalie_changes = (
    series_goalies.groupby(['series_id', 'is_comeback_series', 'is_comeback_goalie'])['Player']
    .apply(list)
    .reset_index()
)
goalie_changes['num_goalies'] = goalie_changes['Player'].apply(len)
goalie_changes['had_change'] = goalie_changes['num_goalies'] > 1

# ── Regular season SV% vs playoff SV% for starting goalies ───────────────────
# Define starter as the goalie with most GP in the series
starters = (
    series_goalies.sort_values('GP', ascending=False)
    .groupby(['series_id', 'is_comeback_goalie'])
    .first()
    .reset_index()
)[['series_id', 'is_comeback_series', 'is_comeback_goalie', 'Player', 'GP', 'SV%', 'team']]

starters = starters.rename(columns={'SV%': 'playoff_sv_pct', 'Player': 'starter'})

# Match to regular season stats by player name + year
reg_season_goalies['year'] = reg_season_goalies['year'].astype(int)
series_goalies['year'] = series_goalies['year'].astype(int)

reg_sv = reg_season_goalies[['Player', 'year', 'SV%']].rename(
    columns={'SV%': 'reg_season_sv_pct'}
)

# Merge year back onto starters via series_id
year_map = series_goalies[['series_id', 'year']].drop_duplicates()
starters = starters.merge(year_map, on='series_id', how='left')
starters = starters.merge(reg_sv, left_on=['starter', 'year'], right_on=['Player', 'year'], how='left')
starters = starters.drop(columns=['Player'])
starters['sv_pct_change'] = (starters['playoff_sv_pct'] - starters['reg_season_sv_pct']).round(4)

# ── Print results ─────────────────────────────────────────────────────────────
print("=== All goalies used per series ===")
print(series_goalies[['series_id', 'is_comeback_series', 'team', 'Player', 'GP', 'GA', 'SA', 'SV%', 'DEC']].to_string(index=False))

print("\n=== SV% by role: comeback team vs opponent ===")
print(sv_summary[['series_id', 'is_comeback_series', 'role', 'goalies_used', 'true_sv_pct', 'total_ga', 'total_sa']].to_string(index=False))

print("\n=== Goalie changes mid-series ===")
print(goalie_changes[['series_id', 'is_comeback_series', 'is_comeback_goalie', 'Player', 'num_goalies', 'had_change']].to_string(index=False))

print("\n=== Starter: regular season SV% vs playoff SV% ===")
print(starters[['series_id', 'is_comeback_series', 'is_comeback_goalie', 'starter', 'reg_season_sv_pct', 'playoff_sv_pct', 'sv_pct_change']].to_string(index=False))
