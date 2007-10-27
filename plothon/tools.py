# plothon/tools.py is a part of Plothon.
# Copyright (C) 2007 Jim Pivarski <jpivarski@gmail.com>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# 
# Full licence is in the file COPYING and at http://www.gnu.org/copyleft/gpl.html

import math, re, itertools

def mean(xlist):
  "Get the mean of a list."
  s, n = 0., 0.
  for x in xlist:
    s += x
    n += 1.
  return s/n

def rms(xlist):
  "Get the actual root mean square (not standard deviation!) of a list."
  s2, n = 0., 0.
  for x in xlist:
    s2 += x**2
    n += 1.
  return math.sqrt(s2/n)

def stdev(xlist):
  "Get the standard deviation of a list."
  s, s2, n = 0., 0., 0.
  for x in xlist:
    s += x
    s2 += x**2
    n += 1.
  return math.sqrt(s2/n - (s/n)**2)

def stdev_unbiased(xlist):
  """Get the unbiased standard deviation of a list.  (This is the version with a 1/(N-1) in it, rather than 1/N.)"""
  s, s2, n = 0., 0., 0.
  for x in xlist:
    s += x
    s2 += x**2
    n += 1.
  return math.sqrt((s2/n - (s/n)**2) * (n/(n-1.)))

def wmean(xlist):
  "Get the weighted mean and uncertainty in weighted mean of a list of (value, error) pairs.  Values with non-positive errors are ignored (dropped from the list)."
  s, w = 0., 0.
  for x, e in xlist:
    if e > 0.:
      wi = 1./e**2
      s += x*wi
      w += wi
  return s/w, math.sqrt(1./w)

def covariance(xlist, ylist):
  "Get the covariance of two equal-length lists."

  if len(xlist) != len(ylist):
    raise ValueError, "Lists must have the same length."

  xmean = mean(xlist)
  ymean = mean(ylist)
  ssxy = 0.
  for x, y in zip(xlist, ylist):
    ssxy += (x - xmean) * (y - ymean)

  return ssxy

def correlation(xlist, ylist):
  "Get the correlation of two equal-length lists."

  if len(xlist) != len(ylist):
    raise ValueError, "Lists must have the same length."

  xmean = mean(xlist)
  ymean = mean(ylist)
  ssxx, ssyy, ssxy = 0., 0., 0.
  for x, y in zip(xlist, ylist):
    ssxx += (x - xmean)**2
    ssyy += (y - ymean)**2
    ssxy += (x - xmean) * (y - ymean)

  return ssxy/math.sqrt(ssxx * ssyy)

###################################################################################

def roundlevel_nsigfigs(num, n):
  """Get the rounding level for a number needed to represent it in n
significant figures.  You can use it like this:

    num = round(num, tools.roundlevel_nsigfigs(num, n))

More often, though, you would use one of roundsig, roundstr, or roundsig_errpair/roundstr_errpair."""
  if num == 0.: return 1
  return n - int(math.ceil(math.log10(abs(num))))
  
def sigfigs(num, n):
  "Round a number to n significant figures."
  return round(num, roundlevel_nsigfigs(num, n))

def sigfigsstr(num, n):
  """Round a number to n significant figures and return the result as
a string."""
  level = roundlevel_nsigfigs(num, n)
  num = round(num, level)
  format = "%."+str(max(level, 0))+"f"
  return format % num

def errpair(num, err, n=2):
  """Round a number and its uncertainty to n significant figures in the
uncertainty (default is two)."""
  level = roundlevel_nsigfigs(err, n)
  return round(num, level), round(err, level)

def errpairstr(num, err, n=2):
  """Round a number and its uncertainty to n significant figures in the
uncertainty (default is two) and return the result as a string."""
  level = roundlevel_nsigfigs(err, n)
  num = round(num, level)
  err = round(err, level)
  format = "%."+str(max(level, 0))+"f"
  return format % num, format % err

###################################################################################

def gauss(x, area, mean, width):
  """A Gaussian bell-curve."""
  return abs(area)*math.exp(-(mean - x)**2 / 2. / abs(width)**2) / abs(width) / math.sqrt(2*math.pi)

###################################################################################

###################################################################################

class Ntuple:
  def __init__(self, iterator, labels=["x"], *args, **kwds):
    self.iterator = iterator
    self.labels = labels
    self.selection = self.labels
    self.slice = None
    self.function = eval("lambda %s: (%s)" % (", ".join(self.selection), ", ".join(self.selection)))
    self.permutation = range(len(self.labels))

    if len(args) + len(kwds) > 0:
      self(*args, **kwds)

  def __call__(self, function, globals=None, slice=None):
    self.slice = slice
    if self.slice != None:
      if (self.slice.start != None and self.slice.start < 0) or \
         (self.slice.stop != None and self.slice.stop < 0) or \
         (self.slice.step != None and self.slice.step < 1):
        raise ValueError, "Ntuple slices can't be relative to the end of the list because the lengths of iterators is not always known or defined."

    if callable(function):
      self.function = function
      self.selection = function.func_code.co_varnames
    else:
      self.selection = []
      for name in compile(function, "", "eval").co_names:
        if name in self.labels:
          self.selection.append(name)

      if globals == None:
        globals = math.__dict__
      else:
        tmp = math.__dict__
        tmp.update(globals)
        globals = tmp
      self.function = eval("lambda %s: (%s)" % (", ".join(self.selection), function), globals)

    self.permutation = []
    for s in self.selection:
      index = None
      for i, label in enumerate(self.labels):
        if s == label:
          index = i
          break

      if index == None:
        raise ValueError, "selection item \"%s\" is not a label" % s

      self.permutation.append(index)

    return self

  def __iter__(self):
    self.current = iter(self.iterator)
    self.index = 0
    if self.slice != None and self.slice.start != None:
      for i in xrange(self.slice.start):
        self.current.next()
        self.index += 1
    return self

  def prepare_next(self): return self.current.next()
  def prepare_args(self, args): return args

  def next(self):
    if self.slice != None and self.slice.stop != None:
      if self.index >= self.slice.stop: raise StopIteration

    values = self.prepare_next()
    self.index += 1

    try:
      if len(values) == len(self.labels):
        args = [values[i] for i in self.permutation]
      else:
        raise TypeError, "iterator does not return %d items at index %d" % (len(self.labels), self.index)
    except TypeError:
      if len(self.labels) != 1:
        raise TypeError, "iterator does not return %d items at index %d" % (len(self.labels), self.index)
      args = [values] * len(self.permutation)

    output = self.function(*self.prepare_args(args))

    if self.slice != None and self.slice.step != None:
      for i in xrange(self.slice.step - 1):
        self.current.next()
        self.index += 1

    return output

  def __add__(self, other):
    return itertools.chain(iter(self), iter(other))

###################################################################################

class TextNtuple(Ntuple):
  def __init__(self, fileName, delimiter="[ \t\n\r,]+", labels=None, *args, **kwds):
    self.fileName = fileName
    if isinstance(delimiter, (str, unicode)):
      self.delimiter = re.compile(delimiter)
    else:
      self.delimiter = delimiter

    if labels == None:
      line = file(self.fileName).readline()
      if line[-1] == "\n":
        line = line[:-1]
      labels = self.delimiter.split(line)

    Ntuple.__init__(self, None, labels, *args, **kwds)

  def __iter__(self):
    self.iterator = file(self.fileName)
    return Ntuple.__iter__(self)

  def prepare_next(self):
    return self.delimiter.split(self.current.next())

  def prepare_args(self, args):
    output = []
    for v in args:
      try:
        output.append(float(v))
      except ValueError:
        output.append(v)
    return output
    
###################################################################################

###################################################################################

###################################################################################

###################################################################################

###################################################################################

###################################################################################

###################################################################################

# optimal binning:
#
#       // http://www.fmrib.ox.ac.uk/analysis/techrep/tr00mj2/tr00mj2/node24.html
#       // Scott, D. 1979. "On optimal and data-based histograms," Biometrika, 66:605-610.
#       // Izenman, A. J. 1991. "Recent developments in nonparametric density estimation," Journal of the American Statistical Association, 86(413):205-224.
#       int bins;
#       for (int i = 0;  i < int(floor(0.25*double(sample_counter)*(1.-leftloss-rightloss)));  i++) ++iter;
#       for (int i = 0;  i < int(floor(0.25*double(sample_counter)*(1.-leftloss-rightloss)));  i++) ++riter;

#       double IQR = *riter - *iter;
#       if (IQR > 0.) bins = int(nearbyint((high - low) / 2. / IQR * pow(double(sample_counter)*double(self->stop - self->start)/double(self->i - self->start), 1./3.)))
#       else {
#          printf("Warning: IQR is %g, so binning is only nearly optimal.\n", IQR);
#          bins = int(nearbyint(pow(double(sample_counter)*double(self->stop - self->start)/double(self->i - self->start), 1./3.)));
#       }
