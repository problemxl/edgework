from edgework.models.base import BaseNHLModel
from edgework.models.team import Team


class Series(BaseNHLModel):
    """Represents a playoff series between two teams."""

    def __init__(self, edgework_client, obj_id=None, top_team=None, bottom_team=None,
                 series_url=None, series_title=None, series_abbreviation=None,
                 series_letter=None, playoff_round=None, top_seed_rank=None,
                 top_seed_rank_abbreviation=None, bottom_seed_rank=None,
                 bottom_seed_rank_abbreviation=None):
        """
        Initialize a Series object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the series
            top_team: The top seeded team in the series
            bottom_team: The bottom seeded team in the series
            series_url: The URL for the series on the NHL website
            series_title: The title of the series, e.g., '1st Round'
            series_abbreviation: The abbreviation for the series, e.g., 'R1'
            series_letter: The letter designation for the series, e.g., 'A'
            playoff_round: The round of the playoffs for this series
            top_seed_rank: The seed rank of the top team in the series
            top_seed_rank_abbreviation: The seed rank abbreviation of the top team in the series
            bottom_seed_rank: The seed rank of the bottom team in the series
            bottom_seed_rank_abbreviation: The seed rank abbreviation of the bottom team in the series
        """
        super().__init__(edgework_client, obj_id)
        self.top_team = top_team
        self.bottom_team = bottom_team
        self.series_url = series_url
        self.series_title = series_title
        self.series_abbreviation = series_abbreviation
        self.series_letter = series_letter
        self.playoff_round = playoff_round
        self.top_seed_rank = top_seed_rank
        self.top_seed_rank_abbreviation = top_seed_rank_abbreviation
        self.bottom_seed_rank = bottom_seed_rank
        self.bottom_seed_rank_abbreviation = bottom_seed_rank_abbreviation
        
    def fetch_data(self):
        """
        Fetch the data for the series.
        """
        # Implementation depends on how data is fetched from the API
        pass

class Playoffs(BaseNHLModel):
    """Represents the playoffs for a given season."""

    def __init__(self, edgework_client, obj_id=None, year=None, series=None,
                 bracket_logo=None, bracket_logo_fr=None):
        """
        Initialize a Playoffs object.
        
        Args:
            edgework_client: The Edgework client
            obj_id: The ID of the playoffs
            year: The year of the playoffs
            series: A list of playoff series in the playoffs
            bracket_logo: The URL for the playoffs bracket logo
            bracket_logo_fr: The URL for the playoffs bracket logo french
        """
        super().__init__(edgework_client, obj_id)
        self.year = year
        self.series = series or []
        self.bracket_logo = bracket_logo
        self.bracket_logo_fr = bracket_logo_fr
        
    def fetch_data(self):
        """
        Fetch the data for the playoffs.
        """
        # Implementation depends on how data is fetched from the API
        pass