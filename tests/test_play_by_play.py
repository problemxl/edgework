import pytest
from unittest.mock import MagicMock, patch

from edgework.models.play import Play
from edgework.models.play_by_play import PlayByPlay


class TestPlayFromApi:
    """Test Play.from_api() method."""

    def test_from_api_goal_play(self):
        """Test creating a Play object from goal play data."""
        play_data = {
            "eventId": 159,
            "periodDescriptor": {
                "number": 1,
                "periodType": "REG",
                "maxRegulationPeriods": 3,
            },
            "timeInPeriod": "00:43",
            "timeRemaining": "19:17",
            "situationCode": "1551",
            "homeTeamDefendingSide": "left",
            "typeCode": 505,
            "typeDescKey": "goal",
            "sortOrder": 17,
            "details": {
                "xCoord": 50,
                "yCoord": 9,
                "zoneCode": "O",
                "shotType": "wrist",
                "scoringPlayerId": 8480802,
                "scoringPlayerTotal": 8,
                "assist1PlayerId": 8477365,
                "assist1PlayerTotal": 8,
                "assist2PlayerId": 8479359,
                "assist2PlayerTotal": 5,
                "eventOwnerTeamId": 7,
                "goalieInNetId": 8474682,
                "awayScore": 0,
                "homeScore": 1,
            },
            "pptReplayUrl": "https://example.com/replay.json",
        }

        mock_client = MagicMock()
        play = Play.from_api(play_data, mock_client)

        assert play._data.get("event_id") == 159
        assert play._data.get("period_number") == 1
        assert play._data.get("type_desc_key") == "goal"
        assert play._fetched is True

    def test_from_api_penalty_play(self):
        """Test creating a Play object from penalty play data."""
        play_data = {
            "eventId": 200,
            "periodDescriptor": {
                "number": 2,
                "periodType": "REG",
                "maxRegulationPeriods": 3,
            },
            "timeInPeriod": "05:30",
            "timeRemaining": "14:30",
            "situationCode": "1552",
            "homeTeamDefendingSide": "right",
            "typeCode": 503,
            "typeDescKey": "penalty",
            "sortOrder": 25,
            "details": {
                "penaltySeverity": "Minor",
                "penaltyMinutes": 2,
                "penaltyType": "Hooking",
                "committedByPlayerId": 8480802,
            },
            "pptReplayUrl": "https://example.com/replay2.json",
        }

        mock_client = MagicMock()
        play = Play.from_api(play_data, mock_client)

        assert play._data.get("type_desc_key") == "penalty"
        assert play._data.get("event_id") == 200
        assert play._fetched is True

    def test_from_api_shot_play(self):
        """Test creating a Play object from shot play data."""
        play_data = {
            "eventId": 300,
            "periodDescriptor": {
                "number": 1,
                "periodType": "REG",
                "maxRegulationPeriods": 3,
            },
            "timeInPeriod": "10:15",
            "timeRemaining": "09:45",
            "situationCode": "1551",
            "homeTeamDefendingSide": "left",
            "typeCode": 506,
            "typeDescKey": "shot-on-goal",
            "sortOrder": 35,
            "details": {
                "xCoord": 85,
                "yCoord": 15,
                "zoneCode": "O",
                "shotType": "slap",
                "shootingPlayerId": 8477365,
            },
            "pptReplayUrl": None,
        }

        mock_client = MagicMock()
        play = Play.from_api(play_data, mock_client)

        assert play._data.get("type_desc_key") == "shot-on-goal"
        assert play._data.get("event_id") == 300
        assert play._fetched is True


class TestPlayProperties:
    """Test Play properties."""

    def test_is_goal(self):
        """Test is_goal property."""
        mock_client = MagicMock()

        goal_play = Play(edgework_client=mock_client, type_desc_key="goal")
        assert goal_play.is_goal is True

        penalty_play = Play(edgework_client=mock_client, type_desc_key="penalty")
        assert penalty_play.is_goal is False

    def test_is_penalty(self):
        """Test is_penalty property."""
        mock_client = MagicMock()

        penalty_play = Play(edgework_client=mock_client, type_desc_key="penalty")
        assert penalty_play.is_penalty is True

        goal_play = Play(edgework_client=mock_client, type_desc_key="goal")
        assert goal_play.is_penalty is False

    def test_is_shot(self):
        """Test is_shot property."""
        mock_client = MagicMock()

        shot_play = Play(edgework_client=mock_client, type_desc_key="shot-on-goal")
        assert shot_play.is_shot is True

        missed_shot = Play(edgework_client=mock_client, type_desc_key="missed-shot")
        assert missed_shot.is_shot is True

        blocked_shot = Play(edgework_client=mock_client, type_desc_key="blocked-shot")
        assert blocked_shot.is_shot is True

        faceoff = Play(edgework_client=mock_client, type_desc_key="faceoff")
        assert faceoff.is_shot is False

    def test_goal_details(self):
        """Test goal_details property."""
        mock_client = MagicMock()

        goal_play = Play(
            edgework_client=mock_client,
            type_desc_key="goal",
            details={"scoringPlayerId": 123, "assist1PlayerId": 456},
        )
        assert goal_play.goal_details is not None

        penalty_play = Play(
            edgework_client=mock_client, type_desc_key="penalty", details={}
        )
        assert penalty_play.goal_details is None

    def test_scoring_player_id(self):
        """Test scoring_player_id property."""
        mock_client = MagicMock()

        goal_play = Play(
            edgework_client=mock_client,
            type_desc_key="goal",
            details={"scoringPlayerId": 8480802},
        )
        assert goal_play.scoring_player_id == 8480802

        no_goal_play = Play(
            edgework_client=mock_client, type_desc_key="faceoff", details={}
        )
        assert no_goal_play.scoring_player_id is None

    def test_assist_player_ids(self):
        """Test assist_player_ids property."""
        mock_client = MagicMock()

        goal_play = Play(
            edgework_client=mock_client,
            type_desc_key="goal",
            details={
                "assist1PlayerId": 8477365,
                "assist2PlayerId": 8479359,
            },
        )
        assists = goal_play.assist_player_ids
        assert len(assists) == 2
        assert 8477365 in assists
        assert 8479359 in assists

        goal_one_assist = Play(
            edgework_client=mock_client,
            type_desc_key="goal",
            details={"assist1PlayerId": 8477365},
        )
        assists = goal_one_assist.assist_player_ids
        assert len(assists) == 1
        assert 8477365 in assists


class TestPlayStringRepresentations:
    """Test Play string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        mock_client = MagicMock()

        play = Play(
            edgework_client=mock_client,
            event_id=159,
            period_number=1,
            time_in_period="00:43",
            type_desc_key="goal",
        )

        result = str(play)
        assert "Period 1 @ 00:43: goal" in result
        assert "ID: 159" in result

    def test_repr_representation(self):
        """Test __repr__ method."""
        mock_client = MagicMock()

        play = Play(
            edgework_client=mock_client,
            event_id=159,
            type_desc_key="goal",
        )

        result = repr(play)
        assert "event_id=159" in result
        assert "type=goal" in result


class TestPlayByPlayFromApi:
    """Test PlayByPlay.from_api() method."""

    def test_from_api_basic(self):
        """Test creating a PlayByPlay object from API data."""
        api_data = {
            "id": 2024020705,
            "season": 20242025,
            "gameType": 2,
            "limitedScoring": False,
            "gameDate": "2025-01-15",
            "venue": {"default": "KeyBank Center"},
            "venueLocation": {"default": "Buffalo"},
            "startTimeUTC": "2025-01-15T23:00:00Z",
            "easternUTCOffset": "-05:00",
            "venueUTCOffset": "-05:00",
            "tvBroadcasts": [],
            "gameState": "OFF",
            "gameScheduleState": "OK",
            "periodDescriptor": {
                "number": 3,
                "periodType": "REG",
                "maxRegulationPeriods": 3,
            },
            "awayTeam": {"id": 12, "abbrev": "CAR", "score": 2},
            "homeTeam": {"id": 7, "abbrev": "BUF", "score": 4},
            "shootoutInUse": False,
            "otInUse": False,
            "clock": {"timeRemaining": "00:00"},
            "displayPeriod": 3,
            "maxPeriods": 3,
            "gameOutcome": {"lastPeriodType": "REG"},
            "rosterSpots": {},
            "regPeriods": {},
            "summary": {},
            "plays": [
                {
                    "eventId": 159,
                    "periodDescriptor": {"number": 1, "periodType": "REG"},
                    "typeDescKey": "goal",
                    "details": {"scoringPlayerId": 8480802},
                },
                {
                    "eventId": 200,
                    "periodDescriptor": {"number": 2, "periodType": "REG"},
                    "typeDescKey": "penalty",
                    "details": {},
                },
            ],
        }

        mock_client = MagicMock()
        play_by_play = PlayByPlay.from_api(api_data, mock_client)

        assert play_by_play._data.get("game_id") == 2024020705
        assert play_by_play._data.get("game_state") == "OFF"
        assert len(play_by_play._data.get("plays")) == 2
        assert play_by_play._fetched is True

    def test_from_api_empty_plays(self):
        """Test creating a PlayByPlay object with no plays."""
        api_data = {
            "id": 2024020705,
            "gameState": "OFF",
            "plays": [],
        }

        mock_client = MagicMock()
        play_by_play = PlayByPlay.from_api(api_data, mock_client)

        assert len(play_by_play._data.get("plays")) == 0


class TestPlayByPlayProperties:
    """Test PlayByPlay properties."""

    def test_plays_property_lazy_loading(self):
        """Test plays property creates Play objects lazily."""
        mock_client = MagicMock()

        api_data = {
            "id": 2024020705,
            "plays": [
                {
                    "eventId": 159,
                    "periodDescriptor": {"number": 1, "periodType": "REG"},
                    "typeDescKey": "goal",
                    "details": {"scoringPlayerId": 8480802},
                }
            ],
        }

        play_by_play = PlayByPlay.from_api(api_data, mock_client)

        assert len(play_by_play.plays) == 1
        assert isinstance(play_by_play.plays[0], Play)

    def test_goals_property(self):
        """Test goals property filters for goals only."""
        mock_client = MagicMock()

        api_data = {
            "id": 2024020705,
            "plays": [
                {
                    "eventId": 1,
                    "typeDescKey": "goal",
                    "periodDescriptor": {"number": 1},
                },
                {
                    "eventId": 2,
                    "typeDescKey": "penalty",
                    "periodDescriptor": {"number": 1},
                },
                {
                    "eventId": 3,
                    "typeDescKey": "shot-on-goal",
                    "periodDescriptor": {"number": 1},
                },
                {
                    "eventId": 4,
                    "typeDescKey": "goal",
                    "periodDescriptor": {"number": 2},
                },
            ],
        }

        play_by_play = PlayByPlay.from_api(api_data, mock_client)

        goals = play_by_play.goals
        assert len(goals) == 2
        assert all(goal.is_goal for goal in goals)

    def test_penalties_property(self):
        """Test penalties property filters for penalties only."""
        mock_client = MagicMock()

        api_data = {
            "id": 2024020705,
            "plays": [
                {
                    "eventId": 1,
                    "typeDescKey": "goal",
                    "periodDescriptor": {"number": 1},
                },
                {
                    "eventId": 2,
                    "typeDescKey": "penalty",
                    "periodDescriptor": {"number": 1},
                },
                {
                    "eventId": 3,
                    "typeDescKey": "penalty",
                    "periodDescriptor": {"number": 2},
                },
            ],
        }

        play_by_play = PlayByPlay.from_api(api_data, mock_client)

        penalties = play_by_play.penalties
        assert len(penalties) == 2
        assert all(penalty.is_penalty for penalty in penalties)

    def test_shots_property(self):
        """Test shots property filters for shots only."""
        mock_client = MagicMock()

        api_data = {
            "id": 2024020705,
            "plays": [
                {
                    "eventId": 1,
                    "typeDescKey": "shot-on-goal",
                    "periodDescriptor": {"number": 1},
                },
                {
                    "eventId": 2,
                    "typeDescKey": "missed-shot",
                    "periodDescriptor": {"number": 1},
                },
                {
                    "eventId": 3,
                    "typeDescKey": "blocked-shot",
                    "periodDescriptor": {"number": 1},
                },
                {
                    "eventId": 4,
                    "typeDescKey": "faceoff",
                    "periodDescriptor": {"number": 1},
                },
            ],
        }

        play_by_play = PlayByPlay.from_api(api_data, mock_client)

        shots = play_by_play.shots
        assert len(shots) == 3
        assert all(shot.is_shot for shot in shots)

    def test_total_plays_property(self):
        """Test total_plays property."""
        mock_client = MagicMock()

        api_data = {
            "id": 2024020705,
            "plays": [
                {
                    "eventId": i,
                    "typeDescKey": "faceoff",
                    "periodDescriptor": {"number": 1},
                }
                for i in range(10)
            ],
        }

        play_by_play = PlayByPlay.from_api(api_data, mock_client)
        assert play_by_play.total_plays == 10

    def test_get_plays_by_period(self):
        """Test get_plays_by_period method."""
        mock_client = MagicMock()

        api_data = {
            "id": 2024020705,
            "plays": [
                {
                    "eventId": 1,
                    "typeDescKey": "faceoff",
                    "periodDescriptor": {"number": 1},
                },
                {
                    "eventId": 2,
                    "typeDescKey": "faceoff",
                    "periodDescriptor": {"number": 2},
                },
                {
                    "eventId": 3,
                    "typeDescKey": "faceoff",
                    "periodDescriptor": {"number": 2},
                },
                {
                    "eventId": 4,
                    "typeDescKey": "faceoff",
                    "periodDescriptor": {"number": 3},
                },
            ],
        }

        play_by_play = PlayByPlay.from_api(api_data, mock_client)

        period_2_plays = play_by_play.get_plays_by_period(2)
        assert len(period_2_plays) == 2

    def test_get_plays_by_team(self):
        """Test get_plays_by_team method."""
        mock_client = MagicMock()

        api_data = {
            "id": 2024020705,
            "plays": [
                {
                    "eventId": 1,
                    "typeDescKey": "goal",
                    "periodDescriptor": {"number": 1},
                    "details": {"eventOwnerTeamId": 7},
                },
                {
                    "eventId": 2,
                    "typeDescKey": "goal",
                    "periodDescriptor": {"number": 2},
                    "details": {"eventOwnerTeamId": 12},
                },
            ],
        }

        play_by_play = PlayByPlay.from_api(api_data, mock_client)

        team_7_plays = play_by_play.get_plays_by_team(7)
        assert len(team_7_plays) == 1

    def test_get_plays_by_player(self):
        """Test get_plays_by_player method."""
        mock_client = MagicMock()

        api_data = {
            "id": 2024020705,
            "plays": [
                {
                    "eventId": 1,
                    "typeDescKey": "goal",
                    "periodDescriptor": {"number": 1},
                    "details": {"scoringPlayerId": 8480802},
                },
                {
                    "eventId": 2,
                    "typeDescKey": "goal",
                    "periodDescriptor": {"number": 2},
                    "details": {"scoringPlayerId": 8477365},
                },
            ],
        }

        play_by_play = PlayByPlay.from_api(api_data, mock_client)

        player_plays = play_by_play.get_plays_by_player(8480802)
        assert len(player_plays) == 1


class TestPlayByPlayStringRepresentations:
    """Test PlayByPlay string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        mock_client = MagicMock()

        play_by_play = PlayByPlay(
            http_client=mock_client,
            obj_id=2024020705,
            game_id=2024020705,
            plays=[],
        )

        result = str(play_by_play)
        assert "game_id=2024020705" in result
        assert "0 plays" in result

    def test_repr_representation(self):
        """Test __repr__ method."""
        mock_client = MagicMock()

        play_by_play = PlayByPlay(
            http_client=mock_client,
            obj_id=2024020705,
            game_id=2024020705,
            plays=[],
        )

        result = repr(play_by_play)
        assert "game_id=2024020705" in result
