# CausalPhylo

> Identification over knowledge graphs, where not every edge has earned its arrow.

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Non--Commercial-orange.svg)](LICENSE)

**CausalPhylo** implements Pearl's backdoor criterion over
[NetworkX](https://networkx.org) directed graphs, together with the
admissibility rules that decide which edges may carry a causal claim in the
first place. It was extracted from [NeoRx](https://github.com/Neoforge-Labs/neorx),
where it is the engine behind causal drug-target identification.

It has one runtime dependency: NetworkX.

## The problem it solves

A graph assembled from public sources mixes two kinds of edge.

Some assert a **mechanism with a direction** — a curated regulatory
interaction where someone has established that A acts on B. Others assert only
that two things **occur together**: a literature co-mention, membership of a
shared pathway, an undirected protein interaction whose arrow exists only
because one protein landed in the first column of an API response.

Running do-calculus over the second kind assumes the very thing a causal
method is supposed to establish. So CausalPhylo partitions the edges first,
and identification runs only on the causal-admissible subgraph. Associational
edges are not discarded — they stop being arrows.

Gene → disease edges are admitted only on genetic evidence. A germline variant
is randomised at conception, so a genetic association carries a
natural-experiment warrant that a co-mention does not — the Mendelian
randomisation argument ([Davey Smith & Ebrahim, 2003](https://doi.org/10.1093/ije/dyg070),
*Int J Epidemiol* 32:1–22). That warrant is what earns the arrow.

## Install

```bash
uv pip install causalphylo
```

## Use

```python
import networkx as nx
from causalphylo import find_adjustment_set

# The textbook confounding shape: U is a common cause of X and D.
G = nx.DiGraph()
G.add_edge("U", "X", edge_type="activates", evidence_class="regulatory")
G.add_edge("U", "D", edge_type="associated_with", evidence_class="genetic_association")
G.add_edge("X", "D", edge_type="associated_with", evidence_class="genetic_association")

verdict = find_adjustment_set(G, "X", "D")

verdict.identifiable      # True
verdict.adjustment_set    # ('U',)
verdict.reason.value      # 'identifiable_by_adjustment'
```

`find_adjustment_set` takes the **full** graph. Restriction to the admissible
subgraph and to its acyclic core happens inside, so no caller can forget it.

Edges carry two attributes that the admissibility rules read: `edge_type` and
`evidence_class`. Nothing else about your graph is assumed — CausalPhylo has no
domain model of its own.

## It tells you *why* it failed

A method that reports only pass/fail gives you a pile of prose to read. These
reasons are a closed enum, so a run's failures aggregate into a distribution:

| `reason` | Meaning |
|---|---|
| `identifiable_by_adjustment` | A valid backdoor adjustment set was found |
| `identifiable_trivially` | No confounder appears in the graph (see the caveat below) |
| `no_causal_path` | No admissible directed path from treatment to outcome |
| `cyclic_component` | Treatment or outcome sits in a feedback loop; d-separation is undefined there |
| `no_valid_adjustment_set` | Confounders exist, but no admissible subset blocks every backdoor path |
| `treatment_absent` / `outcome_absent` | Node is not in the admissible subgraph |

**The trivial case is not a clean bill of health.** A knowledge graph is
open-world: a missing edge is missing knowledge, not evidence of no
confounding. So a trivial verdict carries `n_near_miss_confounders` — how many
nodes regulate the treatment and have *some* association with the outcome that
fell short of admissibility. A target with many near misses is fragile. This is
the same move as an E-value in observational epidemiology: not "there is no
confounding", but "here is how much it would take to break this".

`search_truncated` reports when the subset search hit its bound
(`MAX_ADJUSTMENT_SET_SIZE`, `MAX_CANDIDATE_POOL`) rather than exhausting the
space. It is never hidden.

## API

**`causalphylo.graph_semantics`** — which edges may carry a causal claim

| | |
|---|---|
| `is_causal_admissible(attrs)` | Whether an edge with these attributes may carry a causal claim |
| `causal_subgraph(G)` | The subgraph of admissible edges, attributes preserved |
| `cyclic_components(G)` | Strongly connected components with cycles, self-loops included |
| `acyclic_core(G)` | A DAG carved out of a cyclic graph, plus the nodes removed |
| `CAUSAL_EDGE_TYPES`, `GENETIC_EVIDENCE_CLASSES` | The admissibility vocabularies |

**`causalphylo.backdoor`** — identification on the admissible subgraph

| | |
|---|---|
| `find_adjustment_set(G, treatment, outcome)` | Search for a minimal valid adjustment set |
| `satisfies_backdoor(G, treatment, outcome, adjustment)` | Whether `adjustment` (a frozenset) satisfies the criterion |
| `mutilated_graph(G, treatment)` | G with edges leaving the treatment removed |
| `confounding_sensitivity(dag, full_graph, treatment, outcome)` | Near-miss confounder count behind a trivial verdict |

Cyclic nodes are not silently repaired. `acyclic_core` removes every node in a
feedback loop and names them in `excluded`, because `nx.is_d_separator` requires
a DAG of the whole graph — not merely of the neighbourhood under test.

## Development

```bash
uv venv && uv pip install -e . --group dev
.venv/bin/python -m pytest
```

## Licence

CausalPhylo Source Available License — non-commercial use permitted, commercial
use requires a separate licence. See [LICENSE](LICENSE).

Copyright (c) 2026 Kelyn Paul Njeri, NeoForge Labs.
