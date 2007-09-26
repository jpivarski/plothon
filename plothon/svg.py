# plothon/svg.py is a part of Plothon.
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

import random, sys, os, codecs, re, itertools

tmpFile = "tmp.svg"

class SVG:
  """An SVG object represents an element of an SVG drawing.  Arguments:

    SVG(name, child, child, ..., attribute=value, attribute=value, ...)

The first element is the name of the SVG element, the remaining
non-keyword arguments are children, and the keyword arguments are
attributes.  Here's an example:

    SVG(\"g\", SVG(\"rect\", x=\"1cm\", y=\"1cm\", width=\"1cm\", height=\"1cm\"), \ 
             SVG(\"rect\", x=\"3cm\", y=\"1cm\", width=\"1cm\", height=\"1cm\"), \ 
        id=\"group2\", fill=\"blue\")

corresponds to

    <g id=\"group2\" fill=\"blue\" >
        <rect x=\"1cm\" y=\"3cm\" width=\"1cm\" height=\"1cm\" />
        <rect x=\"3cm\" y=\"3cm\" width=\"1cm\" height=\"1cm\" />
    </g>

After creating an SVG object, you can modify the elements by changing
the \"name\" (string), \"children\" (list), and \"attributes\" (dictionary) members.

SVG has many attribute names containing hyphens (\"-\") and colons
(\":\"), which would be misinterpreted in Python.  Therefore, one
underscore (\"_\") will be mapped to a hyphen and two underscores will
be mapped to a colon.

    >>> s = SVG(\"g\", clip_path=\"url(\#clippath)\", xlink__href=\"#reference\")
    >>> s.attributes
    {'clip-path': 'url(\#clippath)', \"xlink:href\": \"#reference\"}

Once they're in dictionaries, they're quoted, so hyphens and colons
will be used as normal.

TODO: Is it a problem that the order of the attributes is not
preserved in Python?

Convenience indexing: the following are equivalent

    s[5]                      s.children[5]
    s[slice(0, 100, 2)]       s.children[0:100:2]
    s[\"fill\"]               s.attributes[\"fill\"]
    s[5,0,0,3,\"fill\"]       s[5][0][0][3][\"fill\"]

for an SVG instance named s.  __getitem__, __setitem__ and
__delitem__ have been overloaded this way.

Also note that

    x in svg

will recursively search for x in an SVG tree.  Use

    x in svg.children

for the non-recursive version."""

  def __init__(self, *args, **kwds):
    "See class documentation."

    if len(args) == 0: raise TypeError, "SVG element must have a name."
    self.name = args[0]
    self.children = []
    self.attributes = {}
    for i in args[1:]:
      if isinstance(i, dict):
        self.attributes.update(i)
      else:
        self.children.append(i)

    for key_underscore in kwds.keys():
      key_colon = re.sub("__", ":", key_underscore)
      if key_colon != key_underscore:
        kwds[key_colon] = kwds[key_underscore]
        del kwds[key_underscore]
        key_underscore = key_colon

      key_dash = re.sub("_", "-", key_underscore)
      if key_dash != key_underscore:
        kwds[key_dash] = kwds[key_underscore]
        del kwds[key_underscore]

    self.attributes.update(kwds)

  def __getitem__(self, i):
    "Convenience indexing: see class documentation."
    which = self
    if isinstance(i, (list, tuple)):
      for index in i[:-1]:
        which = which[index]
      i = i[-1]

    if isinstance(i, (int, long, slice)): return which.children[i]
    else: return which.attributes[i]

  def __setitem__(self, i, value):
    "Convenience indexing: see class documentation."
    which = self
    if isinstance(i, (list, tuple)):
      for index in i[:-1]:
        which = which[index]
      i = i[-1]

    if isinstance(i, (int, long, slice)): which.children[i] = value
    else: which.attributes[i] = value

  def __delitem__(self, i):
    "Convenience indexing: see class documentation."
    which = self
    if isinstance(i, (list, tuple)):
      for index in i[:-1]:
        which = which[index]
      i = i[-1]

    if isinstance(i, (int, long, slice)): del which.children[i]
    else: del which.attributes[i]

  def __iter__(self):
    return self.depth_first()

  def depth_first(self, depth_limit=None):
    "Return a depth-first iterator over the SVG tree."
    return SVGIteratorDepth(self, (), depth_limit)

  def breadth_first(self, depth_limit=None):
    "Return a breadth-first list of the SVG tree."
    values = list(self.depth_first(depth_limit))
    output = filter(lambda (i, s): not isinstance(i, tuple), values)
    length = 2
    while True:
      extension = filter(lambda (i, s): isinstance(i, tuple) and len(i) == length, values)
      if len(extension) == 0: break
      length += 1
      output.extend(extension)
    return output

  def __contains__(self, value):
    return value in self.attributes

  def __eq__(self, other):
    "Value-based, rather than reference-based, equality."
    if id(self) == id(other): return True
    return isinstance(other, SVG) and self.name == other.name and self.children == other.children and self.attributes == other.attributes
  def __ne__(self, other):
    "Value-based, rather than reference-based, inequality."
    return not (self == other)

  def append(self, x):
    self.children.append(x)

  def prepend(self, x):
    self.children[0:0] = [x]
    
  def __repr__(self):
    return "<svg.SVG %s %s (%d children)>" % (self.name, self.attributes, len(self.children))

  def __str__(self): return self.svg()
  
  def svg(self, depth_limit=None, indent=0):
    """Turn the SVG tree into (potentially) human-readable XML.  Arguments:

    depth_limit    number of levels to recurse: None (default) for all
                   levels, 0 for only the current level
                   Unprinted levels are replaced by \"...\"
    indent         number of spaces to print on the left margin--- used internally.

Note that __str__ has been overloaded, such that

    print s

prints the output of this function.

For faster, more complete svg (suitable for drawing), use the full_svg member function."""

    attrstr = []
    for k, v in self.attributes.items(): attrstr.append(" %s=\"%s\"" % (k, v))
    attrstr = "".join(attrstr)

    if len(self.children) == 0: return "%s<%s%s />" % (" "*indent, self.name, attrstr)

    if depth_limit == None or depth_limit > 0:
      indent_spaces = " "*(indent+4)
      if depth_limit != None: depth_limit -= 1

      childstr = []
      for m in self.children:
        if isinstance(m, SVG): childstr.append(m.svg(depth_limit, indent+4) + "\n")
        elif isinstance(m, str): childstr.append(indent_spaces + m + "\n")
        elif isinstance(m, unicode): childstr.append(indent_spaces + m + "\n")
        else: raise ValueError, "SVG objects must contain only text and SVG objects."
      childstr = "".join(childstr)

    else:
      childstr = "%s...\n" % (" " * (indent+4))

    return "%s<%s%s>\n%s%s</%s>" % (" "*indent, self.name, attrstr, childstr, " "*indent, self.name)

  def save(self, fileName=None, overwrite=False, encoding="utf-8"):
    """Save the tree as an SVG file (calls the full_svg member function).  Arguments:

    fileName                   output fileName, a string
    overwrite                  if False (default), throw an exception rather than overwite an existing file
    encoding                   encoding string, \"utf-8\" by default

This can be called on any SVG element--- it will automatically create the
top-level \"svg\" element."""
    if fileName == None:
      fileName = tmpFile
      overwrite = True

    if not overwrite:
      try:
        os.stat(fileName)
        raise IOError, "File '%s' exists: pass overwrite=True to overwrite it." % fileName
      except OSError: pass
      
    f = codecs.open(fileName, "w", encoding=encoding)
    f.write(self.full_svg())
    f.close()

#   def view(self):
#     """Show the SVG drawing in an interactive window (using the svg.viewer package).
# 
# This can be called on any SVG element--- it will automatically create the
# top-level <svg> if necessary."""
#     import viewer
#     viewer.str(self.full_svg())

  def full_svg(self):
    """Quickly turn the SVG tree into real, plottable XML.

This can be called on any SVG element--- it will automatically create the
top-level <svg> if necessary.

Mostly intended for internal use, calling this directly is sometimes helpful
for diagnostics.

For more easily readable svg, use the svg member function."""

    if self.name == "svg": top = self
    else: top = canvas(self)

    return "<?xml version=\"1.0\" standalone=\"no\"?>\n<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n\n"+("".join(top.__svg_sub()))

  def __svg_sub(self):
    "Internal function."
    output = ["<%s" % self.name]

    for k, v in self.attributes.items(): output.append(" %s=\"%s\"" % (k, v))

    if len(self.children) == 0:
      output.append(" />\n\n")
      return output
    elif self.name == "text" or self.name == "tspan" or self.name == "style":
      output.append(">")
    else:
      output.append(">\n\n")

    for m in self.children:
      if isinstance(m, SVG): output.extend(m.__svg_sub())
      elif isinstance(m, str): output.append(str(m))
      elif isinstance(m, unicode): output.append(unicode(m))
      else: raise ValueError, "SVG objects must contain only text and SVG objects."

    if self.name == "tspan":
      output.append("</%s>" % self.name)
    else:
      output.append("</%s>\n\n" % self.name)
    return output

#####################################################################

class SVGIteratorDepth:
  "Internal class."

  def __init__(self, svg, index, depth_limit):
    self.svg = svg
    self.index = index
    self.shown = False
    self.depth_limit = depth_limit

  def __iter__(self): return self

  def next(self):
    if not self.shown:
      self.shown = True
      if self.index == ():
        return (None,), self.svg
      else:
        return self.index, self.svg

    if not isinstance(self.svg, SVG): raise StopIteration
    if self.depth_limit != None and len(self.index) >= self.depth_limit: raise StopIteration

    if "iterators" not in self.__dict__:
      self.iterators = []
      for i, s in enumerate(self.svg.children):
        self.iterators.append(SVGIteratorDepth(s, self.index + (i,), self.depth_limit))
      for k, s in self.svg.attributes.items():
        self.iterators.append(SVGIteratorDepth(s, self.index + (k,), self.depth_limit))
      self.iterators = itertools.chain(*self.iterators)

    return self.iterators.next()

#####################################################################

def run(program, *args):
  os.spawnvp(os.P_NOWAIT, program, (program,) + args)

#####################################################################

def load(fileName=None):
  if fileName == None: fileName = tmpFile
  return load_stream(file(fileName))

def load_stream(stream):
  """Loads an SVG drawing from a stream into an SVG tree.  Arguments:

    stream         a stream object: can be a file, a string, sys.stdin...

To read an SVG file from disk, call

    s = load(file(\"some.svg\"))"""

  from xml.sax import saxutils, make_parser
  from xml.sax.handler import feature_namespaces, feature_external_ges, feature_external_pes

  class ContentHandler(saxutils.DefaultHandler):
    def __init__(self):
      self.stack = []
      self.output = None
      self.all_whitespace = re.compile("^\s*$")

    def startElement(self, name, attributes):
      s = SVG(name)
      s.attributes = dict(attributes.items())
      if len(self.stack) > 0:
        last = self.stack[-1]
        last.children.append(s)
      self.stack.append(s)

    def characters(self, ch):
      if not isinstance(ch, (str, unicode)) or self.all_whitespace.match(ch) == None:
        if len(self.stack) > 0:
          last = self.stack[-1]
          if len(last.children) > 0 and isinstance(last.children[-1], (str, unicode)):
            last.children[-1] = last.children[-1] + "\n" + ch
          else:
            last.children.append(ch)

    def endElement(self, name):
      if len(self.stack) > 0:
        last = self.stack[-1]
        if isinstance(last, SVG) and last.name == "style" and "type" in last.attributes and last.attributes["type"] == "text/css" and len(last.children) == 1 and isinstance(last.children[0], (str, unicode)):
          last.children[0] = "<![CDATA[\n" + last.children[0] + "]]>"

      self.output = self.stack.pop()

  ch = ContentHandler()
  parser = make_parser()
  parser.setContentHandler(ch)
  parser.setFeature(feature_namespaces, 0)
  parser.setFeature(feature_external_ges, 0)
  parser.parse(stream)
  return ch.output

#####################################################################

def canvas(svg=None, **attributes):
  atts = {"width": "400px", "height": "400px", "viewBox": "0 0 100 100", \
          "xmlns": "http://www.w3.org/2000/svg", "xmlns:xlink": "http://www.w3.org/1999/xlink", "version":"1.1", \
          "style": "stroke:black; fill:none; stroke-width:0.25pt; stroke-linejoin:round; font-size:5; text-anchor:middle", \
          "font-family": "Helvetica,Arial,FreeSans,Sans,sans,sans-serif", \
          }
  atts.update(attributes)

  if svg == None:
    return SVG("svg", **atts)
  else:
    return SVG("svg", svg, **atts)

#####################################################################

def template(fileName, svg, replaceme="REPLACEME"):
  output = load(fileName)
  for i, s in output:
    if isinstance(s, SVG) and s.name == replaceme:
      output[i] = svg
  return output
