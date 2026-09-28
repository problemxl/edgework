"""Coverage-contract tests built on :mod:`tests.endpoint_manifest`.

The contract asserts, for the whole documented API surface:

1. **Completeness** — every registry entry appears in the manifest (or in the
   documented exclusion list) and every manifest entry references an existing,
   callable method.
2. **Route contract** — invoking each manifest entry's client method produces
   exactly one HTTP request whose full URL equals the URL derived from the
   registry template (host + ``/v1`` or language prefix + path-param
   substitution), with query parameters traveling in ``params`` and the
   documented return type produced.
3. **Language handling** — methods accepting ``lang=`` produce the documented
   language-prefixed Stats API URL for alternate languages.
4. **Live OpenAPI comparison (opt-in, non-blocking)** — with
   ``EDGEWORK_OPENAPI_LIVE=1``, the manifest is compared against the live
   ``/model/v1/openapi.json`` document; mismatches are reported as warnings,
   never failures (the live document is unofficial and may change).
"""

import importlib
import json
import os
import re
import urllib.request
import warnings
from string import Formatter
from unittest.mock import Mock
from urllib.parse import urlparse

import pytest

from edgework.const import API_VERSION, BASE_WEB_URL, STATS_API_URL
from edgework.endpoints import API_PATH, get_endpoint
from edgework.http_client import HttpClient
from tests.endpoint_manifest import (
    ENDPOINT_MANIFEST,
    REGISTRY_EXCLUSIONS,
    ManifestEntry,
)

# ---------------------------------------------------------------------------
# Invocation harness
# ---------------------------------------------------------------------------


class _FakeResponse:
    """Minimal stand-in for the ``httpx.Response`` surface clients consume."""

    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200
        self.text = "{}"

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


def _resolve(target: str):
    """Resolve a ``module.Class.method`` dotted path to a bound-callable pair."""
    module_name, class_name, method_name = target.rsplit(".", 2)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cls, getattr(cls, method_name), method_name


def _invoke(entry: ManifestEntry, extra_call: dict | None = None):
    """Invoke a manifest entry against a real ``HttpClient`` whose inner
    ``httpx.Client`` is mocked, returning ``(result, inner_mock)``.

    Using the real ``HttpClient`` means the asserted URL is the one the
    library actually builds (host, ``/v1`` prefix, language prefix, legacy
    prefix stripping) — not a re-implementation of that logic.
    """
    call = dict(entry.call)
    if extra_call:
        call.update(extra_call)

    http = HttpClient()
    real_inner = http._client
    inner = Mock()
    inner.get.return_value = _FakeResponse(entry.payload)
    http._client = inner
    try:
        cls, _, method_name = _resolve(entry.target)
        instance = cls(http)
        result = getattr(instance, method_name)(*entry.args, **call)
    finally:
        http._client = real_inner
        real_inner.close()
    return result, inner


# ---------------------------------------------------------------------------
# Expected-URL derivation from the registry templates
# ---------------------------------------------------------------------------

_FORMATTER = Formatter()


def _substitute(route: str, values: dict) -> str:
    """Substitute ``{placeholder}`` fields in a registry route template."""
    parts = []
    for literal, field_name, _, _ in _FORMATTER.parse(route):
        parts.append(literal)
        if field_name is None:
            continue
        if field_name not in values:
            raise KeyError(
                f"No value provided for placeholder {{{field_name}}} in {route!r}"
            )
        parts.append(str(values[field_name]))
    return "".join(parts)


def _expected_url(entry: ManifestEntry, lang: str | None = None) -> str:
    """Derive the full documented URL for a manifest entry from the registry."""
    route = get_endpoint(entry.registry_key)
    values = {"API_VERSION": API_VERSION, **entry.endpoint_params}
    if entry.web:
        return BASE_WEB_URL + _substitute(route, values)
    values["lang"] = (entry.lang if lang is None else lang) or ""
    return STATS_API_URL + _substitute(route, values).lstrip("/")


def _placeholders(route: str) -> set[str]:
    return {
        field_name
        for _, field_name, _, _ in _FORMATTER.parse(route)
        if field_name is not None
    }


ALL_ENTRIES: list[ManifestEntry] = sorted(
    ENDPOINT_MANIFEST.values(), key=lambda entry: entry.registry_key
)
ALL_KEYS = [entry.registry_key for entry in ALL_ENTRIES]


# ---------------------------------------------------------------------------
# 1. Completeness: registry ↔ manifest ↔ exclusions
# ---------------------------------------------------------------------------


class TestCoverageCompleteness:
    """Every documented registry route is implemented and manifested."""

    def test_every_registry_entry_is_in_manifest_or_excluded(self):
        missing = sorted(
            set(API_PATH) - set(ENDPOINT_MANIFEST) - set(REGISTRY_EXCLUSIONS)
        )
        assert missing == [], (
            "Registry routes without a coverage-manifest entry "
            "(implement them or document the exclusion): " + ", ".join(missing)
        )

    def test_every_manifest_key_exists_in_registry(self):
        unknown = sorted(set(ENDPOINT_MANIFEST) - set(API_PATH))
        assert unknown == [], (
            "Manifest keys not present in the endpoint registry: "
            + ", ".join(unknown)
        )

    def test_exclusions_reference_registry_keys(self):
        unknown = sorted(set(REGISTRY_EXCLUSIONS) - set(API_PATH))
        assert unknown == [], (
            "Exclusions referencing non-existent registry keys: "
            + ", ".join(unknown)
        )

    def test_no_key_is_both_manifested_and_excluded(self):
        overlap = sorted(set(ENDPOINT_MANIFEST) & set(REGISTRY_EXCLUSIONS))
        assert overlap == [], f"Keys both manifested and excluded: {overlap}"

    def test_manifest_size_matches_documented_route_count(self):
        documented = len(API_PATH) - len(REGISTRY_EXCLUSIONS)
        assert len(ENDPOINT_MANIFEST) == documented
        assert documented > 0


class TestManifestIntegrity:
    """Manifest entries reference existing methods and consistent metadata."""

    def test_targets_resolve_to_callables(self):
        broken = []
        for entry in ALL_ENTRIES:
            try:
                cls, func, _ = _resolve(entry.target)
            except (ImportError, AttributeError) as exc:
                broken.append(f"{entry.registry_key} -> {entry.target}: {exc}")
                continue
            if not callable(func):
                broken.append(f"{entry.registry_key} -> {entry.target}: not callable")
        assert broken == [], "Unresolvable manifest targets:\n" + "\n".join(broken)

    def test_also_implemented_by_resolve_to_callables(self):
        broken = []
        for entry in ALL_ENTRIES:
            for target in entry.also_implemented_by:
                try:
                    _, func, _ = _resolve(target)
                except (ImportError, AttributeError) as exc:
                    broken.append(f"{entry.registry_key}: {target}: {exc}")
                    continue
                if not callable(func):
                    broken.append(f"{entry.registry_key}: {target}: not callable")
        assert broken == [], "Unresolvable duplicate accessors:\n" + "\n".join(broken)

    def test_route_family_matches_web_flag(self):
        mismatched = []
        for entry in ALL_ENTRIES:
            route = get_endpoint(entry.registry_key)
            if entry.web:
                ok = route.startswith(("/{API_VERSION}", "/model/{API_VERSION}"))
            else:
                ok = route.startswith("/{lang}") or route == "/ping"
            if not ok:
                mismatched.append(f"{entry.registry_key}: {route}")
        assert mismatched == [], (
            "Web-vs-Stats routing disagrees with the registry template:\n"
            + "\n".join(mismatched)
        )

    def test_endpoint_params_cover_exactly_the_route_placeholders(self):
        mismatched = []
        for entry in ALL_ENTRIES:
            route = get_endpoint(entry.registry_key)
            placeholders = _placeholders(route) - {"API_VERSION", "lang"}
            provided = set(entry.endpoint_params)
            if placeholders != provided:
                mismatched.append(
                    f"{entry.registry_key}: placeholders {sorted(placeholders)} "
                    f"!= endpoint_params {sorted(provided)}"
                )
        assert mismatched == [], (
            "Sample path parameters do not match route placeholders:\n"
            + "\n".join(mismatched)
        )

    def test_expected_params_are_encodable(self):
        bad = []
        for entry in ALL_ENTRIES:
            if not entry.expected_params:
                continue
            for key, value in entry.expected_params.items():
                if not isinstance(key, str) or not isinstance(
                    value, (str, int, float, bool)
                ):
                    bad.append(f"{entry.registry_key}: {key!r}={value!r}")
        assert bad == [], "Non-encodable expected query values:\n" + "\n".join(bad)

    def test_stats_lang_defaults_are_declared(self):
        undeclared = [
            entry.registry_key
            for entry in ALL_ENTRIES
            if not entry.web and entry.lang is None and entry.registry_key != "stats_ping"
        ]
        assert undeclared == []


# ---------------------------------------------------------------------------
# 2. Route contract (parametrized over every documented route)
# ---------------------------------------------------------------------------


def _assert_params(actual, expected) -> None:
    """Query parameters must travel in ``params`` — exact values when declared."""
    if not expected:
        assert actual in (None, {}), f"Expected no query parameters, got {actual!r}"
    else:
        assert actual == expected, (
            f"Query parameters {actual!r} != documented {expected!r}"
        )


@pytest.mark.parametrize("key", ALL_KEYS)
def test_route_contract(key):
    """Every documented route: host+path identity, single request, params in
    ``params``, Web-vs-Stats host, and the documented return type."""
    entry = ENDPOINT_MANIFEST[key]

    result, inner = _invoke(entry)

    # Exactly one HTTP request per canonical route invocation.
    assert inner.get.call_count == 1, (
        f"{key}: expected exactly one HTTP request, got {inner.get.call_count}"
    )

    # Full-URL identity against the documented registry template.
    call_args = inner.get.call_args
    actual_url = call_args.args[0]
    expected_url = _expected_url(entry)
    assert actual_url == expected_url, (
        f"{key}: request URL {actual_url!r} != documented {expected_url!r}"
    )

    # Web-vs-Stats routing: the request hits the documented host.
    if entry.web:
        assert actual_url.startswith(BASE_WEB_URL), (
            f"{key}: Web API route must target {BASE_WEB_URL}"
        )
    else:
        assert actual_url.startswith(STATS_API_URL), (
            f"{key}: Stats API route must target {STATS_API_URL}"
        )

    # Query encoding: parameters never embedded in the route string; the
    # documented values travel through the ``params`` argument.
    assert "?" not in actual_url, (
        f"{key}: query string embedded in route ({actual_url!r})"
    )
    _assert_params(call_args.kwargs.get("params"), entry.expected_params)

    # Return type matches the documented contract.
    if entry.returns is not None:
        assert isinstance(result, entry.returns), (
            f"{key}: return type {type(result).__name__} not in "
            f"{[t.__name__ for t in entry.returns]}"
        )


@pytest.mark.parametrize(
    "key",
    [entry.registry_key for entry in ALL_ENTRIES if entry.lang_kwarg],
)
def test_route_contract_alternate_language(key):
    """Language-capable Stats methods render the alternate-language URL."""
    entry = ENDPOINT_MANIFEST[key]

    _, inner = _invoke(entry, extra_call={"lang": "fr"})

    assert inner.get.call_count == 1
    actual_url = inner.get.call_args.args[0]
    expected_url = _expected_url(entry, lang="fr")
    assert actual_url == expected_url, (
        f"{key}: French request URL {actual_url!r} != documented {expected_url!r}"
    )
    assert "/fr/" in actual_url, f"{key}: language segment missing ({actual_url!r})"


# ---------------------------------------------------------------------------
# 3. Live OpenAPI comparison (opt-in, non-blocking)
# ---------------------------------------------------------------------------

LIVE_OPENAPI_ENV = "EDGEWORK_OPENAPI_LIVE"


def _openapi_enabled() -> bool:
    return os.environ.get(LIVE_OPENAPI_ENV, "").lower() in ("1", "true", "yes")


def _path_template_to_regex(template: str) -> str:
    """Turn a URL path template (``/v1/x/{id}``) into a match regex."""
    return re.sub(r"\{[^}]+\}", "[^/]+", template)


@pytest.mark.skipif(
    not _openapi_enabled(),
    reason=(
        f"opt-in live check: set {LIVE_OPENAPI_ENV}=1 to compare the manifest "
        "against the live /model/v1/openapi.json document"
    ),
)
def test_live_openapi_comparison_non_blocking():
    """Compare the manifest against the live OpenAPI document.

    Non-blocking by design: the live document is unofficial and may change at
    any time, so differences are reported as warnings instead of failures.
    """
    spec_url = (
        BASE_WEB_URL
        + _substitute(get_endpoint("openapi_spec"), {"API_VERSION": API_VERSION})
    )
    try:
        with urllib.request.urlopen(spec_url, timeout=15) as response:  # noqa: S310
            document = json.load(response)
    except Exception as exc:  # pragma: no cover - depends on live network
        pytest.skip(f"Live OpenAPI document unavailable ({exc}); skipping comparison")

    live_paths = set(document.get("paths", {}))
    manifest_paths = {
        urlparse(_expected_url(entry)).path
        for entry in ALL_ENTRIES
        if entry.web
    }

    def _covered(template: str, paths: set[str]) -> bool:
        regex = _path_template_to_regex(template)
        return any(re.fullmatch(regex, candidate) for candidate in paths)

    undocumented = sorted(p for p in live_paths if not _covered(p, manifest_paths))
    stale = sorted(m for m in manifest_paths if not _covered(m, live_paths))

    if undocumented or stale:  # pragma: no cover - depends on live network
        warnings.warn(
            "Live OpenAPI comparison (non-blocking): "
            f"live routes missing from the manifest: {undocumented}; "
            f"manifest routes absent from the live document: {stale}. "
            "Verify the NHL API documentation and update the registry/manifest "
            "if the routes are real.",
            stacklevel=1,
        )
