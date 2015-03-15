# Class plot.PlottablePath #

Arbitrary paths that mix linear segments, Bezier curves, elliptical arcs, and discontinuities are a basic element of SVG.  While SVG path elements may be included in an [svg.SVG](svgSVG.md) representation of an image, there are some circumstances in which one would want to distort an SVG path with a [plot.DataTrans](plotDataTrans.md).  The SVG language only supports linear transformations, but a [plot.DataTrans](plotDataTrans.md) may be any function.

See below for examples (_not yet, but soon!_).

## Arguments (for constructor) ##

| d | _required_ | the path data |
|:--|:-----------|:--------------|
| attributes | _keyword list_ | SVG attributes |

The path data may be a string (or Unicode) of SVG path data as described in the [SVG 1.1 specification](http://www.w3.org/TR/SVG/paths.html).  The PlottablePath parses path data in its constructor and sets the member datum plot.PlottablePath.d to the parsed output.  You may also pass pre-parsed path data in the format described below.

Any attributes are passed to the SVG output.

## Member data ##

### plot.PlottablePath.d ###

Stores the parsed path data as a list of drawing commands.  Each command is a tuple with one of the following structures.
  * ("Z/z",): close the current path
  * ("H/h", x) or ("V/v", y): a horizontal or vertical line segment to x or y
  * ("M/m/L/l/T/t", x, y, global): moveto, lineto, or smooth quadratic curveto point (x, y).  If global=True, (x, y) should not be transformed.
  * ("S/sQ/q", cx, cy, cglobal, x, y, global): polybezier or smooth quadratic curveto point (x, y) using (cx, cy) as a control point.  If cglobal or global=True, (cx, cy) or (x, y) should not be transformed.
  * ("C/c", c1x, c1y, c1global, c2x, c2y, c2global, x, y, global): cubic curveto point (x, y) using (c1x, c1y) and (c2x, c2y) as control points.  If c1global, c2global, or global=True, (c1x, c1y), (c2x, c2y), or (x, y) should not be transformed.
  * ("A/a", rx, ry, rglobal, x-axis-rotation, angle, large-arc-flag, sweep-flag, x, y, global): arcto point (x, y) using the aforementioned parameters.

In all cases, capital letters imply absolute motion to the given points/control points and lower-case letters imply a step which is relative to the previous (x, y) point (if it exists).

For all points, if the corresponding _global_ variable is False, the point is interpreted in user data coordinates and will be transformed by the [plot.DataTrans](plotDataTrans.md).  If _global_ is True, the point is interpreted in the user SVG coordinates and will not be transformed.  Between absolute versus relative motion and global versus local coordinates, there are four ways a given (x, y) pair can be interpreted.

In addition to the legal SVG plot data, parsed PlottablePaths accept the following new command:
  * (",/.", rx, ry, rglobal, angle, x, y, global): an ellipse at point (x, y) with radii (rx, ry).  If _angle_ is 0, the whole ellipse is drawn; otherwise, a partial ellipse is drawn.

This makes it easier to create dots (used internally by [plot.Scatter](plotScatter.md)).  The period (".") version of this command uses absolute positions and the comma (",") version is relative.

### plot.PlottablePath.attributes ###

Attributes which will be passed to the SVG output as a dictionary mapping names to values.

## Methods ##

### plot.PlottablePath.SVG ###

Draws the PlottablePath in a given [plot.DataTrans](plotDataTrans.md) transformation.  Output is an [svg.SVG](svgSVG.md) object.  See [plot.Plottable](plotPlottable.md) for the argument list.

## Considerations ##

Note that elliptical arcs and dots won't be properly transformed in all coordinate transformations.  Only the control points are set to the transformed coordinates.

## Examples ##

_Coming soon!_

## See also ##

  * [plot.Plottable](plotPlottable.md): PlottablePath's superclass
  * Back to [CompleteDocumentation](CompleteDocumentation.md)