# Class plot.Plottables #

A list of [plot.Plottable](plotPlottable.md) objects, represents multiple layers of overlaid content (histogram with errorbars, data with a fit function, overlapping mathematical functions, etc).  Most of the language features associated with Python lists apply to Plottables.

Users generally won't care about this class explicitly; it works behind the scenes to make it possible to overlay content with plus signs.

## Rationale ##

This class exists only to let [plot.Plot](plotPlot.md), [plot.Frame](plotFrame.md), and other plotting classes be more loose in what they accept as their "data" argument.  The following are equivalent,
```
>>> Plot([Function("x", 0, 1), Function("x**2", 0, 1)]).SVG().save()
>>> Plot(Function("x", 0, 1) + Function("x**2", 0, 1)).SVG().save()
```
but the one with square brackets can be annoying when you're trying to type quickly, because it's easy to get "]" and ")" mixed up.  It's also nice that users are not forced to type
```
>>> Plot([Function("x", 0, 1)]).SVG().save()
```
or
```
>>> Plot((Function("x", 0, 1),)).SVG().save()
```
to plot a single object.  If it were me, I would forget the square brackets or comma _every_ time.

One could argue that it would be better for [plot.Plot](plotPlot.md), [plot.Frame](plotFrame.md), etc. to just accept a variable number of Plottable arguments, but that would make it impossible for these functions to accept any other non-keyword arguments, such as xmin, ymin, xmax, and ymax.  Instead, I chose to delimit Plottables with plus signs and arguments with commas.

## Language Features ##

A Plottables object can be created by
  * adding [plot.Plottable](plotPlottable.md) objects together:
```
>>> from plothon.plot import *
>>> Function("x", 0, 1) + Function("x**2", 0, 1) + Function("x**3", 0, 1)
<plothon.plot.Plottables (3 Plottable objects)>
```
  * passing a list to the Plottables constructor:
```
>>> Plottables([Function("x", 0, 1), Function("x**2", 0, 1), Function("x**3", 0, 1)])
<plothon.plot.Plottables (3 Plottable objects)>
```
  * passing the Plottable objects as individual arguments:
```
>>> Plottables(Function("x", 0, 1), Function("x**2", 0, 1), Function("x**3", 0, 1))
<plothon.plot.Plottables (3 Plottable objects)>
```
  * with arbitrary topology:
```
>>> Plottables([Function("x", 0, 1), Plottables([[[Function("x**2", 0, 1)]]], Function("x**3", 0, 1))])
<plothon.plot.Plottables (3 Plottable objects)>
```

The Plottables will always be a flat list (not a tree), always ready for plotting.  You're not supposed to care about all the ways you can create Plottables, just be assured that all reasonable ways work.

Binary adding creates a new Plottables, but adding in place modifies an existing one.
```
>>> p = Function("x", 0, 1) + Function("x**2", 0, 1) 
>>> p, id(p)
(<plothon.plot.Plottables (2 Plottable objects)>, -1211529588)
>>> p += Function("x**3", 0, 1)
>>> p, id(p)
(<plothon.plot.Plottables (3 Plottable objects)>, -1211529588)
```

Plottables are iterable.
```
>>> for p in Plottables(Function("x", 0, 1), Function("x**2", 0, 1), Function("x**3", 0, 1)):
...     print p
... 
<plothon.plot.Function x -> x [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**2 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**3 [0,1] {'stroke-width': '0.5pt'}>
```

Plottables support Python's length function.
```
>>> len(Plottables(Function("x", 0, 1), Function("x**2", 0, 1), Function("x**3", 0, 1)))
3
```

Slices can be retrieved, assigned, and deleted.
```
>>> p = Plottables([Function("x**%d" % i, 0, 1) for i in range(20)])
>>> p
<plothon.plot.Plottables (20 Plottable objects)>
>>> 
>>> for i in p[5:15:3]:
...     print i
... 
<plothon.plot.Function x -> x**5 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**8 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**11 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**14 [0,1] {'stroke-width': '0.5pt'}>
>>> 
>>> p[5:15] = (Function("x**99", 0, 1) + Function("x**100", 0, 1))
>>> 
>>> del p[-1]
>>> 
>>> for i in p:
...     print i
... 
<plothon.plot.Function x -> x**0 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**1 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**2 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**3 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**4 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**99 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**100 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**15 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**16 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**17 [0,1] {'stroke-width': '0.5pt'}>
<plothon.plot.Function x -> x**18 [0,1] {'stroke-width': '0.5pt'}>
```

## Methods ##

### Method plot.Plottables.append ###

Exactly like the append function for Python lists.  When a [plot.Plottable](plotPlottable.md) is appended to the end of a list, it is superimposed on top of all other graphics.

#### Arguments ####

| value | _required_ | a [plot.Plottable](plotPlottable.md) |
|:------|:-----------|:-------------------------------------|

### Method plot.Plottables.prepend ###

Adds a [plot.Plottable](plotPlottable.md) to the beginning of a Plottables list.  When prepended, a graphic is drawn below all other graphics, and may be partially or entirely hidden.

#### Arguments ####

| value | _required_ | a [plot.Plottable](plotPlottable.md) |
|:------|:-----------|:-------------------------------------|

## See also ##

  * [plot.Plottable](plotPlottable.md)
  * Back to [CompleteDocumentation](CompleteDocumentation.md)