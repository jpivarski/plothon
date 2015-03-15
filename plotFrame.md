# Class plot.Frame #

Creates a standard physicist's plot with four axes enclosing a box around the data.  Basic parameters, such as the region of the graphics to display and the positions and text of tick marks, can be guessed if left as None or set explicitly.  Frame objects can only apply linear and logarithmic transformations to the data (class [plot.DataTransWindow](plotDataTransWindow.md)).

While the top and right axes are referred to as "top" and "right," the bottom and left axes are called "x" and "y."  This eases the transition between Frames and [Plot](plotPlot.md)s.

Most of the parameters are configurable, but if you need more control, modify the [svg.SVG](svgSVG.md) output.

See below for examples (_not yet, but soon!_).

## Arguments (for constructor) ##

| data | _required_ | a [plot.Plottable](plotPlottable.md), a list of plot.Plottables, or a [plot.Plottables](plotPlottables.md) list of content to plot; can be [.md](.md) for nothing (except the frame) |
|:-----|:-----------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| xmin | default=None | minimum x in data coordinates |
| ymin | default=None | minimum y in data coordinates |
| xmax | default=None | maximum x in data coordinates |
| ymax | default=None | maximum y in data coordinates |
| parameters | _keyword list_ | list of Plot parameters |

The following are Frame parameters.

| x | default=0. | left edge of the output image |
|:--|:-----------|:------------------------------|
| y | default=0. | upper edge of the output image |
| width | default=100. | width of the output image |
| height | default=100. | height of the output image |
| xlogbase | default=None | if None, the x (bottom) axis is linear; if a number, the x axis is logarithmic with the specified base (for default tick positions) |
| ylogbase | default=None | if None, the y (left) axis is linear; if a number, the y axis is logarithmic with the specified base (for default tick positions) |
| xticks | default=None | dictionary mapping x (bottom) tick positions to tick label strings |
| xminiticks | default=None | list of x (bottom) minitick positions  |
| yticks | default=None | dictionary mapping y (left) tick positions to tick label strings |
| yminiticks | default=None | list of y (left) minitick positions |
| rightticks | default=None | dictionary mapping right tick positions to tick label strings |
| rightminiticks | default=None | list of right minitick positions |
| topticks | default=None | dictionary mapping top tick positions to tick label strings |
| topminiticks | default=None | list of top minitick positions |
| xlabel | default=None | if a string, an x (bottom) axis label is placed below the tick labels |
| ylabel | default=None | if a string, a y (left) axis label is placed to the left of the tick labels (and rotated counter-clockwise) |
| rightlabel | default=None | if a string, a right axis label is placed to the right of the tick labels (and rotated clockwise) |
| toplabel | default=None | if a string, a top axis label is placed above the tick labels (can be a plot title) |
| background | default={} | the background is a rectangle placed behind the data; attributes may be passed through this dictionary (maps attribute names to values).  Default is no stroke and no fill: if {}, an invisible SVG element is created (that can be edited in Inkscape); if None, no element is created. |
| xgrid | default=None | if an attribute dictionary, x (vertical) grid lines are drawn behind the data on the major tick marks; default is a "gray" stroke |
| xminigrid | default=None | if an attribute dictionary, x (vertical) minigrid lines are drawn behind the data on the minitick marks; default is a "lightgray" stroke |
| ygrid | default=None | if an attribute dictionary, y (horizontal) grid lines are drawn behind the data on the major tick marks; default is a "gray" stroke |
| yminigrid | default=None | if an attribute dictionary, y (horizontal) minigrid lines are drawn behind the data on the minitick marks; default is a "lightgray" stroke |
| tick\_length | default=2. | length of tick marks in SVG user units |
| minitick\_length | default=1. | length of minitick marks in SVG user units |
| font\_size | default=5 | height of tick labels in SVG user units |
| draw\_left\_border | default=True | if False, draw left (y) ticks but no left border |
| draw\_top\_border | default=True | if False, draw top ticks but no top border |
| draw\_right\_border | default=True | if False, draw right ticks but no right border |
| draw\_bottom\_border | default=True | if False, draw bottom (x) ticks but no bottom border |
| margin\_left | default=1. | distance in user SVG units between x and the left edge of the drawing |
| margin\_left\_label | default=1. | distance in SVG units between the ylabel and the ytick labels |
| margin\_left\_ticklabel | default=1. | distance in SVG units between the ytick labels and the yticks |
| margin\_top | default=1. | distance in user SVG units between y and the top edge of the plot frame |
| margin\_top\_label | default=1. | distance in user SVG units between the toplabel and the toptick labels |
| margin\_top\_ticklabel | default=1. | distance in user SVG units between the toptick labels and the plot frame |
| margin\_right | default=1. | distance in user SVG units between x+width and the right edge of the drawing |
| margin\_right\_label | default=1. | distance in user SVG units between the rightlabel and the righttick labels |
| margin\_right\_ticklabel | default=1. | distance in user SVG units between the righttick labels and the plot frame |
| margin\_bottom | default=1. | distance in user SVG units between y+height and the bottom edge of the drawing |
| margin\_bottom\_labels | default=1. | distance in user SVG units between the xlabel and the xtick labels |
| margin\_bottom\_ticklabel | default=1. | distance in user SVG units between the xtick labels and the plot frame |

Any arguments with a default value of None will be replaced by reasonable guesses, based on the data.  For instance, xmin, ymin, xmax, and ymax will be set to show all vertices with a comfortable margin.  Ticks will be optimized, given the available space.  These guesses are all calculated when an SVG image is drawn (method plot.Frame.SVG).  Rather than replacing these parameters, the guessed values are stored in the following new member data.

| last\_xmin | value of xmin used in the last plot |
|:-----------|:------------------------------------|
| last\_ymin | value of ymin used in the last plot |
| last\_xmax | value of xmax used in the last plot |
| last\_ymax | value of ymax used in the last plot |
| last\_xticks | value of xticks used in the last plot |
| last\_xminiticks | value of xminiticks used in the last plot |
| last\_yticks |value of yticks used in the last plot |
| last\_yminiticks | value of yminiticks used in the last plot |
| last\_rightticks | value of rightticks used in the last plot |
| last\_rightminiticks | value of rightminiticks used in the last plot |
| last\_topticks | value of topticks used in the last plot |
| last\_topminiticks | value of topminiticks used in the last plot |

```
>>> from plothon.plot import *
>>> p = Frame(Function("x", 0, 1))
>>> print p.xticks
None
>>> print p.last_xticks
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
AttributeError: Frame instance has no attribute 'last_xticks'
>>> p.SVG()
<svg.SVG g {'font-size': 5, 'id': 'plot394', 'clip-path': 'url(#dataclip394)'} (10 children)>
{0.0: '0', 1.0: '1', 0.4: '0.4', 0.8: '0.8', 1.2: '1.2', 0.6: '0.6', 0.2: '0.2', -0.2: u'\u20130.2'}
```

## Language features ##

All parameters (including xmin, ymin, xmax, and ymax) become member data of the Frame instance.  The behavior of SVG drawing is determined by the member data.
```
>>> from plothon.plot import *
>>> p = Frame([], x=20, y=30)
>>> p.x, p.y, p.width
(20, 30, 100.0)
>>> p.width = 80
>>> p.x, p.y, p.width
(20, 30, 80)
```

  * If you forget to set a parameter when you create a named plot, you can always set it later.
  * If you want to create a plot, draw it, and let it disappear without naming it, you can do so by putting all parameters on one command line.
```
>>> from plothon.plot import *
>>> Frame(Function("x**2", 0, 1), 0, 0, 1, 1, xticks={0:"start", 0.5:"middle", 1:"end"}).SVG().save("output.svg")
```

Unrecognized parameters are simply ignored.

## Methods ##

### Method plot.Frame.SVG ###

Used to draw the Frame.  The output of this function is an [svg.SVG](svgSVG.md) object, which can be immediately saved to a file.

#### Arguments ####

| attributes | keyword list | passed to the top-level SVG element (a "g" group) |
|:-----------|:-------------|:--------------------------------------------------|

## Examples ##

_Coming soon!_

## See also ##

  * [plot.Plot](plotPlot.md): a plot with an x and y axis (cross-hairs), rather than an enclosed box.  Any transformation is possible, not just linear and logarithmic.
  * Back to [CompleteDocumentation](CompleteDocumentation.md)