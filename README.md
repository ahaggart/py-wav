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

### Architecture

WorkspaceOrchestrator
- SignalManager: Owns signal table an manages cache
  - SignalCache
- SignalGraph: Provides tools for traversing signal chains
- (File Manager): Owns the serialized version of the workspace

### Signals

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