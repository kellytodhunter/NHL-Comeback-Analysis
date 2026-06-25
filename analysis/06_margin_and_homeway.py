import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'
OUT_DIR  = Path(__file__).parent.parent / 'visualizations'

games = pd.read_csv(DATA_DIR / 'game_logs.csv')
games = games[games['date'].str.startswith('Game')].copy().reset_index(drop=True)

# ── Comeback team perspective ─────────────────────────────────────────────────
def get_scores(row):
    if row['road_team'] == row['comeback_team']:
        return row['road_score'], row['home_score']
    return row['home_score'], row['road_score']

games[['comeback_score', 'opponent_score']] = games.apply(
    lambda r: pd.Series(get_scores(r)), axis=1
)
games['comeback_team_won']  = games['comeback_score'] > games['opponent_score']
games['score_differential'] = games['comeback_score'] - games['opponent_score']
games['abs_margin']         = games['score_differential'].abs()
games['overtime']           = games['overtime'].fillna('').astype(str)
games['is_overtime']        = games['overtime'].str.strip() != ''
games['phase']              = games['game_num'].apply(lambda g: 'Games 1–3' if g <= 3 else 'Games 4–7')

# Win type: blowout (3+ goals), comfortable (2 goals), close (1 goal or OT)
def win_type(row):
    if not row['comeback_team_won']:
        return None
    if row['is_overtime']:
        return 'OT win'
    if row['score_differential'] == 1:
        return '1-goal win'
    if row['score_differential'] == 2:
        return '2-goal win'
    return 'Blowout (3+)'

games['win_type'] = games.apply(win_type, axis=1)

# ── Home/away from comeback team's perspective ────────────────────────────────
games['comeback_is_home'] = games['home_team'] == games['comeback_team']
games['venue'] = games['comeback_is_home'].map({True: 'Home', False: 'Away'})

SERIES_LABELS = {
    '1942_tor_det': '1942 TOR',
    '1975_nyi_pit': '1975 NYI',
    '2010_phi_bos': '2010 PHI',
    '2014_lak_sjs': '2014 LAK',
    '2013_det_chi': '2013 DET',
    '2014_col_min': '2014 MIN',
    '2019_car_wsh': '2019 CAR',
}
COMEBACK_COLOR   = '#C8102E'
COMPARISON_COLOR = '#003087'

# ── ANALYSIS 1: Win margin distribution ──────────────────────────────────────
print("=" * 65)
print("SECTION 1: WIN MARGIN DISTRIBUTION")
print("=" * 65)

wins = games[games['comeback_team_won']].copy()
margin_summary = (
    wins.groupby(['is_comeback_series', 'phase', 'win_type'])
    .size()
    .reset_index(name='count')
)
print(margin_summary.to_string(index=False))

print("\n--- Avg margin of victory (wins only) by phase ---")
avg_margin = (
    wins.groupby(['is_comeback_series', 'phase'])['score_differential']
    .mean().round(2).reset_index()
)
avg_margin['series_type'] = avg_margin['is_comeback_series'].map(
    {True: 'comeback', False: 'comparison'}
)
print(avg_margin[['series_type', 'phase', 'score_differential']].to_string(index=False))

print("\n--- Avg margin of defeat (losses only) by phase ---")
losses = games[~games['comeback_team_won']].copy()
avg_loss = (
    losses.groupby(['is_comeback_series', 'phase'])['score_differential']
    .mean().round(2).reset_index()
)
avg_loss['series_type'] = avg_loss['is_comeback_series'].map(
    {True: 'comeback', False: 'comparison'}
)
print(avg_loss[['series_type', 'phase', 'score_differential']].to_string(index=False))

# ── ANALYSIS 2: Home vs away record ──────────────────────────────────────────
print("\n" + "=" * 65)
print("SECTION 2: HOME VS AWAY RECORD (comeback team perspective)")
print("=" * 65)

venue_record = (
    games.groupby(['series_id', 'is_comeback_series', 'venue'])
    .agg(wins=('comeback_team_won', 'sum'), games=('comeback_team_won', 'count'))
    .reset_index()
)
venue_record['losses']  = venue_record['games'] - venue_record['wins']
venue_record['win_pct'] = (venue_record['wins'] / venue_record['games']).round(3)
venue_record['label']   = venue_record['series_id'].map(SERIES_LABELS)

print(venue_record[['label', 'is_comeback_series', 'venue', 'wins', 'losses', 'win_pct']].to_string(index=False))

print("\n--- Avg by series type and venue ---")
venue_avg = (
    games.groupby(['is_comeback_series', 'venue'])
    .agg(win_pct=('comeback_team_won', 'mean'),
         avg_diff=('score_differential', 'mean'))
    .round(3).reset_index()
)
venue_avg['series_type'] = venue_avg['is_comeback_series'].map(
    {True: 'comeback', False: 'comparison'}
)
print(venue_avg[['series_type', 'venue', 'win_pct', 'avg_diff']].to_string(index=False))

print("\n--- Phase + venue breakdown for comeback series ---")
phase_venue = (
    games[games['is_comeback_series']]
    .groupby(['phase', 'venue'])
    .agg(wins=('comeback_team_won', 'sum'), games=('comeback_team_won', 'count'))
    .reset_index()
)
phase_venue['win_pct'] = (phase_venue['wins'] / phase_venue['games']).round(3)
print(phase_venue.to_string(index=False))

# ── CHART A: Score differential per game, all comeback series ─────────────────
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle('Score Differential Per Game — All Four Comeback Series\n(positive = comeback team winning that game)',
             fontsize=13, fontweight='bold')

comeback_ids = ['1942_tor_det', '1975_nyi_pit', '2010_phi_bos', '2014_lak_sjs']
FULL_NAMES = {
    '1942_tor_det': '1942 Toronto Maple Leafs',
    '1975_nyi_pit': '1975 New York Islanders',
    '2010_phi_bos': '2010 Philadelphia Flyers',
    '2014_lak_sjs': '2014 Los Angeles Kings',
}

for ax, sid in zip(axes.flat, comeback_ids):
    s = games[games['series_id'] == sid].sort_values('game_num').copy()

    colors = [COMEBACK_COLOR if d > 0 else '#555555' for d in s['score_differential']]
    bars = ax.bar(s['game_num'], s['score_differential'], color=colors, edgecolor='white', linewidth=0.5)

    # Mark OT games
    for _, row in s[s['is_overtime']].iterrows():
        ax.text(row['game_num'], row['score_differential'] + (0.15 if row['score_differential'] >= 0 else -0.35),
                'OT', ha='center', fontsize=7, color='black')

    # Mark home vs away
    for _, row in s.iterrows():
        label = 'H' if row['comeback_is_home'] else 'A'
        y_pos = -3.8
        ax.text(row['game_num'], y_pos, label, ha='center', fontsize=7.5,
                color='#333333', fontweight='bold')

    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(3.5, color='black', linewidth=1, linestyle='--', alpha=0.5)
    ax.text(3.65, ax.get_ylim()[1] * 0.85 if ax.get_ylim()[1] > 0 else 3,
            '0–3\nhole', fontsize=7.5, color='black', alpha=0.6)

    ax.set_title(FULL_NAMES[sid], fontsize=10, fontweight='bold')
    ax.set_xlabel('Game number  (H=home  A=away for comeback team)', fontsize=8)
    ax.set_ylabel('Goal differential')
    ax.set_xticks(s['game_num'].tolist())
    ax.set_ylim(-5, 8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()
path = OUT_DIR / 'chart5_margin_per_game.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
plt.close()
print(f"\nSaved {path.name}")

# ── CHART B: Home vs away win % — comeback vs comparison ─────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
fig.suptitle('Home vs Away Win Rate — Comeback Team Perspective\nComeback Series vs Comparison Series',
             fontsize=13, fontweight='bold')

x      = np.arange(2)
width  = 0.35
venues = ['Home', 'Away']

cb   = venue_avg[venue_avg['is_comeback_series'] == True].set_index('venue')['win_pct']
comp = venue_avg[venue_avg['is_comeback_series'] == False].set_index('venue')['win_pct']

ax.bar(x - width/2, [cb.get(v, 0) for v in venues],  width,
       label='Comeback Series',   color=COMEBACK_COLOR,   alpha=0.9)
ax.bar(x + width/2, [comp.get(v, 0) for v in venues], width,
       label='Comparison Series', color=COMPARISON_COLOR, alpha=0.9)

for i, v in enumerate(venues):
    ax.text(i - width/2, cb.get(v, 0) + 0.025,   f"{cb.get(v, 0):.0%}",
            ha='center', fontsize=11, fontweight='bold', color=COMEBACK_COLOR)
    ax.text(i + width/2, comp.get(v, 0) + 0.025,  f"{comp.get(v, 0):.0%}",
            ha='center', fontsize=11, fontweight='bold', color=COMPARISON_COLOR)

ax.set_xticks(x)
ax.set_xticklabels(venues, fontsize=12)
ax.set_ylabel('Win rate (trailing team)', fontsize=10)
ax.set_ylim(0, 1.1)
ax.axhline(0.5, color='grey', linewidth=0.8, linestyle='--', alpha=0.5)
ax.legend(fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
path = OUT_DIR / 'chart6_home_away_winrate.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved {path.name}")

# ── CHART C: Win type breakdown — comeback series games 4-7 ──────────────────
fig, ax = plt.subplots(figsize=(8, 5))
fig.suptitle('How Comeback Teams Won — Games 4–7\nMargin of victory breakdown',
             fontsize=13, fontweight='bold')

cb_wins_late = wins[
    (wins['is_comeback_series'] == True) & (wins['phase'] == 'Games 4–7')
]
type_counts = cb_wins_late['win_type'].value_counts()
order = ['OT win', '1-goal win', '2-goal win', 'Blowout (3+)']
order = [o for o in order if o in type_counts.index]

colors_bar = ['#888888', '#E8A090', '#C8102E', '#7B0020'][:len(order)]
bars = ax.bar(order, [type_counts[o] for o in order], color=colors_bar, edgecolor='white')

for bar, label in zip(bars, order):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
            str(int(bar.get_height())), ha='center', fontsize=12, fontweight='bold')

ax.set_ylabel('Number of games', fontsize=10)
ax.set_ylim(0, max(type_counts) + 1.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
path = OUT_DIR / 'chart7_win_type.png'
plt.savefig(path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved {path.name}")
