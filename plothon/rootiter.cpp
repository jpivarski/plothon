// plothon/rootiter.cpp is a part of Plothon
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

#include "rootiter.h"

static PyMemberDef root_RootIter_members[] = {
   {"index", T_LONG, offsetof(root_RootIter, index), 0, ""},
   {"selection", T_OBJECT, offsetof(root_RootIter, selection), 0, ""},
   {"labels", T_OBJECT, offsetof(root_RootIter, labels), READONLY, ""},
   {"entries", T_LONG, offsetof(root_RootIter, entries), READONLY, ""},
   {"fileName", T_OBJECT, offsetof(root_RootIter, file), READONLY, ""},
   {"path", T_OBJECT, offsetof(root_RootIter, path), READONLY, ""},
   {NULL}
};

static PyTypeObject root_RootIterType = {
   PyObject_HEAD_INIT(NULL)
   0,                         /*ob_size*/
   "plothon.rootiter.Iterator", /*tp_name*/
   sizeof(root_RootIter),     /*tp_basicsize*/
   0,                         /*tp_itemsize*/
   (destructor)root_RootIter_dealloc, /*tp_dealloc*/
   0,                         /*tp_print*/
   0,                         /*tp_getattr*/
   0,                         /*tp_setattr*/
   0,                         /*tp_compare*/
   0,                         /*tp_repr*/
   0,                         /*tp_as_number*/
   0,                         /*tp_as_sequence*/
   0,                         /*tp_as_mapping*/
   0,                         /*tp_hash */
   0,                         /*tp_call*/
   0,                         /*tp_str*/
   0,                         /*tp_getattro*/
   0,                         /*tp_setattro*/
   0,                         /*tp_as_buffer*/
   Py_TPFLAGS_DEFAULT,        /*tp_flags*/
   "An iterator that walks over entries in a ROOT iterator (simple TTree).", /* tp_doc */
   0,		              /* tp_traverse */
   0,		              /* tp_clear */
   0,		              /* tp_richcompare */
   0,		              /* tp_weaklistoffset */
   root_RootIter_iter,        /* tp_iter */
   root_RootIter_next,        /* tp_iternext */
   0,                         /* tp_methods */
   root_RootIter_members,     /* tp_members */
   0,                         /* tp_getset */
   0,                         /* tp_base */
   0,                         /* tp_dict */
   0,                         /* tp_descr_get */
   0,                         /* tp_descr_set */
   0,                         /* tp_dictoffset */
   (initproc)root_RootIter_init, /* tp_init */
   0,                         /* tp_alloc */
   0,                         /* tp_new */
};

static int root_RootIter_init(root_RootIter *self, PyObject *args, PyObject *kwds) {
   char *file;
   char *path;
   static char *kwlist[] = {"fileName", "path", NULL};
   if (!PyArg_ParseTupleAndKeywords(args, kwds, "ss", kwlist, &file, &path)) {
      PyErr_SetString(PyExc_TypeError, "Arguments are: fileName, path to TTree.");
      return -1;
   }

   self->tfile = TFile::Open(file, "READ");
   if (self->tfile == NULL  ||  self->tfile->IsZombie()  ||  !self->tfile->IsOpen()) {
      PyErr_Format(PyExc_IOError, "Could not open file \"%s\".", file);
      return -1;
   }
   
   TObject *obj = self->tfile->Get(path);
   if (obj == NULL  ||  !obj->InheritsFrom("TTree")) {
      PyErr_Format(PyExc_IOError, "Could not get TTree at \"%s\".", path);
      return -1;
   }
   self->ttree = (TTree*)(obj);

   self->file = PyString_FromString(file);
   if (self->file == NULL) {
      return -1;
   }
   self->path = PyString_FromString(path);
   if (self->path == NULL) {
      Py_DECREF(self->file);
      return -1;
   }

   self->labels = root_RootIter_leaves(self);
   self->selection = Py_BuildValue("O", self->labels);
   self->entries = self->ttree->GetEntries();
   self->index = 0;
   self->leaf = new std::vector<TLeaf*>;
   return 0;
}

static PyObject *root_RootIter_dealloc(root_RootIter *self) {
   if (self->file != NULL) Py_DECREF(self->file);
   if (self->path != NULL) Py_DECREF(self->path);
   if (self->selection != NULL) Py_DECREF(self->selection);
   if (self->leaf != NULL) delete self->leaf;
   self->path = NULL;
   self->selection = NULL;
   self->leaf = NULL;
   return NULL;
}

static PyObject *root_RootIter_iter(PyObject *thyself) {
   root_RootIter *self = (root_RootIter*)(thyself);

   self->index = 0;
   self->numleaves = 0;

   const char *errstring = "selection must be a tuple/list of TLeaf names.";

   if (!PyTuple_Check(self->selection)  &&  !PyList_Check(self->selection)) {
      PyErr_SetString(PyExc_TypeError, errstring);
      return NULL;
   }

   self->leaf->clear();
   self->ttree->SetBranchStatus("*", 0);

   for (int i = 0;  i < PySequence_Size(self->selection);  i++) {
      PyObject *item = PySequence_GetItem(self->selection, i);
      if (!PyString_Check(item)) {
	 Py_DECREF(item);
	 PyErr_SetString(PyExc_TypeError, errstring);
	 return NULL;
      }

      std::string str(PyString_AsString(item));
      Py_DECREF(item);

      bool isleaf = false;
      TIterator *iter = self->ttree->GetListOfLeaves()->MakeIterator();
      while (TLeaf *leaf = (TLeaf*)(iter->Next())) {
	 if (std::string(leaf->GetName()) == str) {
	    self->leaf->push_back(leaf);
	    self->ttree->SetBranchStatus(leaf->GetBranch()->GetName(), 1);
	    isleaf = true;
	    break;
	 }
      }

      if (!isleaf) {
	 PyErr_SetString(PyExc_TypeError, errstring);
	 return NULL;
      }
      self->numleaves++;
   }

   return Py_BuildValue("O", thyself);
}

static PyObject *root_RootIter_next(PyObject *thyself) {
   root_RootIter *self = (root_RootIter*)(thyself);

   if (self->index >= self->entries) {
      PyErr_SetNone(PyExc_StopIteration);
      return NULL;
   }

   self->ttree->GetEntry(self->index, 0);

   PyObject *output = PyTuple_New(self->numleaves);
   int i = 0;
   for (std::vector<TLeaf*>::const_iterator leaf = self->leaf->begin();  leaf != self->leaf->end();  ++leaf) {
      PyObject *item;

      int count;
      if ((*leaf)->GetLeafCounter(count) == NULL  &&  count == 1) {
	 item = Py_BuildValue("d", double((*leaf)->GetValue()));
      }
      
      else {
	 int length = (*leaf)->GetLen();
	 item = PyTuple_New(length);
	 if (item == NULL) {
	    Py_DECREF(output);
	    return NULL;
	 }

	 for (int j = 0;  j < length;  j++) {
	    PyObject *val = PyFloat_FromDouble(double((*leaf)->GetValue(j)));
	    if (val == NULL) {
	       Py_DECREF(item);
	       Py_DECREF(output);
	       return NULL;
	    }
	    if (PyTuple_SetItem(item, j, val) != 0) {
	       Py_DECREF(val);
	       Py_DECREF(item);
	       Py_DECREF(output);
	       return NULL;
	    }
	 }
      }

      if (item == NULL) {
	 Py_DECREF(output);
	 return NULL;
      }

      if (PyTuple_SetItem(output, i, item) != 0) {
	 Py_DECREF(item);
	 Py_DECREF(output);
	 return NULL;
      }

      i++;
   }

   self->index++;
   return output;
}

static PyObject *root_RootIter_leaves(root_RootIter *self) {
   PyObject *output = PyList_New(self->ttree->GetListOfLeaves()->GetEntries());
   if (output == NULL) return NULL;

   int i = 0;
   TIterator *iter = self->ttree->GetListOfLeaves()->MakeIterator();
   while (TLeaf *leaf = (TLeaf*)(iter->Next())) {
      PyObject *str = PyString_FromString(leaf->GetName());
      if (str == NULL) {
	 Py_DECREF(output);
	 return NULL;
      }

      if (PyList_SetItem(output, i, str) != 0) {
	 Py_DECREF(str);
	 Py_DECREF(output);
	 return NULL;
      }

      i++;
   }

   return output;
}

PyMODINIT_FUNC initrootiter(void) {
   PyObject *module;

   root_RootIterType.tp_new = PyType_GenericNew;
   if (PyType_Ready(&root_RootIterType) < 0) return;

   module = Py_InitModule3("rootiter", NULL, "ROOTimentary TTree access.");

   Py_INCREF(&root_RootIterType);
   PyModule_AddObject(module, "Iterator", (PyObject*)(&root_RootIterType));
}
