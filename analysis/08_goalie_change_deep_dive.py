import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / 'data' / 'raw'
OUT_DIR = Path(__file__).parent.parent / 'visualizations'

with open(RAW_DIR / 'game_goalie_stats.json') as f:
    data = json.load(f)

g = pd.DataFrame(data)
g['goals_against'] = pd.to_numeric(g['goals_against'], errors='coerce')
g['shots_against'] = pd.to_numeric(g['shots_against'], errors='coerce')
g['save_pct']      = pd.to_numeric(g['save_pct'],      errors='coerce')
g['phase']         = g['game_num'].apply(lambda n: 'Games 1–3' if n <= 3 else 'Games 4–7')

# Identify the starter per game as the goalie with the longest TOI
# TOI format is "MM:SS" — convert to seconds for comparison
def toi_to_seconds(toi_str):
    try:
        m, s = toi_str.strip().split(':')
        return int(m) * 60 + int(s)
    except Exception:
        return 0

g['toi_seconds'] = g['time_on_ice'].apply(toi_to_seconds)

# Mark starter: the goalie with most TOI per team per game
g['is_starter'] = g.groupby(['series_id', 'game_num', 'team'])['toi_seconds'] \
                    .transform(lambda x: x == x.max())

# ── Identify goalie changes ───────────────────────────────────────────────────
# For each comeback team, find the primary starter (most games started)
# and the replacement (appeared after game 3)
COMEBACK_ABBRS = {
    '1942_tor_det': 'TOR',
    '1975_nyi_pit': 'NYI',
    '2010_phi_bos': 'PHI',
    '2014_lak_sjs': 'LAK',
}

cb_goalies = g[g['is_comeback_team'] & g['is_starter']].copy()

print("=" * 65)
print("SECTION 1: COMEBACK TEAM GOALIE GAME-BY-GAME")
print("=" * 65)
for sid, abbr in COMEBACK_ABBRS.items():
    s = cb_goalies[cb_goalies['series_id'] == sid].sort_values('game_num')
    print(f"\n{sid}")
    print(s[['game_num', 'player', 'decision', 'goals_against',
              'shots_against', 'save_pct', 'phase']].to_string(index=False))

# ── Pre/post change SV% for series with a goalie change ──────────────────────
print("\n\n" + "=" * 65)
print("SECTION 2: PRE vs POST GOALIE CHANGE — 1975, 2010, 2014")
print("=" * 65)

# For each series define original starter and replacement
CHANGES = {
    '1975_nyi_pit': {'original': 'Billy Smith',    'replacement': 'Glenn Resch'},
    '2010_phi_bos': {'original': 'Brian Boucher',  'replacement': 'Michael Leighton'},
    '2014_lak_sjs': {'original': 'Jonathan Quick', 'replacement': None},  # no change
}

for sid, change in CHANGES.items():
    print(f"\n--- {sid} ---")
    s = g[(g['series_id'] == sid) & g['is_comeback_team']].copy()

    orig  = change['original']
    repl  = change['replacement']

    orig_games = s[s['player'] == orig].sort_values('game_num')
    repl_games = s[s['player'] == repl].sort_values('game_num') if repl else pd.DataFrame()

    if not orig_games.empty:
        orig_sv  = orig_games['save_pct'].mean()
        orig_ga  = orig_games['goals_against'].sum()
        orig_gms = len(orig_games)
        print(f"  {orig:<20} {orig_gms} games  GA={int(orig_ga)}  avg SV%={orig_sv:.3f}" if pd.notna(orig_sv) else
              f"  {orig:<20} {orig_gms} games  GA={int(orig_ga)}  SV% not recorded (pre-modern era)")

    if not repl_games.empty:
        repl_sv  = repl_games['save_pct'].mean()
        repl_ga  = repl_games['goals_against'].sum()
        repl_gms = len(repl_games)
        print(f"  {repl:<20} {repl_gms} games  GA={int(repl_ga)}  avg SV%={repl_sv:.3f}")

    if change['replacement'] is None:
        print(f"  No goalie change — Quick started all 7 games")

# ── Opponent goaltending: did they decline after game 3? ─────────────────────
print("\n\n" + "=" * 65)
print("SECTION 3: OPPONENT GOALTENDING — performance before and after 0-3")
print("=" * 65)

opp_goalies = g[~g['is_comeback_team'] & g['is_starter']].copy()

for sid in COMEBACK_ABBRS.keys():
    s = opp_goalies[opp_goalies['series_id'] == sid].sort_values('game_num')
    print(f"\n{sid}")
    print(s[['game_num', 'player', 'decision', 'goals_against',
              'save_pct', 'phase']].to_string(index=False))

print("\n--- Avg opponent GA per game: games 1-3 vs 4-7 ---")
opp_phase = (
    opp_goalies.groupby(['series_id', 'phase'])
    .agg(avg_ga=('goals_against', 'mean'), avg_sv=('save_pct', 'mean'))
    .round(3).reset_index()
)
print(opp_phase.to_string(index=False))

# ── CHART A: Comeback team goalie SV% game by game (modern series only) ──────
COMEBACK_COLOR = '#C8102E'

modern_series = ['1975_nyi_pit', '2010_phi_bos', '2014_lak_sjs']
FULL_NAMES = {
    '1975_nyi_pit': '1975 NYI — Smith → Resch',
    '2010_phi_bos': '2010 PHI — Boucher → Leighton',
    '2014_lak_sjs': '2014 LAK — Quick (no change)',
}
GOALIE_COLORS = {
    '1975_nyi_pit': {'Billy Smith': '#888888',    'Glenn Resch': COMEBACK_COLOR},
    '2010_phi_bos': {'Brian Boucher': '#888888',  'Michael Leighton': COMEBACK_COLOR,
                     'Johan Backlund': '#CCCCCC'},
    '2014_lak_sjs': {'Jonathan Quick': COMEBACK_COLOR, 'Martin Jones': '#CCCCCC'},
}

with plt.style.context('dark_background'):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True, facecolor='#111111')
    for ax in axes:
        ax.set_facecolor('#111111')
    fig.suptitle('Comeback Team Goalie SV% Per Game\n(grey = original starter, red = replacement)',
                 fontsize=13, fontweight='bold', color='white')

    for ax, sid in zip(axes, modern_series):
        s = g[(g['series_id'] == sid) & g['is_comeback_team'] & g['is_starter']].sort_values('game_num')
        s = s[s['save_pct'].notna()]

        color_map = GOALIE_COLORS.get(sid, {})
        colors = [color_map.get(p, '#AAAAAA') for p in s['player']]

        bars = ax.bar(s['game_num'], s['save_pct'], color=colors, edgecolor='#333333', linewidth=0.5)

        for _, row in s.iterrows():
            ax.text(row['game_num'], row['save_pct'] + 0.003,
                    f"{row['save_pct']:.3f}", ha='center', fontsize=7.5, fontweight='bold', color='white')

        ax.axhline(0.900, color='#888888', linewidth=0.8, linestyle='--', alpha=0.7)
        ax.text(7.3, 0.901, '.900', fontsize=7.5, color='#888888', alpha=0.8)
        ax.axvline(3.5, color='#888888', linewidth=1, linestyle='--', alpha=0.5)

        ax.set_title(FULL_NAMES[sid], fontsize=9, fontweight='bold', color='white')
        ax.set_xlabel('Game number', fontsize=9, color='white')
        ax.set_ylabel('SV%' if ax == axes[0] else '', color='white')
        ax.set_xticks(s['game_num'].tolist())
        ax.set_ylim(0.82, 1.01)
        ax.tick_params(colors='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#555555')
        ax.spines['bottom'].set_color('#555555')

        handles = [mpatches.Patch(color=c, label=p)
                   for p, c in color_map.items() if p in s['player'].values]
        ax.legend(handles=handles, fontsize=7.5, loc='lower right',
                  facecolor='#222222', edgecolor='#555555', labelcolor='white')

    plt.tight_layout()
    path = OUT_DIR / 'chart11_goalie_sv_per_game.png'
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#111111')
    plt.close()
print(f'\nSaved {path.name}')

# ── CHART B: Opponent goalie GA per game — before and after ──────────────────
OPP_NAMES = {
    '1942_tor_det': 'Johnny Mowers (DET)',
    '1975_nyi_pit': 'Gary Inness (PIT)',
    '2010_phi_bos': 'Tuukka Rask (BOS)',
    '2014_lak_sjs': 'Antti Niemi / Stalock (SJS)',
}

with plt.style.context('dark_background'):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), facecolor='#111111')
    for ax in axes.flat:
        ax.set_facecolor('#111111')
    fig.suptitle('Opponent Goalie Goals Allowed Per Game\n(did they decline after going up 3–0?)',
                 fontsize=13, fontweight='bold', color='white')

    for ax, sid in zip(axes.flat, COMEBACK_ABBRS.keys()):
        s = opp_goalies[opp_goalies['series_id'] == sid].sort_values('game_num')
        colors = ['#AAAAAA' if g <= 3 else '#555555' for g in s['game_num']]
        ax.bar(s['game_num'], s['goals_against'], color=colors, edgecolor='#333333')

        for _, row in s.iterrows():
            name_short = row['player'].split()[-1]
            ax.text(row['game_num'], row['goals_against'] + 0.05,
                    name_short, ha='center', fontsize=7, rotation=45, color='white')

        ax.axvline(3.5, color='#888888', linewidth=1, linestyle='--', alpha=0.5)
        ax.set_title(f"{sid.upper()} — {OPP_NAMES[sid]}", fontsize=9, fontweight='bold', color='white')
        ax.set_xlabel('Game number', fontsize=9, color='white')
        ax.set_ylabel('Goals allowed', color='white')
        ax.set_xticks(s['game_num'].tolist())
        ax.set_ylim(0, 8)
        ax.tick_params(colors='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#555555')
        ax.spines['bottom'].set_color('#555555')

        light = mpatches.Patch(color='#AAAAAA', label='Games 1–3 (leading 3–0)')
        dark  = mpatches.Patch(color='#555555', label='Games 4–7 (defending lead)')
        ax.legend(handles=[light, dark], fontsize=7.5,
                  facecolor='#222222', edgecolor='#555555', labelcolor='white')

    plt.tight_layout()
    path = OUT_DIR / 'chart12_opponent_goalie_ga.png'
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#111111')
    plt.close()
print(f'Saved {path.name}')
