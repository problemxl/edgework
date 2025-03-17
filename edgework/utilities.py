import re


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def dict_camel_to_snake(data):
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            new_key = camel_to_snake(k)
            new_dict[new_key] = dict_camel_to_snake(v) if isinstance(v, (dict, list)) else v
        return new_dict
    elif isinstance(data, list):
        return [dict_camel_to_snake(item) for item in data]
    else:
        return data


d = {
    "clinchIndicator": "p",
    "conferenceAbbrev": "E",
    "conferenceHomeSequence": 1,
    "conferenceL10Sequence": 4,
    "conferenceName": "Eastern",
    "conferenceRoadSequence": 4,
    "conferenceSequence": 1,
    "date": "2024-04-18",
    "divisionAbbrev": "M",
    "divisionHomeSequence": 1,
    "divisionL10Sequence": 4,
    "divisionName": "Metropolitan",
    "divisionRoadSequence": 1,
    "divisionSequence": 1,
    "gameTypeId": 2,
    "gamesPlayed": 82,
    "goalDifferential": 53,
    "goalDifferentialPctg": 0.646341,
    "goalAgainst": 229,
    "goalFor": 282,
    "goalsForPctg": 3.439024,
    "homeGamesPlayed": 41,
    "homeGoalDifferential": 32,
    "homeGoalsAgainst": 110,
    "homeGoalsFor": 142,
    "homeLosses": 11,
    "homeOtLosses": 0,
    "homePoints": 60,
    "homeRegulationPlusOtWins": 27,
    "homeRegulationWins": 24,
    "homeTies": 0,
    "homeWins": 30,
    "l10GamesPlayed": 10,
    "l10GoalDifferential": 6,
    "l10GoalsAgainst": 30,
    "l10GoalsFor": 36,
    "l10Losses": 3,
    "l10OtLosses": 0,
    "l10Points": 14,
    "l10RegulationPlusOtWins": 5,
    "l10RegulationWins": 5,
    "l10Ties": 0,
    "l10Wins": 7,
    "leagueHomeSequence": 2,
    "leagueL10Sequence": 6,
    "leagueRoadSequence": 5,
    "leagueSequence": 1,
    "losses": 23,
    "otLosses": 4,
    "placeName": {
        "default": "NY Rangers"
    },
    "pointPctg": 0.695122,
    "points": 114,
    "regulationPlusOtWinPctg": 0.621951,
    "regulationPlusOtWins": 51,
    "regulationWinPctg": 0.52439,
    "regulationWins": 43,
    "roadGamesPlayed": 41,
    "roadGoalDifferential": 21,
    "roadGoalsAgainst": 119,
    "roadGoalsFor": 140,
    "roadLosses": 12,
    "roadOtLosses": 4,
    "roadPoints": 54,
    "roadRegulationPlusOtWins": 24,
    "roadRegulationWins": 19,
    "roadTies": 0,
    "roadWins": 25,
    "seasonId": 20232024,
    "shootoutLosses": 3,
    "shootoutWins": 4,
    "streakCode": "W",
    "streakCount": 2,
    "teamName": {
        "default": "New York Rangers",
        "fr": "Rangers de New York"
    },
    "teamCommonName": {
        "default": "Rangers"
    },
    "teamAbbrev": {
        "default": "NYR"
    },
    "teamLogo": "https://assets.nhle.com/logos/nhl/svg/NYR_light.svg",
    "ties": 0,
    "waiversSequence": 32,
    "wildcardSequence": 0,
    "winPctg": 0.670732,
    "wins": 55
}

# for key, value in dict_camel_to_snake(d).items():
#     # print key: type of value
#     print(f"{key}: {type(value).__name__}")
