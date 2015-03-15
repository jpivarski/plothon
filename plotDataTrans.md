# Class plot.DataTrans #

Represents an arbitrary transformation from (x,y) points to (x',y') points, for use in [plot.Plot](plotPlot.md) graphics.

## Subclasses ##

  * [plot.DataTransComplex](plotDataTransComplex.md): ![http://plothon.googlecode.com/svn/wiki/CtoC.png](http://plothon.googlecode.com/svn/wiki/CtoC.png) transformations
  * [plot.DataTransLinear](plotDataTransLinear.md): linear and affine transformations
  * [plot.DataTransWindow](plotDataTransWindow.md): maps boxes to boxes for plot windows, including logarithmic and semilog (this is what [plot.Frame](plotFrame.md) uses)

## Arguments (for constructor) ##

| function | _required_ | a string in "x'(x,y), y'(x,y)" form or a Python callable |
|:---------|:-----------|:---------------------------------------------------------|
| globals | default=None | if the function is a string, the globals dictionary provides a context in which to evaluate the string: usually globals=globals() |
| name | default=None | Used in string representation.  If None, the name presented is the function string or the name of the Python callable |
| minusInfinityX | default=None | SVG x coordinate to use when x' is -infinity |
| plusInfinityX | default=None | SVG x coordinate to use when x' is infinity |
| minusInfinityY | default=None | SVG y coordinate to use when y' is -infinity |
| plusInfinityY | default=None | SVG y coordinate to use when y' is infinity |

### function and globals ###

The easiest way to define a new transformation is to type it as a string.  The string must contain two Python expressions that evaluate to numbers, separated by a comma (or one 2-tuple).  The transformation maps from data coordinates representing quantities such as time, temperature, etc. to screen coordinates.  The data coordinates are named "x" and "y", and the screen coordinates are the two elements of the tuple.  You may use any function defined in Python's [math module](http://docs.python.org/lib/module-math.html) and your globals dictionary.  It can be convenient to set globals to Python's built-in globals() function to give yourself access to any variables or functions you have defined.

In the following, `trans` represents a 10 degree rotation.
```
>>> from plothon.plot import *
>>> import math
>>> theta = 10. * math.pi / 180.
>>> trans = DataTrans("cos(theta)*x - sin(theta)*y, sin(theta)*x + cos(theta)*y", globals())
```

See [WarningIntegerDivision](WarningIntegerDivision.md) for a warning about integer division.

It's also possible to define a transformation from a Python callable, which allows for more complicated functions.  With this method, you do not need to name the data coordinates "x" and "y".  The globals dictionary is ignored.
```
>>> def vortex(u, v):
...     r = math.sqrt(u**2 + v**2)
...     return math.cos(r)*u - math.sin(r)*v, math.sin(r)*u + math.cos(r)*v
... 
>>> DataTrans(vortex)
<plothon.plot.DataTrans vortex (id -1210160628)>
```

For functions that can be defined on one line, you can use lambda expressions.  Be sure to put parentheses around the 2-tuple.
```
>>> from math import *
>>> DataTrans(lambda u, v: (cosh(0.1)*u + sinh(0.1)*v, sinh(0.1)*u + cosh(0.1)*v))
<plothon.plot.DataTrans (id -1210779156)>
```

### Fall-back values for infinity ###

The four "infinity" arguments set default values for data members named minusInfinityX, plusInfinityX, minusInfinityY, and plusInfinityY.  Their purpose is to allow transformation functions to map a data point at infinity to a finite value on the screen without raising an exception.  This is especially useful for logarithmic transformations, which are only defined for positive values.  By mapping log(0) and log(-x) to a point such as -1000, curves that cross this threshold will limit to a point far off screen.  Unfortunately, the user doesn't necessarily know the dimensions of the [plot.Plot](plotPlot.md) on the screen, and may choose a value that is not far enough away for the desired visual effect.  When [plot.Plot](plotPlot.md) draws a graphic, it knows its dimensions, and sets the DataTrans object's minusInfinityX, plusInfinityX, minusInfinityY, and plusInfinityY data members appropriately.  Rather than mapping log(0) to -1000, one should map log(0) to minusInfinity.

To use it, the function must accept six arguments: x, y, and the four infinities.  With a function string, the user only needs to name the appropriate arguments.  Here's an example implementation of a logarithmic transformation.
```
>>> from plothon.plot import *
>>> import math
>>> def logkludge(x, minusInfinity):
...   if x <= 0.: return minusInfinity
...   else: return math.log10(x)
... 
>>> tlog = DataTrans("logkludge(x, minusInfinityX), logkludge(y, minusInfinityY)", globals())
>>> tlog.minusInfinityX = -1000.
>>> tlog.minusInfinityY = -1000.
>>> tlog(0, 1)
(-1000.0, 0.0)
```

(In [the future](WishList.md), these four values ought to be replaced by a function of angle in the projective plane.)

## Language features ##

Two DataTrans references are equal if and only if they point to the same DataTrans object.  Thus
```
>>> DataTrans("x, y") == DataTrans("x, y")
False
```

This choice ensures consistent behavior.  One could argue that the two transformations above should be called equal, but what about the following?
```
>>> DataTrans("x, y") == DataTrans(lambda u, v: (u, v))
False
```
These two examples evaluate to different compiled code and there would be no way to guarantee that they are the same without evaluating every possible point (which is impossible).

This is why DataTrans objects include their Python identifiers in their string representations.
```
>>> t1 = DataTrans("x, y")
>>> t2 = t1
>>> t1, t2
(<plothon.plot.DataTrans x,y -> x, y (id -1211890676)>, <plothon.plot.DataTrans x,y -> x, y (id -1211890676)>)
>>> t1 == t2
True
```

A DataTrans can be called like the function it represents.
```
>>> DataTrans("2*x, y")(1, 1)
(2, 1)
```

Python's `in` operator queries the domain of the function (by checking for exceptions).
```
>>> (0, 0) in DataTrans("1./x, 1./y")
False
>>> (1, 1) in DataTrans("1./x, 1./y")
True
```
If your function uses minusInfinityX, plusInfinityX, minusInfinityY, or plusInfinityY to map infinite points to the screen, these points are included in the domain because evaluating them doesn't raise exceptions.

Note that this evaluates the function, so if you're trying to minimize the number of times the function is minimized, use a `try` block.
```
>>> trans = DataTrans("1./x, 1./y")
>>> try:
...     x, y = trans(0, 0)
...     # use the values of x and y, if they exist
... except:
...     pass # do what you would do in case of failure
```

Multiplying DataTrans objects results in a composed function of type [plot.DataTransComposition](plotDataTransComposition.md).
```
>>> DataTrans("2*x, y") * DataTrans("y, x")
<plothon.plot.DataTransComposition (x,y -> 2*x, y) -> (x,y -> y, x) (id -1210884372)>
```

Functions are evaluated from left to right.
```
>>> (DataTrans("2*x, y") * DataTrans("y, x"))(1, 0)
(0, 2)
>>> (DataTrans("y, x") * DataTrans("2*x, y"))(1, 0)
(0, 1)
```

## Methods ##

### Method plot.DataTrans.function ###

This is the Python callable created from the function given in the DataTrans constructor.  It has six arguments: x, y, minusInfinityX, plusInfinityX, minusInfinityY, and plusInfinityY.

### Method plot.DataTrans.derivative ###

Takes the 2-dimensional numerical derivative of the transformation at an (x,y) point, returning a 2-by-2 Jacobian matrix.

![http://plothon.googlecode.com/svn/wiki/derivative.png](http://plothon.googlecode.com/svn/wiki/derivative.png)

where (capital) X and Y are screen coordinates (image of the transformation) and (lowercase) x and y are data coordinates (the preimage).

These two 2-tuples could also be interpreted as _xhat_ and _yhat_, the local unit vectors expressed in global coordinates: (1,0) in data coordinates is _xhat_ in screen coordinates and (0,1) in data coordinates is _yhat_ in screen coordinates.

Because the functional form of the transformation is not necessarily known, the derivative is calculated by finite differences.  The differences are not symmetric around (x,y).

![http://plothon.googlecode.com/svn/wiki/derivative_finitedifference.png](http://plothon.googlecode.com/svn/wiki/derivative_finitedifference.png)

#### Arguments ####

| x | _required_ | x location in data coordinates |
|:--|:-----------|:-------------------------------|
| y | _required_ | y location in data coordinates |
| delta | default=None | size of the small interval over which the finite difference is calculated; if None, defaults to 1e-12 |

The delta parameter should be much smaller than the smallest size scale in your plot (in data coordinates), but larger than the largest scale times your computer's precision (about 8.9e-16).

### Method plot.DataTrans.normderiv ###

Calculates the derivative of the transformation but normalizes _xhat_ and _yhat_ to 1.0 in screen coordinates.  The arguments are the same as for plot.DataTrans.derivative.  This is used to set tick marks that follow the shape of the transformation but have a uniform length given in SVG coordinates.

## See also ##

  * [plot.DataTransComposition](plotDataTransComposition.md): composition of transformations
  * Back to [CompleteDocumentation](CompleteDocumentation.md)