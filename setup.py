#!/usr/bin/env python

from distutils.core import setup, Extension
import os, sys, glob, commands

def rootconfig(*packages, **kw):
  flag_map = {"-I": "include_dirs", "-L": "library_dirs", "-l": "libraries"}
  for token in commands.getoutput("%s/bin/root-config --libs --cflags %s" % (os.getenv("ROOTSYS"), " ".join(packages))).split():
    if token[:2] in flag_map:
      kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
    else:
      kw.setdefault("extra_compile_args", []).append(token)
  for k, v in kw.iteritems(): # remove duplicates
    kw[k] = list(set(v))
  return kw
  
##################################################################################################

ext_modules = []

# ROOT iterator module allows C++ access to TTree ntuples
if "--with-root" in sys.argv:
  ext_modules.append(Extension(os.path.join("plothon", "rootiter"), [os.path.join("plothon", "rootiter.cpp")], **rootconfig()))
  for i, arg in enumerate(sys.argv):
    if arg == "--with-root": break
  del sys.argv[i]

##################################################################################################

setup(name="Plothon",
      version="0.1.2",
      description="Plothon: Data Analysis and Mathematical PLOTting in pyTHON",
      author="Jim Pivarski",
      author_email="jpivarski@gmail.com",
      url="http://code.google.com/p/plothon/",
      package_dir={"plothon": "lib"},
      py_modules=[os.path.join("plothon", "__init__"),
                  os.path.join("plothon", "plot"),
                  os.path.join("plothon", "root"),
                  os.path.join("plothon", "setup"),
                  os.path.join("plothon", "svg"),
                  os.path.join("plothon", "tools"),
                  ],
      ext_modules=ext_modules,
     )
