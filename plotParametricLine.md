# Class plot.ParametricLine #

Given two points, ParametricLine draws a line connecting them using the [plot.Parametric](plotParametric.md) tools.  The advantage of
```
>>> from plothon.plot import *
>>> ParametricLine(0, 0, 1, 1)
<plothon.plot.ParametricLine (0 0) to (1 1)>
```
over
```
>>> Curve([(0,0), (1,1)], mode="lines")
<plothon.plot.Curve (2 nodes) mode=lines {'stroke-width': '0.5pt'}>
```
is that ParametricLine will curve in a non-linear [plot.DataTrans](plotDataTrans.md) coordinate transformation.  Coordinate axes in [plot.Plot](plotPlot.md) are drawn using two ParametricLines.

ParametricLine is a special case and a subclass of [plot.Parametric](plotParametric.md).  The only differences are in the constructor arguments.  For all other information, see [plot.Parametric](plotParametric.md).

See below for examples (not yet, but soon!)

## Arguments (for constructor) ##

| x1 | _required_ | first x position in data coordinates |
|:---|:-----------|:-------------------------------------|
| y1 | _required_ | first y position in data coordinates |
| x2 | _required_ | second x position in data coordinates |
| y2 | _required_ | second y position in data coordinates |
| random\_sampling |  | see [plot.Parametric](plotParametric.md) |
| recursion\_limit |  | see [plot.Parametric](plotParametric.md) |
| linearity\_limit |  | see [plot.Parametric](plotParametric.md) |
| discontinuity\_limit |  | see [plot.Parametric](plotParametric.md) |
| attributes |  | see [plot.Parametric](plotParametric.md) |

All constructor arguments become data members, including x1, y1, x2, and y2.  If you change these endpoints after the ParametricLine has been created, the update will be correctly propagated to the sampling/drawing functions.

The parametric function is defined such that t=0 corresponds to (x1,y1) and t=1 corresponds to (x2,y2).

## Examples ##

_Coming soon!_

## See also ##

  * [plot.Parametric](plotParametric.md): ParametricLine's immediate superclass, where you can find most of its documentation
  * [plot.Plottable](plotPlottable.md): ParametricLine's ultimate superclass
  * Back to [CompleteDocumentation](CompleteDocumentation.md)