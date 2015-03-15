# Class plot.PlottablePoints #

Abstract class for plot contents based on a list of tuples of numbers, such as (x, y).  The simplest example is [plot.Scatter](plotScatter.md), which is a set of circular dots located at a list of (x, y) points.  PlottablePoints objects, including subclasses, may be treated like Python lists to make it easier to add and delete points.  Subclasses of PlottablePoints can be drawn in [plot.Plot](plotPlot.md) and [plot.Frame](plotFrame.md), but direct instances of the PlottablePoints class don't draw anything.  It's an organizational device.

## Subclasses ##

### Concrete subclasses ###

  * [plot.Curve](plotCurve.md): a smooth or piecewise linear curve defined by a set of x, y points
  * [plot.ErrorBars](plotErrorBars.md): circular points with vertical or horizontal error bars (may be asymmetric)
  * [plot.Scatter](plotScatter.md): simple circular points at specified points
  * [plot.SymbolScatter](plotSymbolScatter.md): places arbitrary SVG symbols at the specified points

## Language features ##

PlottablePoints are iterable; the returned values are vertex points, in the following case, 2-tuples interpreted as x and y.
```
>>> from plothon.plot import *
>>> for x, y in Scatter([(0,0), (1,1), (2,2), (3,3), (4,4), (5,5)]):
...     print x, y
... 
0 0
1 1
2 2
3 3
4 4
5 5
```

Python's `len` function and `in` operator are supported.
```
>>> len(Scatter([(0,0), (1,1), (2,2), (3,3), (4,4), (5,5)]))
6
>>> (2,2) in Scatter([(0,0), (1,1), (2,2), (3,3), (4,4), (5,5)])
True
```

Points in a PlottablePoints can be accessed using Python's slice syntax,
```
>>> p = Scatter([(0,0), (1,1), (2,2), (3,3), (4,4), (5,5)])
>>> for x, y in p[3:]:
...     print x, y
... 
3 3
4 4
5 5
>>> for x, y in p[:-2]:
...     print x, y
... 
0 0
1 1
2 2
3 3
>>> for x, y in p[::2]:
...     print x, y
... 
0 0
2 2
4 4
```
... including assignment,
```
>>> p[2] = (99, 99)
>>> for x, y in p:
...     print x, y
... 
0 0
1 1
99 99
3 3
4 4
5 5
```
... and deleting.
```
>>> del p[3:]
>>> for x, y in p:
...     print x, y
... 
0 0
1 1
99 99
```

## Methods ##

### Method plot.PlottablePoints.prepend ###

Add a point to the beginning of the list.

#### Arguments ####

| value | _required_ | the point to prepend |
|:------|:-----------|:---------------------|

### List-like interface methods ###

All of the following methods implement the same functionality as Python lists, with the same arguments.

The only functionality that PlottablePoints objects do not share with lists is concatenation with the plus operator, which is interpreted by the superclass, [plot.Plottable](plotPlottable.md) as superimposing graphical content.  (See also [plot.Plottables](plotPlottables.md).)

#### Adding and removing points ####

  * plot.PlottablePoints.append(value): add a point to the end of the list
  * plot.PlottablePoints.insert(i, value): insert a point at a specified index
  * plot.PlottablePoints.remove(value): removes the first instance of _value_ (if any)
  * plot.PlottablePoints.extend(value): concatenate _value_, another list of points, to the end of the list.  Use this function instead of the plus operator.
  * plot.PlottablePoints.pop(i): delete and return the last index (or optionally index _i_).  The corresponding "push" method is append.

#### Re-ordering points ####

  * plot.PlottablePoints.reverse(): reverse the order of the list of points
  * plot.PlottablePoints.sort(compare): sort the list of points according to a given pairwise comparison function.  The following sorts by x values:
```
>>> p = Scatter([(10, 5), (3, 9), (4, 4), (2, 7), (8, 10)])
>>> p.sort(lambda a, b: cmp(a[0], b[0]))
>>> for x, y in p:
...     print x, y
... 
2 7
3 9
4 4
8 10
10 5
```

#### Searching functions ####

  * plot.PlottablePoints.index(x, start, stop): return the index of the first element equal to _x_, optionally between indices _start_ and _stop_.
  * plot.PlottablePoints.count(value): return the number of elements equal to _value_.

## Data members ##

### plot.PlottablePoints.points ###

The list of points.  Any of the list operations above could be applied directly to plot.PlottablePoints.points, but that's 7 more characters to type.

## Technical details ##

Subclasses of PlottablePoints do not need to reimplement the inner\_ranges method if the first two elements of each tuple represents the (x, y) location of each vertex in data coordinates (by far the most common case).

## See also ##

  * [plot.Plottable](plotPlottable.md): PlottablePoints's superclass
  * Back to [CompleteDocumentation](CompleteDocumentation.md)