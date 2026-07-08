import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data' / 'processed'
RAW_DIR  = Path(__file__).parent.parent / 'data' / 'raw'
OUT_DIR  = Path(__file__).parent.parent / 'visualizations'

# ── Load and merge ────────────────────────────────────────────────────────────
with open(RAW_DIR / 'game_special_teams.json') as f:
    st_raw = json.load(f)

st = pd.DataFrame(st_raw)
st['phase'] = st['game_num'].apply(lambda g: 'Games 1–3' if g <= 3 else 'Games 4–7')

# Load game logs for is_comeback_series and score context
games = pd.read_csv(DATA_DIR / 'game_logs.csv')
games = games[games['date'].str.startswith('Game')].copy().reset_index(drop=True)

meta = games[['series_id', 'game_num', 'is_comeback_series']].drop_duplicates()
st = st.merge(meta, on=['series_id', 'game_num'], how='left')

# ── Compute PP% per game ──────────────────────────────────────────────────────
# Avoid divide-by-zero: 0 PPO → PP% is NaN
st['comeback_pp_pct'] = st.apply(
    lambda r: r['comeback_pp_goals'] / r['comeback_ppo']
    if r['comeback_ppo'] and r['comeback_ppo'] > 0 else None, axis=1
)
st['opponent_pp_pct'] = st.apply(
    lambda r: r['opponent_pp_goals'] / r['opponent_ppo']
    if r['opponent_ppo'] and r['opponent_ppo'] > 0 else None, axis=1
)

# PP differential: comeback team minus opponent (positive = comeback team better)
st['pp_goals_diff'] = st['comeback_pp_goals'] - st['opponent_pp_goals']
st['ppo_diff']      = st['comeback_ppo']      - st['opponent_ppo']
st['pim_diff']      = st['comeback_pim']       - st['opponent_pim']

# ── ANALYSIS 1: Series-level PP summary by phase ──────────────────────────────
print("=" * 65)
print("SECTION 1: SPECIAL TEAMS BY PHASE — comeback series")
print("=" * 65)

cb_phase = (
    st[st['is_comeback_series'] == True]
    .groupby(['series_id', 'phase'])
    .agg(
        cb_pp_goals=('comeback_pp_goals', 'sum'),
        cb_ppo=('comeback_ppo', 'sum'),
        opp_pp_goals=('opponent_pp_goals', 'sum'),
        opp_ppo=('opponent_ppo', 'sum'),
        cb_pim=('comeback_pim', 'sum'),
        opp_pim=('opponent_pim', 'sum'),
    )
    .reset_index()
)
cb_phase['cb_pp_pct']  = (cb_phase['cb_pp_goals']  / cb_phase['cb_ppo'].replace(0, None)).round(3)
cb_phase['opp_pp_pct'] = (cb_phase['opp_pp_goals'] / cb_phase['opp_ppo'].replace(0, None)).round(3)
cb_phase['pp_goals_advantage'] = cb_phase['cb_pp_goals'] - cb_phase['opp_pp_goals']

print(cb_phase[['series_id', 'phase', 'cb_pp_goals', 'cb_ppo', 'cb_pp_pct',
                 'opp_pp_goals', 'opp_ppo', 'opp_pp_pct', 'pp_goals_advantage']].to_string(index=False))

print("\n\n--- Penalty minutes: were comeback teams more or less disciplined? ---")
pim = (
    st[st['is_comeback_series'] == True]
    .groupby(['series_id', 'phase'])
    .agg(cb_pim=('comeback_pim', 'sum'), opp_pim=('opponent_pim', 'sum'))
    .reset_index()
)
pim['pim_diff'] = pim['cb_pim'] - pim['opp_pim']
print(pim.to_string(index=False))

print("\n\n=== SECTION 2: AGGREGATE — comeback vs comparison series ===")
agg = (
    st.groupby(['is_comeback_series', 'phase'])
    .agg(
        cb_pp_goals=('comeback_pp_goals', 'sum'),
        cb_ppo=('comeback_ppo', 'sum'),
        opp_pp_goals=('opponent_pp_goals', 'sum'),
        opp_ppo=('opponent_ppo', 'sum'),
    )
    .reset_index()
)
agg['cb_pp_pct']  = (agg['cb_pp_goals']  / agg['cb_ppo'].replace(0, None)).round(3)
agg['opp_pp_pct'] = (agg['opp_pp_goals'] / agg['opp_ppo'].replace(0, None)).round(3)
agg['net_pp_goals'] = agg['cb_pp_goals'] - agg['opp_pp_goals']
agg['series_type'] = agg['is_comeback_series'].map({True: 'comeback', False: 'comparison'})
print(agg[['series_type', 'phase', 'cb_pp_pct', 'opp_pp_pct', 'net_pp_goals', 'cb_ppo', 'opp_ppo']].to_string(index=False))

# ── CHART A: PP goals per game — comeback team vs opponent, by phase ──────────
COMEBACK_COLOR   = '#C8102E'
COMPARISON_COLOR = '#003087'

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True, facecolor='#111111')
for ax in axes:
    ax.set_facecolor('#111111')
fig.suptitle('Power Play Goals Per Game — Trailing Team vs Opponent\nby Phase and Series Type',
             fontsize=13, fontweight='bold', color='white')

for ax, is_cb, title in [
    (axes[0], True,  'Comeback Series'),
    (axes[1], False, 'Comparison Series'),
]:
    subset = st[st['is_comeback_series'] == is_cb]
    phase_st = (
        subset.groupby('phase')
        .agg(cb_ppg_per_game=('comeback_pp_goals', 'mean'),
             opp_ppg_per_game=('opponent_pp_goals', 'mean'))
        .reset_index()
    )
    x      = np.arange(len(phase_st))
    width  = 0.35
    color  = COMEBACK_COLOR if is_cb else COMPARISON_COLOR

    ax.bar(x - width/2, phase_st['cb_ppg_per_game'],  width,
           label='Trailing team', color=color, alpha=0.9)
    ax.bar(x + width/2, phase_st['opp_ppg_per_game'], width,
           label='Opponent',      color='#888888', alpha=0.7)

    for i, row in phase_st.iterrows():
        ax.text(i - width/2, row['cb_ppg_per_game']  + 0.01, f"{row['cb_ppg_per_game']:.2f}",
                ha='center', fontsize=9, fontweight='bold', color=color)
        ax.text(i + width/2, row['opp_ppg_per_game'] + 0.01, f"{row['opp_ppg_per_game']:.2f}",
                ha='center', fontsize=9, fontweight='bold', color='#555555')

    ax.set_xticks(x)
    ax.set_xticklabels(phase_st['phase'], fontsize=10, color='white')
    ax.set_title(title, fontsize=11, fontweight='bold', color='white')
    ax.set_ylabel('Avg PP goals per game' if ax == axes[0] else '', color='white')
    ax.legend(fontsize=9, facecolor='#222222', edgecolor='#555555', labelcolor='white')
    ax.set_ylim(0, 1.2)
    ax.tick_params(colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#555555')
    ax.spines['bottom'].set_color('#555555')

plt.tight_layout()
path = OUT_DIR / 'chart8_pp_goals_per_game.png'
plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#111111')
plt.close()
print(f'\nSaved {path.name}')

# ── CHART B: Game-by-game net PP goals — all comeback series ─────────────────
fig, axes = plt.subplots(2, 2, figsize=(13, 9), facecolor='#111111')
for ax in axes.flat:
    ax.set_facecolor('#111111')
fig.suptitle('Net Power Play Goals Per Game — All Four Comeback Series\n(positive = trailing team had more PP goals)',
             fontsize=13, fontweight='bold', color='white')

FULL_NAMES = {
    '1942_tor_det': '1942 Toronto Maple Leafs',
    '1975_nyi_pit': '1975 New York Islanders',
    '2010_phi_bos': '2010 Philadelphia Flyers',
    '2014_lak_sjs': '2014 Los Angeles Kings',
}

for ax, sid in zip(axes.flat, ['1942_tor_det', '1975_nyi_pit', '2010_phi_bos', '2014_lak_sjs']):
    s = st[st['series_id'] == sid].sort_values('game_num')
    diffs = s['pp_goals_diff'].tolist()
    game_nums = s['game_num'].tolist()

    colors = [COMEBACK_COLOR if d > 0 else ('#AAAAAA' if d == 0 else '#333333')
              for d in diffs]

    # Use a minimum bar height so zero games are still visible
    display_vals = [d if d != 0 else 0.15 for d in diffs]
    bars = ax.bar(game_nums, display_vals, color=colors, edgecolor='white', linewidth=0.5)

    for game_num, diff, disp in zip(game_nums, diffs, display_vals):
        y_offset = 0.12 if disp >= 0 else -0.28
        ax.text(game_num, disp + y_offset, str(diff),
                ha='center', va='bottom', fontsize=9, fontweight='bold',
                color='white')

    ax.axhline(0, color='#888888', linewidth=0.8)
    ax.axvline(3.5, color='#888888', linewidth=1, linestyle='--', alpha=0.5)
    ax.text(3.6, 2.6, '0–3\nhole', fontsize=7.5, color='#888888', alpha=0.8)
    ax.set_title(FULL_NAMES[sid], fontsize=10, fontweight='bold', color='white')
    ax.set_xlabel('Game number', fontsize=9, color='white')
    ax.set_ylabel('Net PP goals (trailing team)', color='white')
    ax.set_xticks(game_nums)
    ax.set_ylim(-3, 3.2)
    ax.tick_params(colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#555555')
    ax.spines['bottom'].set_color('#555555')

plt.tight_layout()
path = OUT_DIR / 'chart9_net_pp_per_game.png'
plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#111111')
plt.close()
print(f'Saved {path.name}')

# ── CHART C: Penalty minutes discipline shift ─────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5), facecolor='#111111')
ax.set_facecolor('#111111')
fig.suptitle('Penalty Minutes — Trailing Team vs Opponent\nComeback Series: Games 1–3 vs Games 4–7',
             fontsize=13, fontweight='bold', color='white')

pim_agg = (
    st[st['is_comeback_series'] == True]
    .groupby('phase')
    .agg(cb_pim=('comeback_pim', 'mean'), opp_pim=('opponent_pim', 'mean'))
    .reset_index()
)
x     = np.arange(len(pim_agg))
width = 0.35

ax.bar(x - width/2, pim_agg['cb_pim'],  width, label='Trailing team', color=COMEBACK_COLOR, alpha=0.9)
ax.bar(x + width/2, pim_agg['opp_pim'], width, label='Opponent',      color='#888888', alpha=0.7)

for i, row in pim_agg.iterrows():
    ax.text(i - width/2, row['cb_pim']  + 0.2, f"{row['cb_pim']:.1f}",
            ha='center', fontsize=10, fontweight='bold', color=COMEBACK_COLOR)
    ax.text(i + width/2, row['opp_pim'] + 0.2, f"{row['opp_pim']:.1f}",
            ha='center', fontsize=10, fontweight='bold', color='#555555')

ax.set_xticks(x)
ax.set_xticklabels(pim_agg['phase'], fontsize=11, color='white')
ax.set_ylabel('Avg penalty minutes per game', fontsize=10, color='white')
ax.set_ylim(0, 20)
ax.tick_params(colors='white')
ax.legend(fontsize=10, facecolor='#222222', edgecolor='#555555', labelcolor='white')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#555555')
ax.spines['bottom'].set_color('#555555')

plt.tight_layout()
path = OUT_DIR / 'chart10_pim_discipline.png'
plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='#111111')
plt.close()
print(f'Saved {path.name}')
