============
Installation
============

The following instructions pertain to HOPS version 3.24 running with python 3.10. This procedure has been tested on the Harvard FASRC cluster, and is expected to work on any modern Linux/Unix system. If the software packages required to compile HOPS are installed in standard locations such as /usr/local, some of the following environment variables may not need to be explicitly defined.

.. note::
   Build HOPS with the same Python version to be used by the EHT-HOPS pipeline (e.g. the mamba/conda environment used to run the pipeline).
   One way to ensure this is to set up the mamba/conda environment first (with at least future, numpy, scipy, matplotlib installed), activate it, and then build HOPS.

Setting up a new python environment
-----------------------------------

Download the python 3.10 version of `Mamba <https://mamba.readthedocs.io/en/latest/index.html>`_ or `Miniconda installer <https://docs.conda.io/en/latest/miniconda.html>`_ if you prefer conda.
Create a new environment for the pipeline::

   mamba create -n ehthops310 python=3.10

.. note::
   Note that python 3.8 can run the pipeline but cannot generate the summary notebooks using either nbconvert or papermill. Python 3.10 is recommended.

Activate the newly created mamba/conda environment and install the EHT Analysis Toolkit (EAT) library in developer mode (the repository should be cloned to a location with write permissions)::

   git clone https://github.com/sao-eht/eat.git
   pip install -e eat

Install astropy; this should pull in numpy, among other modules::

   mamba install astropy seaborn numpy pandas matplotlib scipy

Verify that the astropy version is 5.3 or below (downgrade if not). This is necessary for the current codebase to work properly::

   mamba install astropy=5.3

Install modules required for generating summary plots non-interactively and viewing them from within the same mamba environment::

   mamba install ipykernel papermill nbconvert jupyter

**Recommended:** EHT-HOPS performs additional calibration and data format conversion tasks beyond iterative fringe-fitting.
These *post-processing* steps (including the stage that generates UVFITS files from HOPS fringe files) need the **eht-imaging** library.
This is currently achieved by cloning the *dev* branch of **eht-imaging** from GitHub and passing its path to the post-processing scripts.
Always ensure that *eht-imaging* is on the *dev* branch to ensure that you are pulling in the latest updates::

   git clone https://github.com/achael/eht-imaging.git
   cd eht-imaging
   git checkout dev
   pip install .

**Recommended:** Some modules such as *scikit-learn*, *statsmodels*, and *pytables* are required only by the post-processing stages following UVFITS conversion.
Though these stages are not yet part of the main pipeline, they are expected to be integrated in the future. Install these modules now to avoid any issues later::

   mamba install scikit-learn future pytables statsmodels

Potential installation issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The pipeline generates summary notebooks with diagnostic plots in both ipynb and html formats.
If the conversion of jupyter notebooks to HTML fails while running the pipeline, ensure that the following is installed::

   mamba install jupyter_contrib_nbextensions

In older systems, scipy might throw a **glibcxx not found** error. If this occurs, update libstdcxx
to at least version 12. Modern installations should already satisfy this requirement::

   mamba install libstdcxx-ng=12

Installing HOPS v3.24
---------------------

Pre-requisites
^^^^^^^^^^^^^^

On Debian-based systems (including Ubuntu), some or all of the following packages may be necessary
to be able to compile HOPS successfully. Note that the exact names might differ on different systems::

   sudo apt install gcc make gfortran libx11-dev ghostscript libfftw3-dev parallel
   sudo apt install gdb flex bison pkg-config autoconf automake gettext libtool

**FFTW** is a pre-requisite for HOPS that should have been installed in the previous step. If not,
download `FFTW <https://fftw.org/>`_ manually and run the following commands to install it::

   ./configure --prefix=</path/to/install/fftw> --enable-shared --enable-threads --enable-openmp
   make
   make install

**PGPLOT** is a pre-requisite for HOPS. Download `PGPLOT <https://sites.astro.caltech.edu/~tjp/pgplot/>`_ and
follow `these <https://www.gnu.org/software/gnuastro/manual/html_node/PGPLOT.html>`_ instructions to
install it. Note that the switch from **g77** to **gfortran** is necessary on any modern Linux system.

Define the following environment variables before compiling HOPS v3.24 so that PGPLOT and FFTW are
discoverable by HOPS during compilation::

   export PGPLOT_DIR="</path/to/pgplot>"
   export LD_LIBRARY_PATH="</path/to/pgplot>":"</path/to/fftw/lib>":$LD_LIBRARY_PATH
   export LDFLAGS="-L</path/to/fftw/lib>"
   export CFLAGS="-I</path/to/fftw/include>"
   export CPPFLAGS="-I</path/to/fftw/include>"
   export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:"</path/to/fftw/lib/pkgconfig>"
  
On some systems the following flags may also have to be set manually to be able to configure HOPS-3.24::

   export FFTW3_LIBS="</path/to/fftw/lib>"
   export FFTW3_CFLAGS="</path/to/fftw/include>"

Downloading and installing HOPS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
   The public version of HOPS shown below does not contain some astronomy-specific utilities. Some parts of the pipeline (such as the *average* command) may not exist or work as expected.
   Please contact the EHT-HOPS pipeline developers for the customised version of HOPS. These utilities will be made available outside HOPS in a future release.

Download `HOPS <https://www.haystack.mit.edu/haystack-observatory-postprocessing-system-hops/>`_::

   wget -nH https://web.mit.edu/haystack-www/hops/hops-3.24-3753.tar.gz

The -nH argument prevents the entire directory structure on the host from being recreated locally.

Regardless of whether you are using the public version of HOPS or the version provided by the
EHT-HOPS pipeline developers, the following steps are the same.

Untar HOPS version 3.24 and in the same location create a build directory in which to compile HOPS::

   mkdir bld-3.24
   cd bld-3.24
   ../hops-3.24/configure --prefix=</path/to/install/hops-3.24> --enable-devel
   make all
   make install

.. note::
   Do not forget the **\-\-enable-devel** flag! Without it, many necessary HOPS postprocessing executables will not be built.

To set up the HOPS environment, run::

   source </path/to/hops-3.24/bin/hops.bash>

Installing the EHT-HOPS pipeline
--------------------------------

Pre-requisites
^^^^^^^^^^^^^^

Some systems may not have GNU parallel installed by default which is used for parallel scan-by-scan fringe-fitting.
Install it from `source <https://www.gnu.org/software/parallel>`_ and add it to the system path::

   export PATH=$PATH:"/path/to/parallel/bin"

Obtaining the EHT-HOPS pipeline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ensure that the new mamba environment is activated, and activate the HOPS shell environment::

   source /path/to/hops-3.24/bin/hops.bash


Clone the EHT-HOPS pipeline from GitHub. The latest version of the EHT-HOPS repository can be found `here <https://github.com/sao-eht/ehthops>`_.
The calibration metadata and summary plot jupyter notebooks are independent repositories mapped to
submodules within *ehthops*. The metadata repository is `here <https://github.com/sao-eht/ehthops-meta>`_
and the summary notebooks are `here <https://github.com/sao-eht/ehthops-plots>`_. The submodules must be
initialized and updated manually as follows::
   
   git clone https://github.com/sao-eht/ehthops.git
   cd ehthops
   git submodule update --init --remote

The HOPS environment is now set up for running the pipeline.
