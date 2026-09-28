"""Client for the NHL Stats API (api.nhle.com/stats/rest).

Report names are validated against :mod:`edgework.stats_reports`, the single
source of truth shared with the ``SkaterStats``/``GoalieStats``/``TeamStats``
models. Query parameters are always passed through ``params`` (never embedded
in route strings) so they are encoded correctly.

Simple resource endpoints (players, draft, franchise, seasons, ...) return the
raw JSON payload — dict or list — because no stable model exists for them.
"""

import warnings
from typing import Any, Optional, Union

from edgework.http_client import HttpClient
from edgework.models.stats import (
    GoalieStats,
    SkaterStats,
    TeamStats,
    validate_limit_and_start,
    validate_season,
)
from edgework.stats_reports import (
    GOALIE_REPORTS,
    SKATER_REPORTS,
    TEAM_REPORTS,
    validate_report,
)
from edgework.utilities import dict_camel_to_snake, validate_season_format

# Web API leaderboard route targets. The language prefix and base URL of
# Stats API routes are added by ``HttpClient``; their registry templates
# live under ``stats_``-prefixed keys in ``edgework.endpoints.API_PATH``
# (e.g. ``stats_players`` -> ``/{lang}/players``). The leaderboard registry
# keys are ``skater_stats_now``, ``skater_stats_season_game_type``,
# ``goalie_stats_now`` and ``goalie_stats_season_game_type``.
_SKATER_LEADERS_NOW = "skater-stats-leaders/current"
_GOALIE_LEADERS_NOW = "goalie-stats-leaders/current"

_REPORT_MODELS = {
    "skater": SkaterStats,
    "goalie": GoalieStats,
    "team": TeamStats,
}


class StatsClient:
    """Client for the documented Stats API resources, reports and leaders."""

    # Canonical report names (single source of truth: edgework.stats_reports).
    skate_reports: tuple[str, ...] = SKATER_REPORTS
    goalie_reports: tuple[str, ...] = GOALIE_REPORTS
    team_reports: tuple[str, ...] = TEAM_REPORTS

    def __init__(self, client: HttpClient):
        """
        Initialize the stats client.

        Args:
            client: HTTP client instance for making API requests.
        """
        self._client = client

    # ------------------------------------------------------------------
    # Shared query-assembly helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_cayenne_exp(
        season: Optional[int],
        game_type: Optional[int],
        cayenne_exp: Optional[str],
    ) -> str:
        """Build the ``cayenneExp`` value for a report request.

        A raw ``cayenne_exp`` escape hatch wins over the built expression;
        otherwise ``seasonId={season}`` is built (season defaults to the
        current season), optionally extended with ``and gameTypeId={n}``.
        """
        if cayenne_exp is not None:
            return cayenne_exp

        expression = f"seasonId={validate_season(season)}"
        if game_type is not None:
            if game_type not in (2, 3):
                raise ValueError(
                    "Game type must be 2 (regular season) or 3 (playoffs)."
                )
            expression = f"{expression} and gameTypeId={game_type}"
        return expression

    @staticmethod
    def _build_report_params(
        aggregate: bool,
        game: bool,
        limit: int,
        start: int,
        sort: Optional[str],
        dir: Optional[str],
        cayenne_exp: str,
        fact_cayenne_exp: Optional[Union[str, list[str]]],
        include: Optional[Union[str, list[str]]],
        exclude: Optional[Union[str, list[str]]],
        extra_params: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Assemble the documented report query parameters.

        Everything is returned as a plain dict for ``HttpClient.get(...,
        params=...)`` so values are encoded correctly; ``extra_params`` is a
        raw escape hatch merged last (it may override the built entries).
        """
        params: dict[str, Any] = {
            "isAggregate": aggregate,
            "isGame": game,
            "limit": limit,
            "start": start,
        }
        if sort is not None:
            params["sort"] = sort
        if dir is not None:
            params["dir"] = dir
        params["cayenneExp"] = cayenne_exp
        if fact_cayenne_exp is not None:
            params["factCayenneExp"] = fact_cayenne_exp
        if include is not None:
            params["include"] = include
        if exclude is not None:
            params["exclude"] = exclude
        if extra_params:
            params.update(extra_params)
        return params

    def _get_report(
        self,
        family: str,
        report: str,
        aggregate: bool,
        game: bool,
        limit: int,
        start: int,
        sort: Optional[str],
        dir: Optional[str],
        season: Optional[int],
        game_type: Optional[int],
        cayenne_exp: Optional[str],
        fact_cayenne_exp: Optional[Union[str, list[str]]],
        include: Optional[Union[str, list[str]]],
        exclude: Optional[Union[str, list[str]]],
        lang: str,
        extra_params: Optional[dict[str, Any]],
    ) -> list:
        """Fetch a skater/goalie/team report and convert rows to models."""
        report = validate_report(family, report)
        limit, start = validate_limit_and_start(limit, start)
        cayenne = self._build_cayenne_exp(season, game_type, cayenne_exp)
        params = self._build_report_params(
            aggregate=aggregate,
            game=game,
            limit=limit,
            start=start,
            sort=sort,
            dir=dir,
            cayenne_exp=cayenne,
            fact_cayenne_exp=fact_cayenne_exp,
            include=include,
            exclude=exclude,
            extra_params=extra_params,
        )

        # Route template: API_PATH["stats_{family}_report"] = /{lang}/{family}/{report}
        response = self._client.get(
            f"{family}/{report}", params=params, web=False, lang=lang
        )
        data = response.json()["data"]

        model_cls = _REPORT_MODELS[family]
        results = []
        for row in data:
            stats_obj = model_cls(
                edgework_client=self._client, **dict_camel_to_snake(row)
            )
            # The report data is already loaded with the caller's exact
            # filters; mark fetched so lazy attribute access serves it from
            # ``_data`` instead of triggering a refetch with default filters.
            stats_obj._fetched = True
            results.append(stats_obj)
        return results

    # ------------------------------------------------------------------
    # Report endpoints (/{lang}/skater|goalie|team/{report})
    # ------------------------------------------------------------------

    def get_skaters_stats(
        self,
        report: str = "summary",
        aggregate: bool = False,
        game: bool = True,
        limit: int = -1,
        start: int = 0,
        sort: str = "points",
        season: Optional[int] = None,
        game_type: Optional[int] = None,
        dir: Optional[str] = None,
        cayenne_exp: Optional[str] = None,
        fact_cayenne_exp: Optional[Union[str, list[str]]] = None,
        include: Optional[Union[str, list[str]]] = None,
        exclude: Optional[Union[str, list[str]]] = None,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> list[SkaterStats]:
        """Fetch skater stats for a report as SkaterStats objects.

        Targets the documented ``/{lang}/skater/{report}`` route (registry
        key ``stats_skater_report``); report names are validated against
        :mod:`edgework.stats_reports`.

        Args:
            report: Report name (default "summary").
            aggregate: Whether to aggregate the stats.
            game: Whether to return game-level stats.
            limit: Number of results (-1 for all).
            start: Starting index for pagination.
            sort: Field to sort by.
            season: Season in YYYYYYYY format; defaults to the current season.
            game_type: Optional game type (2=regular season, 3=playoffs)
                appended to the season filter.
            dir: Optional sort direction ("ASC"/"DESC") for the ``dir`` query
                parameter.
            cayenne_exp: Raw Cayenne filter expression (escape hatch that
                overrides the season/game-type expression).
            fact_cayenne_exp: Optional ``factCayenneExp`` query filter.
            include: Optional ``include`` query filter (string or list; a
                list is sent as repeated query parameters).
            exclude: Optional ``exclude`` query filter (string or list).
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters,
                merged last.

        Returns:
            List of SkaterStats objects (one per report row).
        """
        return self._get_report(
            family="skater",
            report=report,
            aggregate=aggregate,
            game=game,
            limit=limit,
            start=start,
            sort=sort,
            dir=dir,
            season=season,
            game_type=game_type,
            cayenne_exp=cayenne_exp,
            fact_cayenne_exp=fact_cayenne_exp,
            include=include,
            exclude=exclude,
            lang=lang,
            extra_params=extra_params,
        )

    def get_goalies_stats(
        self,
        season: Optional[int] = None,
        report: str = "summary",
        aggregate: bool = False,
        game: bool = True,
        limit: int = -1,
        start: int = 0,
        sort: str = "wins",
        game_type: Optional[int] = None,
        dir: Optional[str] = None,
        cayenne_exp: Optional[str] = None,
        fact_cayenne_exp: Optional[Union[str, list[str]]] = None,
        include: Optional[Union[str, list[str]]] = None,
        exclude: Optional[Union[str, list[str]]] = None,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> list[GoalieStats]:
        """Fetch goalie stats for a report as GoalieStats objects.

        Targets the documented ``/{lang}/goalie/{report}`` route (registry
        key ``stats_goalie_report``); report names are validated against
        :mod:`edgework.stats_reports`.

        Args:
            season: Season in YYYYYYYY format; defaults to the current season.
            report: Report name (default "summary").
            aggregate: Whether to aggregate the stats.
            game: Whether to return game-level stats.
            limit: Number of results (-1 for all).
            start: Starting index for pagination.
            sort: Field to sort by (default "wins").
            game_type: Optional game type (2=regular season, 3=playoffs)
                appended to the season filter.
            dir: Optional sort direction ("ASC"/"DESC") for the ``dir`` query
                parameter.
            cayenne_exp: Raw Cayenne filter expression (escape hatch that
                overrides the season/game-type expression).
            fact_cayenne_exp: Optional ``factCayenneExp`` query filter.
            include: Optional ``include`` query filter (string or list).
            exclude: Optional ``exclude`` query filter (string or list).
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters,
                merged last.

        Returns:
            List of GoalieStats objects (one per report row).
        """
        return self._get_report(
            family="goalie",
            report=report,
            aggregate=aggregate,
            game=game,
            limit=limit,
            start=start,
            sort=sort,
            dir=dir,
            season=season,
            game_type=game_type,
            cayenne_exp=cayenne_exp,
            fact_cayenne_exp=fact_cayenne_exp,
            include=include,
            exclude=exclude,
            lang=lang,
            extra_params=extra_params,
        )

    def get_team_stats(
        self,
        season: Optional[int] = None,
        report: str = "summary",
        aggregate: bool = False,
        game: bool = True,
        limit: int = -1,
        start: int = 0,
        sort: str = "wins",
        game_type: Optional[int] = None,
        dir: Optional[str] = None,
        cayenne_exp: Optional[str] = None,
        fact_cayenne_exp: Optional[Union[str, list[str]]] = None,
        include: Optional[Union[str, list[str]]] = None,
        exclude: Optional[Union[str, list[str]]] = None,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> list[TeamStats]:
        """Fetch team stats for a report as TeamStats objects.

        Targets the documented ``/{lang}/team/{report}`` route (registry key
        ``stats_team_report``); report names are validated against
        :mod:`edgework.stats_reports`.

        Args:
            season: Season in YYYYYYYY format; defaults to the current season.
            report: Report name (default "summary").
            aggregate: Whether to aggregate the stats.
            game: Whether to return game-level stats.
            limit: Number of results (-1 for all).
            start: Starting index for pagination.
            sort: Field to sort by (default "wins").
            game_type: Optional game type (2=regular season, 3=playoffs)
                appended to the season filter.
            dir: Optional sort direction ("ASC"/"DESC") for the ``dir`` query
                parameter.
            cayenne_exp: Raw Cayenne filter expression (escape hatch that
                overrides the season/game-type expression).
            fact_cayenne_exp: Optional ``factCayenneExp`` query filter.
            include: Optional ``include`` query filter (string or list).
            exclude: Optional ``exclude`` query filter (string or list).
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters,
                merged last.

        Returns:
            List of TeamStats objects (one per report row).
        """
        return self._get_report(
            family="team",
            report=report,
            aggregate=aggregate,
            game=game,
            limit=limit,
            start=start,
            sort=sort,
            dir=dir,
            season=season,
            game_type=game_type,
            cayenne_exp=cayenne_exp,
            fact_cayenne_exp=fact_cayenne_exp,
            include=include,
            exclude=exclude,
            lang=lang,
            extra_params=extra_params,
        )

    # ------------------------------------------------------------------
    # Simple resource endpoints (raw JSON; no stable models)
    # ------------------------------------------------------------------

    def _get_resource(
        self,
        target: str,
        params: Optional[dict[str, Any]] = None,
        lang: Optional[str] = "en",
    ) -> Union[dict[str, Any], list[Any]]:
        """GET a Stats API resource target and return the raw JSON payload."""
        response = self._client.get(target, params=params, web=False, lang=lang)
        return response.json()

    def get_players(
        self,
        limit: Optional[int] = None,
        start: Optional[int] = None,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch player information (documented truncated list with a total).

        Targets the documented ``/{lang}/players`` route (registry key
        ``stats_players``).

        Args:
            limit: Optional pagination limit (only sent when provided).
            start: Optional pagination start (only sent when provided).
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if start is not None:
            params["start"] = start
        if extra_params:
            params.update(extra_params)
        return self._get_resource("players", params=params or None, lang=lang)

    def get_skaters(
        self,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch skater information.

        Targets the documented ``/{lang}/skater`` route (registry key
        ``stats_skater``). This is the skater *listing*; report-based stats
        live in :meth:`get_skaters_stats`.

        Args:
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource("skater", lang=lang, params=extra_params)

    def get_skater_leaders(
        self,
        attribute: str,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch Stats API skater leaders for an attribute.

        Targets the documented ``/{lang}/leaders/skaters/{attribute}`` route
        (registry key ``stats_skater_leaders``). This is the Stats API
        leaders listing; the separate Web API leaderboards are served by
        :meth:`get_skater_stats_leaders`.

        Args:
            attribute: Leaderboard attribute (e.g. "points").
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource(
            f"leaders/skaters/{attribute}", lang=lang, params=extra_params
        )

    def get_skater_milestones(
        self,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch skater milestones.

        Targets the documented ``/{lang}/milestones/skaters`` route (registry
        key ``stats_skater_milestones``).

        Args:
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource(
            "milestones/skaters", lang=lang, params=extra_params
        )

    def get_goalie_leaders(
        self,
        attribute: str,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch Stats API goalie leaders for an attribute.

        Targets the documented ``/{lang}/leaders/goalies/{attribute}`` route
        (registry key ``stats_goalie_leaders``).

        Args:
            attribute: Leaderboard attribute (e.g. "gaa").
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource(
            f"leaders/goalies/{attribute}", lang=lang, params=extra_params
        )

    def get_goalie_milestones(
        self,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch goalie milestones.

        Targets the documented ``/{lang}/milestones/goalies`` route (registry
        key ``stats_goalie_milestones``).

        Args:
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource(
            "milestones/goalies", lang=lang, params=extra_params
        )

    def get_draft(
        self,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch draft information.

        Targets the documented ``/{lang}/draft`` route (registry key
        ``stats_draft``). Web API draft rankings/picks live in
        :class:`~edgework.clients.draft_client.DraftClient`.

        Args:
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource("draft", lang=lang, params=extra_params)

    def get_franchises(
        self,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch the list of all franchises.

        Targets the documented ``/{lang}/franchise`` route (registry key
        ``stats_franchise``).

        Args:
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource("franchise", lang=lang, params=extra_params)

    def get_component_seasons(
        self,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch component season information.

        Targets the documented ``/{lang}/componentSeason`` route (registry
        key ``stats_component_season``).

        Args:
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource(
            "componentSeason", lang=lang, params=extra_params
        )

    def get_seasons(
        self,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch season information.

        Targets the documented ``/{lang}/season`` Stats API route (registry
        key ``stats_season``). Note this is distinct from the Web API
        ``/v1/season`` route served by
        :meth:`edgework.clients.utility_client.UtilityClient.get_season`.

        Args:
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource("season", lang=lang, params=extra_params)

    def get_games(
        self,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch game information.

        Targets the documented ``/{lang}/game`` route (registry key
        ``stats_game``).

        Args:
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource("game", lang=lang, params=extra_params)

    def get_game_meta(
        self,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch game metadata.

        Targets the documented ``/{lang}/game/meta`` route (registry key
        ``stats_game_meta``).

        Args:
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource("game/meta", lang=lang, params=extra_params)

    def get_config(
        self,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch configuration information.

        Targets the documented ``/{lang}/config`` route (registry key
        ``stats_config``). Note: ``edgework.models.config.Config`` fetches
        the same route lazily (see Task 5).

        Args:
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource("config", lang=lang, params=extra_params)

    def get_countries(
        self,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch country information (countries with a hockey presence).

        Targets the documented ``/{lang}/country`` route (registry key
        ``stats_country``).

        Args:
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource("country", lang=lang, params=extra_params)

    def get_content_module(
        self,
        template_key: str,
        lang: str = "en",
        extra_params: Optional[dict[str, Any]] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        """Fetch content module information for a template.

        Targets the documented ``/{lang}/content/module/{templateKey}``
        route (registry key ``stats_content_module``).

        Args:
            template_key: Content module template key/name.
            lang: Language code for the Stats API request (default "en").
            extra_params: Raw escape hatch for additional query parameters.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource(
            f"content/module/{template_key}", lang=lang, params=extra_params
        )

    def ping(self) -> Union[dict[str, Any], list[Any]]:
        """Ping the Stats API server to check connectivity.

        Targets the documented root ``/ping`` route (registry key
        ``stats_ping``), which — unlike the other Stats API routes — is not
        language-prefixed.

        Returns:
            Raw JSON payload (dict or list).
        """
        return self._get_resource("ping", lang=None)

    # ------------------------------------------------------------------
    # Web API leaderboards (skater-stats-leaders / goalie-stats-leaders)
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_categories(
        categories: Optional[Union[str, list[str]]]
    ) -> Optional[str]:
        """Normalize a categories argument to the documented query value.

        A string passes through; a non-empty list of strings is joined with
        commas (the documented multi-category encoding); ``None`` and empty
        collections mean "omit the parameter".
        """
        if categories is None:
            return None
        if isinstance(categories, str):
            return categories
        if isinstance(categories, (list, tuple)):
            if not categories:
                return None
            if not all(isinstance(c, str) for c in categories):
                raise ValueError(
                    "categories must be a string or a list of strings."
                )
            return ",".join(categories)
        raise ValueError("categories must be a string or a list of strings.")

    @staticmethod
    def _validate_leader_limit(limit: Optional[int]) -> Optional[int]:
        """Validate the leaderboard ``limit`` query value (positive int)."""
        if limit is None:
            return None
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer when provided.")
        return limit

    @classmethod
    def _build_leaders_params(
        cls,
        categories: Optional[Union[str, list[str]]],
        limit: Optional[int],
    ) -> Optional[dict[str, Any]]:
        """Build the leaderboard query params (omitted entirely when empty)."""
        params: dict[str, Any] = {}
        normalized_categories = cls._normalize_categories(categories)
        validated_limit = cls._validate_leader_limit(limit)
        if normalized_categories is not None:
            params["categories"] = normalized_categories
        if validated_limit is not None:
            params["limit"] = validated_limit
        return params or None

    @staticmethod
    def _deprecate_leaders_game_type(
        categories: Optional[Union[str, list[str]]],
        game_type: Optional[int],
        route: str,
    ) -> tuple[Optional[Union[str, list[str]]], Optional[int]]:
        """Handle the deprecated unused ``game_type`` argument on /current.

        The old method signature was ``(game_type=2)``; a bare int passed
        positionally is therefore treated as that legacy argument. Neither
        value affects the request — the ``/current`` routes have no
        game-type segment — but both emit a ``DeprecationWarning``.
        """
        message = (
            f"game_type is not used by the {route} route and is ignored; "
            "pass categories=/limit= instead and use the *_by_season "
            "methods for season/game-type leaderboards."
        )
        if isinstance(categories, int) and not isinstance(categories, bool):
            warnings.warn(message, DeprecationWarning, stacklevel=3)
            return None, None
        if game_type is not None:
            warnings.warn(message, DeprecationWarning, stacklevel=3)
        return categories, game_type

    def get_skater_stats_leaders(
        self,
        categories: Optional[Union[str, list[str]]] = None,
        limit: Optional[int] = None,
        game_type: Optional[int] = None,
    ) -> dict[str, Any]:
        """Fetch current skater statistics leaders (Web API).

        Targets the documented ``/v1/skater-stats-leaders/current`` route
        (registry key ``skater_stats_now``). This is the Web API leaderboard;
        the Stats API ``/{lang}/leaders/skaters/{attribute}`` listing is
        served by :meth:`get_skater_leaders`.

        Args:
            categories: Single category (``"goals"``) or list of categories
                (``["goals", "assists"]``, joined with commas). Omitted when
                ``None``.
            limit: Positive result-count limit. Omitted when ``None``.
            game_type: **Deprecated / unused.** The ``/current`` route has no
                game-type segment; the argument is accepted for backward
                compatibility and ignored (raises ``DeprecationWarning``).
                Use :meth:`get_skater_stats_leaders_by_season` for
                season/game-type leaderboards.

        Returns:
            Dictionary with current skater leaders.
        """
        categories, game_type = self._deprecate_leaders_game_type(
            categories, game_type, _SKATER_LEADERS_NOW
        )
        params = self._build_leaders_params(categories, limit)
        response = self._client.get(
            _SKATER_LEADERS_NOW, params=params, web=True
        )
        return response.json()

    def get_goalie_stats_leaders(
        self,
        categories: Optional[Union[str, list[str]]] = None,
        limit: Optional[int] = None,
        game_type: Optional[int] = None,
    ) -> dict[str, Any]:
        """Fetch current goalie statistics leaders (Web API).

        Targets the documented ``/v1/goalie-stats-leaders/current`` route
        (registry key ``goalie_stats_now``).

        Args:
            categories: Single category (``"wins"``) or list of categories.
                Omitted when ``None``.
            limit: Positive result-count limit. Omitted when ``None``.
            game_type: **Deprecated / unused.** The ``/current`` route has no
                game-type segment; the argument is accepted for backward
                compatibility and ignored (raises ``DeprecationWarning``).

        Returns:
            Dictionary with current goalie leaders.
        """
        categories, game_type = self._deprecate_leaders_game_type(
            categories, game_type, _GOALIE_LEADERS_NOW
        )
        params = self._build_leaders_params(categories, limit)
        response = self._client.get(
            _GOALIE_LEADERS_NOW, params=params, web=True
        )
        return response.json()

    def get_skater_stats_leaders_by_season(
        self,
        season: str,
        game_type: int = 2,
        categories: Optional[Union[str, list[str]]] = None,
        limit: Optional[int] = None,
    ) -> dict[str, Any]:
        """Fetch skater statistics leaders for a season and game type.

        Targets the documented
        ``/v1/skater-stats-leaders/{season}/{game-type}`` route (registry key
        ``skater_stats_season_game_type``).

        Args:
            season: Season in format "YYYY-YYYY" (e.g., "2023-2024").
            game_type: Game type ID (2=Regular Season, 3=Playoffs).
            categories: Single category or list of categories (joined with
                commas). Omitted when ``None``.
            limit: Positive result-count limit. Omitted when ``None``.

        Returns:
            Dictionary with skater leaders for the specified season.

        Raises:
            ValueError: If the season format is invalid.
        """
        season_id = validate_season_format(season)
        params = self._build_leaders_params(categories, limit)
        response = self._client.get(
            f"skater-stats-leaders/{season_id}/{game_type}",
            params=params,
            web=True,
        )
        return response.json()

    def get_goalie_stats_leaders_by_season(
        self,
        season: str,
        game_type: int = 2,
        categories: Optional[Union[str, list[str]]] = None,
        limit: Optional[int] = None,
    ) -> dict[str, Any]:
        """Fetch goalie statistics leaders for a season and game type.

        Targets the documented
        ``/v1/goalie-stats-leaders/{season}/{game-type}`` route (registry key
        ``goalie_stats_season_game_type``).

        Args:
            season: Season in format "YYYY-YYYY" (e.g., "2023-2024").
            game_type: Game type ID (2=Regular Season, 3=Playoffs).
            categories: Single category or list of categories (joined with
                commas). Omitted when ``None``.
            limit: Positive result-count limit. Omitted when ``None``.

        Returns:
            Dictionary with goalie leaders for the specified season.

        Raises:
            ValueError: If the season format is invalid.
        """
        season_id = validate_season_format(season)
        params = self._build_leaders_params(categories, limit)
        response = self._client.get(
            f"goalie-stats-leaders/{season_id}/{game_type}",
            params=params,
            web=True,
        )
        return response.json()
