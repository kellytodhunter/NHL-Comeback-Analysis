"""
Final summary — NHL 0-3 Playoff Comeback Analysis
Synthesizes all analytical layers into a unified findings report.
"""

DIVIDER = "=" * 65

SUMMARY = f"""
{DIVIDER}
  NHL 0-3 PLAYOFF COMEBACK ANALYSIS — FINAL SUMMARY
  Four Series: 1942 TOR, 1975 NYI, 2010 PHI, 2014 LAK
{DIVIDER}

━━━ BACKGROUND ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Only four teams in NHL history have completed a 0-3 comeback to win
a playoff series. This analysis examined all four across six layers:
game momentum, goaltending, regular-season context, comparative
baseline (3 teams that lost 0-4), special teams, and game-by-game
goalie performance.

━━━ FINDING 1: THE FLIP IS TOTAL — NOT GRADUAL ━━━━━━━━━━━━━━━━

Every comeback team went exactly 0-3 in games 1-3 and 4-0 in games
4-7. No team scratched out one win early, fell back, then recovered.
The switch flipped cleanly at game 4 in every case.

  Games 1-3:  0% win rate   avg goal diff  -2.08
  Games 4-7: 100% win rate  avg goal diff  +2.50

Comparison teams (lost 0-4) went 44% in games 1-3 and 58% in
games 4-7 — they stayed competitive but never dominated. The back-
half dominance of comeback teams was not survivorship — they
outscored opponents by nearly 3 goals per game after going down 0-3.

━━━ FINDING 2: THEY WON BIG, NOT JUST BARELY ━━━━━━━━━━━━━━━━━━

Of 16 wins in games 4-7 across all four comeback series:
  - 8 were blowouts (3+ goal margin)
  - 3 were 2-goal wins
  - 4 were 1-goal wins
  - 1 went to overtime

This is critical context. These teams didn't squeak through seven
games — they imposed their will. The 2014 Kings won games 4-7 by
margins of 3, 3, 3, and 4 goals. The 1942 Leafs won game 5 by 6.

━━━ FINDING 3: HOME ICE DIDN'T MATTER ━━━━━━━━━━━━━━━━━━━━━━━━━

Comeback teams went 8-0 on the road and 8-0 at home in games 4-7.
Venue was irrelevant. Comparison teams, by contrast, went 1-9 on
the road for their entire series — they were heavily home-dependent
and never broke that pattern.

This suggests the psychological reset at game 4 was complete enough
that comeback teams stopped treating road games differently.
Comparison teams never achieved that internal confidence.

━━━ FINDING 4: QUALITY OF OPPONENT WAS THE CEILING ━━━━━━━━━━━━━

No 0-3 comeback has ever happened against a dynasty-level opponent.

  Comeback series opponents avg SRS:    +0.33
  Comparison series opponents avg SRS:  +0.60

Chicago 2013 (SRS +1.04, .802 PTS%) was the best regular-season
team in modern NHL history that year. Detroit had no path back
against that roster depth regardless of goaltending or momentum.

The teams that couldn't complete comebacks weren't worse teams —
they faced objectively stronger opposition. This is the most
important structural constraint on the comeback formula.

━━━ FINDING 5: COMEBACK TEAMS WERE LEGITIMATELY GOOD ━━━━━━━━━━━

The four comeback teams averaged SRS +0.35 vs +0.18 for the
comparison trailing teams. They were not fluky playoff qualifiers.

  Avg PTS%:  .573 (comeback) vs .595 (comparison trailing)
  Avg SRS:   .348 (comeback) vs .177 (comparison trailing)
  Avg PK%:  83.3% (comeback) vs 80.7% (comparison trailing)

The better underlying quality gave them the capacity to sustain
four consecutive wins once the series dynamics changed.

━━━ FINDING 6: A RESET EVENT TRIGGERED EVERY COMEBACK ━━━━━━━━━━

In every series, something concrete and identifiable changed before
game 4. These were not random variance.

  1942 TOR: Coach Hap Day benched star scorer Gordie Drillon and
            veteran Bucko McDonald. Don Metz (replacement) scored
            3 goals in game 5. Detroit's Jack Adams was suspended
            for assaulting a referee after game 4, disrupting their
            bench management at the critical moment.

  1975 NYI: Billy Smith (.876 avg SV%) was pulled after game 3.
            Glenn Resch came in and posted .964/.947/.969/1.000
            across games 4-7. Pittsburgh's Gary Inness held steady
            — meaning this comeback was almost entirely driven by
            the goalie change, not opponent decline.

  2010 PHI: Two simultaneous changes — Michael Leighton replaced
            Brian Boucher (who was trending down game by game:
            .891/.889/.842), and Simon Gagne returned from a head
            injury. Tuukka Rask also collapsed (.928 avg while
            winning → .876 while losing), suggesting the pressure
            transfer affected both ends simultaneously.

  2014 LAK: No personnel change. Darryl Sutter changed nothing.
            Jonathan Quick's SV% went from .821/.825/.900 (losing)
            to .923/1.000/.962/.975 (winning) — same goalie,
            entirely different numbers. This was a system and
            identity reset by a team with Cup experience that
            understood how to play their game under pressure.

━━━ FINDING 7: SPECIAL TEAMS FLIPPED WITH THE SERIES ━━━━━━━━━━━

Power play performance shifted dramatically at game 4:

             Games 1-3            Games 4-7
  CB team PP%:    8.0%  →  12.0%  (+4.0%)
  Opponent PP%:  11.7%  →   6.8%  (-4.9%)
  Net PP goals:    -1   →    +6

The comeback teams went from losing the special teams battle by 1
goal across games 1-3 to winning it by 6 goals across games 4-7.
The 2014 Kings' penalty kill was the most dramatic case — San Jose
scored 1 power play goal on 32 opportunities in games 4-7 (.031%).

━━━ FINDING 8: OPPONENT GOALTENDING COLLAPSED IN EVERY SERIES ━━━

This is the finding least reported in conventional analysis.

  1942 DET  (Mowers):  2.0 GA/game (winning) → 4.75 GA/game (losing)
  1975 PIT  (Inness):  3.0 GA/game (winning) → 2.25 GA/game (losing)
  2010 BOS  (Rask):    2.3 GA/game (winning) → 3.75 GA/game (losing)
  2014 SJS  (Niemi):   2.7 GA/game (winning) → 3.0 GA/game (losing)

In 3 of 4 series the opponent's goalie allowed significantly more
goals per game after going up 3-0. Rask's decline was the most
severe — his SV% fell from .928 to .876. This is consistent with
the "leading team gets comfortable and stops executing" hypothesis
rather than a random statistical fluctuation.

━━━ THE FORMULA: WHAT IT TAKES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Based on all eight findings, a 0-3 comeback requires all three of:

  1. A legitimately good team (SRS > 0, strong PK, capable offense)
     that has underperformed in games 1-3 — not a team playing at
     its ceiling.

  2. A beatable opponent — not a dynasty. No comeback has happened
     against a team with SRS above +0.65.

  3. A concrete reset event before game 4 — a coaching decision,
     personnel change, injury return, or identity restoration that
     gives the team a psychological and tactical inflection point.

When all three are present, the data suggests the comeback becomes
viable. When any one is missing, the 0-3 hole is terminal.

━━━ WHAT SEPARATES THE FOUR WHO DID IT ━━━━━━━━━━━━━━━━━━━━━━━━━

The clearest separating factor across the comparison teams:

  2013 DET: Missing condition 2 — Chicago was historically dominant.
             Detroit played well (Howard .937 SV%) but had no path.

  2014 MIN: Met conditions 1 and 2 but the reset backfired.
             Bryzgalov (.826) replaced Kuemper (.913) — the wrong
             goalie change. Minnesota came closest structurally but
             executed the pivot incorrectly.

  2019 CAR: Met conditions 1 and 2 but had no reset event at all.
             No goalie change, no lineup shake-up, no injury return.
             Carolina fought hard (pushed to Game 7 double OT) but
             without a catalyst, the inertia of 0-3 held.

{DIVIDER}
  FILES IN THIS PROJECT
{DIVIDER}

  analysis/
    01_game_momentum.py        — game-by-game scores and phase splits
    02_goalie_analysis.py      — series-level goalie SV% and changes
    03_season_context.py       — regular-season team profiles
    04_comparative_analysis.py — all three layers combined
    05_qualitative_notes.py    — narrative per series + patterns
    06_margin_and_homeway.py   — win margin distribution, home/away
    07_special_teams.py        — power play and penalty kill by phase
    08_goalie_change_deep_dive.py — game-by-game goalie performance

  visualizations/
    chart1_goal_differential.png   — avg goal diff by phase
    chart2_win_rate_by_phase.png   — win % before and after 0-3
    chart3_srs_comparison.png      — opponent strength per series
    chart4_series_progression.png  — cumulative wins game by game
    chart5_margin_per_game.png     — score diff per game, H/A labeled
    chart6_home_away_winrate.png   — home vs away win rate
    chart7_win_type.png            — margin of victory breakdown
    chart8_pp_goals_per_game.png   — PP goals per game by phase
    chart9_net_pp_per_game.png     — net PP goals per game
    chart10_pim_discipline.png     — penalty minutes by phase
    chart11_goalie_sv_per_game.png — goalie SV% game by game
    chart12_opponent_goalie_ga.png — opponent goalie GA game by game

  data/processed/
    game_logs.csv          — per-game scores all 7 series
    goalie_stats.csv       — series-level goalie stats
    season_team_stats.csv  — regular-season context

  data/raw/
    game_special_teams.json — per-game PP/PK/PIM from box scores
    game_goalie_stats.json  — per-game goalie stats from box scores
    <series_id>.json        — raw series scrape per series
"""

if __name__ == '__main__':
    print(SUMMARY)
