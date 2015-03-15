# Downloading #

  * The current version of Plothon is [plothon-0.1.0.tgz](http://plothon.googlecode.com/files/plothon-0.1.0.tgz), also available from the [downloads tab](http://code.google.com/p/plothon/downloads/list).
  * If you need something newer than this, the latest source code is available from the [source tab](http://code.google.com/p/plothon/source).
  * Older versions can be accessed under the [downloads tab](http://code.google.com/p/plothon/downloads/list).

# Installing #

  1. Unpack the tarball archive (plothon-X.Y.Z.tgz) if your browser doesn't do so automatically.  You may be able to unpack the archive by double-clicking on it.
  1. Be sure that [Python](http://www.python.org) in installed, preferably version 2.4 or newer.
  1. If you have access to the Python distribution (you are using Windows or Mac, or have superuser privledges on Unix/Linux), run `setup.py` with the following command.
```
yourprompt> python setup.py install
```
  1. If you want or need to install Plothon in your home directory instead, use the `--home=` argument.
```
yourprompt> python setup.py install --home=~
```

You have successfully installed Plothon if `import plothon` does not return an error.
```
yourprompt> python
Python 2.4.3 (#2, Oct  6 2006, 07:52:30) 
[GCC 4.0.3 (Ubuntu 4.0.3-1ubuntu5)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import plothon
```

# Alternate installations #

## Fitting with MINUIT ##

To fit data or minimize functions, you'll need to install [PyMinuit](http://code.google.com/p/pyminuit/).

_The following is a place-holder: plothon.fit doesn't exist!!!_

When PyMinuit is properly installed, plothon.fit will load without an error.
```
>>> import plothon.fit
```

_That's not true!  The above will say "ImportError: No module named fit"!  That's why this version is called 0.1.0, after all._

## Installing with the ROOT interface ##

If you are a [ROOT](http://root.cern.ch) user and want Plothon to communicate with ROOT, first make sure that you can access the pyROOT interface.
```
>>> import ROOT
```
See the [pyROOT installation documentation](http://root.cern.ch/root/HowtoPyROOT.html) if the above doesn't work.  The problem may be as simple as setting your PYTHONPATH environment variable.

To use Plothon's [root.RootNtuple](rootRootNtuple.md) interface, you'll need to pass another option to the `setup.py` script.
  1. Make sure that the ROOTSYS environment variable is properly set (as described in [ROOT's installation instructions](http://root.cern.ch/root/Install.html)).  Your ROOTSYS is properly set up if `root-config` yields something like the following.
```
yourprompt> $ROOTSYS/bin/root-config --libs --cflags
-L/home/software/physics/root/lib -lCore -lCint -lRIO -lNet -lHist -lGraf -lGraf3d ...
```
  1. Pass the `--with-root` argument to `setup.py` when you install:
```
yourprompt> python setup.py install --with-root               or
yourprompt> python setup.py install --home=~ --with-root
```

To check that it installed correctly, try
```
>>> import plothon.rootiter
```

# Related tools #

## SVG renderers ##

To view your images or convert them to other file formats, you will need an SVG 1.1-compliant viewer.  Here are some suggestions.

### Viewing ###

  * [Mozilla Firefox](http://www.mozilla.org/projects/svg/) browser
  * [Opera](http://www.opera.com/products/desktop/svg/) browser
  * librsvg2 contains `rsvg-view` for simple SVG viewing on Unix/Linux.  Check your package manager (apt, yum, fink, etc).
  * http://www.svgi.org/ maintains a list of SVG viewers

### Editing and file conversion ###

  * [Inkscape](http://www.inkscape.org/) graphical drawing program
  * [Sodipodi](http://www.sodipodi.com/index.php3) graphical drawing program (ancestor of Inkscape?)

### Developer libraries ###

  * [librsvg](http://librsvg.sourceforge.net/)

I developed an interactive SVG viewer that displays images inside Python, but haven't released it because the GTK multithreading doesn't compile properly in distutils and SVG
rendering from in my version of librsvg2-dev (2.14.4-0ubuntu1) is not adequate.  If anyone is interested in correcting these problems and providing an interactive viewer, I can show you my C code and add you as a developer.  (E-mail me at jpivarski@SPAMNOTgmail.com.  Thanks!)

## Python integrated development environment (IDE) ##

I find it _very_ helpful to interact with Python while I develop plotting scripts in a style similar to [Mathematica notebooks](http://www.wolfram.com/technology/guide/notebook.html).  Python, by itself, does not have this functionality, but there are many ways add it.

### Graphical IDEs ###

  * [This Spyced blog entry](http://spyced.blogspot.com/2005/09/review-of-6-python-ides.html) reviews 6 Python IDEs.
    * [PyDev](http://pydev.sourceforge.net/)
    * [Eric3](http://www.die-offenbachs.de/detlev/eric3.html)
    * [Boa Constructor](http://boa-constructor.sourceforge.net/)
    * [BlackAdder](http://www.thekompany.com/products/blackadder/)
    * [Komodo](http://www.activestate.com/Products/Komodo/)
    * [Wing IDE](http://www.wingware.com/)

### Emacs as an IDE ###

If you use the [Emacs text editor](http://www.gnu.org/software/emacs/), [python-mode](http://sourceforge.net/projects/python-mode/) facilitates interaction with Python while developing a Python script.

I have [modified python-mode](http://plothon.googlecode.com/files/python-mode-jimp.el) to make it more interactive for my own use.  While this is not an official version of python-mode, I have not changed it in years of Python interaction, so I would call it stable.  Once installed, open a Python file and M-x describe-mode for details.