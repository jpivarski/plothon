# Class plot.Curve #

Given a list of points, Curve draws a line connecting them with several interpolation options.  You can use this to draw connected line segments (loop=False) or polygons (loop=True) with the default linear interpolation ("lines").  If you have a function or pair of parametric functions describing your curve, use [plot.Function](plotFunction.md) or [plot.Parametric](plotParametric.md) instead.  If you have a data set, you probably shouldn't connect the points but use something like [plot.Scatter](plotScatter.md) instead, though that's up to you.

See below for examples (not yet, but soon!)

## Arguments (for constructor) ##

| points | _required_ | a list of points to plot |
|:-------|:-----------|:-------------------------|
| mode | default="lines" | how the points will be interpreted |
| loop | default=False | if True, the first point is connected to the last point, closing the loop |
| attributes | _keyword list_ | SVG attributes |

The mode determines what kind of curve to draw, some of which require more points than others.  If too many values are given to specify a point, the extra numbers will be ignored (so that you can easily switch from "bezier"/"velocity"/"foreback" to "lines" or "smooth").

| "lines" | points=[(x,y), (x,y), ...] | piecewise-linear segments joining the (x,y) points |
|:--------|:---------------------------|:---------------------------------------------------|
| "bezier" | points=[(x, y, c1x, c1y, c2x, c2y), ...] | Bezier curve with two control points (control points preceed (x,y), as in SVG paths).  If (c1x,c1y) and (c2x,c2y) both equal (x,y), you get a linear interpolation ("lines") |
| "velocity" | points=[(x, y, vx, vy), ...] | curve that passes through (x,y) with velocity (vx,vy) (one unit of arclength per unit time); in other words, (vx,vy) is the tangent vector at (x,y).  If (vx,vy) is (0,0), you get a linear interpolation ("lines"). |
| "foreback" | points=[(x, y, bx, by, fx, fy), ...] | like "velocity" except that there is a left derivative (bx,by) and a right derivative (fx,fy).  If (bx,by) equals (fx,fy) (with no minus sign), you get a "velocity" curve |
| "smooth" | points=[(x,y), (x,y), ...] | a "velocity" interpolation with (vx,vy)`[i]` equal to ((x,y)`[i+1]` - (x,y)`[i-1])/2`: the minimal derivative |

The constructor arguments become member data and may be changed at any time.  The points can be edited with the language features described in the [plot.PlottablePoints](plotPlottablePoints.md) superclass.

## Methods ##

### plot.Curve.SVG ###

Draws the Curve in a given [plot.DataTrans](plotDataTrans.md) transformation.  Output is an [svg.SVG](svgSVG.md) object.  See [plot.Plottable](plotPlottable.md) for the argument list.

## Examples ##

_Coming soon!_

## See also ##

  * [plot.PlottablePoints](plotPlottablePoints.md): Curve's direct superclass
  * [plot.Plottable](plotPlottable.md): Curve's ultimate superclass
  * Back to [CompleteDocumentation](CompleteDocumentation.md)