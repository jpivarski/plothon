# plothon/root.py is a part of Plothon
# Copyright (C) 2007 Jim Pivarski <jpivarski@gmail.com>
# see http://root.cern.ch for more information about the ROOT physics analysis package
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

import ROOT, plot, tools

def steps(TH1, anchor=0, **attributes):
  bins = TH1.GetNbinsX()
  edges = []
  values = []
  for i in xrange(bins):
    edges.append(TH1.GetBinLowEdge(i+1))
    values.append(TH1.GetBinContent(i+1))
  edges.append(TH1.GetBinLowEdge(bins+1))
  return plothon.plot.Steps(edges, values, anchor=anchor, **attributes)

def errorbars(TH1, anchor=0, **attributes):
  bins = TH1.GetNbinsX()
  xyyerr = []
  for i in xrange(bins):
    xyyerr.append((TH1.GetBinCenter(i+1), TH1.GetBinContent(i+1), TH1.GetBinError(i+1)))
  return plothon.plot.ErrorBars(xyyerr, **attributes)

class RootNtuple(tools.Ntuple):
  def __init__(self, fileName, path, *args, **kwds):
    import rootiter
    self.iterator = rootiter.Iterator(fileName, path)
    self.labels = self.iterator.labels
    self.selection = self.labels
    self.slice = None
    self.function = eval("lambda %s: (%s)" % (", ".join(self.selection), ", ".join(self.selection)))
    self.permutation = range(len(self.labels))

    if len(args) + len(kwds) > 0:
      self(*args, **kwds)
