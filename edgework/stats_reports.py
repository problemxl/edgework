"""Single source of truth for NHL Stats API report names.

The Stats API report endpoints (``/{lang}/skater/{report}``,
``/{lang}/goalie/{report}`` and ``/{lang}/team/{report}``) require a report
identifier in the route. This module centralizes the accepted report names so
that :class:`~edgework.clients.stats_client.StatsClient`,
:class:`~edgework.models.stats.SkaterStats`,
:class:`~edgework.models.stats.GoalieStats` and
:class:`~edgework.models.stats.TeamStats` all validate against one list
instead of maintaining divergent copies.

``*_REPORTS`` tuples hold the canonical report identifiers used by the Stats
API routes. ``*_REPORT_ALIASES`` frozensets hold legacy spellings that older
model-level validation accepted; they are still validated and passed through
unchanged for backward compatibility, but new code should prefer the
canonical names.
"""

SKATER_REPORTS: tuple[str, ...] = (
    "summary",
    "bios",
    "faceoffpercentages",
    "faceoffwins",
    "goalsForAgainst",
    "realtime",
    "penalties",
    "penaltykill",
    "penaltyShots",
    "powerplay",
    "puckPossessions",
    "summaryshooting",
    "percentages",
    "scoringRates",
    "scoringpergame",
    "shootout",
    "shottype",
    "timeonice",
)

GOALIE_REPORTS: tuple[str, ...] = (
    "summary",
    "advanced",
    "bios",
    "daysrest",
    "penaltyShots",
    "savesByStrength",
    "shootout",
    "startedVsRelieved",
)

TEAM_REPORTS: tuple[str, ...] = (
    "summary",
    "faceoffpercentages",
    "daysbetweengames",
    "faceoffwins",
    "goalsagainstbystrength",
    "goalsbyperiod",
    "goalsforbystrength",
    "leadingtrailing",
    "realtime",
    "outshootoutshotby",
    "penalties",
    "penaltykill",
    "penaltykilltime",
    "powerplay",
    "powerplaytime",
    "summaryshooting",
    "percentages",
    "scoretrailfirst",
    "shootout",
    "shottype",
    "goalgames",
)

# Legacy spellings accepted by earlier model-level validation but absent from
# the canonical lists. They remain accepted (and are passed through unchanged,
# so requests keep their historical wire format) for backward compatibility.
SKATER_REPORT_ALIASES: frozenset[str] = frozenset(
    {"penaltyDetails", "penaltyKill", "powerPlay"}
)
GOALIE_REPORT_ALIASES: frozenset[str] = frozenset({"savePercentageByGametate"})
TEAM_REPORT_ALIASES: frozenset[str] = frozenset(
    {
        "goalsForAgainst",
        "penaltyDetails",
        "penaltyKill",
        "powerPlay",
        "puckPossessions",
        "scoringRates",
        "scoringpergame",
        "timeonice",
    }
)

_REPORT_FAMILIES: dict[str, tuple[tuple[str, ...], frozenset[str]]] = {
    "skater": (SKATER_REPORTS, SKATER_REPORT_ALIASES),
    "goalie": (GOALIE_REPORTS, GOALIE_REPORT_ALIASES),
    "team": (TEAM_REPORTS, TEAM_REPORT_ALIASES),
}


def reports_for(family: str) -> tuple[str, ...]:
    """
    Return the canonical report names for a report family.

    Args:
        family: Report family ("skater", "goalie" or "team").

    Returns:
        Tuple of canonical report names.

    Raises:
        ValueError: If the family is unknown.
    """
    if family not in _REPORT_FAMILIES:
        raise ValueError(
            f"Unknown report family: '{family}'. "
            f"Must be one of: {', '.join(sorted(_REPORT_FAMILIES))}"
        )
    return _REPORT_FAMILIES[family][0]


def validate_report(family: str, report: str) -> str:
    """
    Validate a report name against the single source of truth.

    Canonical report names and documented legacy aliases are both accepted;
    the report is returned unchanged so request routes keep their historical
    wire format.

    Args:
        family: Report family ("skater", "goalie" or "team").
        report: The report name to validate.

    Returns:
        The validated report name (unchanged).

    Raises:
        ValueError: If the family is unknown, the report is not a string, or
            the report is not supported for the family.
    """
    if family not in _REPORT_FAMILIES:
        raise ValueError(
            f"Unknown report family: '{family}'. "
            f"Must be one of: {', '.join(sorted(_REPORT_FAMILIES))}"
        )

    canonical, aliases = _REPORT_FAMILIES[family]
    if not isinstance(report, str) or (
        report not in canonical and report not in aliases
    ):
        accepted = tuple(canonical) + tuple(sorted(aliases))
        raise ValueError(
            f"Unsupported {family} report: {report!r}. "
            f"Valid reports: {', '.join(accepted)}"
        )

    return report
