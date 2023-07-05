============
Installation
============

The following instructions pertain to installing HOPS version 3.24 and the EHT-HOPS pipeline with python 3.10.
This procedure has been tested on CentOS, Rocky OS, and Debian systems.
If the software packages required to compile HOPS are installed in standard locations such as **/usr/local**, some of the following environment variables may not need to be defined.

Installing HOPS v3.24
---------------------

.. note::
   Build HOPS with the same Python version to be used by the EHT-HOPS pipeline (e.g. the mamba/conda environment used to run the pipeline).
   One way to ensure this is to set up the mamba/conda environment first (with at least future, numpy, scipy, matplotlib pre-installed), activate it, and then build HOPS.

Before installing HOPS, PGPLOT and FFTW must be installed. Some or all of the following packages may be necessary to be able to compile HOPS successfully.
Note that the exact names might differ on different systems::

   sudo apt install gcc make gfortran libx11-dev ghostscript libfftw3-dev parallel
   sudo apt install gdb flex bison pkg-config autoconf automake gettext libtool

If FFTW3 is installed properly via apt, the following manual installation of FFTW3 may be safely skipped.
Download `PGPLOT <https://sites.astro.caltech.edu/~tjp/pgplot/>`_
and follow the instructions 
`here <https://www.gnu.org/software/gnuastro/manual/html_node/PGPLOT.html>`_ to install it.
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

We will use `Mamba <https://mamba.readthedocs.io/en/latest/index.html>`_ for creating Conda environments for running the pipeline. We will use python version 3.10 for the setup::

   conda create -n eht310 python=3.10

.. note::
   Note that python 3.8 can run the pipeline but cannot generate the summary notebooks using either nbconvert or papermill. Python 3.10 is recommended.

Install the following packages within the new environment::

   conda install -c conda-forge astropy scipy matplotlib pandas seaborn scikit-learn future pytables ipykernel papermill nbconvert jupyter

.. note::
   If **seaborn** doesn't pull in **statsmodels**, then **statsmodels** should also be added to the above command.

.. note::
   Verify that numpy version is <=1.23. If not, downgrade it to 1.23 via conda. This is necessary because some ehtim functionality do not work properly with >=1.24.

Install the EHT Analysis Toolkit (EAT) in developer mode::

   git clone https://github.com/sao-eht/eat.git
   pip install -e eat

eht-imaging is needed for post-processing. Check out the *dev* branch of **eht-imaging** and install locally with **pip**::

   git clone https://github.com/achael/eht-imaging.git
   cd eht-imaging
   git checkout dev
   pip install .

.. note::
   Verify that libstdcxx-ng version is >=12. This is necessary to avoid potential *glibcxx not found* errors during execution.

Some systems may not have GNU parallel installed by default. If this is the case, install parallel from `source <https://www.gnu.org/software/parallel/>`_ and add it to the system path::

   export PATH=$PATH:"/path/to/parallel/bin"
