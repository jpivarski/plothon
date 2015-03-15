# Class plot.Plottable #

Abstract class for plot contents, such as histograms, error bars, and mathematical functions.  Subclasses of Plottable can be drawn in [plot.Plot](plotPlot.md) and [plot.Frame](plotFrame.md), but direct instances of the Plottable class don't draw anything.  It's an organizational device.

## Subclasses ##

### Abstract subclasses ###

  * [plot.PlottablePoints](plotPlottablePoints.md): a list of tuples, usually with two components (x and y), though possibly more (error bars, Bezier control points, etc.).  Includes language features for easily extending and slicing the list

### Concrete subclasses ###

  * [plot.Curve](plotCurve.md): a smooth or piecewise linear curve defined by a set of x, y points
  * [plot.ErrorBars](plotErrorBars.md): circular points with vertical or horizontal error bars (may be asymmetric)
  * [plot.Function](plotFunction.md): a curve defined by a mathematical function y(x)
  * [plot.Parametric](plotParametric.md): a curve defined by two mathematical functions x(t), y(t)
  * [plot.ParametricLine](plotParametricLine.md): a curve defined two endpoints; in linear transformations, this is a line
  * [plot.PlottablePath](plotPlottablePath.md): an SVG path that can be transformed as data
  * [plot.Scatter](plotScatter.md): simple circular points at specified points
  * [plot.Steps](plotSteps.md): "steps" or a "skyline" plot of histogram values
  * [plot.SymbolScatter](plotSymbolScatter.md): places arbitrary SVG symbols at the specified points

## Language features ##

All Plottable subclasses can be overlaid by adding them.  The '+' operator has been overloaded to create a list of Plottables (actually a class called [plothon.plot.Plottables](plotPlottables.md)).
```
>>> from plothon.plot import *
>>> Plottable() + Plottable() + Plottable()
<plothon.plot.Plottables (3 Plottable objects)>
```

## Methods ##

All Plottable subclasses have the following methods.

### Method plot.Plottable.SVG ###

Draws the Plottable in a given transformation, returning an [svg.SVG](svgSVG.md) tree.  Usually called by [plot.Plot](plotPlot.md) or [plot.Frame](plotFrame.md).

This function serves a secondary purpose: it determines the minimum and maximum positions of all drawn vertices, which are used by [plot.Plot](plotPlot.md) and [plot.Frame](plotFrame.md) to determine coordinate ranges, if needed.  When Plottable.SVG is called, it sets or resets the following member data.

| inner\_xmin | minimum x vertex position in data coordinates |
|:------------|:----------------------------------------------|
| inner\_ymin | minimum y vertex position in data coordinates |
| inner\_xmax | maximum x vertex position in data coordinates |
| inner\_ymax | maximum y vertex position in data coordinates |
| outer\_xmin | minimum x vertex position in user SVG coordinates |
| outer\_ymin | minimum y vertex position in user SVG coordinates |
| outer\_xmax | maximum x vertex position in user SVG coordinates |
| outer\_ymax | maximum y vertex position in user SVG coordinates |

#### Arguments ####

| datatrans | default=None | if a [plot.DataTrans](plotDataTrans.md), apply the transformation to the Plottable before drawing it |
|:----------|:-------------|:-----------------------------------------------------------------------------------------------------|
| range\_filter | default=None | may be None or a function from x, y data coordinates to True/False.  If a function, only positions which return True will be included in inner\_xmin, ... outer\_ymax |

The transformation is used for drawing, and it also influences the outer vertex limits.  The range\_filter only affects inner and outer vertex limits.

### Method plot.Plottable.inner\_ranges ###

All Plottable subclasses must implement the inner\_ranges method, but it will not often be called by the user.  This function determines the minimum and maximum vertex positions in data coordinates, and does not draw SVG.  It sets the following data members.

| inner\_xmin | minimum x vertex position in data coordinates |
|:------------|:----------------------------------------------|
| inner\_ymin | minimum y vertex position in data coordinates |
| inner\_xmax | maximum x vertex position in data coordinates |
| inner\_ymax | maximum y vertex position in data coordinates |

This function is used internally by [plot.Plot](plotPlot.md) and [plot.Frame](plotFrame.md) as a quick alternative to plot.Plottable.SVG.  When xmin, ymin, xmax, and ymax are not specified, the plotter needs to find the inner ranges before constructing a transformation, which is then used in plot.Plottable.SVG.  If SVG-drawing is inexpensive, plot.Plottable.inner\_ranges can be a simple call to plot.Plottable.SVG.

## Static member data ##

### defaults ###

Every Plottable subclass has a dictionary of SVG attributes called defaults, which you can modify.  New instances will start with these attributes, unless a given attribute has been overridden with a keyword in the constructor arguments.
```
>>> from plothon.plot import *
>>> Curve.defaults
{'stroke-width': '0.5pt'}
>>> Curve([])
<plothon.plot.Curve (0 nodes) mode=lines {'stroke-width': '0.5pt'}>
>>> Curve.defaults["stroke"] = "blue"
>>> Curve([])
<plothon.plot.Curve (0 nodes) mode=lines {'stroke': 'blue', 'stroke-width': '0.5pt'}>
>>> Curve([], stroke="red")
<plothon.plot.Curve (0 nodes) mode=lines {'stroke': 'red', 'stroke-width': '0.5pt'}>
```

## Examples ##

_Coming soon!_

## See also ##

  * [plot.Plottables](plotPlottables.md): a list of Plottable objects with extra language features
  * Back to [CompleteDocumentation](CompleteDocumentation.md)