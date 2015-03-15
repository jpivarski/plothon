These classes are defined inside [plot.Parametric](plotParametric.md) and are used internally by the sampling algorithm.  As a user, you may find them useful as an iterable record of sampled points, accessed through [plot.Parametric](plotParametric.md).last\_samples (an instance of plot.Parametric.Samples).

# plot.Parametric.Sample #

## Members ##

| t | the value of the independent variable at this point |
|:--|:----------------------------------------------------|
| x, y | (lowercase) the location of the sampled point in data coordinates |
| X, Y | (uppercase) the location of the sampled point in user SVG coordinates |

In the case of [plot.Function](plotFunction.md) (a subclass of [plot.Parametric](plotParametric.md)), t and x are always equal.  If evaluated without a [plot.DataTrans](plotDataTrans.md) transformation, x,y and X,Y are always equal.

# plot.Parametric.Samples #

An iterable list of Sample objects.  (Internally, Samples are stored as a doubly linked list to simplify the sampling algorithm.)

## Language features ##

Samples supports Python's built-in len() function.
```
>>> from plothon.plot import *
>>> p = Parametric("t, t**2", 0, 1)
>>> p.sample()
>>> len(p.last_samples)
17
```

It also supports iteration.
```
>>> for s in p.last_samples:
...     print s.t, s.x, s.y, s.X, s.Y
... 
0 0 0 0 0
0.0403764700746 0.0403764700746 0.00163025933568 0.0403764700746 0.00163025933568
0.12275720171 0.12275720171 0.0150693305716 0.12275720171 0.0150693305716
   .
    .
     .
0.967736616711 0.967736616711 0.936514159322 0.967736616711 0.936514159322
1 1 1 1 1
```

## See also ##

  * [plot.Parametric](plotParametric.md): this class and its subclasses create Samples
  * Back to [CompleteDocumentation](CompleteDocumentation.md)