#!/usr/bin/env python3
"""
Edgework NHL API Demo Script

This script demonstrates the main features of the Edgework NHL API client.
Run this in a fresh environment to see what the library can do!

Requirements:
    pip install edgework

Or install from source:
    pip install -e .
"""

from datetime import datetime

import edgework


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_standings():
    print_section("📊 CURRENT STANDINGS")

    client = edgework.Edgework()
    standings = client.standings.get_standings()

    print(f"Date: {standings.date.strftime('%Y-%m-%d')}")
    print(f"Total teams: {len(standings)}\n")

    print("🏆 Top 5 Teams by Points:")
    all_teams = sorted(standings.seedings, key=lambda s: s.points, reverse=True)[:5]

    for i, team in enumerate(all_teams, 1):
        print(
            f"  {i}. {team.team_abbrev}: {team.points} pts "
            f"({team.wins}-{team.losses}-{team.ot_losses})"
        )

    print("\n🏒 Eastern Conference Top 3:")
    east_top3 = sorted(standings.east_standings, key=lambda s: s.points, reverse=True)[
        :3
    ]
    for team in east_top3:
        print(f"  • {team.team_abbrev}: {team.points} pts")

    print("\n🥅 Western Conference Top 3:")
    west_top3 = sorted(standings.west_standings, key=lambda s: s.points, reverse=True)[
        :3
    ]
    for team in west_top3:
        print(f"  • {team.team_abbrev}: {team.points} pts")


def demo_games():
    print_section("🏒 TODAY'S GAMES")

    client = edgework.Edgework()

    try:
        games = client.games.get_current_games()

        if games:
            print(f"Found {len(games)} game(s) today:\n")
            for game in games:
                away = game._data.get("away_team_abbrev", "TBD")
                home = game._data.get("home_team_abbrev", "TBD")
                away_score = game._data.get("away_team_score", "-")
                home_score = game._data.get("home_team_score", "-")
                state = game._data.get("game_state", "SCHEDULED")

                if state == "OFF":
                    status = "Final"
                elif state == "LIVE":
                    status = "Live"
                else:
                    status = state

                print(f"  {away} {away_score} @ {home_score} {home} [{status}]")
        else:
            print("  No games scheduled for today.")
    except Exception as e:
        print(f"  Note: {e}")


def demo_players():
    print_section("⭐ FEATURED PLAYERS")

    client = edgework.Edgework()

    try:
        spotlight = client.players.get_player_spotlight()

        if spotlight:
            print("Player Spotlight:\n")
            for player in spotlight[:5]:
                name = (
                    player.get("firstName", {}).get("default", "")
                    + " "
                    + player.get("lastName", {}).get("default", "")
                )
                team = player.get("teamAbbrev", "N/A")
                print(f"  ⭐ {name} ({team})")
        else:
            print("  No spotlight players available.")

        print("\n🏒 Player Profile Example (Connor McDavid):")
        player_data = client.players.get_player_landing(8478402)

        if player_data:
            first_name = player_data.get("first_name", "")
            last_name = player_data.get("last_name", "")
            position = player_data.get("position", "N/A")
            team = player_data.get("current_team_abbr", "N/A")

            print(f"  Name: {first_name} {last_name}")
            print(f"  Position: {position}")
            print(f"  Team: {team}")

            stats = (
                player_data.get("featuredStats", {})
                .get("regularSeason", {})
                .get("subSeason", {})
            )
            if stats:
                games = stats.get("gamesPlayed", 0)
                goals = stats.get("goals", 0)
                assists = stats.get("assists", 0)
                points = stats.get("points", 0)
                print(
                    f"  Current Season: {games} GP, {goals} G, {assists} A, {points} P"
                )

    except Exception as e:
        print(f"  Note: {e}")


def demo_draft():
    print_section("🎓 DRAFT INFORMATION")

    client = edgework.Edgework()

    try:
        rankings = client.draft.get_draft_rankings()

        if rankings:
            print(f"Current Draft Rankings: {len(rankings.rankings)} prospects\n")

            print("Top 3 Prospects:")
            top3 = rankings.get_top_prospects(3)
            for i, prospect in enumerate(top3, 1):
                name = f"{prospect.first_name} {prospect.last_name}"
                position = prospect.position
                print(f"  {i}. {name} ({position})")

    except Exception as e:
        print(f"  Note: {e}")


def demo_stats():
    print_section("📈 STATISTICS LEADERS")

    client = edgework.Edgework()

    try:
        skater_leaders = client.stats.get_skater_stats_leaders()

        if skater_leaders:
            print("🏒 Skater Leaders (Points):\n")
            points_leaders = skater_leaders.get("points", {}).get("data", [])[:3]
            for i, player in enumerate(points_leaders, 1):
                name = (
                    player.get("firstName", {}).get("default", "")
                    + " "
                    + player.get("lastName", {}).get("default", "")
                )
                points = player.get("points", 0)
                team = player.get("teamAbbrev", "N/A")
                print(f"  {i}. {name} ({team}): {points} pts")

    except Exception as e:
        print(f"  Note: {e}")


def demo_teams():
    print_section("🏒 TEAM ROSTERS")

    client = edgework.Edgework()

    try:
        print("Toronto Maple Leafs Current Roster:\n")

        roster = client.teams.get_roster("TOR")

        if roster:
            forwards = [p for p in roster if p.position in ["C", "L", "R", "W"]][:3]
            defense = [p for p in roster if p.position == "D"][:2]

            print("  Forwards:")
            for player in forwards:
                number = player.sweater_number or "-"
                print(f"    #{number} {player.first_name} {player.last_name}")

            print("\n  Defense:")
            for player in defense:
                number = player.sweater_number or "-"
                print(f"    #{number} {player.first_name} {player.last_name}")

    except Exception as e:
        print(f"  Note: {e}")


def main():
    print("\n" + "=" * 60)
    print("  🏒 EDGWORK NHL API DEMO 🏒")
    print("  Complete NHL API Python Client")
    print("=" * 60)

    print("\n📦 Version: 0.10.0")
    print("🔗 Repository: https://github.com/problemxl/edgework")
    print("📖 Documentation: See README.md")

    print("\n💡 Quick Start:")
    print("  >>> import edgework")
    print("  >>> client = edgework.Edgework()")
    print("  >>> standings = client.standings.get_standings()")
    print("  >>> games = client.games.get_current_games()")
    print("  >>> player = client.players.get_player(8478402)")

    try:
        demo_standings()
    except Exception as e:
        print(f"Standings demo error: {e}")

    try:
        demo_games()
    except Exception as e:
        print(f"Games demo error: {e}")

    try:
        demo_players()
    except Exception as e:
        print(f"Players demo error: {e}")

    try:
        demo_draft()
    except Exception as e:
        print(f"Draft demo error: {e}")

    try:
        demo_stats()
    except Exception as e:
        print(f"Stats demo error: {e}")

    try:
        demo_teams()
    except Exception as e:
        print(f"Teams demo error: {e}")

    print("\n" + "=" * 60)
    print("  ✅ Demo Complete!")
    print("=" * 60)
    print("\nAvailable Clients:")
    print("  • client.players - Player data and statistics")
    print("  • client.teams - Team information and rosters")
    print("  • client.games - Game data and play-by-play")
    print("  • client.schedule - NHL schedule")
    print("  • client.standings - League standings")
    print("  • client.stats - Statistics and leaders")
    print("  • client.draft - Draft information")
    print("  • client.playoffs - Playoff data")
    print("  • client.network - TV and broadcast info")
    print("  • client.utility - Metadata and utilities")
    print("\nFor more examples, see:")
    print("  • tests/ directory for comprehensive examples")
    print("  • README.md for usage documentation")
    print()


if __name__ == "__main__":
    main()
