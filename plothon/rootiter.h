// plothon/rootiter.h is a part of Plothon
// Copyright (C) 2007 Jim Pivarski <jpivarski@gmail.com>
// see http://root.cern.ch for more information about the ROOT physics analysis package
// 
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
// 
// Full licence is in the file COPYING and at http://www.gnu.org/copyleft/gpl.html

#include <Python.h>
#include <structmember.h>
#include <string>
#include <vector>

#include "TFile.h"
#include "TIterator.h"
#include "TKey.h"
#include "TTree.h"
#include "TLeaf.h"

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

struct root_RootIter {
      PyObject_HEAD
      long index;
      PyObject *selection;
      PyObject *labels;
      PyObject *file;
      PyObject *path;
      long entries;

      TFile *tfile;
      TTree *ttree;
      std::vector<TLeaf*> *leaf;
      int numleaves;
};

static int root_RootIter_init(root_RootIter *self, PyObject *args, PyObject *kwds);
static PyObject *root_RootIter_dealloc(root_RootIter *self);
static PyObject *root_RootIter_next(PyObject *thyself);
static PyObject *root_RootIter_iter(PyObject *thyself);
static PyObject *root_RootIter_leaves(root_RootIter *self);
