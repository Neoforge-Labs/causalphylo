"""
CausalPhylo — identification over mixed-evidence knowledge graphs.

Two questions, kept separate on purpose.

:mod:`causalphylo.graph_semantics` asks which edges may carry a causal
claim at all. A graph assembled from public sources mixes mechanistic,
directed assertions with mere co-occurrence; running do-calculus over
the second kind assumes the very thing the method is meant to establish.

:mod:`causalphylo.backdoor` asks, on the admissible subgraph, whether a
causal effect is identifiable — Pearl's backdoor criterion, reporting
*why* identification failed rather than merely that it did.

Both operate on plain :class:`networkx.DiGraph` objects whose edges
carry ``edge_type`` and ``evidence_class`` attributes. The package has
no domain model of its own and no dependency beyond NetworkX.

``find_adjustment_set`` takes the full graph and restricts to the
admissible acyclic core itself, so no caller can forget that step.

>>> import networkx as nx
>>> from causalphylo import find_adjustment_set
>>> G = nx.DiGraph()
>>> G.add_edge("U", "X", edge_type="activates", evidence_class="regulatory")
>>> G.add_edge("U", "D", edge_type="associated_with",
...            evidence_class="genetic_association")
>>> G.add_edge("X", "D", edge_type="associated_with",
...            evidence_class="genetic_association")
>>> verdict = find_adjustment_set(G, "X", "D")
>>> verdict.identifiable
True
>>> verdict.adjustment_set
('U',)
>>> verdict.reason.value
'identifiable_by_adjustment'
"""

from __future__ import annotations

from causalphylo.backdoor import (
    MAX_ADJUSTMENT_SET_SIZE,
    MAX_CANDIDATE_POOL,
    Identification,
    IdentificationReason,
    confounding_sensitivity,
    find_adjustment_set,
    mutilated_graph,
    satisfies_backdoor,
)
from causalphylo.graph_semantics import (
    CAUSAL_EDGE_TYPES,
    GENETIC_EVIDENCE_CLASSES,
    AcyclicCore,
    acyclic_core,
    causal_subgraph,
    cyclic_components,
    is_causal_admissible,
)

__version__ = "0.1.0"

__all__ = [
    "CAUSAL_EDGE_TYPES",
    "GENETIC_EVIDENCE_CLASSES",
    "MAX_ADJUSTMENT_SET_SIZE",
    "MAX_CANDIDATE_POOL",
    "AcyclicCore",
    "Identification",
    "IdentificationReason",
    "__version__",
    "acyclic_core",
    "causal_subgraph",
    "confounding_sensitivity",
    "cyclic_components",
    "find_adjustment_set",
    "is_causal_admissible",
    "mutilated_graph",
    "satisfies_backdoor",
]
