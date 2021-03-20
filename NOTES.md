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

Q: Should samples still be requested in integer frame amounts?
A: Yes.

Q: How should we convert partial frames to true frames?
A: We will apply ceil() to convert from partials to frames when working with
frame ranges. This logic is provided via `util.frames.to_frames()`.
We will apply round() to convert from partials to frames when working with
signal periods. This logic is provided via `util.frames.to_bufsize()`.

Q: How do we avoid buildup of rounding errors when many small
buffers are involved?
A: When tiling a buffer, we need to upsample to near-integer period then
downsample to the correct frame rate.

Problem 13: Aperiodic signals

Suppose we have a signal X whose output is the value of signal Y transformed
according to the value of signal Z. Suppose Y is an unbounded signal, while Z is
bounded by the range (A, B).

So the value of X is f(Y,Z) for range (A, B), and Y for (-inf, A) and (B, inf).
We cannot assign a true period to X, since it extends infinitely, nor can we
compute an internal period, since there is a finite region transformed by Z.
How can we proceed?

Approach 1: Allow aperiodic signals.

Q: What are the spectral characteristics of aperiodic signals?
Q: Can we tile aperiodic signals?

Conclusion: Aperiodic signals are inoperable for complex use cases. Rather than
building around the expectation that `get_period` may return `None`, we should
prevent the creation of aperiodic signals. See **Approach 3**.

Approach 2: Use the bounds of the workspace.

We can assign an internally-consistent period to an aperiodic signal by
reporting a period large enough that no signal would ever sample outside of one
period.

Circular dependency problem

Compute cost problem

Approach 3: Do not allow aperiodic signals.

Introduce `AperiodicResultException` for identifying these situations.

Solution: We will go with Approach 3.

Problem 14: Offset range

Suppose we offset a signal with range (X, Y) by Z. What is the range of the
transformed signal?

Approach 1: Include the offset in the new range.

This approach is appealing because the offset will be included in operations
such as tiling and fourier analysis, which is intuitive.

On the other hand, including the offset in the range means users must structure
their signal chains to account for offsets when doing spectral operations.

Approach 2: Do not include the offset in the new range.

We can still achieve intuitive tiling behaviors with a "set range" source. This
though this will add some complexity to signal graphs, using an explicit
"set range" transform gives the user more leeway in the ordering of transforms.

Solution: We will go with Approach 2.

Problem 15: Should we allow unbounded signals?

Consideration 1: Aperiodic signals

Allowing unbounded signals leads us to the issue of "aperiodic" signals, which
substantially increases both  the complexity of signal implementations and the
tooling we must build to help users deal with aperiodic signals in their
workspace.

In the simple case, a user adds a new signal to the workspace that resolves as
aperiodic. Remediating this is simple: (1) revert the creation of the signal and
(2) provide instructions to manipulate source signals to prevent aperiodic
results.

More complex cases arise with chains of signals whose range is dependent on that
of their sources. A user might modify a signal in one place and find that a
different signal farther up the signal chain *becomes* aperiodic as a result.
Remediating this is not simple. While reverting the modification would certainly
resolve the issue, it is difficult to issue guidance on preventing the issue
from occurring again, 

Consideration 2: Pure Parameters

The core consideration to allowing unbounded signals is for their use as
"pure parameters", either as constants or as basic waveforms. Requiring bounds
to be set for all signals makes our pure parameter ergonomics worse:
1. If the base signal's range changes, the parameters range must be adjusted
accordingly.
1. The data models of simple signals becomes bloated with range information.

On the other hand, the ergonomic issues given above are less concerning than the
potential difficulty in resolving aperiodic signal chains, discussed above.

Consideration 3: Period vs Range

In order to support unbounded signals, we include both a period and a range in
the Signal interface. Period is only useful for unbounded signals, and is
generally derived from the range for bounded signals.

Solution: We will not allow unbounded signals.
