# py-wav

A meager attempt at a DAW.

## design

### Data Model

py-wav uses a flat data model to represent the processing graph.

```json
[
  { "name":  "a", "refs":  ["b", "c"] },
  { "name":  "b", "refs":  ["d"] },
  { "name":  "c", "refs":  ["e"] },
  { "name":  "d", "refs":  ["f"] },
  { "name":  "e", "refs":  ["f"] },
  { "name":  "f", "refs":  [] }
]
```
becomes
```
   -> b -> d
 /          \
a             -> f
 \          /
   -> c -> e
```

Caching is handled by wrapping raw processing in cache nodes. Cache nodes act
as a proxy for the underlying processing node. When a cache node is sampled, it
will first attempt to fetch a sample from the cache. If no cache entry is
found, the cache node will fetch the sample from its underlying node and store
the result in the cache for re-use.

Cache invalidation uses a DAG constructed from node data. For the "d -> f"
relationship given above, an "f -> d" relationship is added to the cache
dependency DAG. If changes are made to node "f", we must invalidate the buffer
cache for "f", then walk the cache DAG and invalidate any other buffer caches
traversed, including the cache for node "d".

### Framework

Signal -> Reference Node -> Signal Manager -> Cache Node -> Cache -> Signal

`SignalCache`
* owns uuid map?
* signal cache should be operate behind reference table

`SignalManager`
* owns reference map

### Signals

Problem 1: Spectral-first signals must have a temporal component.
* convert spectral signal to temporal domain
* get bounds from child

Problem 2: Parametrized inputs.

moot

Problem 3: Templating

Suppose an end user wants to copy and reuse a set of signals. How can we support
this?

Approach 1: Templates as a first-class data type.

Templates are inserted into the graph. At compile time, templates are resolved
to their component Signals.

Pro:
* Templates are easy to manipulate after creation

Con:
* More complex graph compilation.

Approach 2: Templates as a data generation strategy.

Templates are resolved on creation and add their components directly into the
graph.

Pro:
* Simpler graph compilation.

Con:
* Components cannot be manipulated in groups without additional support.

Problem 4: Scaling and Sliding

All signals have an offset of 0.

To represent signal y at offset x, create signal z that samples y starting at x

```
cache
 | 0123..x.....
----------------
y| yyyyy0000000
z| 0000000yyyyy
```

Problem 5: "Deep Sampling"

Suppose we have a signal W sampled into the workspace by signal X, and a
signal Y sampled into the workspace by signal Z. Can we sample W into Y
with respect to their representations in X and Z?

Approach 1: Require transformations to be "reversible"

We can sample W into Y by transforming W into the space of Y. This is achieved
by transforming W into absolute space via X, then applying the inverse of Z to
transform W into Y-space.

The two transform types of concern are "sliding" transforms that offset a
signal, and "scaling" transforms that speed up or slow down a signal.

Transforming W into Y-space will require a "path" to transform along. Consider
the following scenario, where R is the root node.
```
   -> X -> W
 /         ^
R  -> A ---|
 \         v
   -> Z -> Y
```
As shown above, both W and Y are sampled into the root along two paths. If our
goal is to "sample W into Y" we must include context for this action. In the
problem presented, the "sampling path" is W -> X -> R -> Z -> Y.

Takeaways:
* Requiring "reversibility" will introduce complexity to the Signal model
* Properly describing a "deep sample" via reversibility is complex and will
  not be intuitive to end users.

Approach 2: Do not allow deep sampling. Sampling ignores parent transformations.

Sampling always happens in the coordinate space of the Signal being sampled. If
Y is sampling W, Y directly samples a frame range from W. If W is an audible
signal whose timing relative to Y is important, then W and Y must be children
of the same node.

Takeaways:
* Direct sampling allows for a much simpler Signal model.
* Direct sampling imposes some restrictions on the topography of the graph.

Problem 6: Signal substitution

Suppose signal Y samples signal x. We would like to apply a transform Z to X
before it is consumed by Y. How can we support this?

Though signal Y samples signal X, it is not aware of signal X's uuid. Signal y
instead holds a reference A which can be resolved by the signal manager to
signal X. To insert our transform, create the signal Z holding reference B.
Update the signal manager such that reference A resolves to signal Z, and 
reference B resolves to signal X.

Problem 7: Transform minimization

Suppose we have a chain of signals V -> W -> X -> Y -> Z, where W and Y are
spectral-primary signals and V, X, and Z are temporal-primary signals. To
compute V, we will need to compute two fourier transforms, for Y -> Z and
W -> X, and two fourier inverses, for X -> Y and V -> W. If V, W, X, and Y are
linear operations, we can reorder them to V -> X -> W -> Y -> Z. This ordering
requires only one fourier transform (Y -> Z) and one fourier inverse (X -> W).

We can implement this reordering by modifying the reference table. 

In order to optimize, nodes will need to implement one:

`is_linear`: True if the node's operations are linear. Default to False.

We will also need to know the "primary domain" associated with any graph edge.
This information can be provided "dynamically" as part of the call to the
signal manager.

`resolve_reference(uuid, domain: Optional[str]=None)`

Problem 8: Rendering

Rendering will be done in the context of a selected node. All child nodes of the
selected node will be shown.

Problem 9: Circular imports

If the Signal class is aware of the Signal Manager class, this results in a
circular import due to the use of the Wrapper Signal by the manager.

Approach 1: Signal refs are pre-resolved. Signal does not need to interact with
the manager directly.

This approach has the problem that we cannot provide caller-specific information
when resolving the references.

#### Data

Data-centric design.

`type`: The name of the source type.
`uuid`: Every source must have a UUID

#### Methods

`get_temporal`: Returns a sample of the signal in the temporal domain.
* start: The start of the range to sample, in (absolute?) Frames
* end: The end of the range to sample, in (absolute?) Frames

`get_spectral`: Returns a sample of the signal in the spectral domain.

This method always returns a buffer equal in size to the **period** of the
signal.

`get_period`: The Period of the source, in Frames.

`get_offset`: The offset of the source, in Frames.

### Signal Manager

The heart of the data model

`get_signal(uuid: str)`: Returns a `Signal` object given a UUID string.

Signals are passed a reference to the Signal Manager during construction, which
they may use to resolve UUID references into `Signal` objects. The returned
Signal objects provide a layer of indirection to allow for caching and lazy
loading of the backing Signal objects.

### Rendering