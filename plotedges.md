# Function plot.edges #

Creates uniform edges for [plot.Steps](plotSteps.md).  See [plot.Steps](plotSteps.md) for examples.

## Arguments ##

| low | _required_ | the left edge of the first bin |
|:----|:-----------|:-------------------------------|
| high | _required_ | the right edge of the last bin |
| numbins | _required_ | the number of bins |

This function outputs a list of numbins+1 numbers, uniformly-spaced from low to high, inclusive.

## See also ##

  * [plot.Steps](plotSteps.md): draws histogram steps, the primary application
  * Back to [CompleteDocumentation](CompleteDocumentation.md)