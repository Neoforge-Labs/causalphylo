# Identification

Once the graph is restricted to the edges that
[earn an arrow](admissibility.md), the question becomes whether a causal effect
can be computed from observational data at all.

## The criterion

A set `Z` satisfies the backdoor criterion relative to `(X, Y)` when

1. no node in `Z` is a descendant of `X`, and
2. `Z` blocks every path between `X` and `Y` that starts with an arrow **into**
   `X`

(Pearl, *Causality*, 2nd ed., Def. 3.3.1).

Both halves matter. The descendant condition rules out conditioning on a
mediator or a collider downstream of the treatment. And blocking only the
*backdoor* paths — never the causal path itself — is what a plain d-separation
test does not give you for free.

!!! info "How the second half is tested"
    To use a generic d-separation routine, the edges **leaving** the treatment
    are removed first. That deletes the causal path, and anything `X` causes,
    while leaving every backdoor path exactly as it was.

    This is not the same mutilation as `mutilated_graph`, which removes the
    edges **into** the treatment to build the interventional graph
    G<sub>X&#772;</sub>. The two are easy to confuse and mean opposite things.

## One call

```python
from causalphylo import find_adjustment_set

verdict = find_adjustment_set(G, treatment="X", outcome="D")
```

`find_adjustment_set` takes the full graph and does the restriction itself —
`causal_subgraph`, then `acyclic_core` — so no caller can skip it. It returns a
frozen `Identification`:

| Field | Meaning |
|---|---|
| `identifiable` | Whether the effect is identifiable |
| `adjustment_set` | The minimal valid set, as a tuple |
| `reason` | An `IdentificationReason`, always set |
| `search_truncated` | Whether the subset search hit its bound |
| `n_near_miss_confounders` | Confounders the graph hints at but does not license |

## The reasons

```python
import networkx as nx
from causalphylo import find_adjustment_set

REG = {"edge_type": "activates",       "evidence_class": "regulatory"}
GEN = {"edge_type": "associated_with", "evidence_class": "genetic_association"}
LIT = {"edge_type": "associated_with", "evidence_class": "literature"}
```

### `identifiable_by_adjustment`

A confounder is present and adjustable.

```python
G = nx.DiGraph()
G.add_edge("U", "X", **REG); G.add_edge("U", "D", **GEN); G.add_edge("X", "D", **GEN)
find_adjustment_set(G, "X", "D")
# identifiable=True  adjustment_set=('U',)  reason='identifiable_by_adjustment'
```

### `identifiable_trivially`

No confounder appears in the graph, so the empty set satisfies the criterion.

```python
G = nx.DiGraph()
G.add_edge("X", "D", **GEN); G.add_edge("W", "X", **REG); G.add_edge("W", "D", **LIT)
find_adjustment_set(G, "X", "D")
# identifiable=True  adjustment_set=()  reason='identifiable_trivially'
# n_near_miss_confounders=1
```

!!! warning "A trivial verdict is not a clean bill of health"
    A knowledge graph is open-world. A missing edge is **missing knowledge**,
    not evidence of no confounding.

    So a trivial verdict carries `n_near_miss_confounders`: how many nodes
    reach the treatment and carry *some* edge to the outcome that fell short of
    admissibility. Above, `W` regulates `X` and is associated with `D` — but
    only by literature, so it is exactly the kind of confounder the graph hints
    at and cannot license.

    A target with many near misses is fragile. This is the same move as an
    [E-value](https://doi.org/10.7326/M16-2607) in observational epidemiology:
    not "there is no confounding", but "here is how much it would take to break
    this".

### `no_causal_path`

No admissible directed path from treatment to outcome. An association on its
own produces this, because it never became an arrow.

```python
G = nx.DiGraph(); G.add_edge("X", "D", **LIT)
find_adjustment_set(G, "X", "D")
# identifiable=False  reason='no_causal_path'
```

### `cyclic_component`

Treatment or outcome sits in a feedback loop, where d-separation is undefined.

```python
G = nx.DiGraph()
G.add_edge("X", "D", **GEN); G.add_edge("X", "Y", **REG); G.add_edge("Y", "X", **REG)
find_adjustment_set(G, "X", "D")
# identifiable=False  reason='cyclic_component'
```

### `no_valid_adjustment_set`

Confounders exist, but no admissible subset blocks every backdoor path.

### `treatment_absent` / `outcome_absent`

The node is not in the admissible subgraph — it may exist in your graph and
have had no admissible edge.

```python
G = nx.DiGraph(); G.add_edge("X", "D", **GEN)
find_adjustment_set(G, "ZZZ", "D")   # reason='treatment_absent'
find_adjustment_set(G, "X", "ZZZ")   # reason='outcome_absent'
```

## Search bounds, reported not hidden

The subset search is bounded, because the number of candidate subsets grows as
C(pool, size):

```python
>>> from causalphylo import MAX_ADJUSTMENT_SET_SIZE, MAX_CANDIDATE_POOL
>>> MAX_ADJUSTMENT_SET_SIZE, MAX_CANDIDATE_POOL
(3, 20)

```

Reaching a bound sets `search_truncated`. It is never silently swallowed:

```python
G = nx.DiGraph(); G.add_edge("X", "D", **GEN)
for i in range(25):                      # 25 confounders, pool bound is 20
    G.add_edge(f"U{i}", "X", **REG); G.add_edge(f"U{i}", "D", **GEN)

find_adjustment_set(G, "X", "D")
# identifiable=False  reason='no_valid_adjustment_set'  search_truncated=True
```

A `False` with `search_truncated=True` means *not found within the bound* — not
*does not exist*. Treat the two differently.

## Working at a lower level

```python
from causalphylo import causal_subgraph, acyclic_core, satisfies_backdoor

dag = acyclic_core(causal_subgraph(G)).dag

satisfies_backdoor(dag, "X", "D", frozenset({"U"}))   # True
satisfies_backdoor(dag, "X", "D", frozenset())        # False
```

`satisfies_backdoor` expects a DAG containing both nodes, which
`find_adjustment_set` guarantees before calling it. Reaching for it directly
means taking on that guarantee yourself.
