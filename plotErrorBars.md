# plot.ErrorBars #

Draws error bars and/or dots at a list of points.  Multi-valued error bars can be formed by composing several ErrorBars drawings.

See below for examples (not yet, but soon!)

## Arguments (for constructor) ##

| points | _required_ | a list of points to plot |
|:-------|:-----------|:-------------------------|
| mode | default="y" | "x" for horizontal error bars, "y" for vertical error bars, "xy" for both, and "ax", "ay" for asymmetric error bars |
| draw\_mode | default=".=|" | parts of the error bar to draw: "." for a central dot, "=" for the caps at the ends of the bar, and "|" for the bar itself |
| radius | default=1. | radius of the dots in user SVG coordinates (if drawn) |
| cap\_length | default=1. | length of the caps in user SVG coordinates (if drawn) |
| attributes | _keyword list_ | SVG attributes |

The mode determines how points is interpreted.  The first two values in each point are always the central value (x,y).  If horizontal error bars are to be drawn, the next value is the length of the horizontal error bars (from the central value to the end, in data coordinates).  If vertical error bars are to be drawn, the next value is their lengths.  If an error bar is asymmetric, it requires two values, rather than one.  Asymmetric error bars should be written as (negative, positive), where the first is left or down and the second is right or up.  If both are positive or both are negative, both error bars will be drawn on the same side of the point.

It is difficult (and dangerous!) to try to keep track of how the points are interpreted by counting the entries, so the plot.ErrorBars.interpret method prints a message explaining exactly how the points will be interpreted.

The characters in mode and draw\_mode can be given in any order (except that "a" always modifies the "x" or "y" that it immediately preceeds).

You may want to supress drawing points (draw\_mode without a ".") or vertical bars (without a "|") because you are composing ErrorBars to make a multi-valued error bar.  For instance, statistical and systematic errors are sometimes drawn on the same bar, which can be done by representing the sum in quadrature of the two with an ErrorBars that draws ".=|" overlaid by an ErrorBars representing the statistics only with "=".  This avoids overlapping points and vertical bars, which sometimes don't render well.  (See examples below.)

The constructor arguments become member data and may be changed at any time. The points can be edited with the language features described in the [plot.PlottablePoints](plotPlottablePoints.md) superclass.

## Methods ##

## plot.ErrorBars.SVG ##

Draws the ErrorBars in a given [plot.DataTrans](plotDataTrans.md) transformation. Output is an [svg.SVG](svgSVG.md) object. See [plot.Plottable](plotPlottable.md) for the argument list.

## plot.ErrorBars.interpret ##

Parse mode, draw\_mode, and determine how points will be interpreted.  By default, this prints a helpful message to the user.

### Arguments ###

| printout | default=True | if False, suppress output (when used as an internal function) |
|:---------|:-------------|:--------------------------------------------------------------|

Here is an example of the output.
```
>>> ErrorBars([(0,0,1,2,3,4)], mode="xay").interpret()
Data mode: x error bars, asymmetric y bars
Draw mode: circular points, caps at +-1 sigma, lines from -1 to 1 sigma

In each entry, [0:2] is the x,y point
               [2] is the length of the symmetric x error bars
               [3:5] are the ends of the asymmetric y error bars

For example, in points[0] = (0, 0, 1, 2, 3, 4),
(0, 0) is the x,y point, 1 is the x error bar, (2, 3) are y error bars
```

## Examples ##

_Coming soon!_

## See also ##

  * [plot.PlottablePoints](plotPlottablePoints.md): ErrorBars's direct superclass
  * [plot.Plottable](plotPlottable.md): ErrorBars's ultimate superclass
  * Back to [CompleteDocumentation](CompleteDocumentation.md)