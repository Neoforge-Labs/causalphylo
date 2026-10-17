# Changelog

All notable changes to CausalPhylo will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] — 2026-10-17

First release as a standalone package.

`graph_semantics` and `backdoor` were written inside
[NeoRx](https://github.com/Neoforge-Labs/neorx) and extracted here with their
commit history. They were the part of NeoRx's causal code that depended on
nothing but NetworkX, while NeoRx itself imported admissibility back out of
them — a cycle one distribution can hold and two cannot. So the boundary was
drawn where the dependency graph allows a real one.

### Added

- `causalphylo.graph_semantics` — `is_causal_admissible`, `causal_subgraph`,
  `cyclic_components`, `acyclic_core`, and the `CAUSAL_EDGE_TYPES` /
  `GENETIC_EVIDENCE_CLASSES` vocabularies. Which edges may carry a causal
  claim, and a DAG carved out of a graph with feedback loops that names what
  it removed.
- `causalphylo.backdoor` — `find_adjustment_set`, `satisfies_backdoor`,
  `mutilated_graph`, `confounding_sensitivity`, and the `Identification` /
  `IdentificationReason` verdict types. Pearl's backdoor criterion, reporting
  *why* identification failed as a closed enum rather than as prose, and
  carrying `n_near_miss_confounders` so a trivial verdict cannot be mistaken
  for an absence of confounding.
- Documentation at [causalphylo.neoforgelabs.tech](https://causalphylo.neoforgelabs.tech/).
  Every `>>>` example in it runs as part of the test suite.

### Changed from the NeoRx original

Behaviour is unchanged. Three things were cleaned up rather than carried:

- `IdentificationReason` is a `StrEnum` instead of inheriting `str` and `Enum`
  separately. Member values and identity comparisons are identical; every
  consumer read `.value` or compared with `is`, which was checked before the
  change and is covered by NeoRx's own suite.
- A test asserting that `Identification` is immutable caught a blind
  `Exception`, which a typo would also have satisfied. It names
  `FrozenInstanceError` now.
- An unused import of `confounding_sensitivity` is gone. Both of its tests
  reach it through `find_adjustment_set`; it still has no direct unit test.
