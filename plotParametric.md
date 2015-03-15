# Class plot.Parametric #

Given a pair of functions (x(t),y(t)) and endpoints for t, Parametric draws the resulting curve.  More points are evaluated near corners and discontinuities than linear segments.

See below for examples (not yet, but soon!)

## Subclasses ##

  * [plot.Function](plotFunction.md): the independent variable is the horizontal axis
  * [plot.ParametricLine](plotParametricLine.md): a parametric curve joining two points

## Arguments (for constructor) ##

All arguments are described in more detail in the subsections below this table.

| function | _required_ | a string in "x(t), y(t)" form or a Python callable |
|:---------|:-----------|:---------------------------------------------------|
| low | _required_ | minimal value of t to plot |
| high | _required_ | maximal value of t to plot |
| globals | default=None | if the function is a string, the globals dictionary provides a context in which to evaluate the string: usually globals=globals() |
| random\_sampling | default=True | if False, select sample points by exactly bisecting the interval; if True, randomly bisect between 30% and 70% |
| recursion\_limit | default=15 | maximum number of bisections (maximum number of evaluated points is 2<sup>recursion_limit</sup>) |
| linearity\_limit | default=0.1 | deviations from a straight line smaller than linearity\_limit (in user SVG coordinates) do not need to be sampled further |
| discontinuity\_limit | default=5. | sampled points that are more distant than discontinuity\_limit (in user SVG coordinates) are either sampled more thoroughly or the curve is broken |
| attributes | _keyword list_ | SVG attributes |

### Defining a parametric function ###

The easiest way to define a new function is to type it as a string.  The string must contain two Python expressions that evaluate to numbers, separated by a comma (or one 2-tuple).  The independent variable is called "t", and you may use any function defined in Python's [math module](http://docs.python.org/lib/module-math.html) and your globals dictionary.  It can be convenient to set globals to Python's built-in globals() function to give yourself access to any variables or functions you have defined.
```
>>> from plothon.plot import *
>>> a = 3.14159
>>> p = Parametric("t/a, sin(t)", 0, 1, globals())
>>> p
<plothon.plot.Parametric t -> t/a, sin(t) [0,1] {'stroke-width': '0.5pt'}>
>>> p(3.14159)
(1.0, 2.6535897933527261e-06)
```

See [WarningIntegerDivision](WarningIntegerDivision.md) for a warning about integer division in Parametric function strings.

It's also possible to define a Parametric function from a Python callable, which allows for more complicated functions.  With this method, you do not need to name your independent variable "t".  The globals dictionary is ignored.
```
>>> def f(x):
...   if x < 0: return x, -1
...   else: return x, 1
... 
>>> Parametric(f, 0, 1)
<plothon.plot.Parametric f [0,1] {'stroke-width': '0.5pt'}>
```

For functions that can be defined on one line, you can use lambda expressions.  Be sure to put parentheses around the 2-tuple.
```
>>> Parametric(lambda q: (q**2, q**3), 0, 1)
<plothon.plot.Parametric [0,1] {'stroke-width': '0.5pt'}>
```

### The sampling algorithm ###

When the function is evaluated by Parametric.SVG, Parametric.sample, or Parametric.PlottablePath (see below), the following algorithm is applied.

  1. The left and right endpoints are evaluated.
  1. A midpoint between these two is evaluated, exactly halfway between left and right if random\_sampling=False or somewhere between 30% and 70% if random\_sampling=True (the default).  Without random\_sampling, the algorithm is guaranteed to be deterministic but it might sample a periodic function incorrectly.
  1. If the midpoint (as seen in user SVG coordinates) is within discontinuity\_limit of the two endpoints and it lies within linearity\_limit of the line between the two endpoints, the curve is considered linear enough to draw as a line segment.
  1. If not, the (left, midpoint) and (midpoint, right) segments are subdivided recursively.
  1. If the recursion reaches recursion\_limit and the endpoints are still more than discontinuity\_limit from each other, no line segment is drawn.  This is a discontinuity in the function.

The algorithm has a recursion minimum of 3 (at least 2<sup>3</sup> = 8 points).  Note that computation time can rise quickly with recursion\_limit if the function is not well behaved.

## Language features ##

A Parametric object can be called like a Python function.
```
>>> from plothon.plot import *
>>> p = Parametric("1./(1.-t), 1./(t-1.)", 0, 1)
>>> p(2.)
(-1.0, 1.0)
```

The `in` operator is interpreted as a question about the domain of the function.
```
>>> 1. in p
False
>>> 1.1 in p
True
```

## Methods ##

### plot.Parametric.SVG ###

Draws the Parametric curve in a given [plot.DataTrans](plotDataTrans.md) transformation.  Output is an [svg.SVG](svgSVG.md) object.  See [plot.Plottable](plotPlottable.md) for the argument list.

Calling Parametric.SVG evaluates the function and defines a set of sample points, storing them in the data member named last\_samples.

### plot.Parametric.sample ###

Explicitly ask for the function to be evaluated, defining a set of sample points in last\_samples.  This method does not create graphical output.

#### Arguments ####

| datatrans | default=None | the [plot.DataTrans](plotDataTrans.md) coordinate transformation |
|:----------|:-------------|:-----------------------------------------------------------------|

Note that the coordinate transformation affects the choice of sample points, because points will be spaced roughly uniformly in user SVG units, not the data coordinate units.

### plot.Parametric.subsample ###

Recursively called by Parametric.sample(), not likely to be called by the user.

### plot.Parametric.PlottablePath ###

Evaluates the function and returns a [plot.PlottablePath](plotPlottablePath.md) object.

#### Arguments ####

| datatrans | default=None | the [plot.DataTrans](plotDataTrans.md) coordinate transformation |
|:----------|:-------------|:-----------------------------------------------------------------|
| local | default=True | if True, the [plot.PlottablePath](plotPlottablePath.md) will be expressed in the data coordinates; if False, it will be expressed in user SVG coordinates |

The [plot.PlottablePath](plotPlottablePath.md) will be properly interpreted whether it is in local coordinates or global coordiantes (global versus local is stored in plottablePath.d).  If it is expressed in local coordinates, you can choose a different coordinate transformation later, but the spacing of sampled points may not be optimal for the new coordinates.

### plot.Parametric.last\_points ###

Converts last\_samples into data coordinates with a [(x,y), (x,y), (x,y), ...] format suitable for [plot.PlottablePoints](plotPlottablePoints.md) such as [plot.Scatter](plotScatter.md) and [plot.Curve](plotCurve.md).  This method does not evaluate the function and it raises an exception if last\_samples has not been created with Parametric.SVG(), Parametric.samples(), or Parametric.PlottablePath().

## Member data ##

The constructor arguments become member data and may be changed at any time.

### last\_samples ###

After the function has been evaluated, the Parametric class acquires a new member, last\_samples.  This is the list of sampled points represented as a [plot.Parametric.Samples](plotParametricSample.md) object, which can be iterated over.  See [plot.Parametric.Samples](plotParametricSample.md) for details.

If you want an [(x,y), (x,y), (x,y), ...] list, call Parametric.last\_points().

## Examples ##

_Coming soon!_

## See also ##

  * [plot.Plottable](plotPlottable.md): Parametric's superclass
  * [plot.Parametric.Sample and plot.Parametric.Samples](plotParametricSample.md): iterable format for last\_samples
  * Back to [CompleteDocumentation](CompleteDocumentation.md)