# Class plot.SymbolScatter #

Draws an arbitrary SVG symbol at each of a list of points.  SymbolScatter is capable of drawing dots (in fact, it's the default), but [plot.Scatter](plotScatter.md) combines all dots in a single path, while SymbolScatter invokes SVG's "use" element for each point, so [plot.Scatter](plotScatter.md) is often more efficient.

For error bars, see [plot.ErrorBars](plotErrorBars.md).  To draw SVG symbols with error bars, compose a [plot.ErrorBars](plotErrorBars.md) without dots under a SymbolScatter.

See below for examples (not yet, but soon!)

## Arguments (for constructor) ##

| points | _required_ | a list of points to plot |
|:-------|:-----------|:-------------------------|
| symbol | default=None | SVG symbol to use; creates a simple dot symbol if None |
| width | None | if not None, this width is passed to every symbol |
| height | None | if not None, this height is passed to every symbol |
| attributes | _keyword list_ | SVG attributes |

The points argument must be a list of (x,y) pairs. Additional values beyond x and y will be ignored.

The symbol is an [svg.SVG](svgSVG.md) object, with the following structure:
```
svg.SVG("symbol", <SVG drawing commands centered on zero>, viewBox="0 0 1 1", overflow="visible")
```
Be careful about assinging one SVG object to two or more SymbolScatter drawings.  If you change the appearance of the symbol, it will change in all plots, which may not be what you want.  The [plot.make\_symbol](plotmake_symbol.md) function creates new symbol objects with unique identifiers based on templates.

The constructor arguments become member data and may be changed at any time. The points can be edited with the language features described in the [plot.PlottablePoints](plotPlottablePoints.md) superclass.

## Methods ##

### plot.SymbolScatter.SVG ###

Draws the SymbolScatter in a given [plot.DataTrans](plotDataTrans.md) transformation. Output is an [svg.SVG](svgSVG.md) object. See [plot.Plottable](plotPlottable.md) for the argument list.

## Example ##

_Coming soon!_

## See also ##

  * [plot.make\_symbol](plotmake_symbol.md): creates a new SVG symbol object
  * [plot.PlottablePoints](plotPlottablePoints.md): SymbolScatter's direct superclass
  * [plot.Plottable](plotPlottable.md): SymbolScatter's ultimate superclass
  * Back to [CompleteDocumentation](CompleteDocumentation.md)