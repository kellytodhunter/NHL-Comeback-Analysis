# NHL 0-3 Playoff Comeback Analysis

A comprehensive data analysis of every team in NHL history to complete a 0-3 playoff comeback. Four teams have done it. This project examines what separated them from the teams that couldn't — across game momentum, goaltending, regular-season quality, special teams, and opponent strength.

---

## The Four Teams

| Year | Comeback Team | Opponent | Round |
|------|--------------|----------|-------|
| 1942 | Toronto Maple Leafs | Detroit Red Wings | Stanley Cup Final |
| 1975 | New York Islanders | Pittsburgh Penguins | Quarterfinals |
| 2010 | Philadelphia Flyers | Boston Bruins | Eastern Conference Semifinals |
| 2014 | Los Angeles Kings | San Jose Sharks | Western Conference First Round |

Three comparison series (teams that went down 0-3 and lost) were included as a baseline: 2013 Detroit vs Chicago, 2014 Minnesota vs Colorado, 2019 Carolina vs Washington.

---

## Key Findings

**1. The flip is total — not gradual.**
Every comeback team went exactly 0-3 in games 1-3 and 4-0 in games 4-7. No team scratched out an early win and recovered gradually. The switch flipped cleanly at game 4 every time.

| Phase | Win Rate | Avg Goal Differential |
|-------|----------|----------------------|
| Games 1–3 | 0% | -2.08 |
| Games 4–7 | 100% | +2.50 |

**2. The cumulative goal deficit was erased completely — and then some.**
All four teams dug deep into negative territory on cumulative goal differential through the first three games, then crossed back to positive by the end of the series. The 2014 Kings entered game 4 at -9 cumulative goals and finished +4. The reversal wasn't gradual — it was sudden and total.

**3. They won big, not barely.**
Of 16 wins across games 4-7: 8 were blowouts (3+ goal margin), 3 were 2-goal wins, 4 were 1-goal wins, and only 1 went to overtime. These teams didn't survive — they dominated.

**4. Home ice had zero effect.**
Comeback teams went 8-0 on the road and 8-0 at home in games 4-7. Comparison teams went 1-9 away from home for their entire series. Once the psychological reset happened, venue was irrelevant.

**5. Opponent quality was the hard ceiling.**
No 0-3 comeback has ever happened against a dynasty-level team. Comeback series opponents averaged SRS +0.33; comparison series opponents averaged SRS +0.60. Chicago in 2013 (SRS +1.04) was historically dominant — Detroit had no path back regardless of anything else.

**6. Special teams flipped with the series.**
Comeback teams went from losing the PP battle by 1 goal in games 1-3 to winning it by 6 goals in games 4-7. Opponent PP% dropped from 11.7% to 6.8% after going up 3-0.

**7. Both goalies shifted simultaneously.**
In 3 of 4 series, the comeback team's goalie improved *and* the opponent's goalie declined at the same time. Tuukka Rask's SV% fell from .928 (while winning) to .876 (while losing). This points to pressure dynamics affecting both teams — not just one personnel decision.

**8. A concrete reset event triggered every comeback.**

| Series | Reset Event |
|--------|-------------|
| 1942 TOR | Coach Hap Day benched star scorer Gordie Drillon; Detroit's coach Jack Adams suspended for assaulting a referee |
| 1975 NYI | Goalie change: Billy Smith (.876 SV%) → Glenn Resch (.970 SV%) |
| 2010 PHI | Goalie change: Boucher → Leighton + Simon Gagne returned from injury |
| 2014 LAK | No personnel change — system and identity reset by a Cup-experienced team |

---

## The Formula

A 0-3 comeback requires all three of the following:

1. **A legitimately good team** — one that has underperformed in games 1-3, not one playing at its ceiling
2. **A beatable opponent** — no comeback has occurred against a team with SRS above +0.65
3. **A concrete reset event** — a coaching decision, personnel change, injury return, or identity restoration before game 4

Every comparison team was missing at least one condition. Every comeback team had all three.

---

## Project Structure

```
NHL_Comeback_Analysis/
├── scrapers/
│   ├── series_config.py           # Series URLs and metadata
│   ├── scrape_series.py           # Game scores, skater/goalie stats per series
│   ├── scrape_season_stats.py     # Regular-season team stats
│   ├── scrape_game_boxscores.py   # Per-game special teams from box scores
│   ├── scrape_game_goalies.py     # Per-game goalie stats from box scores
│   └── parse_to_csv.py            # Converts raw JSON to clean CSVs
│
├── analysis/
│   ├── 01_game_momentum.py        # Game-by-game scores and phase splits
│   ├── 02_goalie_analysis.py      # Series-level goalie SV% and changes
│   ├── 03_season_context.py       # Regular-season team profiles
│   ├── 04_comparative_analysis.py # All layers combined side by side
│   ├── 05_qualitative_notes.py    # Narrative context per series
│   ├── 06_margin_and_homeway.py   # Win margin distribution and home/away splits
│   ├── 07_special_teams.py        # Power play and penalty kill by phase
│   ├── 08_goalie_change_deep_dive.py # Game-by-game goalie performance
│   └── 09_final_summary.py        # Complete findings report
│
├── visualizations/
│   ├── 01_charts.py               # Chart generation script
│   ├── 01_charts.py               # Main chart generation script
│   ├── chart1_goal_differential.png
│   ├── chart2_cumulative_goal_diff.png
│   ├── chart3_srs_comparison.png
│   ├── chart4_series_progression.png
│   ├── chart5_margin_per_game.png
│   ├── chart6_home_away_winrate.png
│   ├── chart7_win_type.png
│   ├── chart8_pp_goals_per_game.png
│   ├── chart9_net_pp_per_game.png
│   ├── chart10_pim_discipline.png
│   ├── chart11_goalie_sv_per_game.png
│   └── chart12_opponent_goalie_ga.png
│
└── data/
    ├── raw/                        # JSON files from scrapers
    └── processed/                  # Clean CSVs for analysis
```

---

## Data Sources

All data scraped from [Hockey Reference](https://www.hockey-reference.com) using `requests` and `BeautifulSoup`. Data includes:

- Per-game series scores (7 series × 7 games)
- Goalie stats per game (player, GA, SA, SV%, TOI, decision)
- Per-game special teams (PP goals, PP opportunities, PIM from box scores)
- Regular-season team stats (PTS%, GF/G, GA/G, PP%, PK%, SRS)

The 1942 series predates shot-tracking, so SV% is unavailable for that era.

---

## Running the Project

**Requirements**
```
python 3.9+
pandas
requests
beautifulsoup4
lxml
matplotlib
seaborn
```

**Install dependencies**
```bash
pip install pandas requests beautifulsoup4 lxml matplotlib seaborn
```

**Scrape data** (respects Hockey Reference's rate limit — allow ~10 min)
```bash
cd scrapers
python scrape_series.py
python scrape_season_stats.py
python scrape_game_boxscores.py
python scrape_game_goalies.py
python parse_to_csv.py
```

**Run analysis**
```bash
cd analysis
python 01_game_momentum.py
python 04_comparative_analysis.py
python 09_final_summary.py   # Full findings report
```

**Generate charts**
```bash
cd visualizations
python 01_charts.py
```

---

## Tools

- **Python** — data collection, analysis, visualization
- **pandas** — data manipulation
- **matplotlib** — charts
- **BeautifulSoup / requests** — web scraping
- **Hockey Reference** — data source
