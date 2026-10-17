# CausalPhylo

> Identification over knowledge graphs, where not every edge has earned its arrow.

CausalPhylo implements **Pearl's backdoor criterion** over
[NetworkX](https://networkx.org) directed graphs, together with the
admissibility rules that decide which edges may carry a causal claim in the
first place.

It has one runtime dependency: NetworkX. It has no domain model of its own.

## The problem it solves

A graph assembled from public sources mixes two kinds of edge.

Some assert a **mechanism with a direction** — a curated regulatory interaction
where someone has established that A acts on B. Others assert only that two
things **occur together**: a literature co-mention, membership of a shared
pathway, an undirected protein interaction whose arrow exists only because one
protein landed in the first column of an API response.

Running do-calculus over the second kind assumes the very thing a causal method
is supposed to establish.

So CausalPhylo partitions the edges first, and identification runs only on the
causal-admissible subgraph. Associational edges are not discarded — they stop
being arrows. See [Which edges earn an arrow](admissibility.md).

## Install

```bash
uv pip install causalphylo
```

Requires Python 3.12 or newer.

## Thirty seconds

The textbook confounding shape: `U` is a common cause of both the treatment
`X` and the outcome `D`, so the effect of `X` on `D` is identifiable only after
adjusting for `U`.

```python
import networkx as nx
from causalphylo import find_adjustment_set

G = nx.DiGraph()
G.add_edge("U", "X", edge_type="activates",       evidence_class="regulatory")
G.add_edge("U", "D", edge_type="associated_with", evidence_class="genetic_association")
G.add_edge("X", "D", edge_type="associated_with", evidence_class="genetic_association")

verdict = find_adjustment_set(G, "X", "D")
```

```python
verdict.identifiable    # True
verdict.adjustment_set  # ('U',)
verdict.reason.value    # 'identifiable_by_adjustment'
```

Every edge carries two attributes that the admissibility rules read:
`edge_type` and `evidence_class`. Nothing else about your graph is assumed.

`find_adjustment_set` takes the **full** graph. Restriction to the admissible
subgraph and to its acyclic core happens inside, so no caller can forget that
step.

## It tells you why it failed

A method that reports only pass or fail hands you a pile of prose to read.
CausalPhylo's reasons are a closed enum, so a run's failures aggregate into a
distribution instead:

```python
>>> from causalphylo import IdentificationReason
>>> [r.value for r in IdentificationReason]
['identifiable_by_adjustment', 'identifiable_trivially', 'no_causal_path',
 'cyclic_component', 'no_valid_adjustment_set', 'treatment_absent',
 'outcome_absent']

```

Each one is explained in [Identification](identification.md), including why a
trivial verdict is **not** a clean bill of health.

## Where it comes from

CausalPhylo was extracted from [NeoRx](https://github.com/Neoforge-Labs/neorx),
a causal drug-target discovery platform, where it is the engine behind target
identification. It carries the commit history of that work.

The biomedical vocabulary in the defaults reflects that origin — gene-to-disease
edges, genetic evidence classes. The algorithms do not care: they operate on
edge attributes and graph structure.

## Citing

If you use CausalPhylo in research, cite NeoRx — see
[its citation file](https://github.com/Neoforge-Labs/neorx/blob/main/CITATION.cff).
