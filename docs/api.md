# API reference

Everything below is re-exported from the top level, so
`from causalphylo import find_adjustment_set` and
`from causalphylo.backdoor import find_adjustment_set` are equivalent.

## causalphylo.graph_semantics

Which edges may carry a causal claim. See
[Which edges earn an arrow](admissibility.md).

::: causalphylo.graph_semantics
    options:
      show_root_heading: false
      members:
        - is_causal_admissible
        - causal_subgraph
        - cyclic_components
        - acyclic_core
        - AcyclicCore

### Vocabularies

`CAUSAL_EDGE_TYPES`
:   Frozenset of `edge_type` values that assert a directed mechanism.

`GENETIC_EVIDENCE_CLASSES`
:   Frozenset of `evidence_class` values that license a gene-to-disease arrow.

## causalphylo.backdoor

Identification on the admissible subgraph. See
[Identification](identification.md).

::: causalphylo.backdoor
    options:
      show_root_heading: false
      members:
        - find_adjustment_set
        - Identification
        - IdentificationReason
        - satisfies_backdoor
        - mutilated_graph
        - confounding_sensitivity

### Search bounds

`MAX_ADJUSTMENT_SET_SIZE`
:   Largest adjustment set the search will consider. Default `3`.

`MAX_CANDIDATE_POOL`
:   Largest candidate pool the search will draw from. Default `20`.

Reaching either bound sets `Identification.search_truncated`.
