"""Tests for the shared Stats API report-name source of truth (Task 4).

Covers every accepted canonical report name per family, the legacy aliases,
rejection of unsupported names, and the model classes validating against the
same source (with unchanged wire format for legacy spellings).
"""

from unittest.mock import Mock

import pytest

from edgework.http_client import HttpClient
from edgework.models.stats import GoalieStats, SkaterStats, TeamStats
from edgework.stats_reports import (
    GOALIE_REPORT_ALIASES,
    GOALIE_REPORTS,
    SKATER_REPORT_ALIASES,
    SKATER_REPORTS,
    TEAM_REPORT_ALIASES,
    TEAM_REPORTS,
    reports_for,
    validate_report,
)


class TestCanonicalReports:
    """Every canonical report name is accepted for its family."""

    @pytest.mark.parametrize("report", SKATER_REPORTS)
    def test_skater_reports_accepted(self, report):
        assert validate_report("skater", report) == report

    @pytest.mark.parametrize("report", GOALIE_REPORTS)
    def test_goalie_reports_accepted(self, report):
        assert validate_report("goalie", report) == report

    @pytest.mark.parametrize("report", TEAM_REPORTS)
    def test_team_reports_accepted(self, report):
        assert validate_report("team", report) == report

    def test_reports_for_returns_canonical_tuples(self):
        assert reports_for("skater") == SKATER_REPORTS
        assert reports_for("goalie") == GOALIE_REPORTS
        assert reports_for("team") == TEAM_REPORTS

    def test_aliases_disjoint_from_canonical(self):
        """Legacy aliases are spellings *outside* the canonical lists."""
        assert SKATER_REPORT_ALIASES.isdisjoint(SKATER_REPORTS)
        assert GOALIE_REPORT_ALIASES.isdisjoint(GOALIE_REPORTS)
        assert TEAM_REPORT_ALIASES.isdisjoint(TEAM_REPORTS)


class TestLegacyReportAliases:
    """Legacy model-level spellings remain accepted and pass through."""

    @pytest.mark.parametrize(
        "report", sorted(SKATER_REPORT_ALIASES | {"penaltykill", "powerplay"})
    )
    def test_skater_aliases_and_canonical_case_variants(self, report):
        assert validate_report("skater", report) == report

    @pytest.mark.parametrize("report", sorted(GOALIE_REPORT_ALIASES))
    def test_goalie_aliases_accepted(self, report):
        assert validate_report("goalie", report) == report

    @pytest.mark.parametrize(
        "report", sorted(TEAM_REPORT_ALIASES | {"penaltykill", "powerplay"})
    )
    def test_team_aliases_accepted(self, report):
        assert validate_report("team", report) == report


class TestReportRejection:
    """Unsupported report names and families are rejected."""

    @pytest.mark.parametrize("family", ["skater", "goalie", "team"])
    def test_unsupported_report_rejected(self, family):
        with pytest.raises(ValueError, match="Unsupported"):
            validate_report(family, "not_a_report")

    def test_cross_family_report_rejected(self):
        """'advanced' is goalie-only; 'goalgames' is team-only."""
        with pytest.raises(ValueError):
            validate_report("skater", "advanced")
        with pytest.raises(ValueError):
            validate_report("goalie", "goalgames")

    def test_skater_alias_rejected_for_goalie(self):
        with pytest.raises(ValueError):
            validate_report("goalie", "penaltyDetails")

    def test_non_string_report_rejected(self):
        with pytest.raises(ValueError):
            validate_report("skater", 123)

    def test_empty_report_rejected(self):
        with pytest.raises(ValueError):
            validate_report("team", "")

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="Unknown report family"):
            validate_report("referee", "summary")

    def test_unknown_family_rejected_by_reports_for(self):
        with pytest.raises(ValueError, match="Unknown report family"):
            reports_for("referee")


class TestModelsValidateAgainstSharedSource:
    """The stats models validate reports via edgework.stats_reports."""

    @pytest.fixture
    def mock_client(self):
        client = Mock(spec=HttpClient)
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"data": []}
        client.get.return_value = response
        return client

    def test_skater_model_accepts_canonical_and_alias(
        self, mock_client: Mock
    ):
        for report in ("summary", "powerPlay", "penaltyDetails"):
            stats = SkaterStats(mock_client, obj_id=1)
            stats.fetch_data(report=report, season=20232024)
        assert mock_client.get.call_count == 3

    def test_goalie_model_accepts_canonical_and_alias(
        self, mock_client: Mock
    ):
        for report in ("summary", "savePercentageByGametate"):
            stats = GoalieStats(mock_client, obj_id=1)
            stats.fetch_data(report=report, season=20232024)
        assert mock_client.get.call_count == 2

    def test_team_model_alias_keeps_wire_format(self, mock_client: Mock):
        """Legacy aliases pass through unchanged (no silent remapping)."""
        stats = TeamStats(mock_client, obj_id=10)
        stats.fetch_data(report="powerPlay", season=20232024)

        mock_client.get.assert_called_once_with(
            endpoint="stats",
            path="team/powerPlay?isAggregate=False&isGame=True&limit=-1&start=0&sort=wins&cayenneExp=seasonId=20232024",
            params=None,
            web=False,
        )

    @pytest.mark.parametrize(
        "model_cls,family",
        [(SkaterStats, "skater"), (GoalieStats, "goalie"), (TeamStats, "team")],
    )
    def test_models_reject_unsupported_reports(
        self, mock_client: Mock, model_cls, family
    ):
        stats = model_cls(mock_client, obj_id=1)
        with pytest.raises(ValueError, match=f"Unsupported {family} report"):
            stats.fetch_data(report="not_a_report", season=20232024)
        mock_client.get.assert_not_called()
