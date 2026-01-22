from dataclasses import dataclass
from typing import Optional


@dataclass
class PlayoffSeries:
    series_id: int
    conference: str
    round: int
    series_name: str
    series_code: str
    series_status: str
    match_type: int
    series_summary: Optional[str] = None
    series_leader: Optional[str] = None

    def __str__(self):
        return f"{self.series_name}: {self.series_status}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, PlayoffSeries):
            return self.series_id == other.series_id
        return False


@dataclass
class PlayoffBracket:
    season: int
    series: list[PlayoffSeries]

    def __str__(self):
        return f"Playoff Bracket {self.season}: {len(self.series)} series"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, PlayoffBracket):
            return self.season == other.season
        return False

    @classmethod
    def from_api(cls, data: dict) -> "PlayoffBracket":
        series_list = []
        for round_data in data.get("rounds", []):
            for series_data in round_data.get("series", []):
                series = PlayoffSeries(
                    series_id=series_data.get("seriesId"),
                    conference=round_data.get("conference", ""),
                    round=round_data.get("number", 0),
                    series_name=series_data.get("seriesName", ""),
                    series_code=series_data.get("seriesCode", ""),
                    series_status=series_data.get("seriesStatus", ""),
                    match_type=series_data.get("matchType", 0),
                    series_summary=series_data.get("seriesSummary"),
                    series_leader=series_data.get("seriesLeader"),
                )
                series_list.append(series)

        return cls(
            season=data.get("seasonId"),
            series=series_list,
        )
