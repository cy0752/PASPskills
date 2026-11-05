# Changelog

All notable changes to this project will be documented in this file.

This project uses semantic versioning while it is pre-1.0:
- Minor releases (`0.x.0`) may add workflows, reference coverage, templates, scripts, or installation behavior.
- Patch releases (`0.x.y`) should be backward-compatible fixes to docs, references, routing, verifier behavior, or installer bugs.
- Breaking changes before `1.0.0` should be called out explicitly in the release notes.

## [Unreleased]

## [0.1.15] - 2026-11-05

### Changed

- Install the complete runtime package directly into
  `.agents/skills/pasp-helper/` by default, sharing it with Claude through a
  project-local link. New installations no longer add a root `skills/`
  directory or legacy `.codex/skills/` aliases.
- Default to an independent copy; retain `--copy` and offer explicit `--link`
  for development installations that follow an external source package.
- Resolve knowledge and subskill resources from the loaded helper root,
  including delegated verifier instructions and shell examples.
- Update installation, upgrade and authoring documentation for this layout.

### Fixed

- Migrate recognized legacy root installations with `--force`, retaining a
  backup of real old package files outside skill discovery directories.
  Preserve unrelated root folders, selected source packages and user-home
  configuration.

The scientific helper implementations and parameter contracts are unchanged.

## [0.1.14] - 2026-11-02

### Added

- Synchronize the evolved runtime package: L2 four-state geometry mapping,
  primitive-cell preparation, input preflight and native delivery checks.
- L3 geometry/input preparation, method-6 batching, dependency checks, fitting
  limits, study contracts, reconstruction checks and final handoff helpers,
  with bundled regression tests and workflow integrity guidance.

### Changed

- Refine L2/L3 routing and verifier contracts, L3 fitting references and
  prescribed-spin direction-constraint requirements, and L4 model handoff gates.
- Document runtime/helper dependencies, upgrades and the distinction between
  the main-branch package version and separately published GitHub Releases.

### Fixed

- Install discoverable Codex skills under `.agents/skills/`, retaining
  `.codex/skills/` compatibility aliases and Claude project entries.
- Preserve the runtime source when an installation targets its own directory;
  resolve source symlinks before copying so `--copy` creates an independent
  runtime package.

The synchronized software checks do not establish independent scientific
generalization, MC/MD validity or performance claims.

## [0.1.0] - 2026-06-24

### Added

- Initial version tracking with `VERSION`, `CHANGELOG.md`, and `LICENSE`.
- Initial public release baseline for the PASP skills package.
- Runtime skills under `skills/` for PASP workflow guidance and reference lookup.
- Installation script for setting up the PASP skills package in target projects.
- Workflow coverage for spin models, effective Hamiltonian, Monte Carlo, dynamics, GA search, tight binding, and spin-induced polarization.
- Self-contained runtime knowledge under `skills/knowledge/`, including workflows, reference material, templates, and helper scripts.
