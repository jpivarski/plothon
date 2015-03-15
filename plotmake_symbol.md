# Function plot.make\_symbol #

Creates a new [svg.SVG](svgSVG.md) symbol object from a template.

## Arguments ##

| template | default="dot" | name of template |
|:---------|:--------------|:-----------------|
| name | default=None | the id of the new symbol; if None, a unique name is assigned |
| attributes | _keyword list_ | SVG attributes applied to the new symbol's drawing commands (not the symbol itself) |

The templates are in a dictionary called plot.symbolTemplates, which maps names to [svg.SVG](svgSVG.md) symbols.  The plot.symbolTemplates dictionary currently contains
| dot | a circle |
|:----|:---------|
| box | a square |
| uptri | an equilateral triangle pointing up |
| downtri | an equilateral triangle pointing down |
All of the templates have fill="black", stroke="none".  For outlines instead of filled shapes, set fill="none", stroke=

&lt;color&gt;

.

## See also ##

  * see [plot.SymbolScatter](plotSymbolScatter.md): draws the symbol at a list of points
  * Back to [CompleteDocumentation](CompleteDocumentation.md)