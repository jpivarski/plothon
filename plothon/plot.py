# plothon/plot.py is a part of Plothon.
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

import svg, math, cmath, random, re, sys, copy, itertools

epsilon = 1e-5

#####################################################################

class DataTrans:
  def __repr__(self):
    if self.name == None: return "<plothon.plot.DataTrans (id %d)>" % id(self)
    else: return "<plothon.plot.DataTrans %s (id %d)>" % (self.name, id(self))

  def __init__(self, function, name=None, globals=None, minusInfinityX=None, plusInfinityX=None, minusInfinityY=None, plusInfinityY=None):
    if callable(function):
      if function.func_name == "<lambda>": self.name = None
      else: self.name = function.func_name

      if function.func_code.co_argcount == 2:
        self.function = lambda x, y, minusInfinityX, plusInfinityX, minusInfinityY, plusInfinityY: function(x, y)
      elif function.func_code.co_argcount == 6:
        self.function = function
      else:
        raise TypeError, "function must take 2 variables (x,y) or 6 (x,y,minusInfinityX,plusInfinityX,minusInfinityY,plusInfinityY)"

    else:
      self.name = "x,y -> %s" % function

      if globals == None:
        globals = math.__dict__
      else:
        tmp = math.__dict__
        tmp.update(globals)
        globals = tmp
      self.function = eval("lambda x, y, minusInfinityX, plusInfinityX, minusInfinityY, plusInfinityY: (%s)" % function, globals)

    if name != None: self.name = name
    self.minusInfinityX = minusInfinityX
    self.plusInfinityX = plusInfinityX
    self.minusInfinityY = minusInfinityY
    self.plusInfinityY = plusInfinityY

  def __mul__(self, other):
    return DataTransComposition(self, other)

  def __call__(self, x, y):
    return self.function(x, y, self.minusInfinityX, self.plusInfinityX, self.minusInfinityY, self.plusInfinityY)

  def __contains__(self, (x, y)):
    try:
      self(x, y)
      return True
    except:
      return False
    
  def derivative(self, x, y, delta=None):
    if delta == None: delta = epsilon
    X0, Y0 = self(x, y)
    xhatx, xhaty = self(x + delta, y)
    yhatx, yhaty = self(x, y + delta)
    return (1.*(xhatx - X0)/delta, 1.*(xhaty - Y0)/delta), (1.*(yhatx - X0)/delta, 1.*(yhaty - Y0)/delta)

  def normderiv(self, x, y, delta=None):
    if delta == None: delta = epsilon
    X0, Y0 = self(x, y)
    xhatx, xhaty = self(x + delta, y)
    xhatx, xhaty = xhatx - X0, xhaty - Y0
    xhatmag = math.sqrt(xhatx**2 + xhaty**2)
    yhatx, yhaty = self(x, y + delta)
    yhatx, yhaty = yhatx - X0, yhaty - Y0
    yhatmag = math.sqrt(yhatx**2 + yhaty**2)
    if abs(xhatmag) > 0. and abs(yhatmag) > 0.:
      return ((1.*xhatx/xhatmag, 1.*xhaty/xhatmag), (1.*yhatx/yhatmag, 1.*yhaty/yhatmag))
    else:
      return (None, None), (None, None)

#####################################################################

class DataTransLinear(DataTrans):
  def __repr__(self):
    if self.name == None: return "<plothon.plot.DataTransLinear (id %d)>" % id(self)
    else: return "<plothon.plot.DataTransLinear %g (id %d)>" % (self.name, id(self))

  def __init__(self, a, b, c, d, x0=0., y0=0., name=None, minusInfinityX=None, plusInfinityX=None, minusInfinityY=None, plusInfinityY=None):
    self.name = "x,y -> %g x + %g y + %g, %g x + %g y + %g" % (a, c, x0, b, d, y0)
    self.a, self.b, self.c, self.d, self.x0, self.y0 = a, b, c, d, x0, y0
    
    if name != None: self.name = name
    self.minusInfinityX = minusInfinityX
    self.plusInfinityX = plusInfinityX
    self.minusInfinityY = minusInfinityY
    self.plusInfinityY = plusInfinityY

  def function(self, x, y, minusInfinityX, plusInfinityX, minusInfinityY, plusInfinityY):
    return self.a*x + self.c*y + self.x0, self.b*x + self.d*y + self.y0

  def derivative(self, x, y, delta=None):
    return (self.a, self.b), (self.c, self.d)

  def normderiv(self, x, y, delta=None):
    xhatnorm = math.sqrt(self.a**2 + self.b**2)
    yhatnorm = math.sqrt(self.c**2 + self.d**2)
    return (self.a/xhatnorm, self.b/xhatnorm), (self.c/yhatnorm, self.d/yhatnorm)

#####################################################################

class DataTransComplex(DataTrans):
  def __repr__(self):
    if self.name == None: return "<plothon.plot.DataTransComplex (id %d)>" % id(self)
    else: return "<plothon.plot.DataTransComplex %s (id %d)>" % (self.name, id(self))

  def __init__(self, function, name=None, globals=None, minusInfinityX=None, plusInfinityX=None, minusInfinityY=None, plusInfinityY=None):
    if callable(function):
      if function.func_name == "<lambda>": self.name = None
      else: self.name = function.func_name

      if function.func_code.co_argcount == 1:
        self.function = lambda z, minusInfinityX, plusInfinityX, minusInfinityY, plusInfinityY: function(z)
      elif function.func_code.co_argcount == 5:
        self.function = function
      else:
        raise TypeError, "function must take 1 complex variable or 5 variables (z,minusInfinityX,plusInfinityX,minusInfinityY,plusInfinityY)"

    else:
      self.name = "z -> %s" % function

      if globals == None:
        globals = cmath.__dict__
      else:
        tmp = cmath.__dict__
        tmp.update(globals)
        globals = tmp
      self.function = eval("lambda z, minusInfinityX, plusInfinityX, minusInfinityY, plusInfinityY: (%s)" % function, globals)

    if name != None: self.name = name
    self.minusInfinityX = minusInfinityX
    self.plusInfinityX = plusInfinityX
    self.minusInfinityY = minusInfinityY
    self.plusInfinityY = plusInfinityY

  def __call__(self, *args):
    if len(args) == 1 and isinstance(args[0], complex): z = args[0]
    elif len(args) == 2: z = args[0] + args[1]*1j
    else:
      raise TypeError, "Arguments must be z (the complex number) or x, y (the real and imaginary parts)."

    output = self.function(z, self.minusInfinityX, self.plusInfinityX, self.minusInfinityY, self.plusInfinityY)
    if isinstance(output, complex): return output.real, output.imag
    else: return output

#####################################################################

class DataTransComposition(DataTrans):
  def __repr__(self):
    return "<plothon.plot.DataTransComposition %s (id %d)>" % (" -> ".join(map(lambda t: "("+t.name+")", self.tforms)), id(self))

  def __init__(self, *args, **kwds):
    self.tforms = args
    self.flatten()

    self.minusInfinityX = None
    self.plusInfinityX = None
    self.minusInfinityY = None
    self.plusInfinityY = None

    for name, value in kwds.items():
      if name == "minusInfinityX": self.minusInfinityX = value
      elif name == "plusInfinityX": self.plusInfinityX = value
      elif name == "minusInfinityY": self.minusInfinityY = value
      elif name == "plusInfinityY": self.plusInfinityY = value
      else:
        raise TypeError, "\"%s\" is not a keyword argument for DataTransComposition." % name

  def __call__(self, x, y):
    for t in self.tforms:
      t.minusInfinityX = self.minusInfinityX
      t.plusInfinityX = self.plusInfinityX
      t.minusInfinityY = self.minusInfinityY
      t.plusInfinityY = self.plusInfinityY
      x, y = t(x, y)
    return x, y

  def flatten(self):
    try:
      i = 0
      while True:
        while isinstance(self.tforms[i], (list, tuple, DataTransComposition)):
          self.tforms[i:i+1] = list(self.tforms[i])
        i += 1
    except IndexError: pass
    self.tforms = filter(lambda x: x != None, self.tforms)

  def __imul__(self, other):
    self.tforms.append(other)
    self.flatten()
    return self

  def __mul__(self, other):
    return DataTransComposition(self, other)

  def __iter__(self): return iter(self.tforms)

  def __len__(self): return len(self.tforms)

  def __getitem__(self, x): return self.tforms[x]

  def __setitem__(self, x, value): self.tforms[x] = value

  def __delitem__(self, x): del self.tforms[x]

  def append(self, value): self.tforms.append(value)

  def prepend(self, value): self.tforms[0:0] = [value]

#####################################################################




#####################################################################

# hammerAitoff = DataTrans("sqrt(8)*cos(y)*sin(x/2.)/sqrt(1 + cos(y)*cos(x/2.)), sqrt(2)*sin(y)/sqrt(1 + cos(y)*cos(x/2.))", name="Hammer-Aitoff equal-area sphere")

#####################################################################

class DataTransWindow(DataTrans):
  def __repr__(self):
    if self.xlogbase == None: xlogbase = ""
    else: xlogbase = " xlog%g" % self.xlogbase

    if self.ylogbase == None: ylogbase = ""
    else: ylogbase = " ylog%g" % self.ylogbase

    return "<plothon.plot.DataTransWindow (%g, %g) (%g, %g) -> (%g, %g) (%g, %g)%s%s>" \
           % (self.xmin, self.ymin, self.xmax, self.ymax, self.x, self.y + self.height, self.x + self.width, self.y, xlogbase, ylogbase)

  def __eq__(self, other):
    return isinstance(other, DataTransWindow) and \
           (self.x == other.x) and (self.y == other.y) and \
           (self.width == other.width) and (self.height == other.height) and \
           (self.xmin == other.xmin) and (self.xmax == other.xmax) and \
           (self.ymin == other.ymin) and (self.ymax == other.ymax) and \
           (self.xlogbase == other.xlogbase) and (self.ylogbase == other.ylogbase) and \
           (self.minusInfinityX == other.minusInfinityX) and (self.plusInfinityX == other.plusInfinityX) and \
           (self.minusInfinityY == other.minusInfinityY) and (self.plusInfinityY == other.plusInfinityY)

  def __ne__(self, other): return not (self == other)

  def __init__(self, x, y, width, height, xmin, ymin, xmax, ymax, xlogbase=None, ylogbase=None, \
               minusInfinityX=None, plusInfinityX=None, minusInfinityY=None, plusInfinityY=None):
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.xmin = xmin
    self.xmax = xmax
    self.ymin = ymin
    self.ymax = ymax
    self.xlogbase = xlogbase
    self.ylogbase = ylogbase
    self.minusInfinityX = minusInfinityX
    self.plusInfinityX = plusInfinityX
    self.minusInfinityY = minusInfinityY
    self.plusInfinityY = plusInfinityY

  def function(self, x, y, minusInfinityX, plusInfinityX, minusInfinityY, plusInfinityY):
    ox1 = self.x
    oy1 = self.y
    ox2 = self.x + self.width
    oy2 = self.y + self.height
    ix1 = self.xmin
    iy1 = self.ymin
    ix2 = self.xmax
    iy2 = self.ymax
    
    xindomain, yindomain = True, True

    if self.xlogbase != None:
      if x <= 0.: xindomain = False
      else: x = math.log(x, self.xlogbase)

      if ix1 <= 0.: raise ValueError, "xmin cannot be %g if xlogbase is %g." % (ix1, self.xlogbase)
      else: ix1 = math.log(ix1, self.xlogbase)

      if ix2 <= 0.: raise ValueError, "xmax cannot be %g if xlogbase is %g." % (ix2, self.xlogbase)
      else: ix2 = math.log(ix2, self.xlogbase)

    if self.ylogbase != None:
      if y <= 0.: yindomain = False
      else: y = math.log(y, self.ylogbase)

      if iy1 <= 0.: raise ValueError, "ymin cannot be %g if ylogbase is %g." % (iy1, self.ylogbase)
      else: iy1 = math.log(iy1, self.ylogbase)

      if iy2 <= 0.: raise ValueError, "ymax cannot be %g if ylogbase is %g." % (iy2, self.ylogbase)
      else: iy2 = math.log(iy2, self.ylogbase)

    if xindomain: x = ox1 + 1.*(x - ix1)/(ix2 - ix1) * (ox2 - ox1)
    else: x = minusInfinityX

    if yindomain: y = oy1 + 1.*(iy2 - y)/(iy2 - iy1) * (oy2 - oy1)
    else: y = minusInfinityY

    return x, y

  def normderiv(self, x, y, delta=None):
    # DataTransWindows are always rectilinear!
    return ((1., 0.), (0., 1.))

#####################################################################

class Plottable:
  def __repr__(self): return "<plothon.plot.Plottable (id %d)>" % id(self)

  def SVG(self, datatrans=None, range_filter=None):
    self.inner_xmin, self.inner_ymin, self.inner_xmax, self.inner_ymax = None, None, None, None
    self.outer_xmin, self.outer_ymin, self.outer_xmax, self.outer_ymax = None, None, None, None
    return svg.SVG("g")

  def inner_ranges(self, range_filter=None):
    self.inner_xmin, self.inner_ymin, self.inner_xmax, self.inner_ymax = None, None, None, None

  def increment_inner_ranges(self, x, y):
    if x != None:
      if self.inner_xmin == None or x < self.inner_xmin: self.inner_xmin = x
      if self.inner_xmax == None or x > self.inner_xmax: self.inner_xmax = x
    if y != None:
      if self.inner_ymin == None or y < self.inner_ymin: self.inner_ymin = y
      if self.inner_ymax == None or y > self.inner_ymax: self.inner_ymax = y

  def increment_outer_ranges(self, X, Y):
    if X != None:
      if self.outer_xmin == None or X < self.outer_xmin: self.outer_xmin = X
      if self.outer_xmax == None or X > self.outer_xmax: self.outer_xmax = X
    if Y != None:
      if self.outer_ymin == None or Y < self.outer_ymin: self.outer_ymin = Y
      if self.outer_ymax == None or Y > self.outer_ymax: self.outer_ymax = Y

  def __add__(self, other):
    return Plottables(self, other)

#####################################################################

class Plottables:
  def __repr__(self): return "<plothon.plot.Plottables (%d Plottable objects)>" % len(self)

  def __init__(self, *args):
    self.data = list(args)
    self.flatten()
    
  def flatten(self):
    try:
      i = 0
      while True:
        while isinstance(self.data[i], (list, tuple, Plottables)):
          self.data[i:i+1] = list(self.data[i])
        i += 1
    except IndexError: pass

  def __iadd__(self, other):
    self.data.append(other)
    self.flatten()
    return self

  def __add__(self, other):
    return Plottables(self, other)

  def __iter__(self): return iter(self.data)

  def __len__(self): return len(self.data)

  def __getitem__(self, x): return self.data[x]

  def __setitem__(self, x, value): self.data[x] = value

  def __delitem__(self, x): del self.data[x]

  def append(self, value): self.data.append(value)

  def prepend(self, value): self.data[0:0] = [value]

#####################################################################

class PlottablePath(Plottable):
  defaults = {}

  def __repr__(self): return "<plothon.plot.PlottablePath (%d nodes) %s>" % (len(self.d), self.attributes)

  def __init__(self, d, **attributes):
    if isinstance(d, (str, unicode)):
      self.d = self.parse(d)
    else:
      self.d = d

    self.attributes = dict(self.defaults)
    self.attributes.update(attributes)

  def parse_whitespace(self, index, pathdata):
    while index < len(pathdata) and pathdata[index] in (" ", "\t", "\r", "\n"): index += 1
    return index, pathdata

  def parse_command(self, index, pathdata):
    index, pathdata = self.parse_whitespace(index, pathdata)

    if index >= len(pathdata): return None, index, pathdata
    command = pathdata[index]
    if "A" <= command <= "Z" or "a" <= command <= "z":
      index += 1
      return command, index, pathdata
    else: 
      return None, index, pathdata

  def parse_number(self, index, pathdata):
    index, pathdata = self.parse_whitespace(index, pathdata)

    if index >= len(pathdata): return None, index, pathdata
    first_digit = pathdata[index]

    if "0" <= first_digit <= "9" or first_digit in ("-", "+", "."):
      start = index
      while index < len(pathdata) and ("0" <= pathdata[index] <= "9" or pathdata[index] in ("-", "+", ".", "e", "E")):
        index += 1
      end = index

      index = end
      return float(pathdata[start:end]), index, pathdata
    else: 
      return None, index, pathdata

  def parse_boolean(self, index, pathdata):
    index, pathdata = self.parse_whitespace(index, pathdata)

    if index >= len(pathdata): return None, index, pathdata
    first_digit = pathdata[index]

    if first_digit in ("0", "1"):
      index += 1
      return int(first_digit), index, pathdata
    else:
      return None, index, pathdata

  def parse(self, pathdata):
    output = []
    index = 0
    while True:
      command, index, pathdata = self.parse_command(index, pathdata)
      index, pathdata = self.parse_whitespace(index, pathdata)

      if command == None and index == len(pathdata): break  # this is the normal way out of the loop
      if command in ("Z", "z"):
        output.append((command,))

      ######################
      elif command in ("H", "h", "V", "v"):
        errstring = "Path command \"%s\" requires a number at index %d." % (command, index)
        num1, index, pathdata = self.parse_number(index, pathdata)
        if num1 == None: raise ValueError, errstring

        while num1 != None:
          output.append((command, num1))
          num1, index, pathdata = self.parse_number(index, pathdata)

      ######################
      elif command in ("M", "m", "L", "l", "T", "t"):
        errstring = "Path command \"%s\" requires an x,y pair at index %d." % (command, index)
        num1, index, pathdata = self.parse_number(index, pathdata)
        num2, index, pathdata = self.parse_number(index, pathdata)

        if num1 == None: raise ValueError, errstring

        while num1 != None:
          if num2 == None: raise ValueError, errstring
          output.append((command, num1, num2, False))

          num1, index, pathdata = self.parse_number(index, pathdata)
          num2, index, pathdata = self.parse_number(index, pathdata)

      ######################
      elif command in ("S", "s", "Q", "q"):
        errstring = "Path command \"%s\" requires a cx,cy,x,y quadruplet at index %d." % (command, index)
        num1, index, pathdata = self.parse_number(index, pathdata)
        num2, index, pathdata = self.parse_number(index, pathdata)
        num3, index, pathdata = self.parse_number(index, pathdata)
        num4, index, pathdata = self.parse_number(index, pathdata)

        if num1 == None: raise ValueError, errstring

        while num1 != None:
          if num2 == None or num3 == None or num4 == None: raise ValueError, errstring
          output.append((command, num1, num2, False, num3, num4, False))

          num1, index, pathdata = self.parse_number(index, pathdata)
          num2, index, pathdata = self.parse_number(index, pathdata)
          num3, index, pathdata = self.parse_number(index, pathdata)
          num4, index, pathdata = self.parse_number(index, pathdata)
          
      ######################
      elif command in ("C", "c"):
        errstring = "Path command \"%s\" requires a c1x,c1y,c2x,c2y,x,y sextuplet at index %d." % (command, index)
        num1, index, pathdata = self.parse_number(index, pathdata)
        num2, index, pathdata = self.parse_number(index, pathdata)
        num3, index, pathdata = self.parse_number(index, pathdata)
        num4, index, pathdata = self.parse_number(index, pathdata)
        num5, index, pathdata = self.parse_number(index, pathdata)
        num6, index, pathdata = self.parse_number(index, pathdata)
        
        if num1 == None: raise ValueError, errstring

        while num1 != None:
          if num2 == None or num3 == None or num4 == None or num5 == None or num6 == None: raise ValueError, errstring

          output.append((command, num1, num2, False, num3, num4, False, num5, num6, False))

          num1, index, pathdata = self.parse_number(index, pathdata)
          num2, index, pathdata = self.parse_number(index, pathdata)
          num3, index, pathdata = self.parse_number(index, pathdata)
          num4, index, pathdata = self.parse_number(index, pathdata)
          num5, index, pathdata = self.parse_number(index, pathdata)
          num6, index, pathdata = self.parse_number(index, pathdata)

      ######################
      elif command in ("A", "a"):
        errstring = "Path command \"%s\" requires a rx,ry,angle,large-arc-flag,sweep-flag,x,y septuplet at index %d." % (command, index)
        num1, index, pathdata = self.parse_number(index, pathdata)
        num2, index, pathdata = self.parse_number(index, pathdata)
        num3, index, pathdata = self.parse_number(index, pathdata)
        num4, index, pathdata = self.parse_boolean(index, pathdata)
        num5, index, pathdata = self.parse_boolean(index, pathdata)
        num6, index, pathdata = self.parse_number(index, pathdata)
        num7, index, pathdata = self.parse_number(index, pathdata)

        if num1 == None: raise ValueError, errstring

        while num1 != None:
          if num2 == None or num3 == None or num4 == None or num5 == None or num6 == None or num7 == None: raise ValueError, errstring

          output.append((command, num1, num2, False, num3, num4, num5, num6, num7, False))

          num1, index, pathdata = self.parse_number(index, pathdata)
          num2, index, pathdata = self.parse_number(index, pathdata)
          num3, index, pathdata = self.parse_number(index, pathdata)
          num4, index, pathdata = self.parse_boolean(index, pathdata)
          num5, index, pathdata = self.parse_boolean(index, pathdata)
          num6, index, pathdata = self.parse_number(index, pathdata)
          num7, index, pathdata = self.parse_number(index, pathdata)

    return output

  def inner_ranges(self, range_filter=None):
    self.SVG(None, range_filter)

  def SVG(self, datatrans=None, range_filter=None):
    Plottable.SVG(self, datatrans, range_filter)

    x, y, X, Y = None, None, None, None
    output = []
    for datum in self.d:
      try:
        iter(datum)
      except TypeError:
        raise TypeError, "pathdata elements must be iterables."

      command = datum[0]

      ######################
      if command in ("Z", "z"):
        x, y = None, None
        output.append("Z")

      ######################
      elif command in ("H", "h", "V", "v"):
        command, num1 = datum

        if command == "H" or (command == "h" and x == None): x = num1
        elif command == "h": x += num1
        elif command == "V" or (command == "v" and y == None): y = num1
        elif command == "v": y += num1

        if datatrans == None: X, Y = x, y
        else: X, Y = datatrans(x, y)
        if range_filter == None or range_filter(x, y):
          self.increment_inner_ranges(x, y)
          self.increment_outer_ranges(X, Y)

        output.append("L%g %g" % (X, Y))
        
      ######################
      elif command in ("M", "m", "L", "l", "T", "t"):
        command, num1, num2, isglobal12 = datum

        if datatrans == None or isglobal12:
          if command < "a" or X == None or Y == None:
            X, Y = num1, num2
          else:
            X += num1
            Y += num2
          x, y = X, Y

        else:
          if command < "a" or x == None or y == None:
            x, y = num1, num2
          else:
            x += num1
            y += num2
          X, Y = datatrans(x, y)

        if command not in ("M", "m") and (range_filter == None or range_filter(x, y)):
          self.increment_inner_ranges(x, y)
          self.increment_outer_ranges(X, Y)
        
        COMMAND = command.capitalize()
        output.append("%s%g %g" % (COMMAND, X, Y))

      ######################
      elif command in ("S", "s", "Q", "q"):
        command, num1, num2, isglobal12, num3, num4, isglobal34 = datum

        if datatrans == None or isglobal12:
          if command < "a" or X == None or Y == None:
            CX, CY = num1, num2
          else:
            CX = X + num1
            CY = Y + num2

        else:
          if command < "a" or x == None or y == None:
            cx, cy = num1, num2
          else:
            cx = x + num1
            cy = y + num2
          CX, CY = datatrans(cx, cy)

        if datatrans == None or isglobal34:
          if command < "a" or X == None or Y == None:
            X, Y = num3, num4
          else:
            X += num3
            Y += num4
          x, y = X, Y

        else:
          if command < "a" or x == None or y == None:
            x, y = num3, num4
          else:
            x += num3
            y += num4
          X, Y = datatrans(x, y)

        if range_filter == None or range_filter(x, y):
          self.increment_inner_ranges(x, y)
          self.increment_outer_ranges(X, Y)

        COMMAND = command.capitalize()
        output.append("%s%g %g %g %g" % (COMMAND, CX, CY, X, Y))

      ######################
      elif command in ("C", "c"):
        command, num1, num2, isglobal12, num3, num4, isglobal34, num5, num6, isglobal56 = datum

        if datatrans == None or isglobal12:
          if command < "a" or X == None or Y == None:
            C1X, C1Y = num1, num2
          else:
            C1X = X + num1
            C1Y = Y + num2

        else:
          if command < "a" or x == None or y == None:
            c1x, c1y = num1, num2
          else:
            c1x = x + num1
            c1y = y + num2
          C1X, C1Y = datatrans(c1x, c1y)

        if datatrans == None or isglobal34:
          if command < "a" or X == None or Y == None:
            C2X, C2Y = num3, num4
          else:
            C2X = X + num3
            C2Y = Y + num4

        else:
          if command < "a" or x == None or y == None:
            c2x, c2y = num3, num4
          else:
            c2x = x + num3
            c2y = y + num4
          C2X, C2Y = datatrans(c2x, c2y)

        if datatrans == None or isglobal56:
          if command < "a" or X == None or Y == None:
            X, Y = num5, num6
          else:
            X += num5
            Y += num6
          x, y = X, Y

        else:
          if command < "a" or x == None or y == None:
            x, y = num5, num6
          else:
            x += num5
            y += num6
          X, Y = datatrans(x, y)

        if range_filter == None or range_filter(x, y):
          self.increment_inner_ranges(x, y)
          self.increment_outer_ranges(X, Y)

        COMMAND = command.capitalize()
        output.append("%s%g %g %g %g %g %g" % (COMMAND, C1X, C1Y, C2X, C2Y, X, Y))

      ######################
      elif command in ("A", "a"):
        command, num1, num2, isglobal12, angle, large_arc_flag, sweep_flag, num3, num4, isglobal34 = datum

        oldx, oldy = x, y
        OLDX, OLDY = X, Y

        if datatrans == None or isglobal34:
          if command < "a" or X == None or Y == None:
            X, Y = num3, num4
          else:
            X += num3
            Y += num4
          x, y = X, Y

        else:
          if command < "a" or x == None or y == None:
            x, y = num3, num4
          else:
            x += num3
            y += num4
          X, Y = datatrans(x, y)
        
        if x != None and y != None:
          centerx, centery = (x + oldx)/2., (y + oldy)/2.
        CENTERX, CENTERY = (X + OLDX)/2., (Y + OLDY)/2.

        if datatrans == None or isglobal12:
          RX = CENTERX + num1
          RY = CENTERY + num2

        else:
          rx = centerx + num1
          ry = centery + num2
          RX, RY = datatrans(rx, ry)

        if range_filter == None or range_filter(x, y):
          self.increment_inner_ranges(x, y)
          self.increment_outer_ranges(X, Y)

        COMMAND = command.capitalize()
        output.append("%s%g %g %g %d %d %g %g" % (COMMAND, RX - CENTERX, RY - CENTERY, angle, large_arc_flag, sweep_flag, X, Y))

      elif command in (",", "."):
        command, num1, num2, isglobal12, angle, num3, num4, isglobal34 = datum
        if datatrans == None or isglobal34:
          if command == "." or X == None or Y == None:
            X, Y = num3, num4
          else:
            X += num3
            Y += num4
            x, y = None, None

        else:
          if command == "." or x == None or y == None:
            x, y = num3, num4
          else:
            x += num3
            y += num4
          X, Y = datatrans(x, y)

        if datatrans == None or isglobal12:
          RX = X + num1
          RY = Y + num2

        else:
          rx = x + num1
          ry = y + num2
          RX, RY = datatrans(rx, ry)

        RX, RY = RX - X, RY - Y

        if range_filter == None or range_filter(x, y):
          self.increment_inner_ranges(x, y)
          self.increment_outer_ranges(X, Y)

        X1, Y1 = X + RX * math.cos(angle*math.pi/180.), Y + RX * math.sin(angle*math.pi/180.)
        X2, Y2 = X + RY * math.sin(angle*math.pi/180.), Y - RY * math.cos(angle*math.pi/180.)
        X3, Y3 = X - RX * math.cos(angle*math.pi/180.), Y - RX * math.sin(angle*math.pi/180.)
        X4, Y4 = X - RY * math.sin(angle*math.pi/180.), Y + RY * math.cos(angle*math.pi/180.)

#         output.append("M %g %g L %g %g" % (X1, Y1, X3, Y3)) # for debugging
#         output.append("M %g %g L %g %g" % (X2, Y2, X4, Y4)) # for debugging

        output.append("M%g %gA%g %g %g 0 0 %g %gA%g %g %g 0 0 %g %gA%g %g %g 0 0 %g %gA%g %g %g 0 0 %g %g" \
                      % (X1, Y1, RX, RY, angle, X2, Y2, RX, RY, angle, X3, Y3, RX, RY, angle, X4, Y4, RX, RY, angle, X1, Y1))

    return svg.SVG("path", d="".join(output), **self.attributes)

#####################################################################

class Parametric(Plottable):
  defaults = {"stroke-width": "0.5pt"}

  def __repr__(self):
    if self.name == None: return "<plothon.plot.Parametric [%g,%g] %s>" % (self.low, self.high, self.attributes)
    else: return "<plothon.plot.Parametric %s [%g,%g] %s>" % (self.name, self.low, self.high, self.attributes)
  
  def __init__(self, function, low, high, globals=None, random_sampling=True, recursion_limit=15, linearity_limit=0.1, discontinuity_limit=5., **attributes):
    self.low, self.high = low, high

    self.attributes = dict(self.defaults)
    self.attributes.update(attributes)

    self.random_sampling = random_sampling
    self.recursion_limit = recursion_limit
    self.linearity_limit = linearity_limit
    self.discontinuity_limit = discontinuity_limit

    if callable(function):
      if function.func_name == "<lambda>": self.name = None
      else: self.name = function.func_name

      if function.func_code.co_argcount == 1:
        self.function = function
      else:
        raise TypeError, "function must take only 1 variable"

    else:
      self.name = "t -> %s" % function

      if globals == None:
        globals = math.__dict__
      else:
        tmp = math.__dict__
        tmp.update(globals)
        globals = tmp
      self.function = eval("lambda t: (%s)" % function, globals)

  def __call__(self, t): return self.function(t)

  def __contains__(self, t):
    try:
      self(t)
      return True
    except:
      return False

  class Sample:
    def __repr__(self):
      t, x, y, X, Y = self.t, self.x, self.y, self.X, self.Y
      if t != None: t = "%g" % t
      if x != None: x = "%g" % x
      if y != None: y = "%g" % y
      if X != None: X = "%g" % X
      if Y != None: Y = "%g" % Y
      return "<plothon.plot.Parametric.Sample t=%s x=%s y=%s X=%s Y=%s>" % (t, x, y, X, Y)

    def __init__(self, t): self.t = t

    def link(self, left, right): self.left, self.right = left, right

    def evaluate(self, function, datatrans):
      try:
        self.x, self.y = function(self.t)
      except Exception, err:
        if err == "unpack non-sequence":
          raise TypeError, "function must return exactly two values"
        else:
          self.x, self.y = None, None

      if self.x == None or self.y == None:
        self.X, self.Y = None, None

      else:
        if datatrans == None: self.X, self.Y = self.x, self.y
        else: self.X, self.Y = datatrans(self.x, self.y)

  class Samples:
    def __repr__(self): return "<plothon.plot.Parametric.Samples (%d samples)>" % len(self)

    def __init__(self, left, right): self.left, self.right = left, right

    def __len__(self):
      count = 0
      current = self.left
      while current != None:
        count += 1
        current = current.right
      return count

    def __iter__(self):
      self.current = self.left
      return self

    def next(self):
      current = self.current
      if current == None: raise StopIteration
      self.current = self.current.right
      return current

  def sample(self, datatrans=None):
    oldrecursionlimit = sys.getrecursionlimit()
    sys.setrecursionlimit(self.recursion_limit + 100)
    try:
      # the best way to keep all the information while sampling is to make a linked list
      if not (self.low < self.high): raise ValueError, "low must be less than high"
      low, high = self.Sample(self.low), self.Sample(self.high)
      low.link(None, high)
      high.link(low, None)

      low.evaluate(self.function, datatrans)
      high.evaluate(self.function, datatrans)

      # adaptive sampling between the low and high points
      self.subsample(low, high, 0, datatrans)
      self.last_samples = self.Samples(low, high)
    finally:
      sys.setrecursionlimit(oldrecursionlimit)

  def subsample(self, left, right, depth, datatrans=None):
    if self.random_sampling:
      mid = self.Sample(left.t + random.uniform(0.3, 0.7) * (right.t - left.t))
    else:
      mid = self.Sample(left.t + 0.5 * (right.t - left.t))

    left.right = mid
    right.left = mid
    mid.link(left, right)
    mid.evaluate(self.function, datatrans)

    if left.X == None or left.Y == None or right.X == None or right.Y == None:
      if depth < self.recursion_limit:
        self.subsample(left, mid, depth+1, datatrans)
        self.subsample(mid, right, depth+1, datatrans)
      return
      
    if mid.X != None and mid.Y != None:
      # calculate the distance of closest approach of mid to the line between left and right
      numer = left.X*(right.Y - mid.Y) + mid.X*(left.Y - right.Y) + right.X*(mid.Y - left.Y)
      denom = math.sqrt((left.X - right.X)**2 + (left.Y - right.Y)**2)

      # if we haven't sampled enough or left fails to be close enough to right, or mid fails to be linear enough...
      if depth < 3 or (denom == 0 and left.t != right.t) or denom > self.discontinuity_limit**2 or (denom != 0. and abs(numer/denom) > self.linearity_limit):

        # and we haven't sampled too many points
        if depth < self.recursion_limit:
          self.subsample(left, mid, depth+1, datatrans)
          self.subsample(mid, right, depth+1, datatrans)

        else:
          # We've sampled many points and yet it's still not a small linear gap.
          # Break the line: it's a discontinuity
          mid.y = mid.Y = None

  def inner_ranges(self, range_filter=None):
    self.SVG(None, range_filter)

  def SVG(self, datatrans=None, range_filter=None):
    self.sample(datatrans)

    Plottable.SVG(self, datatrans, range_filter)
    for s in self.last_samples:
      if range_filter == None or range_filter(s.x, s.y):
        self.increment_inner_ranges(s.x, s.y)
        self.increment_outer_ranges(s.X, s.Y)

    output = []
    for s in self.last_samples:
      if s.X != None and s.Y != None:
        if s.left == None or s.left.X == None or s.left.Y == None:
          output.append("M%g %g" % (s.X, s.Y))
        else:
          output.append("L%g %g" % (s.X, s.Y))
#          output.append("l 1 1 m -2 0 l 1 -1 l -1 -1 m 2 0 l -1 1") # for debugging

    return svg.SVG("path", d="".join(output), **self.attributes)

  def PlottablePath(self, datatrans=None, local=True):
    self.sample(datatrans)

    output = []
    for s in self.last_samples:
      if s.X != None and s.Y != None:
        if s.left == None or s.left.X == None or s.left.Y == None:
          command = "M"
        else:
          command = "L"

        if local: output.append((command, s.x, s.y, False))
        else: output.append((command, s.X, s.Y, True))

    return PlottablePath(output, **self.attributes)

  def last_points(self):
    if "last_samples" not in self.__dict__ or self.last_samples == None: return []
    else:
      output = []
      for s in self.last_samples:
        if s.x != None and s.y != None and s.X != None and s.y != None:
          output.append((s.x, s.y))
      return output

#####################################################################

class Function(Parametric):
  defaults = {"stroke-width": "0.5pt"}

  def __repr__(self):
    if self.name == None: return "<plothon.plot.Function [%g,%g] %s>" % (self.low, self.high, self.attributes)
    else: return "<plothon.plot.Function %s [%g,%g] %s>" % (self.name, self.low, self.high, self.attributes)

  def __init__(self, function, low, high, globals=None, random_sampling=True, recursion_limit=15, linearity_limit=0.1, discontinuity_limit=5., **attributes):
    self.low, self.high = low, high

    self.attributes = dict(self.defaults)
    self.attributes.update(attributes)

    self.random_sampling = random_sampling
    self.recursion_limit = recursion_limit
    self.linearity_limit = linearity_limit
    self.discontinuity_limit = discontinuity_limit

    if callable(function):
      if function.func_name == "<lambda>": self.name = None
      else: self.name = function.func_name

      if function.func_code.co_argcount == 1:
        self.function = lambda t: (t, function(t))
      else:
        raise TypeError, "function must take only 1 variable"

    else:
      self.name = "x -> %s" % function

      if globals == None:
        globals = math.__dict__
      else:
        tmp = math.__dict__
        tmp.update(globals)
        globals = tmp
      self.function = eval("lambda x: (x, %s)" % function, globals)

  def __call__(self, x): return self.function(x)[1]

#####################################################################

class ParametricLine(Parametric):
  defaults = {"stroke-width": "0.5pt"}

  def __repr__(self):
    return "<plothon.plot.ParametricLine (%g %g) to (%g %g)>" % (self.x1, self.y1, self.x2, self.y2)

  def __init__(self, x1, y1, x2, y2, random_sampling=True, recursion_limit=10, linearity_limit=0.1, discontinuity_limit=5., **attributes):
    self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
    self.low, self.high = 0., 1.

    self.attributes = dict(self.defaults)
    self.attributes.update(attributes)

    self.random_sampling = random_sampling
    self.recursion_limit = recursion_limit
    self.linearity_limit = linearity_limit
    self.discontinuity_limit = discontinuity_limit

  def make_function(self):
    self.function = lambda t: (self.x1 + t*(self.x2 - self.x1), self.y1 + t*(self.y2 - self.y1))

  def __call__(self, t):
    self.make_function()
    return self.function(t)

  def PlottablePath(self, datatrans=None, local=True):
    self.make_function()
    return Parametric.PlottablePath(self, datatrans, local)

  def SVG(self, datatrans=None, range_filter=None):
    self.make_function()
    return Parametric.SVG(self, datatrans, range_filter)

#####################################################################

class PlottablePoints(Plottable):
  def __repr__(self):
    return "<plothon.plot.PlottablePoints (%d points)>" % len(self)

  def __getitem__(self, i):
    if isinstance(i, slice):
      return self.__class__(self.points[i], **self.attributes)
    else:
      return self.points[i]

  def __setitem__(self, i, value): self.points[i] = value

  def __delitem__(self, i): del self.points[i]

  def __len__(self): return len(self.points)

  def __iter__(self): return iter(self.points)

  def __contains__(self, i): return i in self.points

  def prepend(self, value): self.insert(0, value)

  def append(self, value): self.points.append(value)
  
  def extend(self, value): self.points.extend(value)

  def count(self, value): return self.points.count(i)

  def index(self, *args): return self.points.index(*args)

  def insert(self, i, value): self.points.insert(i, value)

  def remove(self, value): return self.points.remove(value)

  def pop(self, i): return self.points.pop(i)

  def reverse(self): return self.points.reverse()

  def sort(self, compare): return self.points.sort(compare)

  def inner_ranges(self, range_filter=None):
    Plottable.inner_ranges(self, range_filter)
    for p in self.points:
      if range_filter == None or range_filter(p[0], p[1]):
        self.increment_inner_ranges(p[0], p[1])

#####################################################################

class Curve(PlottablePoints):
  defaults = {"stroke-width": "0.5pt"}

  def __repr__(self):
    return "<plothon.plot.Curve (%d nodes) mode=%s %s>" % (len(self), self.mode, self.attributes)

  def __init__(self, points, mode="lines", loop=False, **attributes):
    self.points = points
    self.mode = mode
    self.loop = loop

    self.attributes = dict(self.defaults)
    self.attributes.update(attributes)

  def SVG(self, datatrans=None, range_filter=None):
    Plottable.SVG(self, datatrans, range_filter)

    if self.mode == "lines": mode = "L"
    elif self.mode == "bezier": mode = "B"
    elif self.mode == "velocity": mode = "V"
    elif self.mode == "foreback": mode = "F"
    elif self.mode == "smooth":
      mode = "S"

      vx, vy = [0.]*len(self.points), [0.]*len(self.points)
      for i in xrange(len(self.points)):
        inext = (i+1) % len(self.points)
        iprev = (i-1) % len(self.points)

        vx[i] = (self.points[inext][0] - self.points[iprev][0])/2.
        vy[i] = (self.points[inext][1] - self.points[iprev][1])/2.
        if not self.loop and (i == 0 or i == len(self.points)-1):
          vx[i], vy[i] = 0., 0.

    else:
      raise ValueError, "mode must be one of (\"lines\", \"bezier\", \"velocity\", \"foreback\", \"smooth\")"

    d = []
    indexes = range(len(self.points))
    if self.loop and len(self.points) > 0: indexes.append(0)

    for i in indexes:
      inext = (i+1) % len(self.points)
      iprev = (i-1) % len(self.points)

      x, y = self.points[i][0], self.points[i][1]

      if datatrans == None: X, Y = x, y
      else: X, Y = datatrans(x, y)

      if range_filter == None or range_filter(x, y):
        self.increment_inner_ranges(x, y)
        self.increment_outer_ranges(X, Y)

      if d == []:
        d.append("M%g %g" % (X, Y))

      elif mode == "L":
        d.append("L%g %g" % (X, Y))

      elif mode == "B":
        c1x, c1y = self.points[i][2], self.points[i][3]
        if datatrans == None: C1X, C1Y = c1x, c1y
        else: C1X, C1Y = datatrans(c1x, c1y)

        c2x, c2y = self.points[i][4], self.points[i][5]
        if datatrans == None: C2X, C2Y = c2x, c2y
        else: C2X, C2Y = datatrans(c2x, c2y)

        d.append("C%g %g %g %g %g %g" % (X, Y, C1X, C1Y, C2X, C2Y))

      elif mode == "V":
        c1x, c1y = self.points[iprev][2]/3. + self.points[iprev][0], self.points[iprev][3]/3. + self.points[iprev][1]
        c2x, c2y = self.points[i][2]/-3. + x, self.points[i][3]/-3. + y

        if datatrans == None: C1X, C1Y = c1x, c1y
        else: C1X, C1Y = datatrans(c1x, c1y)
        if datatrans == None: C2X, C2Y = c2x, c2y
        else: C2X, C2Y = datatrans(c2x, c2y)

        d.append("C%g %g %g %g %g %g" % (C1X, C1Y, C2X, C2Y, X, Y))

      elif mode == "F":
        c1x, c1y = self.points[iprev][4]/3. + self.points[iprev][0], self.points[iprev][5]/3. + self.points[iprev][1]
        c2x, c2y = self.points[i][2]/-3. + x, self.points[i][3]/-3. + y

        if datatrans == None: C1X, C1Y = c1x, c1y
        else: C1X, C1Y = datatrans(c1x, c1y)
        if datatrans == None: C2X, C2Y = c2x, c2y
        else: C2X, C2Y = datatrans(c2x, c2y)

        d.append("C%g %g %g %g %g %g" % (C1X, C1Y, C2X, C2Y, X, Y))

      elif mode == "S":
        c1x, c1y = vx[iprev]/3. + self.points[iprev][0], vy[iprev]/3. + self.points[iprev][1]
        c2x, c2y = vx[i]/-3. + x, vy[i]/-3. + y

        if datatrans == None: C1X, C1Y = c1x, c1y
        else: C1X, C1Y = datatrans(c1x, c1y)
        if datatrans == None: C2X, C2Y = c2x, c2y
        else: C2X, C2Y = datatrans(c2x, c2y)

        d.append("C%g %g %g %g %g %g" % (C1X, C1Y, C2X, C2Y, X, Y))

    if self.loop and len(self.points) > 0: d.append("Z")

    return svg.SVG("path", d="".join(d), **self.attributes)

#####################################################################

class Scatter(PlottablePoints):
  defaults = {"stroke": "none", "fill": "black"}

  def __repr__(self):
    return "<plothon.plot.Scatter (%d points) %s>" % (len(self), self.attributes)
  
  def __init__(self, points, radius=1., **attributes):
    self.points = points
    self.radius = radius

    self.attributes = dict(self.defaults)
    self.attributes.update(attributes)

  def SVG(self, datatrans=None, range_filter=None):
    Plottable.SVG(self, datatrans, range_filter)

    d = []
    for p in self.points:
      x, y = p[0], p[1]

      if datatrans == None: X, Y = x, y
      else: X, Y = datatrans(x, y)

      if range_filter == None or range_filter(x, y):
        self.increment_inner_ranges(x, y)
        self.increment_outer_ranges(X, Y)
      
      d.append((".", self.radius, self.radius, True, 0, X, Y, True))

    return PlottablePath(d=d, **self.attributes).SVG()
    
#####################################################################

class ErrorBars(PlottablePoints):
  defaults = {}

  def __repr__(self):
    return "<plothon.plot.ErrorBars (%d points) mode=%s %s>" % (len(self), self.mode, self.attributes)

  def __init__(self, points, mode="y", draw_mode=".=|", radius=1., cap_length=1, **attributes):
    self.points = points
    self.mode = mode
    self.draw_mode = draw_mode
    self.radius = radius
    self.cap_length = cap_length

    self.attributes = dict(self.defaults)
    self.attributes.update(attributes)

  def interpret(self, printout=True):
    i = self.mode.find("x")
    draw_xbars = (i != -1)
    draw_xbars_asymmetric = False
    if draw_xbars and i != 0: draw_xbars_asymmetric = (self.mode[i-1] == "a")

    i = self.mode.find("y")
    draw_ybars = (i != -1)
    draw_ybars_asymmetric = False
    if draw_ybars and i != 0: draw_ybars_asymmetric = (self.mode[i-1] == "a")

    draw_points = (self.draw_mode.find(".") != -1)
    draw_caps = (self.draw_mode.find("=") != -1)
    draw_lines = (self.draw_mode.find("|") != -1)

    i = 0
    point_start = i
    i += 2
    point_end = i

    if draw_xbars:
      xbar_start = i
      if draw_xbars_asymmetric: i += 2
      else: i += 1
      xbar_end = i
    else:
      xbar_start, xbar_end = -1, -1

    if draw_ybars:
      ybar_start = i
      if draw_ybars_asymmetric: i += 2
      else: i += 1
      ybar_end = i
    else:
      ybar_start, ybar_end = -1, -1
    
    if printout:
      str_params = []
      if draw_xbars:
        if draw_xbars_asymmetric: str_params.append("asymmetric x bars")
        else: str_params.append("x error bars")
      if draw_ybars:
        if draw_ybars_asymmetric: str_params.append("asymmetric y bars")
        else: str_params.append("y error bars")
      print "Data mode: " + ", ".join(str_params)

      str_params = []
      if draw_points: str_params.append("circular points")
      if draw_caps: str_params.append("caps at +-1 sigma")
      if draw_lines: str_params.append("lines from -1 to 1 sigma")
      print "Draw mode: " + ", ".join(str_params)

      print
      print "In each entry, [%d:%d] is the x,y point" % (point_start, point_end)
      if draw_xbars:
        if draw_xbars_asymmetric:
          print "               [%d:%d] are the ends of the asymmetric x error bars" % (xbar_start, xbar_end)
        else:
          print "               [%d] is the length of the symmetric x error bars" % xbar_start
      if draw_ybars:
        if draw_ybars_asymmetric:
          print "               [%d:%d] are the ends of the asymmetric y error bars" % (ybar_start, ybar_end)
        else:
          print "               [%d] is the length of the symmetric y error bars" % ybar_start

      if len(self.points) == 0:
        print "No points available for an example."
      else:
        def tuplestr(x):
          return "(" + ", ".join(map(lambda value: "%g" % value, x)) + ")"

        print
        print "For example, in points[0] = %s," % tuplestr(self.points[0])
        str_params = ["%s is the x,y point" % tuplestr(self.points[0][point_start:point_end])]
        if draw_xbars:
          if draw_xbars_asymmetric: str_params.append("%s are x error bars" % tuplestr(self.points[0][xbar_start:xbar_end]))
          else: str_params.append("%g is the x error bar" % self.points[0][xbar_start])
        if draw_ybars:
          if draw_ybars_asymmetric: str_params.append("%s are y error bars" % tuplestr(self.points[0][ybar_start:ybar_end]))
          else: str_params.append("%g is the y error bar" % self.points[0][ybar_start])
        print ", ".join(str_params)

    else:
      return draw_xbars, draw_xbars_asymmetric, draw_ybars, draw_ybars_asymmetric, draw_points, draw_caps, draw_lines, \
             point_start, point_end, xbar_start, xbar_end, ybar_start, ybar_end

  def SVG(self, datatrans=None, range_filter=None):
    Plottable.SVG(self, datatrans, range_filter)

    draw_xbars, draw_xbars_asymmetric, draw_ybars, draw_ybars_asymmetric, draw_points, draw_caps, draw_lines, \
                point_start, point_end, xbar_start, xbar_end, ybar_start, ybar_end = self.interpret(printout=False)

    dpoints = []
    d = []
    for p in self.points:
      x, y = p[point_start:point_end]

      if datatrans == None: X, Y = x, y
      else: X, Y = datatrans(x, y)

      if range_filter == None or range_filter(x, y):
        self.increment_inner_ranges(x, y)
        self.increment_outer_ranges(X, Y)
      
      if draw_points:
        dpoints.append((".", self.radius, self.radius, True, 0, X, Y, True))
      d.append(("M", X, Y, True))

      if draw_xbars:
        if draw_xbars_asymmetric:
          xlow, xhigh = p[xbar_start:xbar_end]
        else:
          xlow, xhigh = -p[xbar_start], p[xbar_start]
        xlow += x
        xhigh += x

        if datatrans == None: XLOW, YLOW = xlow, y
        else: XLOW, YLOW = datatrans(xlow, y)
        if datatrans == None: XHIGH, YHIGH = xhigh, y
        else: XHIGH, YHIGH = datatrans(xhigh, y)

        d.append(("M", XLOW, YLOW, True))

        if draw_caps:
          (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(xlow, y)
          if yhatx != None and yhaty != None:
            d.append(("M", XLOW - yhatx*self.cap_length, YLOW - yhaty*self.cap_length, True))
            d.append(("L", XLOW + yhatx*self.cap_length, YLOW + yhaty*self.cap_length, True))
            d.append(("M", XLOW, YLOW, True))

        if draw_lines:
          d.append(("L", XHIGH, YHIGH, True))
        else:
          d.append(("M", XHIGH, YHIGH, True))

        if draw_caps:
          (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(xhigh, y)
          if yhatx != None and yhaty != None:
            d.append(("M", XHIGH - yhatx*self.cap_length, YHIGH - yhaty*self.cap_length, True))
            d.append(("L", XHIGH + yhatx*self.cap_length, YHIGH + yhaty*self.cap_length, True))
            d.append(("M", XHIGH, YHIGH, True))

        d.append(("M", X, Y, True))

      if draw_ybars:
        if draw_ybars_asymmetric:
          ylow, yhigh = p[ybar_start:ybar_end]
        else:
          ylow, yhigh = -p[ybar_start], p[ybar_start]
        ylow += y
        yhigh += y

        if datatrans == None: XLOW, YLOW = x, ylow
        else: XLOW, YLOW = datatrans(x, ylow)
        if datatrans == None: XHIGH, YHIGH = x, yhigh
        else: XHIGH, YHIGH = datatrans(x, yhigh)

        d.append(("M", XLOW, YLOW, True))

        if draw_caps:
          (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(x, ylow)
          if xhatx != None and xhaty != None:
            d.append(("M", XLOW - xhatx*self.cap_length, YLOW - xhaty*self.cap_length, True))
            d.append(("L", XLOW + xhatx*self.cap_length, YLOW + xhaty*self.cap_length, True))
            d.append(("M", XLOW, YLOW, True))

        if draw_lines:
          d.append(("L", XHIGH, YHIGH, True))
        else:
          d.append(("M", XHIGH, YHIGH, True))

        if draw_caps:
          (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(x, yhigh)
          if xhatx != None and xhaty != None:
            d.append(("M", XHIGH - xhatx*self.cap_length, YHIGH - xhaty*self.cap_length, True))
            d.append(("L", XHIGH + xhatx*self.cap_length, YHIGH + xhaty*self.cap_length, True))
            d.append(("M", XHIGH, YHIGH, True))

        d.append(("M", X, Y, True))

    nofill = {}
    nostroke = {}
    
    nofill.update(self.attributes)
    nofill["fill"] = "none"

    nostroke.update(self.attributes)
    nostroke["stroke"] = "none"
    if "stroke" in nofill:
      nostroke["fill"] = nofill["stroke"]
    else:
      nostroke["fill"] = "black"

    return svg.SVG("g", PlottablePath(d=d, **nofill).SVG(), PlottablePath(d=dpoints, **nostroke).SVG())

#####################################################################

# class ErrorEllipse(PlottablePoints):
#   def __repr__(self):
#     return "<plothon.plot.ErrorEllipse (%d points) %s>" % (len(self), self.attributes)

#   def __init__(self, points, **attributes):
#     self.points = points
#     self.attributes = attributes

#   def SVG(self, datatrans=None, range_filter=None):
#     Plottable.SVG(self, datatrans, range_filter)

#     output = SVG("g")
#     for p in self.points:
#       x, y = p[0], p[1]

#       if datatrans == None: X, Y = x, y
#       else: X, Y = datatrans(x, y)

#       if range_filter == None or range_filter(x, y):
#         self.increment_inner_ranges(x, y)
#         self.increment_outer_ranges(X, Y)

#       output.append()

#####################################################################

def edges(low, high, numbins):
  """Create a list of edges from a low value, a high value, and a
number of bins."""
  low, high = min(low, high), max(low, high)
  edgelist = []
  stepsize = (high - low)/float(numbins)
  current = low
  for i in range(numbins):
    edgelist.append(current)
    current += stepsize
  edgelist.append(high)
  return edgelist

#####################################################################

class Steps(Plottable):
  defaults = {"stroke-linejoin": "miter"}

  def __repr__(self):
    return "<plothon.plot.Steps (%d points) %s" % (len(self.values), self.attributes)

  def __init__(self, edges, values, anchor=0, **attributes):
    self.values = values
    self.edges = edges
    self.anchor = anchor

    self.attributes = dict(self.defaults)
    self.attributes.update(attributes)

  def xy(self):
    if len(self.edges) == 2:
      edges = []
      stepsize = 1.*(self.edges[1] - self.edges[0])/len(self.values)
      current = self.edges[0]
      for i in xrange(len(self.values)):
        edges.append(current)
        current += stepsize
      edges.append(self.edges[1])
      
    else: edges = self.edges

    output = []
    if self.anchor != None:
      output.append((edges[0], self.anchor))

    last = edges[0]
    for e, v in itertools.izip(itertools.islice(edges, 1, None), self.values):
      output.append((last, v))
      output.append((e, v))
      last = e
    
    if self.anchor != None:
      output.append((edges[-1], self.anchor))

    return output

  def inner_ranges(self, range_filter=None):
    Plottable.inner_ranges(self, range_filter)
    xy = self.xy()
    for i, (x, y) in enumerate(xy):
      if self.anchor == None or not (i == 0 or i == len(xy)-1):
        if range_filter == None or range_filter(x, y):
          self.increment_inner_ranges(x, y)

  def SVG(self, datatrans=None, range_filter=None):
    Plottable.SVG(self, datatrans, range_filter)

    d = []
    xy = self.xy()
    for i, (x, y) in enumerate(xy):
      if datatrans == None: X, Y = x, y
      else: X, Y = datatrans(x, y)

      if self.anchor == None or not (i == 0 or i == len(xy)-1):
        if range_filter == None or range_filter(x, y):
          self.increment_inner_ranges(x, y)
          self.increment_outer_ranges(X, Y)
      
      if d == []:
        d.append(("M", X, Y, True))
      else:
        d.append(("L", X, Y, True))

    return PlottablePath(d=d, **self.attributes).SVG()

#####################################################################

symbolTemplates = {"dot": svg.SVG("symbol", svg.SVG("circle", cx=0, cy=0, r=1, stroke="none", fill="black"), viewBox="0 0 1 1", overflow="visible"), \
                   "box": svg.SVG("symbol", svg.SVG("rect", x1=-1, y1=-1, x2=1, y2=1, stroke="none", fill="black"), viewBox="0 0 1 1", overflow="visible"), \
                   "uptri": svg.SVG("symbol", svg.SVG("path", d="M -1 0.866 L 1 0.866 L 0 -0.866 Z", stroke="none", fill="black"), viewBox="0 0 1 1", overflow="visible"), \
                   "downtri": svg.SVG("symbol", svg.SVG("path", d="M -1 -0.866 L 1 -0.866 L 0 0.866 Z", stroke="none", fill="black"), viewBox="0 0 1 1", overflow="visible"), \
                   }

def make_symbol(template="dot", name=None, **attributes):
  output = copy.deepcopy(symbolTemplates[template])
  output[0].attributes.update(attributes)

  if name == None: output["id"] = "s%d" % random.randint(0, sys.maxint)
  else: output["id"] = name

  return output

#####################################################################

class SymbolScatter(PlottablePoints):
  defaults = {}

  def __repr__(self):
    return "<plothon.plot.SymbolScatter (%d symbols) %s>" % (len(self), self.attributes)

  def __init__(self, points, symbol=None, width=1, height=1, **attributes):
    self.points = points
    self.width = width
    self.height = height

    self.attributes = dict(self.defaults)
    self.attributes.update(attributes)

    if symbol != None: self.symbol = symbol
    else: self.symbol = make_symbol("dot")

  def SVG(self, datatrans=None, range_filter=None):
    Plottable.SVG(self, datatrans, range_filter)

    output = svg.SVG("g", svg.SVG("defs", self.symbol))
    name = "#%s" % self.symbol["id"]

    for p in self.points:
      x, y = p[0], p[1]

      if datatrans == None: X, Y = x, y
      else: X, Y = datatrans(x, y)

      if range_filter == None or range_filter(x, y):
        self.increment_inner_ranges(x, y)
        self.increment_outer_ranges(X, Y)
      
      output.append(svg.SVG("use", x=X, y=Y, width=self.width, height=self.height, xlink__href=name))
      
    return output

#####################################################################

#####################################################################

#####################################################################

#####################################################################

#####################################################################

#####################################################################

#####################################################################

def number_format(x):
  output = "%g" % x

  if output[0] == "-":
    output = u"\u2013" + output[1:]

  index = output.find("e")
  if index != -1:
    uniout = unicode(output[:index]) + u"\u00d710"
    saw_nonzero = False
    for n in output[index+1:]:
      if n == "+": pass # uniout += u"\u207a"
      elif n == "-": uniout += u"\u207b"
      elif n == "0":
        if saw_nonzero: uniout += u"\u2070"
      elif n == "1":
        saw_nonzero = True
        uniout += u"\u00b9"
      elif n == "2":
        saw_nonzero = True
        uniout += u"\u00b2"
      elif n == "3":
        saw_nonzero = True
        uniout += u"\u00b3"
      elif "4" <= n <= "9":
        saw_nonzero = True
        if saw_nonzero: uniout += eval("u\"\\u%x\"" % (0x2070 + ord(n) - ord("0")))
      else: uniout += n

    if uniout[:2] == u"1\u00d7": uniout = uniout[2:]
    return uniout

  return output

#####################################################################

def tick_format(ticks, format=number_format):
  output = {}
  for x in ticks:
    output[x] = format(x)
  return output

def tick_unlabel(ticks):
  output = {}
  for x in ticks:
    output[x] = ""
  return output

def tick_drop(ticks, x):
  for xi in ticks.keys():
    if abs(xi - x) < epsilon:
      del ticks[xi]
  return ticks

#####################################################################

def ticks_regular(low, high, N, format=number_format):
  if low >= high: raise ValueError, "low must be less than high."

  output = {}
  x = low
  for i in xrange(N):
    label = format(x)
    if abs(x) < epsilon * (high - low): label = "0"
    output[x] = label
    x += (high - low)/(N-1.)
  return output

def ticks(low, high, maxchars=20, format=number_format):
  if low >= high: raise ValueError, "low must be less than high."

  counter = 0
  granularity = 10**math.ceil(math.log10(max(abs(low), abs(high))))
  lowN = math.ceil(1.*low / granularity)
  highN = math.floor(1.*high / granularity)

  while (lowN > highN):
    countermod3 = counter % 3
    if countermod3 == 0: granularity *= 0.5
    elif countermod3 == 1: granularity *= 0.4
    else: granularity *= 0.5
    counter += 1
    lowN = math.ceil(1.*low / granularity)
    highN = math.floor(1.*high / granularity)

  last_granularity = granularity
  last_trial = None

  while True:
    trial = {}
    chars = 0
    for n in range(int(lowN), int(highN)+1):
      x = n * granularity
      label = format(x)
      if abs(x) < epsilon * (high - low): label = "0"
      chars += len(label)
      trial[x] = label

    if chars > maxchars:
      if last_trial == None:
        v1, v2 = low, high
        return {v1: format(v1), v2: format(v2)}
      else:
        low_in_ticks, high_in_ticks = False, False
        for t in last_trial.keys():
          if 1.*abs(t - low)/last_granularity < epsilon: low_in_ticks = True
          if 1.*abs(t - high)/last_granularity < epsilon: high_in_ticks = True

        lowN = 1.*low / last_granularity
        highN = 1.*high / last_granularity
        if abs(lowN - round(lowN)) < epsilon and not low_in_ticks:
          last_trial[low] = format(low)
        if abs(highN - round(highN)) < epsilon and not high_in_ticks:
          last_trial[high] = format(high)
        return last_trial

    last_granularity = granularity
    last_trial = trial

    countermod3 = counter % 3
    if countermod3 == 0: granularity *= 0.5
    elif countermod3 == 1: granularity *= 0.4
    else: granularity *= 0.5
    counter += 1
    lowN = math.ceil(1.*low / granularity)
    highN = math.floor(1.*high / granularity)

#####################################################################

def miniticks(low, high, original_ticks):
  if len(original_ticks) < 2: original_ticks = ticks(low, high)
  original_ticks = original_ticks.keys()
  original_ticks.sort()

  if low > original_ticks[0] + epsilon or high < original_ticks[-1] - epsilon:
    raise ValueError, "original_ticks {%g...%g} extend beyond [%g, %g]." % (original_ticks[0], original_ticks[-1], low, high)

  granularities = []
  for i in range(len(original_ticks)-1):
    granularities.append(original_ticks[i+1] - original_ticks[i])
  spacing = 10**(math.ceil(math.log10(min(granularities)) - 1))

  output = []
  x = original_ticks[0] - math.ceil(1.*(original_ticks[0] - low) / spacing) * spacing

  while x <= high:
    if x >= low:
      already_in_ticks = False
      for t in original_ticks:
        if abs(x-t) < epsilon * (high - low): already_in_ticks = True
      if not already_in_ticks: output.append(x)
    x += spacing
  return output

#####################################################################

def logticks(low, high, base=10, maxchars=20, format=number_format):
  if low >= high: raise ValueError, "low must be less than high."

  lowN = math.floor(math.log(low, base))
  highN = math.ceil(math.log(high, base))
  output = {}
  for n in range(int(lowN), int(highN)+1):
    x = base**n
    label = format(x)
    if low <= x <= high: output[x] = label

  for i in range(1, len(output)):
    keys = output.keys()
    keys.sort()
    keys = keys[::i]
    values = map(lambda k: output[k], keys)
    if len("".join(values)) < maxchars:
      for k in output.keys():
        if k not in keys:
          output[k] = ""
      break

  if len(output) <= 2:
    output2 = ticks(low, high, maxchars=int(math.ceil(maxchars/2.)), format=format)
    lowest = min(output2)

    for k in output:
      if k < lowest: output2[k] = output[k]
    output = output2

  return output

#####################################################################

def logminiticks(low, high, base=10):
  if low >= high: raise ValueError, "low must be less than high."

  lowN = math.floor(math.log(low, base))
  highN = math.ceil(math.log(high, base))
  output = []
  num_ticks = 0
  for n in range(int(lowN), int(highN)+1):
    x = base**n
    if low <= x <= high: num_ticks += 1
    for m in range(2, int(math.ceil(base))):
      minix = m * x
      if low <= minix <= high: output.append(minix)

  if num_ticks <= 2: return []
  else: return output

#####################################################################

class Frame:
  def __repr__(self):
    return "<plothon.plot.Frame (%d Plottable objects)>" % len(self.data)

  def __init__(self, data, xmin=None, ymin=None, xmax=None, ymax=None, **parameters):
    if isinstance(data, Plottable):
      self.data = [data]
    elif isinstance(data, Plottables):
      self.data = list(data)
    else:
      try: self.data = list(data)
      except TypeError: raise TypeError, "data must be a Plottable or a list of Plottables."

    self.xmin = xmin
    self.ymin = ymin
    self.xmax = xmax
    self.ymax = ymax

    for k, v in {"x": 0., "y": 0., "width": 100., "height": 100., \
                 "xlogbase": None, "ylogbase": None, \
                 "xticks": None, "xminiticks": None, "yticks": None, "yminiticks": None, \
                 "rightticks": None, "rightminiticks": None, "topticks": None, "topminiticks": None, \
                 "xlabel": None, "ylabel": None, "rightlabel": None, "toplabel": None, \
                 "background": {}, "xgrid": None, "xminigrid": None, "ygrid": None, "yminigrid": None, \
                 "tick_length": 2., "minitick_length": 1., \
                 "font_size": 5, \
                 "draw_left_border": True, "draw_top_border": True, "draw_right_border": True, "draw_bottom_border": True, \
                 "margin_bottom": 1., "margin_bottom_label": 1., "margin_bottom_ticklabel": 1., \
                 "margin_left": 1., "margin_left_label": 1., "margin_left_ticklabel": 1., \
                 "margin_right": 1., "margin_right_label": 1., "margin_right_ticklabel": 1., \
                 "margin_top": 1., "margin_top_label": 1., "margin_top_ticklabel": 1., \
                 }.items():
      self.__dict__[k] = v

      self.__dict__.update(parameters)

  def SVG(self, **attributes):
    idnum = random.randint(0, 1000)

    atts = {"font-size": self.font_size, "id": "frame%d" % idnum}
    atts.update(attributes)
    output = svg.SVG("g", **atts)

    self.determine_ranges()
    self.determine_ticks()

    x1, y1, x2, y2 = self.x, self.y, self.x + self.width, self.y + self.height

    x1_data = x1 + self.margin_left + self.margin_left_label + self.margin_left_ticklabel
    if self.ylabel != None: x1_data += self.font_size
    if self.last_yticks != None:
      mostchars = 0
      for v in self.last_yticks.values():
        if len(v) > mostchars: mostchars = len(v)
      x1_data += max(0, (mostchars-1)) * 0.9 * self.font_size + 3.

    y1_data = y1 + self.margin_top + self.margin_top_label + self.margin_top_ticklabel
    if self.toplabel != None: y1_data += self.font_size
    if self.last_topticks != None:
      mostchars = 0
      for v in self.last_topticks.values():
        if len(v) > mostchars:
          mostchars = len(v)
      if mostchars > 0:
        y1_data += self.font_size

    x2_data = x2 - self.margin_right - self.margin_right_label - self.margin_right_ticklabel
    if self.rightlabel != None: x2_data -= self.font_size
    if self.last_rightticks != None:
      mostchars = 0
      for v in self.last_rightticks.values():
        if len(v) > mostchars: mostchars = len(v)
      x2_data -= max(0, (mostchars-1)) * self.font_size

    y2_data = y2 - self.margin_bottom - self.margin_bottom_label - self.margin_bottom_ticklabel
    if self.xlabel != None: y2_data -= self.font_size
    if self.last_xticks != None:
      mostchars = 0
      for v in self.last_xticks.values():
        if len(v) > mostchars: mostchars = len(v)
      if mostchars > 0:
        y2_data -= self.font_size

    xmid = (x1_data + x2_data) / 2.
    ymid = (y1_data + y2_data) / 2.

    # axis labels
    if self.xlabel != None:
      output.append(svg.SVG("text", self.xlabel, stroke="none", fill="black", x=0, y=0, transform="translate(%g, %g)" % (xmid, y2 - self.margin_bottom), id=("xlabel%d" % idnum)))
    if self.ylabel != None:
      output.append(svg.SVG("text", self.ylabel, stroke="none", fill="black", x=0, y=0, transform="translate(%g, %g) rotate(-90)" % (x1 + self.margin_left + self.font_size, ymid), id=("ylabel%d" % idnum)))
    if self.rightlabel != None:
      output.append(svg.SVG("text", self.rightlabel, stroke="none", fill="black", x=0, y=0, transform="translate(%g, %g) rotate(90)" % (x2 - self.margin_right - self.font_size, ymid), id=("rightlabel%d" % idnum)))
    if self.toplabel != None:
      output.append(svg.SVG("text", self.toplabel, stroke="none", fill="black", x=0, y=0, transform="translate(%g, %g)" % (xmid, y1 + self.margin_top + self.font_size), id=("toplabel%d" % idnum)))

    # it's just more convenient to start thinking in terms of x1, y1,
    # x2, y2 being the whole universe from this point on
    x1, y1, x2, y2 = x1_data, y1_data, x2_data, y2_data
    width, height = x2 - x1, y2 - y1

    # clipping region for the data
    clippath_name = ("clippath%d" % idnum)
    clippath = svg.SVG("clipPath", svg.SVG("path", d="M %g %g L %g %g L %g %g L %g %g Z" % (x1, y1, x1+width, y1, x1+width, y1+height, x1, y1+height)), id=clippath_name)
    output.append(clippath)

    self.window = DataTransWindow(x1, y1, width, height, self.last_xmin, self.last_ymin, self.last_xmax, self.last_ymax, \
                                   self.xlogbase, self.ylogbase, (x1 - 10 * (x2 - x1)), None, (y1 + (x2 - x1) + 10 * (y2 - y1)), None)

    # background
    if self.background != None:
      background = {"x": x1, "y": y1, "width": width, "height": height, "stroke": "none", "fill": "none", "id": ("background%d" % idnum)}
      background.update(self.background)
      output.append(svg.SVG("rect", **background))

    # minigrid lines (x)
    if self.xminigrid != None:
      xgrid_lines = svg.SVG("g", stroke="lightgray", stroke_dasharray="1,1", id=("xminigrid%d" % idnum))

      for x in self.last_xminiticks:
        X, Y = self.window(x, self.last_ymin)
        if (abs(X - x1) > epsilon or not self.draw_left_border) and (abs(X - x2) > epsilon or not self.draw_right_border):
          xgrid = {"x1": X, "y1": y1, "x2": X, "y2": y2}
          xgrid.update(self.xminigrid)
          xgrid_lines.append(svg.SVG("line", **xgrid))
      output.append(xgrid_lines)

    # minigrid lines (y)
    if self.yminigrid != None:
      ygrid_lines = svg.SVG("g", stroke="lightgray", stroke_dasharray="1,1", id=("yminigrid%d" % idnum))

      for y in self.last_yminiticks:
        X, Y = self.window(self.last_xmin, y)
        if (abs(Y - y1) > epsilon or not self.draw_top_border) and (abs(Y - (y2)) > epsilon or not self.draw_bottom_border):
          ygrid = {"x1": x1, "y1": Y, "x2": x2, "y2": Y}
          ygrid.update(self.yminigrid)
          ygrid_lines.append(svg.SVG("line", **ygrid))
      output.append(ygrid_lines)

    # grid lines (x)
    if self.xgrid != None:
      xgrid_lines = svg.SVG("g", stroke="gray", id=("xgrid%d" % idnum))

      for x in self.last_xticks.keys():
        X, Y = self.window(x, self.last_ymin)
        if (abs(X - x1) > epsilon or not self.draw_left_border) and (abs(X - x2) > epsilon or not self.draw_right_border):
          xgrid = {"x1": X, "y1": y1, "x2": X, "y2": y2}
          xgrid.update(self.xgrid)
          xgrid_lines.append(svg.SVG("line", **xgrid))
      output.append(xgrid_lines)

    # grid lines (y)
    if self.ygrid != None:
      ygrid_lines = svg.SVG("g", stroke="gray", id=("ygrid%d" % idnum))

      for y in self.last_yticks.keys():
        X, Y = self.window(self.last_xmin, y)
        if (abs(Y - y1) > epsilon or not self.draw_top_border) and (abs(Y - (y2)) > epsilon or not self.draw_bottom_border):
          ygrid = {"x1": x1, "y1": Y, "x2": x2, "y2": Y}
          ygrid.update(self.ygrid)
          ygrid_lines.append(svg.SVG("line", **ygrid))
      output.append(ygrid_lines)

    # the data
    datasvg = svg.SVG("g", clip_path="url(#%s)" % clippath_name, id=("data%d" % idnum))
    for dp in self.data:
      if not isinstance(dp, Plottable): raise TypeError, "data must be a list of Plottables."
      datasvg.append(dp.SVG(self.window))
    output.append(datasvg)

    # xticks and bottom border
    xtick_path = []
    if self.draw_bottom_border:
      xtick_path.append("M%g %gL%g %g" % (x1, y2, x2, y2))

    xtick_labels = svg.SVG("g", stroke="none", fill="black", id=("xticklabels%d" % idnum))
    for x, label in self.last_xticks.items():
      X, Y = self.window(x, self.last_ymin)
      if abs(X - x1) > epsilon and abs(X - x2) > epsilon:
        xtick_path.append("M%g %gL%g %g" % (X, Y, X, Y - self.tick_length))
      xtick_labels.append(svg.SVG("text", label, x=X, y=(Y + self.font_size + self.margin_bottom_ticklabel)))

    for x in self.last_xminiticks:
      X, Y = self.window(x, self.last_ymin)
      if abs(X - x1) > epsilon and abs(X - x2) > epsilon:
        xtick_path.append("M%g %gL%g %g" % (X, Y, X, Y - self.minitick_length))

    if self.draw_bottom_border:
      xtick_path.append("M%g %gL%g %g" % (x2 - epsilon, y2, x2, y2))

    xtick_path = "".join(xtick_path)
    xtick_path = svg.SVG("path", d=xtick_path, id=("xticks%d" % idnum))
    output.append(xtick_path)
    output.append(xtick_labels)

    # yticks and left border
    ytick_path = []
    if self.draw_left_border:
      ytick_path.append("M%g %gL%g %g" % (x1, y2, x1, y1))

    ytick_labels = svg.SVG("g", stroke="none", fill="black", text_anchor="end", id=("yticklabels%d" % idnum))
    for y, label in self.last_yticks.items():
      X, Y = self.window(self.last_xmin, y)
      if abs(Y - y1) > epsilon and abs(Y - (y2)) > epsilon:
        ytick_path.append("M%g %gL%g %g" % (X, Y, X + self.tick_length, Y))
      ytick_labels.append(svg.SVG("text", label, x=X - self.margin_left_ticklabel, y=(Y + self.font_size*0.35)))

    for y in self.last_yminiticks:
      X, Y = self.window(self.last_xmin, y)
      if abs(Y - y1) > epsilon and abs(Y - (y2)) > epsilon:
        ytick_path.append("M%g %gL%g %g" % (X, Y, X + self.minitick_length, Y))

    if self.draw_left_border:
      ytick_path.append("M%g %gL%g %g" % (x1, y1 + epsilon, x1, y1))

    ytick_path = "".join(ytick_path)
    ytick_path = svg.SVG("path", d=ytick_path, id=("yticks%d" % idnum))
    output.append(ytick_path)
    output.append(ytick_labels)

    # rightticks and right border
    righttick_path = []
    if self.draw_right_border:
      righttick_path.append("M%g %gL%g %g" % (x2, y2, x2, y1))

    righttick_labels = svg.SVG("g", stroke="none", fill="black", text_anchor="start", id=("rightticklabels%d" % idnum))
    for y, label in self.last_rightticks.items():
      X, Y = self.window(self.last_xmax, y)
      if abs(Y - y1) > epsilon and abs(Y - (y2)) > epsilon:
        righttick_path.append("M%g %gL%g %g" % (X, Y, X - self.tick_length, Y))
      if label != "":
        righttick_labels.append(svg.SVG("text", label, x=X + self.margin_right_ticklabel, y=(Y + self.font_size*0.35)))

    for y in self.last_rightminiticks:
      X, Y = self.window(self.last_xmax, y)
      if abs(Y - y1) > epsilon and abs(Y - (y2)) > epsilon:
        righttick_path.append("M%g %gL%g %g" % (X, Y, X - self.minitick_length, Y))

    if self.draw_right_border:
      righttick_path.append("M%g %gL%g %g" % (x2, y1 + epsilon, x2, y1))

    righttick_path = "".join(righttick_path)
    righttick_path = svg.SVG("path", d=righttick_path, id=("rightticks%d" % idnum))
    output.append(righttick_path)
    output.append(righttick_labels)
    
    # topticks and top border
    toptick_path = []
    if self.draw_top_border:
      toptick_path.append("M%g %gL%g %g" % (x1, y1, x2, y1))

    toptick_labels = svg.SVG("g", stroke="none", fill="black", id=("topticklabels%d" % idnum))
    for x, label in self.last_topticks.items():
      X, Y = self.window(x, self.last_ymax)
      if abs(X - x1) > epsilon and abs(X - x2) > epsilon:
        toptick_path.append("M%g %gL%g %g" % (X, Y, X, Y + self.tick_length))
      if label != "":
        toptick_labels.append(svg.SVG("text", label, x=X, y=Y - self.margin_top_ticklabel))

    for x in self.last_topminiticks:
      X, Y = self.window(x, self.last_ymax)
      if abs(X - x1) > epsilon and abs(X - x2) > epsilon:
        toptick_path.append("M%g %gL%g %g" % (X, Y, X, Y + self.minitick_length))

    if self.draw_top_border:
      toptick_path.append("M%g %gL%g %g" % (x2 - epsilon, y1, x2, y1))

    toptick_path = "".join(toptick_path)
    toptick_path = svg.SVG("path", d=toptick_path, id=("topticks%d" % idnum))
    output.append(toptick_path)
    output.append(toptick_labels)

    return output

  def determine_ranges(self):
    if self.xmin == None or self.xmax == None or self.ymin == None or self.ymax == None:
      if self.xlogbase == None and self.ylogbase == None:
        range_filter = None
      elif self.xlogbase != None and self.ylogbase == None:
        range_filter = lambda x, y: x > 0.
      elif self.xlogbase != None and self.ylogbase != None:
        range_filter = lambda x, y: x > 0. and y > 0.
      else:
        range_filter = lambda x, y: y > 0.

      xmin, ymin, xmax, ymax = None, None, None, None
      
      # loop over all the data paths to find the min/max
      for dp in self.data:
        if not isinstance(dp, Plottable): raise TypeError, "data must be a list of Plottables."
        dp.inner_ranges(range_filter)  # this sets inner_*min, inner_*max
        if dp.inner_xmin != None and (xmin == None or dp.inner_xmin < xmin): xmin = dp.inner_xmin
        if dp.inner_xmax != None and (xmax == None or dp.inner_xmax > xmax): xmax = dp.inner_xmax
        if dp.inner_ymin != None and (ymin == None or dp.inner_ymin < ymin): ymin = dp.inner_ymin
        if dp.inner_ymax != None and (ymax == None or dp.inner_ymax > ymax): ymax = dp.inner_ymax

      if self.xlogbase == None:
        if xmin == None: xmin = 0.
        if xmax == None: xmax = 1./1.2
      else:
        if xmin == None: xmin = 0.1
        if xmax == None: xmax = 10.

      if self.ylogbase == None:
        if ymin == None: ymin = 0.
        if ymax == None: ymax = 1./1.2
      else:
        if ymin == None: ymin = 0.1
        if ymax == None: ymax = 10.
      
      width = xmax - xmin
      height = ymax - ymin
      if xmin == xmax:
        if self.xlogbase == None:
          xmin -= 1.
          xmax += 1.
        else:
          xmin /= 1.*self.xlogbase
          xmax *= self.xlogbase
      else:
        if self.xlogbase == None:
          if xmin >= 0. and xmin - 0.2 * width < 0.: xmin = 0.
          else: xmin -= 0.2 * width
          xmax += 0.2 * width

        else:
          xmin /= 1.*self.xlogbase
          xmax *= self.xlogbase

      if ymin == ymax:
        if self.ylogbase == None:
          ymin -= 1.
          ymax += 1.
        else:
          ymin /= 1.*self.ylogbase
          ymax *= self.ylogbase
      else:
        if self.ylogbase == None:
          if ymin >= 0. and ymin - 0.2 * height < 0.: ymin = 0.
          else: ymin -= 0.2 * height
          ymax += 0.2 * height

        else:
          ymin /= 1.*self.ylogbase
          ymax *= self.ylogbase

    if self.xmin != None: self.last_xmin = self.xmin
    else: self.last_xmin = xmin

    if self.xmax != None: self.last_xmax = self.xmax
    else: self.last_xmax = xmax

    if self.ymin != None: self.last_ymin = self.ymin
    else: self.last_ymin = ymin

    if self.ymax != None: self.last_ymax = self.ymax
    else: self.last_ymax = ymax

  def determine_ticks(self):
    if self.xticks == None:
      maxchars = int(math.ceil(self.width*20./100.))
      if self.xlogbase == None:
        self.last_xticks = ticks(self.last_xmin, self.last_xmax, maxchars=maxchars)
        if self.xminiticks == None:
          self.last_xminiticks = miniticks(self.last_xmin, self.last_xmax, self.last_xticks)
        else:
          self.last_xminiticks = self.xminiticks
      else:
        self.last_xticks = logticks(self.last_xmin, self.last_xmax, self.xlogbase, maxchars=maxchars)
        if self.xminiticks == None:
          self.last_xminiticks = logminiticks(self.last_xmin, self.last_xmax, self.xlogbase)
        else:
          self.last_xminiticks = self.xminiticks
    else:
      self.last_xticks = self.xticks
      if self.xminiticks == None:
        if self.xlogbase == None:
          self.last_xminiticks = miniticks(self.last_xmin, self.last_xmax, self.last_xticks)
        else:
          self.last_xminiticks = logminiticks(self.last_xmin, self.last_xmax, self.xlogbase)
      else:
        self.last_xminiticks = self.xminiticks

    if self.yticks == None:
      maxchars = int(math.ceil(self.height*30./100.))
      if self.ylogbase == None:
        self.last_yticks = ticks(self.last_ymin, self.last_ymax, maxchars=maxchars)
        if self.yminiticks == None:
          self.last_yminiticks = miniticks(self.last_ymin, self.last_ymax, self.last_yticks)
        else:
          self.last_yminiticks = self.yminiticks
      else:
        self.last_yticks = logticks(self.last_ymin, self.last_ymax, self.ylogbase, maxchars=maxchars)
        if self.yminiticks == None:
          self.last_yminiticks = logminiticks(self.last_ymin, self.last_ymax, self.ylogbase)
        else:
          self.last_yminiticks = self.yminiticks
    else:
      self.last_yticks = self.yticks
      if self.yminiticks == None:
        if self.ylogbase == None:
          self.last_yminiticks = miniticks(self.last_ymin, self.last_ymax, self.last_yticks)
        else:
          self.last_yminiticks = logminiticks(self.last_ymin, self.last_ymax, self.ylogbase)
      else:
        self.last_yminiticks = self.yminiticks

    if self.rightticks == None:
      self.last_rightticks = tick_unlabel(self.last_yticks)
      if self.rightminiticks == None:
        self.last_rightminiticks = self.last_yminiticks
      else:
        self.last_rightminiticks = self.rightminiticks
    else:
      self.last_rightticks = self.rightticks
      if self.rightminiticks == None:
        if self.ylogbase == None:
          self.last_rightminiticks = miniticks(self.last_ymin, self.last_ymax, self.last_rightticks)
        else:
          self.last_rightminiticks = logminiticks(self.last_ymin, self.last_ymax, self.ylogbase)
      else:
        self.last_rightminiticks = self.rightminiticks

    if self.topticks == None:
      self.last_topticks = tick_unlabel(self.last_xticks)
      if self.topminiticks == None:
        self.last_topminiticks = self.last_xminiticks
      else:
        self.last_topminiticks = self.topminiticks
    else:
      self.last_topticks = self.topticks
      if self.topminiticks == None:
        if self.xlogbase == None:
          self.last_topminiticks = miniticks(self.last_xmin, self.last_xmax, self.last_topticks)
        else:
          self.last_topminiticks = logminiticks(self.last_xmin, self.last_xmax, self.xlogbase)
      else:
        self.last_topminiticks = self.topminiticks

#####################################################################

class Plot:
  def __repr__(self):
    return "<plothon.plot.Plot (%d Plottable objects)>" % len(self.data)

  def __init__(self, data, xmin=None, ymin=None, xmax=None, ymax=None, **parameters):
    if isinstance(data, Plottable):
      self.data = [data]
    elif isinstance(data, Plottables):
      self.data = list(data)
    else:
      try: self.data = list(data)
      except TypeError: raise TypeError, "data must be a Plottable or a list of Plottables."

    self.xmin = xmin
    self.ymin = ymin
    self.xmax = xmax
    self.ymax = ymax

    for k, v in {"datatrans": None, \
                 "x": 0., "y": 0., "width": 100., "height": 100., \
                 "draw_axis": True, "draw_arrows": True, \
                 "xticks": None, "xminiticks": None, "yticks": None, "yminiticks": None, \
                 "xaxis": 0., "yaxis": 0., \
                 "transform_text": False, \
                 "xlabel": None, "ylabel": None, \
                 "tick_length": 1.5, "minitick_length": 0.75, \
                 "font_size": 5, \
                 "margin_xticklabel": 1., "margin_yticklabel": 1., \
                 "margin_avoidance": 5., \
                 "margin_left": 5., "margin_top": 5., "margin_right": 5., "margin_bottom": 5. \
                 }.items():
      self.__dict__[k] = v

      self.__dict__.update(parameters)

  def SVG(self, **attributes):
    idnum = random.randint(0, 1000)

    # clipping region
    clippath_name = "dataclip%d" % idnum
    clippath = svg.SVG("clipPath", svg.SVG("rect", x=self.x, y=self.y, width=self.width, height=self.height), id=clippath_name)

    atts = {"font-size": self.font_size, "clip-path": "url(#%s)" % clippath_name, "id": "plot%d" % idnum}
    atts.update(attributes)
    output = svg.SVG("g", clippath, **atts)

    self.determine_ranges()  # does determine_ticks() internally

    if self.last_yticks != None:
      mostchars = 0
      for v in self.last_yticks.values():
        if len(v) > mostchars: mostchars = len(v)
      yaxis_width = max(0, (mostchars-1)) * 0.9 * self.font_size + 3. + self.margin_xticklabel

    if self.last_xticks != None:
      mostchars = 0
      for v in self.last_xticks.values():
        if len(v) > mostchars: mostchars = len(v)
      if mostchars > 0:
        xaxis_height = self.font_size
      else:
        xaxis_height = 0.

    if self.datatrans != None:
      Xmin, Xaxis = self.datatrans(self.last_xmin, self.last_xaxis)
      Xmax, Xaxis = self.datatrans(self.last_xmax, self.last_xaxis)
      Yaxis, Ymin = self.datatrans(self.last_yaxis, self.last_ymin)
      Yaxis, Ymax = self.datatrans(self.last_yaxis, self.last_ymax)
    else:
      Xmin, Xaxis = self.last_xmin, self.last_xaxis
      Xmax, Xaxis = self.last_xmax, self.last_xaxis
      Yaxis, Ymin = self.last_yaxis, self.last_ymin
      Yaxis, Ymax = self.last_yaxis, self.last_ymax

    x1 = self.x + self.margin_left
    y1 = self.y + self.margin_top
    x2 = self.x + self.width - self.margin_right
    y2 = self.y + self.height - self.margin_bottom

    if self.draw_axis and self.datatrans == None:
      xnormalization = 1.*xaxis_height/abs(y2 - y1) * abs(self.last_ymax - self.last_ymin)
      ynormalization = 1.*yaxis_width/abs(x2 - x1) * abs(self.last_xmax - self.last_xmin)
      if abs(Yaxis) > 0:
        x1 += max(0, (1.*(Xmin - Yaxis)/ynormalization + 1.) * yaxis_width)
      if abs(Xaxis) > 0:
        y2 -= max(0, (1.*(Ymin - Xaxis)/xnormalization + 1.) * xaxis_height)

    self.window = DataTransWindow(x1, y1, x2 - x1, y2 - y1, self.outer_xmin, self.outer_ymin, self.outer_xmax, self.outer_ymax)
    datatrans = DataTransComposition(self.datatrans, self.window) # first apply self.datatrans, then window

    # the data
    datasvg = svg.SVG("g", clip_path="url(#%s)" % clippath_name, id=("data%d" % idnum))
    for dp in self.data:
      if not isinstance(dp, Plottable): raise TypeError, "data must be a list of Plottables."
      datasvg.append(dp.SVG(datatrans))
    output.append(datasvg)

    if self.draw_axis:
      Xcross, Ycross = datatrans(self.last_yaxis, self.last_xaxis)
      Xmin, Xaxis = datatrans(self.last_xmin, self.last_xaxis)
      Xmax, Xaxis = datatrans(self.last_xmax, self.last_xaxis)
      Yaxis, Ymin = datatrans(self.last_yaxis, self.last_ymin)
      Yaxis, Ymax = datatrans(self.last_yaxis, self.last_ymax)

      # prepare the (curving?) axis lines
      if self.datatrans == None:
        (x1, y1) = datatrans(self.last_xmin, self.last_xaxis)
        (x2, y2) = datatrans(self.last_xmax, self.last_xaxis)
        xaxis_path = PlottablePath([("M", x1, y1, True), ("L", x2, y2, True)], id=("xaxis%d" % idnum))
        (x1, y1) = datatrans(self.last_yaxis, self.last_ymin)
        (x2, y2) = datatrans(self.last_yaxis, self.last_ymax)
        yaxis_path = PlottablePath([("M", x1, y1, True), ("L", x2, y2, True)], id=("yaxis%d" % idnum))
      else:
        xaxis_path = ParametricLine(self.last_xmin, self.last_xaxis, self.last_xmax, self.last_xaxis, id=("xaxis%d" % idnum), stroke_width="0.25pt").PlottablePath(datatrans, False)
        yaxis_path = ParametricLine(self.last_yaxis, self.last_ymin, self.last_yaxis, self.last_ymax, id=("yaxis%d" % idnum), stroke_width="0.25pt").PlottablePath(datatrans, False)

      # create the xticks and the xtick labels
      xtick_labels = svg.SVG("g", stroke="none", fill="black", id=("xticklabels%d" % idnum))
      for x, label in self.last_xticks.items():
        X, Y = datatrans(x, self.last_xaxis)
        if abs(X - Xcross) > epsilon or abs(Y - Ycross) > epsilon:
          (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(x, self.last_xaxis)
          if xhatx != None and xhaty != None and yhatx != None and yhaty != None:
            if not self.draw_arrows or (abs(X - Xmin) > epsilon and abs(X - Xmax) > epsilon):
              xaxis_path.d.append(("M", X - self.tick_length*yhatx, Y - self.tick_length*yhaty, True))
              xaxis_path.d.append(("L", X + self.tick_length*yhatx, Y + self.tick_length*yhaty, True))

            if abs(X - Xcross) > self.margin_avoidance or abs(Y - Ycross) > self.margin_avoidance:
              if self.datatrans != None:
                X += (self.tick_length + self.margin_xticklabel)*yhatx
                Y += (self.tick_length + self.margin_xticklabel)*yhaty
                if self.transform_text:
                  xtick_labels.append(svg.SVG("text", label, transform="matrix(%g, %g, %g, %g, %g, %g)" % (xhatx, xhaty, -yhatx, -yhaty, X, Y)))
                else:
                  vectx, vecty = xhatx + yhatx, xhaty + yhaty
                  angle = math.atan2(vecty, vectx) + math.pi/4.
                  xtick_labels.append(svg.SVG("text", label, transform="matrix(%g, %g, %g, %g, %g, %g)" % (math.cos(angle), math.sin(angle), -math.sin(angle), math.cos(angle), X, Y)))
              else:
                xtick_labels.append(svg.SVG("text", label, transform="translate(%g, %g)" % (X, Y + self.tick_length + self.font_size + self.margin_xticklabel)))

      for x in self.last_xminiticks:
        X, Y = datatrans(x, self.last_xaxis)
        if abs(X - Xcross) > epsilon or abs(Y - Ycross) > epsilon:
          (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(x, self.last_xaxis)
          if xhatx != None and xhaty != None and yhatx != None and yhaty != None:
            xaxis_path.d.append(("M", X - self.minitick_length*yhatx, Y - self.minitick_length*yhaty, True))
            xaxis_path.d.append(("L", X + self.minitick_length*yhatx, Y + self.minitick_length*yhaty, True))

      # create the yticks and the ytick labels
      if self.datatrans == None:
        ytick_labels = svg.SVG("g", stroke="none", fill="black", text_anchor="end", id=("yticklabels%d" % idnum))
      else:
        ytick_labels = svg.SVG("g", stroke="none", fill="black", text_anchor="middle", id=("yticklabels%d" % idnum))

      for y, label in self.last_yticks.items():
        X, Y = datatrans(self.last_yaxis, y)
        if abs(X - Xcross) > epsilon or abs(Y - Ycross) > epsilon:
          (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(self.last_yaxis, y)
          if xhatx != None and xhaty != None and yhatx != None and yhaty != None:
            if not self.draw_arrows or (abs(Y - Ymin) > epsilon and abs(Y - Ymax) > epsilon):
              yaxis_path.d.append(("M", X - self.tick_length*xhatx, Y - self.tick_length*xhaty, True))
              yaxis_path.d.append(("L", X + self.tick_length*xhatx, Y + self.tick_length*xhaty, True))

            if abs(X - Xcross) > self.margin_avoidance or abs(Y - Ycross) > self.margin_avoidance:
              if self.datatrans != None:
                X += (self.tick_length + self.margin_yticklabel)*xhatx
                Y += (self.tick_length + self.margin_yticklabel)*xhaty
                if self.transform_text:
                  ytick_labels.append(svg.SVG("text", label, transform="matrix(%g, %g, %g, %g, %g, %g)" % (-yhatx, -yhaty, -xhatx, -xhaty, X, Y)))
                else:
                  vectx, vecty = xhatx + yhatx, xhaty + yhaty
                  angle = math.atan2(vecty, vectx) + 3.*math.pi/4.
                  ytick_labels.append(svg.SVG("text", label, transform="matrix(%g, %g, %g, %g, %g, %g)" % (math.cos(angle), math.sin(angle), -math.sin(angle), math.cos(angle), X, Y)))
              else:
                ytick_labels.append(svg.SVG("text", label, x=(X - self.tick_length - self.margin_yticklabel), y=(Y + self.font_size*0.35)))

      for y in self.last_yminiticks:
        X, Y = datatrans(self.last_yaxis, y)
        if abs(X - Xcross) > epsilon or abs(Y - Ycross) > epsilon:
          (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(self.last_yaxis, y)
          if xhatx != None and xhaty != None and yhatx != None and yhaty != None:
            yaxis_path.d.append(("M", X - self.minitick_length*xhatx, Y - self.minitick_length*xhaty, True))
            yaxis_path.d.append(("L", X + self.minitick_length*xhatx, Y + self.minitick_length*xhaty, True))

      # actually add the axes and tick labels to the drawing
      output.append(xaxis_path.SVG())
      output.append(xtick_labels)
      output.append(yaxis_path.SVG())
      output.append(ytick_labels)

      if self.draw_arrows:
        leftarrow = svg.SVG("path", d="M 0 0 L 0.5 -1.2 L -3 0 L 0.5 1.2 L 0 0 z", stroke="none", fill="black", id=("leftarrow%d" % idnum))
        toparrow = svg.SVG("path", d="M 0 0 L -1.2 0.5 L 0 -3 L 1.2 0.5 L 0 0 z", stroke="none", fill="black", id=("toparrow%d" % idnum))
        rightarrow = svg.SVG("path", d="M 0 0 L -0.5 -1.2 L 3 0 L -0.5 1.2 L 0 0 z", stroke="none", fill="black", id=("rightarrow%d" % idnum))
        bottomarrow = svg.SVG("path", d="M 0 0 L -1.2 -0.5 L 0 3 L 1.2 -0.5 L 0 0 z", stroke="none", fill="black", id=("bottomarrow%d" % idnum))

        X, Y = datatrans(self.last_xmin, self.last_xaxis)
        (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(self.last_xmin, self.last_xaxis)
        if xhatx != None and xhaty != None:
          leftarrow["transform"] = "matrix(%g, %g, %g, %g, %g, %g)" % (xhatx, xhaty, yhatx, yhaty, X, Y)
        else:
          leftarrow["transform"] = "translate(%g, %g)" % (X, Y)

        X, Y = datatrans(self.last_xmax, self.last_xaxis)
        (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(self.last_xmax, self.last_xaxis)
        if xhatx != None and xhaty != None:
          rightarrow["transform"] = "matrix(%g, %g, %g, %g, %g, %g)" % (xhatx, xhaty, yhatx, yhaty, X, Y)
        else:
          rightarrow["transform"] = "translate(%g, %g)" % (X, Y)

        X, Y = datatrans(self.last_yaxis, self.last_ymin)
        (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(self.last_yaxis, self.last_ymin)
        if xhatx != None and xhaty != None:
          toparrow["transform"] = "matrix(%g, %g, %g, %g, %g, %g)" % (xhatx, xhaty, yhatx, yhaty, X, Y)
        else:
          toparrow["transform"] = "translate(%g, %g)" % (X, Y)

        X, Y = datatrans(self.last_yaxis, self.last_ymax)
        (xhatx, xhaty), (yhatx, yhaty) = datatrans.normderiv(self.last_yaxis, self.last_ymax)
        if xhatx != None and xhaty != None:
          bottomarrow["transform"] = "matrix(%g, %g, %g, %g, %g, %g)" % (xhatx, xhaty, yhatx, yhaty, X, Y)
        else:
          bottomarrow["transform"] = "translate(%g, %g)" % (X, Y)

        output.append(leftarrow)
        output.append(rightarrow)
        output.append(bottomarrow)
        output.append(toparrow)

    return output

  def determine_ranges(self):
    self.last_xmin, self.last_ymin, self.last_xmax, self.last_ymax = self.xmin, self.ymin, self.xmax, self.ymax
    self.outer_xmin, self.outer_ymin, self.outer_xmax, self.outer_ymax = None, None, None, None
    
    xmin, ymin, xmax, ymax = self.last_xmin, self.last_ymin, self.last_xmax, self.last_ymax
    if self.datatrans == None:
      def range_filter(x, y):
        return ((xmin == None or xmin <= x) and \
                (ymin == None or ymin <= y) and \
                (xmax == None or x <= xmax) and \
                (ymax == None or y <= ymax))
    else:
      def range_filter(x, y):
        return ((xmin == None or xmin <= x) and \
                (ymin == None or ymin <= y) and \
                (xmax == None or x <= xmax) and \
                (ymax == None or y <= ymax) and \
                (x, y) in self.datatrans)

    for dp in self.data:
      if not isinstance(dp, Plottable): raise TypeError, "data must be a list of Plottables."
      if self.datatrans == None:
        dp.inner_ranges(range_filter)  # this sets inner_*min, inner_*max
        if dp.inner_xmin != None and (self.last_xmin == None or dp.inner_xmin < self.last_xmin): self.last_xmin = dp.inner_xmin
        if dp.inner_xmax != None and (self.last_xmax == None or dp.inner_xmax > self.last_xmax): self.last_xmax = dp.inner_xmax
        if dp.inner_ymin != None and (self.last_ymin == None or dp.inner_ymin < self.last_ymin): self.last_ymin = dp.inner_ymin
        if dp.inner_ymax != None and (self.last_ymax == None or dp.inner_ymax > self.last_ymax): self.last_ymax = dp.inner_ymax
      else:
        dp.SVG(self.datatrans, range_filter)  # this sets outer_*min, outer_*max
        if dp.inner_xmin != None and (self.last_xmin == None or dp.inner_xmin < self.last_xmin): self.last_xmin = dp.inner_xmin
        if dp.inner_xmax != None and (self.last_xmax == None or dp.inner_xmax > self.last_xmax): self.last_xmax = dp.inner_xmax
        if dp.inner_ymin != None and (self.last_ymin == None or dp.inner_ymin < self.last_ymin): self.last_ymin = dp.inner_ymin
        if dp.inner_ymax != None and (self.last_ymax == None or dp.inner_ymax > self.last_ymax): self.last_ymax = dp.inner_ymax
        if dp.outer_xmin != None and (self.outer_xmin == None or dp.outer_xmin < self.outer_xmin): self.outer_xmin = dp.outer_xmin
        if dp.outer_xmax != None and (self.outer_xmax == None or dp.outer_xmax > self.outer_xmax): self.outer_xmax = dp.outer_xmax
        if dp.outer_ymin != None and (self.outer_ymin == None or dp.outer_ymin < self.outer_ymin): self.outer_ymin = dp.outer_ymin
        if dp.outer_ymax != None and (self.outer_ymax == None or dp.outer_ymax > self.outer_ymax): self.outer_ymax = dp.outer_ymax

    if self.last_xmin == None: self.last_xmin = 0.
    if self.last_ymin == None: self.last_ymin = 0.
    if self.last_xmax == None: self.last_xmax = 0.
    if self.last_ymax == None: self.last_ymax = 0.

    if self.last_xmin == self.last_xmax:
      self.last_xmin -= 1.
      self.last_xmax += 1.
    else:
      width = self.last_xmax - self.last_xmin
      self.last_xmin -= 0.2 * width
      self.last_xmax += 0.2 * width

    if self.last_ymin == self.last_ymax:
      self.last_ymin -= 1.
      self.last_ymax += 1.
    else:
      height = self.last_ymax - self.last_ymin
      self.last_ymin -= 0.2 * height
      self.last_ymax += 0.2 * height

    if self.xmin != None: self.last_xmin = self.xmin
    if self.ymin != None: self.last_ymin = self.ymin
    if self.xmax != None: self.last_xmax = self.xmax
    if self.ymax != None: self.last_ymax = self.ymax

    if self.last_ymin < self.xaxis < self.last_ymax:
      self.last_xaxis = self.xaxis
    elif self.last_ymin < self.xaxis:
      self.last_xaxis = self.last_ymax
    else:
      self.last_xaxis = self.last_ymin

    if self.last_xmin < self.yaxis < self.last_xmax:
      self.last_yaxis = self.yaxis
    elif self.last_xmin < self.yaxis:
      self.last_yaxis = self.last_xmax
    else:
      self.last_yaxis = self.last_xmin

    self.determine_ticks()

    for x, y in map(lambda x: (x, self.last_xaxis), self.last_xticks.keys() + self.last_xminiticks + [self.last_xmin, self.last_xmax]) + \
        map(lambda y: (self.last_yaxis, y), self.last_yticks.keys() + self.last_yminiticks + [self.last_ymin, self.last_ymax]):
      if self.datatrans != None: X, Y = self.datatrans(x, y)
      else: X, Y = x, y

      if X != None:
        if self.outer_xmin == None or X < self.outer_xmin: self.outer_xmin = X
        if self.outer_xmax == None or X > self.outer_xmax: self.outer_xmax = X
      if Y != None:
        if self.outer_ymin == None or Y < self.outer_ymin: self.outer_ymin = Y
        if self.outer_ymax == None or Y > self.outer_ymax: self.outer_ymax = Y

    if self.datatrans == None:
      self.outer_xmin, self.outer_ymin, self.outer_xmax, self.outer_ymax = self.last_xmin, self.last_ymin, self.last_xmax, self.last_ymax

  def determine_ticks(self):
    if self.xticks == None:
      maxchars = int(math.ceil(self.width*20./100.))
      self.last_xticks = ticks(self.last_xmin, self.last_xmax, maxchars=maxchars)
      if self.xminiticks == None:
        self.last_xminiticks = miniticks(self.last_xmin, self.last_xmax, self.last_xticks)
      else:
        self.last_xminiticks = self.xminiticks
    else:
      self.last_xticks = self.xticks
      if self.xminiticks == None:
        self.last_xminiticks = miniticks(self.last_xmin, self.last_xmax, self.last_xticks)
      else:
        self.last_xminiticks = self.xminiticks

    if self.yticks == None:
      maxchars = int(math.ceil(self.height*20./100.))
      self.last_yticks = ticks(self.last_ymin, self.last_ymax, maxchars=maxchars)
      if self.yminiticks == None:
        self.last_yminiticks = miniticks(self.last_ymin, self.last_ymax, self.last_yticks)
      else:
        self.last_yminiticks = self.yminiticks
    else:
      self.last_yticks = self.yticks
      if self.yminiticks == None:
        self.last_yminiticks = miniticks(self.last_ymin, self.last_ymax, self.last_yticks)
      else:
        self.last_yminiticks = self.yminiticks

#####################################################################

#####################################################################

#####################################################################

