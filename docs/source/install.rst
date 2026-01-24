============
Installation
============

The following instructions pertain to HOPS version 3.24 running with python 3.10. This procedure has been tested on the Harvard FASRC cluster, and is expected to work on any modern Linux/Unix system. If the software packages required to compile HOPS are installed in standard locations such as /usr/local, some of the following environment variables may not need to be explicitly defined.

.. note::
   Build HOPS with the same Python version to be used by the EHT-HOPS pipeline (e.g. the mamba/conda environment used to run the pipeline).
   One way to ensure this is to set up the mamba/conda environment first (with at least future, numpy, scipy, matplotlib installed), activate it, and then build HOPS.

Setting up a new python environment
-----------------------------------

Install `Mamba <https://mamba.readthedocs.io/en/latest/index.html>`_ or `micromamba <https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html>`_.
In the following we will use micromamba::

   micromamba create -n ehthops310 python=3.10

.. note::
   Note that python 3.8 can run the pipeline but cannot generate the summary notebooks using either nbconvert or papermill. Python 3.10 is recommended.

Activate the newly created mamba/conda environment::

   micromamba activate ehthops310

Install the EHT Analysis Toolkit (EAT) library in developer mode (the repository should be cloned to a location with write permissions)::

   git clone https://github.com/sao-eht/eat.git
   pip install -e eat

Install necessary modules::

   micromamba install astropy seaborn numpy pandas matplotlib scipy h5py

Install modules required for generating summary plots non-interactively and viewing them from within the same mamba environment::

   mircomamba install ipykernel papermill nbconvert jupyter adjusttext

Install paramsurvey using pip within the mamba environment (necessary for importing eht-imaging)::

   pip install paramsurvey

EHT-HOPS performs additional calibration and data format conversion tasks beyond iterative fringe-fitting.
These *post-processing* steps (including the stage that generates UVFITS files from HOPS fringe files) need the **eht-imaging** library.
This is currently achieved by cloning the *dev* branch of **eht-imaging** from GitHub and passing its path to the post-processing scripts.
Always ensure that *eht-imaging* is on the *dev* branch to ensure that you are pulling in the latest updates::

   git clone https://github.com/achael/eht-imaging.git
   cd eht-imaging
   git checkout dev

After this, set your PYTHONPATH to include the *eht-imaging* directory::

   export PYTHONPATH=$PYTHONPATH:"/path/to/eht-imaging"

**Recommended:** eht-imaging uses **pynfft** for performing some tasks, although these are not necessary for running the calibration pipeline.
For completion, **pynfft** can be installed using mamba::

   micromamba install pynfft

Note that this installs both **nfft** and **pynfft** in the mamba environment and will *downgrade* **numpy** to version 1.26.

**Recommended:** Some modules such as *scikit-learn*, *statsmodels*, and *pytables* are required only by the post-processing stages following UVFITS conversion.
Though these stages are not yet part of the main pipeline, they are expected to be integrated in the future. Install these modules now to avoid any issues later::

   micromamba install scikit-learn future pytables statsmodels

Potential installation issues:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The pipeline generates summary notebooks with diagnostic plots in both ipynb and html formats.
If the conversion of jupyter notebooks to HTML fails while running the pipeline, ensure that the following package is installed::

   micromamba install jupyter_contrib_nbextensions

In some older Linux systems, scipy might throw a **glibcxx not found** error. If this occurs, update **libstdcxx**
to at least version 12. Modern installations should already satisfy this requirement::

   micromamba install libstdcxx-ng=12

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

**NOTE:** If FFTW has been installed in a non-standard path, the following environment variables may be necessary. Try this only if HOPS complains
that FFTW3 is missing::

   export FFTW3_LIBS="-L</path/to/fftw/lib>"
   export FFTW3_CFLAGS="-I</path/to/fftw/include>"



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

The HOPS developers recommend building HOPS in a separate directory from the source code (this is separate from the install directory for HOPS).
Untar HOPS version 3.24 (or 3.26) to */path/to/parentdir* and in *parentdir* create a build directory in which to compile HOPS.
The install location for HOPS binaries is specified using the **--prefix** option passed to configure::

   tar -xvzf hops-3.24-3753.tar.gz
   mkdir bld-3.24 # same level as hops-3.24
   cd bld-3.24
   ../hops-3.24/configure --prefix=</path/to/install/hops-3.24> --enable-devel
   make all
   make install

.. note::
   Do not forget the **\-\-enable-devel** flag above! Without it, some necessary HOPS utilities will not be built.

To set up the HOPS environment, run::

   source </path/to/hops-3.24/bin/hops.bash>

Installing the EHT-HOPS pipeline
--------------------------------

Pre-requisites
^^^^^^^^^^^^^^

Some systems may not have GNU parallel installed by default which is used for parallel scan-by-scan fringe-fitting.
Install it from `source <https://www.gnu.org/software/parallel>`_ and add it to the system path::

   export PATH=$PATH:"/path/to/parallel/bin"

Ensure that the new mamba environment is activated, and activate the HOPS shell environment::

   source /path/to/hops-3.24/bin/hops.bash

The HOPS environment is now set up for running the pipeline. If everything above has been done correctly, all the HOPS executables (e.g. hops*, fourfit, aedit,
CorAsc2, etc.) and the EAT executables in **eat/bin** in the source code should be available in the shell environment.

Obtaining the EHT-HOPS pipeline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clone the EHT-HOPS pipeline from GitHub. The latest version of the EHT-HOPS repository can be found `here <https://github.com/sao-eht/ehthops>`_::
   
   git clone https://github.com/sao-eht/ehthops.git

.. note::
   Until version 0.5.0, the EHT-HOPS pipeline used submodules to store and track metadata and summary notebooks. This is no longer the case,
   with these files now being stored directly in the main repository. Some metadata required for post-processing (such as a
   directory containing *antab* files) must be manually copied to the metadata directory, $METADIR, since the pipeline does not 
   automatically download them, but will expect them for performing apriori amplitude calibration. See also :ref:`Metadata organization <metadata-organization>`.

Additional documentation on HOPS can be found at `MIT Haystack website <https://www.haystack.mit.edu/haystack-observatory-postprocessing-system-hops/>`_.
