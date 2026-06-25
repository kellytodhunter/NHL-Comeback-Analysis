import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'

games = pd.read_csv(DATA_DIR / 'game_logs.csv')

# ── Filter to playoff games only ─────────────────────────────────────────────
games = games[games['date'].str.startswith('Game')].copy()
games = games.reset_index(drop=True)

# ── Comeback team perspective columns ────────────────────────────────────────
def get_scores(row):
    if row['road_team'] == row['comeback_team']:
        return row['road_score'], row['home_score']
    else:
        return row['home_score'], row['road_score']

games[['comeback_score', 'opponent_score']] = games.apply(
    lambda row: pd.Series(get_scores(row)), axis=1
)

games['comeback_team_won'] = games['comeback_score'] > games['opponent_score']
games['score_differential'] = games['comeback_score'] - games['opponent_score']
games['overtime'] = games['overtime'].fillna('').astype(str)
games['is_overtime'] = games['overtime'].str.strip() != ''

# ── Cumulative series record ──────────────────────────────────────────────────
games['comeback_wins_cumulative'] = games.groupby('series_id')['comeback_team_won'].cumsum()
games['opponent_wins_cumulative'] = games.groupby('series_id')['comeback_team_won'].transform(
    lambda x: (~x).cumsum()
)

# ── Summary: win/loss record in games 1-3 vs games 4-7 ───────────────────────
games['phase'] = games['game_num'].apply(lambda g: 'games_1_3' if g <= 3 else 'games_4_7')

phase_summary = (
    games.groupby(['series_id', 'is_comeback_series', 'phase'])['comeback_team_won']
    .agg(wins='sum', games='count')
    .reset_index()
)
phase_summary['losses'] = phase_summary['games'] - phase_summary['wins']
phase_summary['win_pct'] = (phase_summary['wins'] / phase_summary['games']).round(3)

# ── Score differential summary ───────────────────────────────────────────────
diff_summary = (
    games.groupby(['series_id', 'is_comeback_series', 'phase'])['score_differential']
    .mean()
    .round(2)
    .reset_index()
    .rename(columns={'score_differential': 'avg_goal_diff'})
)

# ── Overtime summary ─────────────────────────────────────────────────────────
ot_summary = (
    games.groupby(['series_id', 'is_comeback_series'])['is_overtime']
    .agg(ot_games='sum', total_games='count')
    .reset_index()
)
ot_summary['ot_rate'] = (ot_summary['ot_games'] / ot_summary['total_games']).round(3)

# ── Print results ─────────────────────────────────────────────────────────────
print("=== Game-by-game scores (comeback team perspective) ===")
print(games[['series_id', 'game_num', 'comeback_score', 'opponent_score',
             'comeback_team_won', 'score_differential', 'is_overtime',
             'comeback_wins_cumulative', 'opponent_wins_cumulative']].to_string())

print("\n=== Win % by phase (games 1-3 vs 4-7) ===")
print(phase_summary.to_string(index=False))

print("\n=== Avg goal differential by phase ===")
print(diff_summary.to_string(index=False))

print("\n=== Overtime frequency per series ===")
print(ot_summary.to_string(index=False))
