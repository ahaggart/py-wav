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

Workspace
* Controls the signal workspace, connects components

SignalManager
* Owns signal table
* Initializes signals

SignalCache
* Stores intermediate data for re-use
* Falls back to SignalProvider on cache miss
 
SignalGraph
* Provides tools for traversing signal chains
* Iterate signals in dependency order

File Manager
* Owns the serialized version of the workspace
* Provides raw data access

Startup:
1. Load project file from disk
1. Iterate signals -> add graph entries
1. Traverse DAG -> initialize signals in dependency order

Adding a signal:

Removing a signal:


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

`get_range`: The range covered by the signal, in Partial Frames.

### Signal Manager

The heart of the data model

`get_signal(uuid: str)`: Returns a `Signal` object given a UUID string.

Signals are passed a reference to the Signal Manager during construction, which
they may use to resolve UUID references into `Signal` objects. The returned
Signal objects provide a layer of indirection to allow for caching and lazy
loading of the backing Signal objects.

### Rendering

Tray-based UI

#### Toolbar
The toolbar will provide shortcuts for manipulating the workspace

P0:
1. Reset focus to root signal.
1. Show/Hide view trays

#### Track/Lane Tray

The track tray lays out signals in parallel lanes. This will be the primary
control for arranging signals spatially, and for selecting signals for focus.

Terms:

__Block__: The visual representation of a signal. A rectangle whose width and
position on screen represent the signal's range.

P0:
1. All inputs to the "focused" signal, arranged spatially
1. Can drill down in-place
1. Select signal for focus in various trays
1. Create or modify offset with click-and-drag
1. Edge Drag: See below

P1:
1. Show signals rendered as .wav

##### Feature: Edge Drag

When a user clicks and drags on the edge of a __block__, there are a number of
responses that would be intuitive:
1. Dilation: Dilate the signal such that its dilated range aligns the rendered
__block__ with the cursor position.
1. Tiling: Tile the signal such that the tiled range aligns the rendered
__block__ with the cursor position.
1. Setting Range: Change the reported range of the signal such that the range
aligns the rendered __block__ with the cursor position.

Should we have a default behavior?
How can we switch between behaviors?

_Approach 1_: Select the behavior based on the signal type

Each signal type has a single edge-drag behavior associated with it.
We must choose a "default" behavior for most signal types, or not allow edge
dragging on most signals.

This approach will require the user to manually wrap the target signal in a
derived signal with the correct edge-drag behavior.

Assessment:
* Explicit control and clear behavior
* Very slow and clunky

_Approach 2_: Select the behavior with a hotkey

Edge dragging can be initiated only when the user is holding a hotkey
corresponding to a fill option.

Assessment:
* Relatively explicit control and behavior
* Steeper learning curve due to low visual feedback
* Best combined with another approach

_Approach 3_: Select the behavior before initiating the action

Select the fill mode from the toolbar. This might be one configurable fill tool,
or several distinct filling tools.

The fill tool is used by edge-dragging the desired block.

This approach can be streamlined using hotkeys.

Required: cursor modes

_Approach 4_: Select the behavior after completing the action

Give user a visual representation of the new range. When the cursor is released,
use a modal (or other UI control) to select the fill method.

We can streamline this workflow with Approach 2, by allowing the user to hold a
hotkey corresponding to the fill type during the edge-drag.

_Decision_: _Approach 3_ Pre-selection via toolbar or hotkey
1. The Track Tray will need to track cursor state
1. We can implement _Approach 4_ alongside this method if desired

##### Feature: Visual Linking

We would like for the user to be able to click-and-drag between blocks in order
to compose signal chains.

#### Detail Tray:

The detail tray allows the user to manipulate the inputs to the focused signal.
It will be the primary control for creating or modifying signal data.

#### Graph Tray
