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

Problem 9: Discrete fourier analysis of signals unbounded in one direction

At a high level there are three cases for discrete fourier analysis:
1. Bounded in both directions
2. Unbounded in both directions
3. Unbounded in one direction

For cases (1) and (2), discrete fourier analysis works as expected. For case
(3), we cannot perform true fourier analysis since the signal does not have a
"period". A similar problem arises when tiling case (3) signals.

For case (3) signals, we consider the period as if the signal were unbounded in
both directions. This allows us to perform fourier analysis that is accurate in
the non-zero regions.

When spectral-dominated signals are converted back to the temporal domain, they
should respect the values given by `get_range`.

Problem 10: Range creep

OffsetSignal extends the range of its child in the direction of offset. These
extensions compound with multiple offsets.

Suppose signal X has a range of (Y, Z). Signal W offsets X by +2 frames, and
has a range of (Y, Z+2). Signal V offsets W by -2 frames, and has a range of
(Y-2, Z+2).

Thus X's range covers (Z-Y) frames while V's range covers (Z+2-(Y-2)) frames.
V is the same signal as X, but the reported range covers 4 additional frames.

We cannot easily remove range creep without violating encapsulation. In
situations where range creep is a problem, such as tiling, the workaround is
to use a TruncatedSignal to manually set the range.

Problem 11: Parameter types

For many derived signals we would like to be able to transform the child signal
according some other input signal. For example, we may want to scale the child
signal X at point Z by the value of signal Y at point Z. We may also want to
scale the child signal by some constant W. What is the best way to support
this?

Approach 1: Defined separate derived signals for different parameter types.

With this approach, we may define a ScaledSignal taking a constant factor and a
ParameterScaledSignal taking a reference. The input field types are determined
by the signal type and do not vary.

However, we must define multiple signal types for any parametrized logic block.
In the example given above, "scaling" logic has 1 parameter, so we would define
two types to express constant and parametrized scaling. For n parametrizable
inputs, the number of types required to enumerate all combinations of constant
and parametrized inputs is 2^n. This enumeration will not scale for
multi-parameter transforms. There are not many multi-parameter transforms which
cannot be broken down into smaller components.

Enumerating constant and parametrizable inputs burdens the front-end with the
management of variants and could potentially create churn when the types are
interchanged.

Approach 2: Variably typed references via UUID format requirements.

We can infer the type of a reference if we impose requirements on the structure
of node UUIDs. For example, a signal may be required to have a UUID starting
with "signal:" while a constant would have a UUID starting with "constant:".

Approach 3: Do not allow constant inputs, use constant-value signals.

Instead of trying to determine the type of an input, we can insert a
constant-valued signal into the graph when a constant input is desired. This
allows us to maintain a simpler type system, at the cost of additional nodes
in the signal graph.

Decision: We will go with (Approach 3).

Problem 12: Frame rounding

When sampling a signal, we provide an integer `start` and `end` to ensure that
the output buffer size is always known. A problem arises when dealing with frame
amounts that are not integers.

Aggressively flooring Frame amounts to integers introduces rounding error which
compounds as we traverse deeper into the signal graph.

Solution: Do not round Frame amounts until they are needed for indexing.