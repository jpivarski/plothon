# Class plot.Steps #

Given a list of bin edges and values, Steps draws them as the outline of a bar graph with no space between the bars.  This is the most common way to draw histograms.  The resulting image looks like a staircase (hence "Steps") or a city skyline.

See below for examples (not yet, but soon!)

## Arguments (for constructor) ##

| edges | _required_ | a list of N+1 increasing x-values, separating bin cells |
|:------|:-----------|:--------------------------------------------------------|
| values | _required_ | a list of N y-values in each of the above cells |
| anchor | default=0 | the left edge of the first bin and right edge of the last bin are connected with vertical lines to the anchor value, unless anchor=None |
| attributes | _keyword list_ | SVG attributes |

The number of edges is one more than the number of values because the values sit between neighboring pairs of edges.  If you like, you can consider the first N edges as the left boundaries of bins and the last edge as the right boundary of the last bin.

For your convenience, the [plot.edges](plotedges.md) function creates uniform bin edges.
```
>>> from plothon.plot
>>> edges(0, 1, 5)
[0, 0.20000000000000001, 0.40000000000000002, 0.60000000000000009, 0.80000000000000004, 1]
>>> Steps(edges(0, 1, 5), [88., 22., 44., 33., 11.])
<plothon.plot.Steps (5 points) {'stroke-linejoin': 'miter'}
```

The anchor is important for filling the steps.  By returning to a given y value (0 by default), the fill region is guaranteed to have a horizontal edge.

The constructor arguments become data members and can be changed at any time.

## Methods ##

### plot.Steps.SVG ###

Draws the Steps in a given [plot.DataTrans](plotDataTrans.md) transformation. Output is an [svg.SVG](svgSVG.md) object. See [plot.Plottable](plotPlottable.md) for the argument list.

### plot.Steps.xy ###

Returns the x-y positions of step vertices in a [(x,y), (x,y), (x,y), ...] format suitable for [plot.PlottablePoints](plotPlottablePoints.md) such as [plot.Scatter](plotScatter.md) and [plot.Curve](plotCurve.md).

## Examples ##

_Coming soon!_

## See also ##

  * [plot.Plottable](plotPlottable.md): Steps's superclass
  * [plot.edges](plotedges.md): convenience function for making uniform edges
  * Back to [CompleteDocumentation](CompleteDocumentation.md)