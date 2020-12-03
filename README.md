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

### Sources

### Transforms