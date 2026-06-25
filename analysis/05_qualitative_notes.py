"""
Qualitative research layer — narrative context for each of the four
0-3 comeback series. Covers: pre-series context, what went wrong in
games 1-3, the turning point, and what drove games 4-7.

Sources: publicly available hockey history. Items marked [VERIFY]
should be confirmed against primary sources before citing.
"""

SERIES_NARRATIVES = {

    "1942_tor_det": {
        "teams": "Toronto Maple Leafs vs Detroit Red Wings — Stanley Cup Final",
        "context": (
            "Toronto finished 2nd in the regular season (.594 PTS%), "
            "Detroit finished 5th (.438). On paper Toronto were clear favorites, "
            "making their 0-3 hole one of the most surprising collapses in NHL history. "
            "Conn Smythe, the Leafs' owner, was away preparing to enlist in WWII, "
            "leaving Frank Selke to manage the team."
        ),
        "games_1_3": (
            "Detroit's Jack Adams coached aggressively, exploiting Toronto's "
            "defensive lapses. The Leafs were outscored 12-6 across three games "
            "and looked disorganized. Key veterans were underperforming — "
            "notably Gordie Drillon, who had been the team's top scorer during "
            "the regular season but was invisible in the playoffs."
        ),
        "turning_point": (
            "Before Game 4, coach Hap Day made a bold and controversial decision: "
            "he benched Gordie Drillon and veteran defenseman Bucko McDonald, "
            "replacing them with younger, harder-working players including Don Metz. "
            "He also read the team a letter from a young female fan urging them not "
            "to give up — a motivational tactic that became famous in Leafs lore. "
            "The lineup change fundamentally altered Toronto's energy and work ethic. "
            "[VERIFY: letter story is widely cited but some historians dispute details]"
        ),
        "games_4_7": (
            "Toronto outscored Detroit 19-9 across games 4-7. Don Metz, the "
            "replacement player, scored 3 goals in Game 5 alone (a 9-3 blowout). "
            "Turk Broda was steady throughout — the goaltending didn't change, "
            "the lineup and attitude did. Detroit's Jack Adams was suspended for "
            "Game 5 onward after assaulting referee Mel Harwood following Game 4, "
            "which disrupted Detroit's bench management at a critical moment. "
            "[VERIFY: Adams suspension details]"
        ),
        "key_factor": "Coaching decision (lineup change) + opponent disruption (Adams suspension)",
        "underdog": False,
    },

    "1975_nyi_pit": {
        "teams": "New York Islanders vs Pittsburgh Penguins — Quarterfinals",
        "context": (
            "The Islanders were only in their third NHL season (expansion team, 1972). "
            "Pittsburgh were slight favorites at .556 PTS% vs NYI's .550. "
            "Al Arbour was in his second full season coaching the Islanders, "
            "building what would become a dynasty. Denis Potvin was a 21-year-old "
            "defenseman already regarded as one of the best in the game."
        ),
        "games_1_3": (
            "Billy Smith started in goal for the Islanders and struggled badly — "
            "0-3 record, allowing 14 goals across three games (.884 SV%). "
            "Pittsburgh's offense, led by Syl Apps Jr. and Jean Pronovost, "
            "consistently broke through. The Islanders were outscored 14-9 "
            "and showed little of the defensive structure that would define "
            "their dynasty years."
        ),
        "turning_point": (
            "Al Arbour pulled Billy Smith and started Glenn Resch for Game 4. "
            "Resch was spectacular — .969 SV% across four games (only 4 goals allowed "
            "in 128 shots). The goalie change was the single most decisive factor "
            "in this comeback. Resch's confidence transformed the team in front of him. "
            "The Islanders also tightened defensively, limiting Pittsburgh's Grade-A chances."
        ),
        "games_4_7": (
            "The Islanders outscored Pittsburgh 12-5 in games 4-7. Resch was "
            "unbeatable. Denis Potvin and Clark Gillies were physical and dominant. "
            "Pittsburgh's Gary Inness (.922 SV% across the series) actually played "
            "well but couldn't match Resch. The Islanders won Game 7 1-0, "
            "with Resch recording the shutout. This series is considered the "
            "foundational moment of the Islanders dynasty — the belief that they "
            "could win in pressure situations."
        ),
        "key_factor": "Goalie change (Billy Smith → Glenn Resch) + defensive tightening",
        "underdog": True,
    },

    "2010_phi_bos": {
        "teams": "Philadelphia Flyers vs Boston Bruins — Eastern Conference Semifinals",
        "context": (
            "Boston were the higher seed (.555 vs PHI's .537) and had Tuukka Rask "
            "playing well. Philadelphia had struggled through the first round. "
            "The Flyers were considered done after going down 0-3, and most "
            "analysts treated the series as over. Head coach Peter Laviolette "
            "faced pressure to overhaul his lineup."
        ),
        "games_1_3": (
            "Brian Boucher started for Philadelphia and was unsteady — .891 SV%, "
            "allowing 12 goals across three games. Boucher lost Game 1 in OT, "
            "Game 2 in regulation, and was pulled in Game 3 after allowing 4 goals. "
            "Philadelphia's offense also sputtered, scoring only 7 goals across the "
            "three losses. Mike Richards and Claude Giroux were below their usual level."
        ),
        "turning_point": (
            "Two things changed before Game 4: "
            "(1) Michael Leighton replaced Brian Boucher in goal. Leighton was a "
            "journeyman who had bounced around the league, but he was brilliant in "
            "relief — .943 SV%, allowing only 4 goals in three games. "
            "(2) Simon Gagne returned from a head injury he suffered in the first round. "
            "Gagne was a veteran scorer and his return gave the Flyers a complete "
            "lineup. He scored the overtime winner in Game 5 and was instrumental "
            "throughout the back half. [VERIFY: exact timing of Gagne's return, "
            "whether it was Game 4 or Game 5]"
        ),
        "games_4_7": (
            "Philadelphia scored 4+ goals in every game after going down 0-3. "
            "Leighton allowed only 1 goal in Game 4 (5-4 PHI win, OT) and Game 7 "
            "(4-3 PHI win). The Flyers' forecheck became relentless. "
            "Tuukka Rask, who had been strong early, allowed 3 goals in Game 7. "
            "Boston's Marc Savard had been injured earlier in the playoffs "
            "(a brutal hit by Matt Cooke in the first round) and his absence "
            "became more pronounced as the series extended — Boston lost their "
            "primary playmaker at a critical time. [VERIFY: Savard's exact status "
            "for each game of this series]"
        ),
        "key_factor": "Goalie change (Boucher → Leighton) + Gagne's return from injury",
        "underdog": True,
    },

    "2014_lak_sjs": {
        "teams": "Los Angeles Kings vs San Jose Sharks — Western Conference First Round",
        "context": (
            "San Jose were the clear regular-season favorite — .677 PTS% vs LAK's .610, "
            "SRS gap of 0.2 in San Jose's favor. The Sharks had been one of the best "
            "teams in the Western Conference all year. The Kings had won the Cup in 2012 "
            "under Darryl Sutter and still had their core intact, but were considered "
            "a slight underdog. Game 3 went to overtime, adding to the sense of "
            "inevitability around San Jose."
        ),
        "games_1_3": (
            "Los Angeles were outscored 17-8 in the first three games. Game 2 was "
            "a 7-2 blowout that made the series look completely one-sided. "
            "Jonathan Quick was actually solid (.914 SV% for the full series), "
            "meaning the deficit was driven by LA's offense going quiet and "
            "San Jose's Antti Niemi playing extremely well early. "
            "The Kings' structured defensive system — one of their hallmarks — "
            "was not functioning properly in the first three games."
        ),
        "turning_point": (
            "Darryl Sutter made no dramatic lineup changes and didn't switch goalies. "
            "What changed was the Kings' defensive structure and their willingness "
            "to impose their style physically. In Game 4, LA held San Jose to "
            "3 goals (6-3 win) and reestablished their grinding, shot-suppression game. "
            "Drew Doughty was dominant — his ice time and defensive influence "
            "became the anchor of the turnaround. The team also simplified — "
            "fewer risky plays, more puck battles along the boards. "
            "[VERIFY: any specific Sutter line changes between Game 3 and Game 4]"
        ),
        "games_4_7": (
            "Los Angeles outscored San Jose 18-5 across games 4-7 — the most "
            "dominant back-half performance of any comeback series. San Jose's Antti Niemi "
            "collapsed completely: pulled in Game 5 (gave up 3 goals), replaced by "
            "Alex Stalock who also struggled. The Kings held San Jose to 1 goal "
            "in both Games 6 and 7. Jeff Carter and Anze Kopitar drove the offense. "
            "The Kings' shot suppression returned to its usual elite level — "
            "San Jose went from controlling play to looking disorganized. "
            "Los Angeles went on to win the Stanley Cup that year, defeating "
            "the Rangers in 5 games — making this the most successful 0-3 "
            "comeback in terms of ultimate outcome."
        ),
        "key_factor": "System reset (defensive structure restored) + opponent goaltending collapse",
        "underdog": True,
    },
}

COMPARISON_NOTES = {
    "2013_det_chi": (
        "Detroit went 2-1 in games 1-3 — they were actually competitive early. "
        "But Chicago in 2013 was historically dominant (.802 PTS%, 1.04 SRS) — "
        "the best regular-season team in the modern era to that point. "
        "Detroit's Jimmy Howard played well (.937 SV%) but it wasn't enough. "
        "The gap in roster quality — Toews, Kane, Keith, Crawford — "
        "was too wide for Detroit to overcome in the back half."
    ),
    "2014_col_min": (
        "Minnesota made a goalie change (Bryzgalov for Kuemper) but it backfired — "
        "Bryzgalov posted only .826 SV%. Colorado's Semyon Varlamov was strong "
        "throughout (.913). This is the case that most closely resembles a comeback "
        "attempt — Minnesota won three straight games after going down 0-3 — "
        "but Colorado held on in Game 7. The difference from true comeback teams: "
        "Minnesota's goalie change hurt rather than helped."
    ),
    "2019_car_wsh": (
        "Carolina actually won 4 games and pushed it to Game 7, "
        "making this the closest comparison series to a comeback. "
        "Washington won Game 7 in double overtime. "
        "Carolina's Petr Mrazek was below his regular-season level (.899 vs .914). "
        "Washington's Alex Ovechkin and Nicklas Backstrom provided veteran leadership "
        "in clutch moments that Carolina — a younger team — couldn't match. "
        "No goalie change, no injury-return catalyst, no lineup overhaul: "
        "Carolina just ran out of rope."
    ),
}


def print_narrative(series_id, data):
    print(f"\n{'='*65}")
    print(f"  {data['teams']}")
    print(f"{'='*65}")
    print(f"\nCONTEXT\n  {data['context']}")
    print(f"\nGAMES 1–3: WHAT WENT WRONG\n  {data['games_1_3']}")
    print(f"\nTURNING POINT\n  {data['turning_point']}")
    print(f"\nGAMES 4–7: WHAT DROVE THE COMEBACK\n  {data['games_4_7']}")
    print(f"\nKEY FACTOR: {data['key_factor']}")
    print(f"UNDERDOG:   {data['underdog']}")


def print_comparison(series_id, note):
    print(f"\n--- {series_id} (comparison — lost 0–4) ---")
    print(f"  {note}")


if __name__ == "__main__":
    print("\n" + "█"*65)
    print("  QUALITATIVE ANALYSIS — NHL 0-3 COMEBACK SERIES")
    print("█"*65)

    print("\n\n=== COMEBACK SERIES ===")
    for sid, data in SERIES_NARRATIVES.items():
        print_narrative(sid, data)

    print("\n\n=== COMPARISON SERIES — WHY THEY COULDN'T COMPLETE THE COMEBACK ===")
    for sid, note in COMPARISON_NOTES.items():
        print_comparison(sid, note)

    print("\n\n" + "="*65)
    print("CROSS-SERIES PATTERNS — WHAT ALL FOUR COMEBACKS SHARE")
    print("="*65)
    patterns = [
        "1. The trailing team was a legitimately good team (SRS avg +0.35), not a fluke playoff qualifier.",
        "2. The opponent was beatable — no comeback happened against a dynasty-level team.",
        "3. A concrete reset event occurred before Game 4 in every series:",
        "     1942: coaching lineup change (Drillon/McDonald benched)",
        "     1975: goalie change (Smith → Resch)",
        "     2010: goalie change (Boucher → Leighton) + Gagne return",
        "     2014: structural/system reset (no personnel change, but identity restored)",
        "4. The back half was dominant — not just competitive. Avg goal diff +2.50 in games 4-7.",
        "5. In 3 of 4 cases, the opponent's goaltending declined in the back half.",
        "6. Penalty kill was consistently strong for comeback teams (avg 83.3%).",
    ]
    for p in patterns:
        print(f"  {p}")
