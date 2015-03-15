# Class plot.Plot #

Creates a standard mathematician's plot with a horizontal x axis and a vertical y axis (cross-hairs).  Basic parameters, such as the region of the graphics to display and the positions and text of tick marks, can be guessed if left as None or set explicitly.  Plot objects can apply arbitrary transformations to the data (class [plot.DataTrans](plotDataTrans.md)), some of which result in curving coordinate axes.

Most of the parameters are configurable, but if you need more control, modify the [svg.SVG](svgSVG.md) output.

See below for examples (_not yet, but soon!_).

## Arguments (for constructor) ##

| data | _required_ | a [plot.Plottable](plotPlottable.md), a list of plot.Plottables, or a [plot.Plottables](plotPlottables.md) list of content to plot; can be [.md](.md) for nothing (except the axis) |
|:-----|:-----------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| xmin | default=None | minimum x in data coordinates |
| ymin | default=None | minimum y in data coordinates |
| xmax | default=None | maximum x in data coordinates |
| ymax | default=None | maximum y in data coordinates |
| parameters | _keyword list_ | list of Plot parameters |

The following are Plot parameters.

| datatrans | default=None | transformation function to apply to the data, an instance of class [plot.DataTrans](plotDataTrans.md) |
|:----------|:-------------|:------------------------------------------------------------------------------------------------------|
| x | default=0. | left edge of the output image |
| y | default=0. | upper edge of the output image |
| width | default=100. | width of the output image |
| height | default=100. | height of the output image |
| draw\_axis | default=True | if False, only draw the data |
| draw\_arrows | default=True | if False, don't draw arrows |
| xticks | default=None | dictionary mapping x tick positions to tick label strings |
| xminiticks | default=None | list of x minitick positions |
| yticks | default=None | dictionary mapping y tick positions to tick label strings |
| yminiticks | default=None | list of y minitick positions |
| xaxis | default=0. | the y (vertical) position of the x axis |
| yaxis | default=0. | the x (horizontal) position of the y axis |
| transform\_text | default=False | if True, distort tick label text with the datatrans transformation (linear approximation); if False, only rotate the text |
| xlabel | default=None | _Not yet implemented_ |
| ylabel | default=None | _Not yet implemented_ |
| tick\_length | default=1.5 | length of tick marks in SVG user units |
| minitick\_length | default=0.75 | length of minitick marks in SVG user units |
| font\_size | default=5 | height of tick labels in SVG user units |
| margin\_xticklabel | default=1. | distance between the x ticks and the x tick labels |
| margin\_yticklabel | default=1. | distance between the y ticks and the y tick labels |
| margin\_avoidance | default=5. | x tick labels are not drawn when they're too close to the y axis (overlapping is ugly); this parameter specifies the region of avoidance in SVG user units |
| margin\_left | default=5. | distance in user SVG units between x and the left edge of the drawing |
| margin\_top | default=5. | distance in user SVG units between y and the top edge of the drawing |
| margin\_right | default=5. | distance in user SVG units between x+width and the right edge of the drawing |
| margin\_bottom | default=5. | distance in user SVG units between y+height and the bottom edge of the drawing |

Any arguments with a default value of None will be replaced by reasonable guesses, based on the data.  For instance, xmin, ymin, xmax, and ymax will be set to show all vertices with a comfortable margin.  Ticks will be optimized, given the available space.  These guesses are all calculated when an SVG image is drawn (method plot.Plot.SVG).  Rather than replacing these parameters, the guessed values are stored in the following new member data.

| last\_xmin | value of xmin used in the last plot |
|:-----------|:------------------------------------|
| last\_ymin | value of ymin used in the last plot |
| last\_xmax | value of xmax used in the last plot |
| last\_ymax | value of ymax used in the last plot |
| last\_xticks | value of xticks used in the last plot |
| last\_xminiticks | value of xminiticks used in the last plot |
| last\_yticks |value of yticks used in the last plot |
| last\_yminiticks | value of yminiticks used in the last plot |
| last\_xaxis | value of xaxis used in the last plot |
| last\_yaxis | value of yaxis used in the last plot |

```
>>> from plothon.plot import *
>>> p = Plot(Function("x", 0, 1))
>>> print p.xticks
None
>>> print p.last_xticks
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
AttributeError: Plot instance has no attribute 'last_xticks'
>>> p.SVG()
<svg.SVG g {'font-size': 5, 'id': 'plot394', 'clip-path': 'url(#dataclip394)'} (10 children)>
{0.0: '0', 1.0: '1', 0.4: '0.4', 0.8: '0.8', 1.2: '1.2', 0.6: '0.6', 0.2: '0.2', -0.2: u'\u20130.2'}
```

## Language features ##

All parameters (including xmin, ymin, xmax, and ymax) become member data of the Plot instance.  The behavior of SVG drawing is determined by the member data.
```
>>> from plothon.plot import *
>>> p = Plot([], x=20, y=30)
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
>>> Plot(Function("x**2", 0, 1), 0, 0, 1, 1, xticks={0:"start", 0.5:"middle", 1:"end"}).SVG().save("output.svg")
```

Unrecognized parameters are simply ignored.

## Methods ##

### Method plot.Plot.SVG ###

Used to draw the Plot.  The output of this function is an [svg.SVG](svgSVG.md) object, which can be immediately saved to a file.

#### Arguments ####

| attributes | keyword list | passed to the top-level SVG element (a "g" group) |
|:-----------|:-------------|:--------------------------------------------------|

## Examples ##

_Coming soon!_

## See also ##

  * [plot.Frame](plotFrame.md): a plot with an enclosing frame, rather than cross-hairs.  Easier to implement logarithmic transformations.
  * Back to [CompleteDocumentation](CompleteDocumentation.md)