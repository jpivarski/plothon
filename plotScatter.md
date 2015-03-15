# plot.Scatter #

Scatter draws a list of points as colored dots.  For more general symbols, see [plot.SymbolScatter](plotSymbolScatter.md).  For vertical or horizontal error bars, see [plot.ErrorBars](plotErrorBars.md).

See below for examples (not yet, but soon!)

## Arguments (for constructor) ##

| points | _required_ | a list of points to plot |
|:-------|:-----------|:-------------------------|
| radius | default=1. | radius of the dots in user SVG coordinates |
| attributes | _keyword list_ | SVG attributes |

The points argument must be a list of (x,y) pairs.  Additional values beyond x and y will be ignored.

The constructor arguments become member data and may be changed at any time. The points can be edited with the language features described in the [plot.PlottablePoints](plotPlottablePoints.md) superclass.

## Methods ##

### plot.Scatter.SVG ###

Draws the Scatter in a given [plot.DataTrans](plotDataTrans.md) transformation. Output is an [svg.SVG](svgSVG.md) object. See [plot.Plottable](plotPlottable.md) for the argument list.

## Examples ##

_Coming soon!_

## See also ##

  * [plot.PlottablePoints](plotPlottablePoints.md): Scatter's direct superclass
  * [plot.Plottable](plotPlottable.md): Scatter's ultimate superclass
  * Back to [CompleteDocumentation](CompleteDocumentation.md)