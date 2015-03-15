# Class plot.Function #

Given a function y(x) and endpoints for x, Function draws the resulting curve.  More points are evaluated near corners and discontinuities than linear segments.

Function is a special case and a subclass of [plot.Parametric](plotParametric.md).  The only difference is the way the first argument is interpreted; for all other information, see [plot.Parametric](plotParametric.md).

See below for examples (not yet, but soon!)

### Defining a function ###

The easiest way to define a new function is to type it as a string.  The string must be a Python expression that evaluates to a number.  The independent variable is called "x", and you may use any function defined in Python's [math module](http://docs.python.org/lib/module-math.html) and your globals dictionary.  It can be convenient to set globals to Python's built-in globals() function to give yourself access to any variables or functions you have defined.
```
>>> from plothon.plot import *
>>> a = 2.
>>> p = Function("a*sin(x)", 0, 1, globals())
>>> p
<plothon.plot.Function x -> a*sin(x) [0,1] {'stroke-width': '0.5pt'}>
>>> p(1.57)
1.9999993658636692
```

See [WarningIntegerDivision](WarningIntegerDivision.md) for a warning about integer division in Function strings.

It's also possible to define a function from a Python callable, which allows for more complicated functions.  With this method, you do not need to name your independent variable "x".  The globals dictionary is ignored.
```
>>> def f(x):
...   if x < 0: return -1
...   else: return 1
... 
>>> Function(f, 0, 1)
<plothon.plot.Function f [0,1] {'stroke-width': '0.5pt'}>
```

For functions that can be defined on one line, you can use lambda expressions.
```
>>> Function(lambda q: q**2, 0, 1)
<plothon.plot.Function [0,1] {'stroke-width': '0.5pt'}>
```

## Examples ##

_Coming soon!_

## See also ##

  * [plot.Parametric](plotParametric.md): Function's immediate superclass, where you can find most of its documentation
  * [plot.Plottable](plotPlottable.md): Function's ultimate superclass
  * Back to [CompleteDocumentation](CompleteDocumentation.md)