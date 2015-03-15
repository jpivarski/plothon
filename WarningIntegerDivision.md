# Warning: integer division #

In Python, the ratio of two integers is an integer, even if it must truncate the result:
```
>>> 1/2
0
>>> 1./2.
0.5
```
This feature applies to function strings as well.
```
>>> Parametric("t/2, t/3", 0, 1)(2)
(1, 0)
>>> Parametric("t/2, t/3", 0, 1)(2.)
(1.0, 0.66666666666666663)
```

There are two ways to guarantee rational division in function strings.
  1. Convert variables into floats
```
>>> Parametric("float(t)/2, float(t)/3", 0, 1)(2)
(1.0, 0.66666666666666663)
```
  1. Multiply expressions by 1.0 (make sure that the 1.0 multiplication happens first in the order of operations)
```
>>> Parametric("1.*t/2, 1.*t/3", 0, 1)(2)
(1.0, 0.66666666666666663)
```

To guarantee rational division in all other cases, simply
```
>>> from __future__ import division
```
as the first line in your script (before any other import statements).  Now ratios like `1/2` will always return `0.5`, except in function strings.

## See also ##

  * [plot.Parametric](plotParametric.md) uses function strings "x(t), y(t)"
  * [plot.Function](plotFunction.md) uses function strings "y(x)"
  * [plot.DataTrans](plotDataTrans.md) uses function strings "x'(x,y), y'(x,y)"
  * [plot.DataTransComplex](plotDataTransComplex.md) uses function strings "z'(z)"
  * Back to [CompleteDocumentation](CompleteDocumentation.md)