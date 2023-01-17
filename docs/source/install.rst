============
Installation
============

The following instructions pertain to installing HOPS version 3.24 and the EHT-HOPS pipeline with python 3.10.
While this procedure has been tested on the Harvard FASRC cluster, it is expected to work on any modern Linux system.
If the software packages required to compile HOPS are installed in standard locations such as **/usr/local**, some of the following environment variables may not need to be defined.

Installing HOPS v3.24
---------------------

Before installing HOPS, PGPLOT and FFTW must be installed. On a new Debian-based system (including Ubuntu),
some or all of the following packages may be necessary to be able to compile HOPS successfully::

   sudo apt install gcc make gfortran libx11-dev ghostscript libfftw3-dev parallel
   sudo apt install gdb flex bison pkg-config autoconf automake gettext libtool

If FFTW3 is installed properly via apt, the following manual installation of FFTW3 may be safely skipped.
Download `PGPLOT <https://sites.astro.caltech.edu/~tjp/pgplot/>`_
from source and follow the instructions 
`here <https://www.gnu.org/software/gnuastro/manual/html_node/PGPLOT.html>`_ to install it.
Note that the switch from g77 to gfortran is necessary for any modern Linux installation. Download `FFTW <https://fftw.org/>`_ from source and run the following commands::

   ./configure --prefix=/path/to/install/fftw --enable-shared --enable-threads --enable-openmp
   make
   make install

Define the following environment variables before compiling HOPS v3.24 so that PGPLOT and FFTW are discovered properly during compilation::

   export PGPLOT_DIR="/path/to/pgplot"
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"/path/to/pgplot":"/path/to/fftw/lib"
   export LDFLAGS="-Lpath/to/fftw/lib"
   export CFLAGS="-I/path/to/fftw/include"
   export CPPFLAGS="-I/path/to/fftw/include"
   export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:"/path/to/fftw/lib/pkgconfig"
  
On some systems the following flags may also have to be set manually to be able to configure HOPS-3.24::

   export FFTW3_LIBS="/path/to/fftw/lib"
   export FFTW3_CFLAGS="/path/to/fftw/include"

Create a build directory in which to compile HOPS (without the **--enable-devel** flag, many HOPS postprocessing executables will not be built)::

   mkdir bld-3.24
   cd bld-3.24
   ../hops-3.24/configure --prefix=/path/to/install/hops-3.24 --enable-devel
   make all
   make install

To set up the HOPS environment, run the following command::

   source /path/to/hops-3.24/bin/hops.bash


Setting up a new python environment
-----------------------------------

Download
`Miniconda installer <https://docs.conda.io/en/latest/miniconda.html>`_ 
for python 3.10 (note that python 3.8 can run the pipeline but cannot generate the summary notebooks using either nbconvert or papermill). Create a new conda environment for the pipeline::

   conda create -n hops310 python=3.10

Activate the newly created conda environment and install the EHT Analysis Toolkit (EAT) in developer mode (the repository should be cloned to a location with write permissions)::

   git clone https://github.com/sao-eht/eat.git
   pip install -e eat

Some modules such as **scikit-learn**, **statsmodels**, and **pytables** are required only for post-processing with eat.

Install astropy; this should pull in **numpy**, among other modules::

   conda install -c conda-forge astropy

Install other required modules as follows (if **seaborn** doesn't pull in **statsmodels**, then **statsmodels** should also be added to the following command)::

   conda install -c conda-forge scipy matplotlib pandas seaborn scikit-learn future pytables

Install modules required for generating summary plots non-interactively::

   conda install -c conda-forge ipykernel papermill nbconvert

It is possible that at stage 1 of the EHT-HOPS pipeline, the eat program **alma_pcal** might throw a *glibcxx not found* error via scipy. If this occurs, update **libstdcxx** version to 12::

   conda install -c conda-forge libstdcxx-ng=12

The post-processing steps also need eht-imaging to be present. Note that, at the moment, a hard-link to the source code is passed to the post-processing script **6.uvfits/bin/2.import**.
To do this, check out the *dev* branch from **eht-imaging** and install locally with **pip**::

   git clone https://github.com/achael/eht-imaging.git
   cd eht-imaging
   git checkout dev
   pip install .

Optionally, to view and re-run the summary notebooks, jupyter must be installed::

   conda install -c conda-forge jupyter

Also, some systems may not have GNU parallel installed by default. If that is the case, install it from source and add it to the system path::

   export PATH=$PATH:"/path/to/parallel/bin"
