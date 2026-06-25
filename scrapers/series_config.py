"""
Configuration for the four NHL 0-3 playoff comeback series.
Hockey Reference URLs and metadata for each series.
"""

COMEBACK_SERIES = [
    {
        "id": "1942_tor_det",
        "year": 1942,
        "round": "Stanley Cup Finals",
        "comeback_team": "Toronto Maple Leafs",
        "opponent": "Detroit Red Wings",
        "comeback_team_abbr": "TOR",
        "opponent_abbr": "DET",
        "hr_url": "https://www.hockey-reference.com/playoffs/1942-detroit-red-wings-vs-toronto-maple-leafs-stanley-cup-final.html",
        "notes": "First 0-3 comeback in NHL history. Pre-advanced stats era.",
    },
    {
        "id": "1975_nyi_pit",
        "year": 1975,
        "round": "Quarterfinals",
        "comeback_team": "New York Islanders",
        "opponent": "Pittsburgh Penguins",
        "comeback_team_abbr": "NYI",
        "opponent_abbr": "PIT",
        "hr_url": "https://www.hockey-reference.com/playoffs/1975-new-york-islanders-vs-pittsburgh-penguins-quarter-finals.html",
        "notes": "Early Islanders dynasty era.",
    },
    {
        "id": "2010_phi_bos",
        "year": 2010,
        "round": "Second Round",
        "comeback_team": "Philadelphia Flyers",
        "opponent": "Boston Bruins",
        "comeback_team_abbr": "PHI",
        "opponent_abbr": "BOS",
        "hr_url": "https://www.hockey-reference.com/playoffs/2010-boston-bruins-vs-philadelphia-flyers-eastern-conference-semi-finals.html",
        "notes": "Michael Leighton replaced Brian Boucher in goal.",
    },
    {
        "id": "2014_lak_sjs",
        "year": 2014,
        "round": "First Round",
        "comeback_team": "Los Angeles Kings",
        "opponent": "San Jose Sharks",
        "comeback_team_abbr": "LAK",
        "opponent_abbr": "SJS",
        "hr_url": "https://www.hockey-reference.com/playoffs/2014-los-angeles-kings-vs-san-jose-sharks-western-first-round.html",
        "notes": "Kings went on to win the Stanley Cup.",
    },
]

# Teams that lost 0-4 after going down 0-3 — used as comparison baseline.
# Selected to roughly match era and seeding of comeback teams.
COMPARISON_SERIES = [
    {
        "id": "2013_det_chi",
        "year": 2013,
        "round": "Second Round",
        "trailing_team": "Detroit Red Wings",
        "leading_team": "Chicago Blackhawks",
        "trailing_abbr": "DET",
        "leading_abbr": "CHI",
        "hr_url": "https://www.hockey-reference.com/playoffs/2013-chicago-blackhawks-vs-detroit-red-wings-western-conference-semi-finals.html",
        "notes": "Detroit went down 0-3 and lost in 7.",
    },
    {
        "id": "2014_col_min",
        "year": 2014,
        "round": "First Round",
        "trailing_team": "Minnesota Wild",
        "leading_team": "Colorado Avalanche",
        "trailing_abbr": "MIN",
        "leading_abbr": "COL",
        "hr_url": "https://www.hockey-reference.com/playoffs/2014-colorado-avalanche-vs-minnesota-wild-western-first-round.html",
        "notes": "Minnesota went down 0-3, lost series.",
    },
    {
        "id": "2019_car_wsh",
        "year": 2019,
        "round": "Second Round",
        "trailing_team": "Carolina Hurricanes",
        "leading_team": "Washington Capitals",
        "trailing_abbr": "CAR",
        "leading_abbr": "WSH",
        "hr_url": "https://www.hockey-reference.com/playoffs/2019-carolina-hurricanes-vs-washington-capitals-eastern-first-round.html",
        "notes": "Carolina went down 0-3, lost series.",
    },
]
