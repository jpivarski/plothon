## Step-by-step tutorials ##

  * HowToInstall: _Instructions for downloading and installing_
  * TutorialForPhysicists: _Introduction to Plothon for data analysis_
  * TutorialForWikipedia: _How to use Plothon to make Wikipedia plots_

## Future of Plothon ##

  * [Bug tracking](http://code.google.com/p/plothon/issues/list): _Post bug reports here_
  * WishList: _Features that we plan to add to Plothon and their priorities_

## Warnings about the Python language ##

  * [WarningIntegerDivision](WarningIntegerDivision.md): Division of any two integers returns an integer, even if it must be truncated
  * [WarningReferences](WarningReferences.md): All Python objects, even simple types like numbers, are references

## Reference ##

  * [Alphabetized index](http://code.google.com/p/plothon/w/list?can=2&q=Docs-UserReference&colspec=Summary+Changed)
  * [Example index](http://code.google.com/p/plothon/w/list?can=2&q=Docs-Examples&colspec=Summary+Changed)

### Classes that make plots ###

  * [plot.Plot](plotPlot.md): coordinate axis, transformable by [plot.DataTrans](plotDataTrans.md)
  * [plot.Frame](plotFrame.md): enclosing frame for linear, log, and semilog plots [plot.DataTransWindow](plotDataTransWindow.md)

### Classes that plot content ###

#### Generic superclasses ####

None of these plot content, but they organize the classes which do.

  * [plot.Plottable](plotPlottable.md): everything that plots content must descend from this
  * [plot.Plottables](plotPlottables.md): a list of [plot.Plottable](plotPlottable.md)s with convenience operators
  * [plot.PlottablePoints](plotPlottablePoints.md): a list of points to be plotted with convenience operators

#### Lines and curves ####

  * [plot.PlottablePath](plotPlottablePath.md): shape defined by an SVG path specification (a way to deform SVG art with [plot.DataTrans](plotDataTrans.md))

  * [plot.Curve](plotCurve.md): shape defined by a list of numbers (can be piecewise linear, smoothed, Bezier, or described by velocity)

  * [plot.Parametric](plotParametric.md): shape defined by x(t), y(t) (string or function)
    * [plot.Parametric.Sample and plot.Parametric.Samples](plotParametricSample.md): iterate over sampled points

  * [plot.Function](plotFunction.md): shape defined by a function y(x) (special case of [plot.Parametric](plotParametric.md))

  * [plot.ParametricLine](plotParametricLine.md): line between two points, deformable by [plot.DataTrans](plotDataTrans.md) (special case of [plot.Parametric](plotParametric.md))

  * [plot.Steps](plotSteps.md): draw a list of values as steps or a skyline (used for histograms)
    * [plot.edges](plotedges.md): creates a uniform list of edges, helpful for building [plot.Steps](plotSteps.md)

#### Data points ####

  * [plot.Scatter](plotScatter.md): draw dots at each point for a list of (x,y) pairs

  * [plot.SymbolScatter](plotSymbolScatter.md): draw SVG symbols at each point
    * [plot.make\_symbol](plotmake_symbol.md): creates a new SVG symbol, helpful for building [plot.SymbolScatter](plotSymbolScatter.md)

  * [plot.ErrorBars](plotErrorBars.md): draw error bars at a list of points (can be asymmetric)

### Data Transformations ###

  * [plot.DataTrans](plotDataTrans.md): a generic transformation of (x,y) to (x',y') (string or function)
  * [plot.DataTrans.Composition](plotDataTransComposition.md): a composition of N transformations
  * [plot.DataTransComplex](plotDataTransComplex.md): a generic transformation of a complex number z to z' (string or function)
  * [plot.DataTransLinear](plotDataTransLinear.md): linear transformation defined by a 2-by-2 matrix
  * [plot.DataTransWindow](plotDataTransWindow.md): linear or logarithmic special case with a convenient representation

### Functions that make axis ticks ###

Tick marks are represented by dictionaries from positions in data coordinates to label strings, and miniticks (shorter ticks without labels) are lists of positions in data coordinates.  It is therefore easy to create ticks by hand, but it is often more convenient to call these functions.

  * [plot.ticks\_regular](plotticks_regular.md): specified number of ticks between specified endpoints
  * [plot.ticks](plotticks.md): optimized ticks for a linear axis
  * [plot.miniticks](plotminiticks.md): optimized miniticks (shorter, no labels) for a linear axis
  * [plot.logticks](plotlogticks.md): optimized ticks for a logarithmic axis
  * [plot.logminiticks](plotlogminiticks.md): optimized miniticks for a logarithmic axis

#### Functions that modify existing ticks ####

  * [plot.tick\_format](plottick_format.md): replace string labels with a given value-to-string function
  * [plot.tick\_unlabel](plottick_unlabel.md): replace string labels with empty strings
  * [plot.tick\_drop](plottick_drop.md): drop a tick mark, allowing for round-off error in the position look-up

#### Functions that turn tick positions into tick labels ####

  * [plot.number\_format](plotnumber_format.md): converts values to strings, including Unicode minus signs and scientific notation

### Navigating and modifying SVG ###

  * [svg.SVG](svgSVG.md): class that represents an SVG element or tree
    * [svg.SVG printing](svgSVGprint.md): printing an SVG tree for human reading or rendering
    * [svg.SVG iteration](svgSVGiteration.md): iterating over an SVG tree
    * [svg.run](svgrun.md): convenience function for executing an external editor
  * [svg.canvas](svgcanvas.md): creates a top-level SVG element, useful for changing the aspect ratio
  * [svg.template](svgtemplate.md): creates a top-level SVG element from a file
  * [svg.load](svgload.md): loads an SVG file into an [svg.SVG](svgSVG.md)

### Data analysis tools ###

#### Simple statistics on lists/iterators ####

  * [tools.mean and tools.wmean](toolsmean.md): mean and weighted mean
  * [tools.rms, tools.stdev, and tools.stdev\_unbiased](toolsrms.md): root-mean-square, standard deviation, and unbiased standard deviation
  * [tools.covariance and tools.correlation](toolscovariance.md): covariance and correlation of two lists

#### Pretty-printing numbers ####

  * [tools.sigfigs and tools.sigfigsstr](toolssigfigs.md): print a number in _N_ significant figures
  * [tools.errpair and tools.errpairstr](toolserrpair.md): print a number and its uncertainty in the same number of significant figures

#### Ntuple-iterators ####

  * [tools.Ntuple](toolsNtuple.md): treat any iterable as a statistical dataset of _N_ named variables
  * [tools.TextNtuple](toolsTextNtuple.md): access a text file of numbers as a [tools.Ntuple](toolsNtuple.md)
  * [root.RootNtuple](rootRootNtuple.md): access a [ROOT](http://root.cern.ch) `TTree` as a [tools.Ntuple](toolsNtuple.md)

#### ROOT-Plothon bridge ####

  * [root.steps](rootsteps.md): draw a [ROOT](http://root.cern.ch) `TH1` histogram with [plot.Steps](plotSteps.md)
  * [root.errorbars](rooterrorbars.md): draw a [ROOT](http://root.cern.ch) `TH1` histogram or profile with [plot.ErrorBars](plotErrorBars.md)

#### Common mathematical functions ####

  * [tools.gauss](toolsgauss.md): a Gaussian bell-curve