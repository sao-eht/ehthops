============
Installation
============

The following instructions pertain to installing HOPS version 3.24 and the EHT-HOPS pipeline with python 3.10. While this procedure has been tested on the Harvard FASRC cluster, it is expected to work on any modern Linux system. If the software packages required to compile HOPS are installed in standard locations such as /usr/local, some of the following environment variables may not need to be defined.

Installing HOPS v3.24
---------------------

.. note::
   Build HOPS with the same Python version to be used by the EHT-HOPS pipeline (e.g. the mamba/conda environment used to run the pipeline).
   One way to ensure this is to set up the mamba/conda environment first (with at least future, numpy, scipy, matplotlib pre-installed), activate it, and then build HOPS.

Before installing HOPS, PGPLOT and FFTW must be installed. On a new Debian-based system (including Ubuntu), some or all of the following packages may be 
necessary to be able to compile HOPS successfully. Note that the exact names might differ on different systems::

   sudo apt install gcc make gfortran libx11-dev ghostscript libfftw3-dev parallel
   sudo apt install gdb flex bison pkg-config autoconf automake gettext libtool

If FFTW3 is installed properly via apt, the following manual installation of FFTW3 may be safely skipped.
Download `PGPLOT <https://sites.astro.caltech.edu/~tjp/pgplot/>`_
and follow the `instructions <https://www.gnu.org/software/gnuastro/manual/html_node/PGPLOT.html>`_ to install it.
Note that the switch from g77 to gfortran is necessary for any modern GNU/Linux system.
Download `FFTW <https://fftw.org/>`_ and run the following commands::

   ./configure --prefix=</path/to/install/fftw> --enable-shared --enable-threads --enable-openmp
   make
   make install

Define the following environment variables before compiling HOPS v3.24 so that PGPLOT and FFTW are discoverable during compilation::

   export PGPLOT_DIR="</path/to/pgplot>"
   export LD_LIBRARY_PATH="</path/to/pgplot>":"</path/to/fftw/lib>":$LD_LIBRARY_PATH
   export LDFLAGS="-L</path/to/fftw/lib>"
   export CFLAGS="-I</path/to/fftw/include>"
   export CPPFLAGS="-I</path/to/fftw/include>"
   export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:"</path/to/fftw/lib/pkgconfig>"
  
On some systems the following flags may also have to be set manually to be able to configure HOPS-3.24::

   export FFTW3_LIBS="</path/to/fftw/lib>"
   export FFTW3_CFLAGS="</path/to/fftw/include>"

Download `HOPS <https://www.haystack.mit.edu/haystack-observatory-postprocessing-system-hops/>`_ via anonymous ftp::

   wget -r ftp://gemini.haystack.mit.edu/pub/hops

The above command checks out all past versions of HOPS under *gemini.haystack.mit.edu/pub/hops*.
Untar the latest version of HOPS (as on June 2023, version 3.24). At the same location where hops-3.24 is untarred, create a build directory in which to compile HOPS::

   mkdir bld-3.24
   cd bld-3.24
   ../hops-3.24/configure --prefix=</path/to/install/hops-3.24> --enable-devel
   make all
   make install

.. note::
   Without the **--enable-devel** flag, many necessary HOPS postprocessing executables will not be built.

To set up the HOPS environment, run the following command::

   source </path/to/hops-3.24/bin/hops.bash>


Setting up a new python environment
-----------------------------------

Download `Miniconda installer <https://docs.conda.io/en/latest/miniconda.html>`_ for python 3.10 or `Mamba <https://mamba.readthedocs.io/en/latest/index.html>`_::

   conda create -n eht310 python=3.10

.. note::
   Note that python 3.8 can run the pipeline but cannot generate the summary notebooks using either nbconvert or papermill. Python 3.10 is recommended.

Activate the newly created conda environment and install the EHT Analysis Toolkit (EAT) in developer mode (the repository should be cloned to a location with write permissions)::

   git clone https://github.com/sao-eht/eat.git
   pip install -e eat

Install astropy; this should pull in numpy, among other modules::

   conda install -c conda-forge astropy

Install other required modules as follows (if seaborn doesn't pull in statsmodels, then statsmodels should also be added to the following command)::

   conda install -c conda-forge scipy matplotlib pandas seaborn scikit-learn future pytables

Verify that the numpy version is <=1.23 (downgrade if not). This is necessary for eht-imaging to work properly::

   conda install -c conda-forge numpy=1.23

Install modules required for generating summary plots non-interactively::

   conda install -c conda-forge ipykernel papermill nbconvert

It is possible that at stage 1 of the EHT-HOPS pipeline, the eat program alma_pcal might throw a 'glibcxx not found' error via scipy. If this occurs, update libstdcxx version to 12::

   conda install -c conda-forge libstdcxx-ng=12

The post-processing steps also need eht-imaging installed. Note that, at the moment, a hard-link to the source code is passed to the post-processing script 6.uvfits/bin/2.import.
To do this, check out the dev branch fromeht-imaging and install locally with pip::

   git clone https://github.com/achael/eht-imaging.git
   cd eht-imaging
   git checkout dev
   pip install .

Optionally, to view and re-run the summary notebooks interactively, jupyter must be installed::

   conda install -c conda-forge jupyter

The pipeline generates summary notebooks with diagnostic plots in both ipynb and html formats. To prevent the (possible) failure of html file creation from notebooks,
ensure that the following is installed::

   conda install -c conda-forge jupyter_contrib_nbextensions

Check out the `EHT-HOPS <https://github.com/eventhorizontelescope/ehthops>`_ pipeline.
