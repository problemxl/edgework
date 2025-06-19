from httpx import Client


class TeamClient:
    def __init__(self, client: Client):
        self.client = client
        
    def get_teams(self) -> list[Team]:
        """ Fetch a list of teams from NHL.

        Returns
        -------
        list[Team]
            A list of teams.
        """
        pass

    def get_roster(self, team_code:str) -> Roster:
        """ Fetch a roster for a team from NHL.

        Parameters
        ----------
        team_code : str
            The team code for the team
        
        Returns
        -------
        Roster
            A roster for the team.
        """
        pass
        