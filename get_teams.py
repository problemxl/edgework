from edgework.clients.team_client import TeamClient
from edgework.http_client import HttpClient

def get_all_team_info():
    """
    Fetches and prints information for all NHL teams.
    """
    with HttpClient() as client:
        team_client = TeamClient(client=client)
        try:
            all_teams = team_client.get_teams()
            if all_teams:
                print("NHL Team Information:")
                for team in all_teams:
                    print(f"  Team ID: {team.obj_id}")
                    print(f"  Team Name: {team.name}")
                    print(f"  Abbreviation: {team.abbrev}")
                    print(f"  Full Name: {team.full_name}")
                    print("-" * 30)
            else:
                print("No team information found.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_all_team_info()