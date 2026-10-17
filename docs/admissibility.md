# Which edges earn an arrow

An arrow in a causal diagram is a claim: intervene on the tail and the head
responds. Most edges in a knowledge graph were never asserted with that
strength. CausalPhylo's first job is to say which ones were.

## The rule

An edge is causal-admissible when either:

1. its `edge_type` names a **directed mechanism** — someone has asserted that
   the source acts on the target; or
2. it is a gene-to-disease **association backed by genetic evidence**.

```python
>>> from causalphylo import CAUSAL_EDGE_TYPES, GENETIC_EVIDENCE_CLASSES
>>> sorted(CAUSAL_EDGE_TYPES)
['activates', 'causes', 'downregulates', 'inhibits', 'phosphorylates',
 'regulates', 'upregulates']
>>> sorted(GENETIC_EVIDENCE_CLASSES)
['genetic_association', 'somatic_mutation']

```

Everything else is associational.

```python
from causalphylo import is_causal_admissible

is_causal_admissible({"edge_type": "activates",       "evidence_class": "regulatory"})
is_causal_admissible({"edge_type": "associated_with", "evidence_class": "genetic_association"})
is_causal_admissible({"edge_type": "associated_with", "evidence_class": "literature"})
is_causal_admissible({"edge_type": "interacts_with",  "evidence_class": "regulatory"})
is_causal_admissible({"edge_type": "participates_in", "evidence_class": ""})
```

| Edge | Admissible |
|---|---|
| `activates` / `regulatory` | **True** |
| `associated_with` / `genetic_association` | **True** |
| `associated_with` / `literature` | False |
| `interacts_with` / `regulatory` (STRING) | False |
| `participates_in` (pathway membership) | False |

## Why genetic evidence is the exception

A germline variant is randomised at conception. A genetic association
therefore carries a natural-experiment warrant that a co-mention does not —
this is the Mendelian randomisation argument
([Davey Smith & Ebrahim, 2003](https://doi.org/10.1093/ije/dyg070),
*Int J Epidemiol* 32:1–22). That warrant is what earns the arrow.

A literature co-mention earns nothing. Two genes appear in one abstract for
reasons that include a shared assay, a shared author, and a shared review.

## Why an undirected interaction earns nothing

!!! note "STRING interactions are not arrows"
    A protein–protein interaction is symmetric. When it reaches you as a
    directed edge, the direction is an artefact of which protein the API
    returned first. Admitting it would let the ordering of a response
    determine a causal conclusion.

## Pruning the graph

`causal_subgraph` keeps the admissible edges with their attributes intact, and
drops nodes left with no admissible edge — a node participating in no causal
relation can be neither treatment, outcome, nor confounder.

```python
import networkx as nx
from causalphylo import causal_subgraph

G = nx.DiGraph()
G.add_edge("U", "X",         edge_type="activates",       evidence_class="regulatory")
G.add_edge("X", "D",         edge_type="associated_with", evidence_class="genetic_association")
G.add_edge("P", "D",         edge_type="associated_with", evidence_class="literature")
G.add_edge("X", "pathway:1", edge_type="participates_in", evidence_class="")

sub = causal_subgraph(G)
```

```python
sorted(G.nodes())     # ['D', 'P', 'U', 'X', 'pathway:1']
sorted(sub.nodes())   # ['D', 'U', 'X']
sorted(sub.edges())   # [('U', 'X'), ('X', 'D')]
```

`P` and `pathway:1` are gone. The association that linked `P` to `D` still
exists in your own graph and can still contribute to evidence scoring — it is
simply not an arrow here.

## Feedback loops

`nx.is_d_separator` requires a DAG of the **whole** graph, not merely of the
neighbourhood under test. Biological regulatory networks are full of feedback,
so cyclic nodes have to come out — and `acyclic_core` names the ones it
removed rather than silently repairing them.

```python
from causalphylo import acyclic_core

G = nx.DiGraph()
G.add_edge("a", "b")   # a and b form a 2-cycle
G.add_edge("b", "a")
G.add_edge("b", "c")
G.add_edge("c", "d")

core = acyclic_core(G)
```

```python
sorted(core.excluded)                             # ['a', 'b']
sorted(core.dag.nodes())                          # ['c', 'd']
nx.is_directed_acyclic_graph(core.dag)            # True
```

Self-loops count as cycles. A node that regulates itself is excluded on the
same grounds.

Identification involving an excluded node reports
`cyclic_component` rather than guessing an acyclic orientation. Choosing a
direction to break the loop would be inventing the mechanism the method is
supposed to test.

## Adapting the vocabulary

The edge types and evidence classes above are frozensets of plain strings.
If your graph speaks a different vocabulary, map it to these names when you
build the graph. CausalPhylo deliberately has no configuration layer: the
admissibility rule is an argument about evidence, and burying it in a settings
file would make it look like a preference.
