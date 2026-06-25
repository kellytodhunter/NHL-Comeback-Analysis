import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

DATA_DIR  = Path(__file__).parent.parent / 'data' / 'processed'
OUT_DIR   = Path(__file__).parent
OUT_DIR.mkdir(exist_ok=True)

games   = pd.read_csv(DATA_DIR / 'game_logs.csv')
goalies = pd.read_csv(DATA_DIR / 'goalie_stats.csv')
season  = pd.read_csv(DATA_DIR / 'season_team_stats.csv')

# ── Shared prep ───────────────────────────────────────────────────────────────
games = games[games['date'].str.startswith('Game')].copy().reset_index(drop=True)

def get_scores(row):
    if row['road_team'] == row['comeback_team']:
        return row['road_score'], row['home_score']
    return row['home_score'], row['road_score']

games[['comeback_score', 'opponent_score']] = games.apply(
    lambda r: pd.Series(get_scores(r)), axis=1
)
games['comeback_team_won']  = games['comeback_score'] > games['opponent_score']
games['score_differential'] = games['comeback_score'] - games['opponent_score']
games['overtime']           = games['overtime'].fillna('').astype(str)
games['is_overtime']        = games['overtime'].str.strip() != ''
games['phase']              = games['game_num'].apply(lambda g: 'Games 1–3' if g <= 3 else 'Games 4–7')

COMEBACK_COLOR    = '#C8102E'  # red
COMPARISON_COLOR  = '#003087'  # navy
NEUTRAL_LIGHT     = '#F0F0F0'

SERIES_LABELS = {
    '1942_tor_det': '1942 TOR',
    '1975_nyi_pit': '1975 NYI',
    '2010_phi_bos': '2010 PHI',
    '2014_lak_sjs': '2014 LAK',
    '2013_det_chi': '2013 DET',
    '2014_col_min': '2014 MIN',
    '2019_car_wsh': '2019 CAR',
}

# ── CHART 1: Goal differential per game — games 1-3 vs 4-7 ───────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
fig.suptitle('Average Goal Differential by Phase\n(Trailing Team Perspective)',
             fontsize=14, fontweight='bold', y=1.02)

for ax, series_type, title, color in [
    (axes[0], True,  'Comeback Series', COMEBACK_COLOR),
    (axes[1], False, 'Comparison Series (Lost 0–4)', COMPARISON_COLOR),
]:
    subset = games[games['is_comeback_series'] == series_type]
    phase_diff = (
        subset.groupby(['series_id', 'phase'])['score_differential']
        .mean()
        .reset_index()
    )
    series_ids = sorted(phase_diff['series_id'].unique())
    x = np.arange(len(series_ids))
    width = 0.35

    early = phase_diff[phase_diff['phase'] == 'Games 1–3'].set_index('series_id')['score_differential']
    late  = phase_diff[phase_diff['phase'] == 'Games 4–7'].set_index('series_id')['score_differential']

    bars1 = ax.bar(x - width/2, [early.get(s, 0) for s in series_ids],
                   width, label='Games 1–3', color=color, alpha=0.5)
    bars2 = ax.bar(x + width/2, [late.get(s, 0) for s in series_ids],
                   width, label='Games 4–7', color=color, alpha=0.95)

    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.set_xticks(x)
    ax.set_xticklabels([SERIES_LABELS[s] for s in series_ids], fontsize=9)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_ylabel('Avg Goal Diff (trailing team)' if ax == axes[0] else '')
    ax.legend(fontsize=8)
    ax.set_ylim(-5, 6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(OUT_DIR / 'chart1_goal_differential.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved chart1_goal_differential.png")

# ── CHART 2: Cumulative goal differential across all 7 games ─────────────────
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle('Cumulative Goal Differential — All Four Comeback Series\n(Comeback team perspective: positive = ahead on goals)',
             fontsize=13, fontweight='bold')

comeback_series = ['1942_tor_det', '1975_nyi_pit', '2010_phi_bos', '2014_lak_sjs']
FULL_NAMES = {
    '1942_tor_det': '1942 Toronto Maple Leafs',
    '1975_nyi_pit': '1975 New York Islanders',
    '2010_phi_bos': '2010 Philadelphia Flyers',
    '2014_lak_sjs': '2014 Los Angeles Kings',
}

for ax, sid in zip(axes.flat, comeback_series):
    s = games[games['series_id'] == sid].sort_values('game_num').copy()
    s['cumulative_diff'] = s['score_differential'].cumsum()

    # Shade area under/over zero
    ax.fill_between(s['game_num'], s['cumulative_diff'], 0,
                    where=(s['cumulative_diff'] >= 0),
                    color=COMEBACK_COLOR, alpha=0.25, interpolate=True)
    ax.fill_between(s['game_num'], s['cumulative_diff'], 0,
                    where=(s['cumulative_diff'] < 0),
                    color='#555555', alpha=0.25, interpolate=True)

    ax.plot(s['game_num'], s['cumulative_diff'], color=COMEBACK_COLOR,
            linewidth=2.5, marker='o', markersize=7, zorder=3)

    # Label each point
    for _, row in s.iterrows():
        offset = 0.4 if row['cumulative_diff'] >= 0 else -0.7
        ax.text(row['game_num'], row['cumulative_diff'] + offset,
                f"{int(row['cumulative_diff']):+d}",
                ha='center', fontsize=8, fontweight='bold', color=COMEBACK_COLOR)

    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(3.5, color='black', linewidth=1, linestyle='--', alpha=0.5)
    ax.text(3.6, ax.get_ylim()[0] * 0.85 if ax.get_ylim()[0] < 0 else -1,
            '0–3\nhole', fontsize=7.5, color='black', alpha=0.6)

    ax.set_title(FULL_NAMES[sid], fontsize=10, fontweight='bold')
    ax.set_xlabel('Game number', fontsize=9)
    ax.set_ylabel('Cumulative goal differential', fontsize=9)
    ax.set_xticks(s['game_num'].tolist())
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(OUT_DIR / 'chart2_cumulative_goal_diff.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved chart2_cumulative_goal_diff.png")

# ── CHART 3: Opponent strength (SRS) — comeback vs comparison ────────────────
numeric_cols = ['Rk', 'PTS%', 'GF/G', 'GA/G', 'PP%', 'PK%', 'SRS']
for col in numeric_cols:
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

fig, ax = plt.subplots(figsize=(11, 5))
fig.suptitle('Regular-Season Strength (SRS) — Trailing Team vs Leading Team\nper Series',
             fontsize=13, fontweight='bold')

all_series = ['1942_tor_det', '1975_nyi_pit', '2010_phi_bos', '2014_lak_sjs',
              '2013_det_chi', '2014_col_min', '2019_car_wsh']
x = np.arange(len(all_series))
width = 0.35

trailing_srs = []
leading_srs  = []
for sid in all_series:
    s = teams[teams['series_id'] == sid]
    tr = s[s['role'].isin(['comeback', 'trailing'])]['SRS'].values
    ld = s[s['role'].isin(['opponent', 'leading'])]['SRS'].values
    trailing_srs.append(tr[0] if len(tr) else 0)
    leading_srs.append(ld[0] if len(ld) else 0)

is_comeback = [True, True, True, True, False, False, False]
trailing_colors = [COMEBACK_COLOR if c else COMPARISON_COLOR for c in is_comeback]

bars1 = ax.bar(x - width/2, trailing_srs, width, label='Trailing Team', color=trailing_colors, alpha=0.9)
bars2 = ax.bar(x + width/2, leading_srs,  width, label='Leading Team',  color='#888888', alpha=0.7)

ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
ax.set_xticks(x)
ax.set_xticklabels([SERIES_LABELS[s] for s in all_series], fontsize=9)
ax.set_ylabel('Simple Rating System (SRS)', fontsize=10)
ax.set_xlabel('← Comeback Series  |  Comparison Series →', fontsize=9, labelpad=8)

# Divider line between comeback and comparison
ax.axvline(3.5, color='black', linewidth=1.2, linestyle=':')

red_patch  = mpatches.Patch(color=COMEBACK_COLOR,   label='Trailing — Comeback Series')
blue_patch = mpatches.Patch(color=COMPARISON_COLOR, label='Trailing — Comparison Series')
grey_patch = mpatches.Patch(color='#888888',         label='Leading Team')
ax.legend(handles=[red_patch, blue_patch, grey_patch], fontsize=9)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(OUT_DIR / 'chart3_srs_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved chart3_srs_comparison.png")

# ── CHART 4: Cumulative series score — game by game for each comeback ─────────
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle('Series Score Progression — All Four Comeback Teams\n(Cumulative wins: trailing team vs opponent)',
             fontsize=13, fontweight='bold')

comeback_series = ['1942_tor_det', '1975_nyi_pit', '2010_phi_bos', '2014_lak_sjs']
FULL_NAMES = {
    '1942_tor_det': '1942 Toronto Maple Leafs',
    '1975_nyi_pit': '1975 New York Islanders',
    '2010_phi_bos': '2010 Philadelphia Flyers',
    '2014_lak_sjs': '2014 Los Angeles Kings',
}

for ax, sid in zip(axes.flat, comeback_series):
    s = games[games['series_id'] == sid].sort_values('game_num')
    s = s.copy()
    s['cb_wins_cum']  = s['comeback_team_won'].cumsum()
    s['opp_wins_cum'] = (~s['comeback_team_won']).cumsum()

    ax.plot(s['game_num'], s['opp_wins_cum'], color='#888888', linewidth=2.5,
            marker='o', markersize=6, label='Opponent wins')
    ax.plot(s['game_num'], s['cb_wins_cum'],  color=COMEBACK_COLOR, linewidth=2.5,
            marker='o', markersize=6, label='Comeback team wins')

    # Mark the 0-3 point
    ax.axvline(3.5, color='black', linewidth=1, linestyle='--', alpha=0.5)
    ax.text(3.6, 0.15, '0–3\nhole', fontsize=7.5, color='black', alpha=0.6)

    ax.set_title(FULL_NAMES[sid], fontsize=10, fontweight='bold')
    ax.set_xlabel('Game number', fontsize=9)
    ax.set_ylabel('Cumulative wins', fontsize=9)
    ax.set_xticks(s['game_num'].tolist())
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.set_ylim(-0.2, 4.5)
    ax.legend(fontsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig(OUT_DIR / 'chart4_series_progression.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved chart4_series_progression.png")

print("\nAll charts saved to visualizations/")
