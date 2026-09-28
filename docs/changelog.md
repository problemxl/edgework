# Changelog

All notable changes to Edgework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No unreleased changes.

## [0.11.0] - 2026-09-28

### Added
- Complete NHL endpoint coverage with a registry-to-client coverage manifest and contract tests.
- NHL Edge support through `client.edge`, including landing, detail, comparison, metric detail, and top-10 endpoints.
- Goal Visualizer puck and player tracking frames through `get_goal_frames()` and frame helpers.
- Research and API documentation for NHL Edge and Goal Visualizer routes.
- Comprehensive documentation site with auto-generated API docs.
- GitHub Pages deployment with MkDocs.
- Advanced usage examples and patterns.
- Complete API reference documentation.

### Changed
- Extended NHL clients, endpoint routing, HTTP handling, and models for the complete endpoint surface.
- Documentation is auto-generated from docstrings using mkdocstrings.
- Improved documentation navigation and organization.

### Tests
- Full suite: 967 passed, 9 skipped.

## [Previous Versions]

For version history prior to this documentation update, please refer to git commit history or GitHub releases.

---

## Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities
