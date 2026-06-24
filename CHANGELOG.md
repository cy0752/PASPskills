# Changelog

All notable changes to this project will be documented in this file.

This project uses semantic versioning while it is pre-1.0:
- Minor releases (`0.x.0`) may add workflows, reference coverage, templates, scripts, or installation behavior.
- Patch releases (`0.x.y`) should be backward-compatible fixes to docs, references, routing, verifier behavior, or installer bugs.
- Breaking changes before `1.0.0` should be called out explicitly in the release notes.

## [Unreleased]

### Added

- Initial version tracking with `VERSION`, `CHANGELOG.md`, and `LICENSE`.

## [0.1.0] - 2026-06-24

### Added

- Initial public release baseline for the PASP skills package.
- Runtime skills under `skills/` for PASP workflow guidance and reference lookup.
- Installation script for setting up the PASP skills package in target projects.
- Workflow coverage for spin models, effective Hamiltonian, Monte Carlo, dynamics, GA search, tight binding, and spin-induced polarization.
- Self-contained runtime knowledge under `skills/knowledge/`, including workflows, reference material, templates, and helper scripts.
