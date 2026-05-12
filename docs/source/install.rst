================================================
Installing the EHT-HOPS pipeline
================================================

This page describes how to prepare the *meta environment* required to run the EHT-HOPS pipeline under SLURM.
This environment consists of:

1. A ``HOPS`` installation [version 3.26],
2. A Python virtual environment shipped alongside ``ehthops`` (+ local copies of ``EAT`` and ``eht-imaging``).

HOPS (one-time setup)
--------------------------------

Pre-requisites
^^^^^^^^^^^^^^

1. On Ubuntu/Debian, install the required build tools and libraries with:

.. code-block:: bash

   sudo apt update
   sudo apt install gcc make gfortran libx11-dev ghostscript libfftw3-dev parallel
   sudo apt install gdb flex bison pkg-config autoconf automake gettext libtool

On a shared HPC system, you may not have ``sudo`` access and the system may not
use ``apt``. In that case, first check whether the required tools are already
available (note that the command-line invocation of ``ghostscript`` is ``gs``):

.. code-block:: bash

   for cmd in gcc make gfortran gs parallel gdb flex bison pkg-config autoconf automake gettext libtoolize; do
       if command -v "$cmd" >/dev/null 2>&1; then
           printf "OK      %-12s %s\n" "$cmd" "$(command -v "$cmd")"
       else
           printf "MISSING %-12s\n" "$cmd"
       fi
   done

   if pkg-config --exists fftw3; then
       echo "OK      fftw3       $(pkg-config --modversion fftw3)"
   else
       echo "MISSING fftw3 or pkg-config cannot find fftw3"
   fi

For any missing dependency, check if it is available as an environment module. For instance:

.. code-block:: bash

   module avail gcc
   module avail fftw
   module avail ghostscript
   module avail parallel

If they are, load them with ``module load`` and ensure that the environment variables they set are
properly exported in the shell. For instance, if ``fftw`` is available as a module, loading it with

.. code-block:: bash

   module load fftw

should set the necessary environment variables for HOPS to find it during compilation.

.. note::
   At this point, if you are still missing dependencies, ask the system administrators to install
   the equivalent packages or provide them through the module system. Instructions for a custom 
   ``FFTW3`` installation are provided below.

2. **If** ``FFTW3`` **is still missing**, install it manually `from the official page
<https://fftw.org/>`_. Since a custom installation will not place ``FFTW3`` in a standard location,
HOPS might complain that ``FFTW3`` is missing. To prevent this, ensure that the following environment
variables are set:

.. code-block:: bash

   export FFTW3_LIBS="-L</path/to/fftw/lib> -lfftw3"
   export FFTW3_CFLAGS="-I</path/to/fftw/include>"

3. Download `PGPLOT <https://sites.astro.caltech.edu/~tjp/pgplot/>`_ and follow
`these instructions <https://www.gnu.org/software/gnuastro/manual/html_node/PGPLOT.html>`_
to install it. Note that the recommended switch from ``g77`` to ``gfortran`` is necessary
on any modern Linux system.

4. Define the following environment variables before compiling HOPS so that ``PGPLOT`` and ``FFTW`` are
discoverable by HOPS during compilation:

.. code-block:: bash

   export PGPLOT_DIR="</path/to/pgplot>"
   export LD_LIBRARY_PATH="</path/to/pgplot>":"</path/to/fftw/lib>":$LD_LIBRARY_PATH
   export LDFLAGS="-L</path/to/fftw/lib>"
   export CFLAGS="-I</path/to/fftw/include>"
   export CPPFLAGS="-I</path/to/fftw/include>"
   export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:"</path/to/fftw/lib/pkgconfig>"

Downloading and installing HOPS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The public release of HOPS does not contain some astronomy-specific utilities. Some parts of the pipeline
(such as the ``average`` command) may not exist or work as expected. The utilities missing from public
HOPS releases will be ported to ``eat`` in a future release, until which time ``ehthops`` relies on a
custom version of HOPS 3.26 with the necessary utilities included.

.. warning::
   **Please contact the EHT-HOPS pipeline developers** to obtain the correct version of HOPS
   compatible with ``ehthops``.

The developers of HOPS recommend building the software in an isolated ``build`` directory and installing it in
a separate location specified using ``configure --prefix``. Assuming that we are unpacking the custom
HOPS 3.26 version obtained from the developers to ``/home/user/software/src`` and installing it under
``/home/user/software/installed/hops-3.26``, the installation steps would be as follows:

.. code-block:: bash

   cd /home/user/software/src
   tar -xvzf hops-dv-tc-3.26swc.tar.gz # this will create a directory named hops-3.26
   mkdir bld-3.26 # at the same directory level as hops-3.26
   cd bld-3.26
   ../hops-3.26/configure --prefix=/home/user/software/installed/hops-3.26 --enable-devel
   make all
   make install

.. warning::

   The ``--enable-devel`` flag is mandatory to ensure that certain HOPS utilities used within ``ehthops``
   are built and installed.

Once installed, the HOPS environment can be activated in the shell with

.. code-block:: bash

   source /home/user/software/installed/hops-3.26/bin/hops.bash

Python environment and local dependencies
------------------------------------------------

Pre-requisites
^^^^^^^^^^^^^^^^^

1. The EHT-HOPS pipeline is managed by the fast Python package manager ``uv``. The best way to install
``uv`` on an HPC cluster is via ``pipx`` which installs ``uv`` in an isolated environment.
Install ``pipx`` `via pip <https://pipx.pypa.io/stable/installation/>`_ or `from
source <https://github.com/pypa/pipx>`_ and add it to your ``PATH`` environment variable. Then install
``uv`` via ``pipx``:

.. code-block:: bash

   pipx install uv

``uv`` should now be available as a command in the shell environment.

Optionally (recommended on HPC filesystems where hardlink behaviour may be noisy or unreliable),
suppress hardlink warnings by telling ``uv`` to copy files instead of linking them.

.. code-block:: bash

   export UV_LINK_MODE=copy

.. note::
   We support and recommend ``uv`` to ensure that the Python environment is properly isolated and
   reproducible across different systems and users. Other tools such as ``conda`` or ``mamba``
   may also be used, but the user is responsible for ensuring that the correct versions of all
   dependencies are installed and that the environment is properly activated when running the pipeline. 

Installing the base ``ehthops`` Python environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
   We recommend repeating the following steps every time ``ehthops`` is cloned and set up for a new data reduction
   to ensure that the Python environment is properly configured.

Clone `the EHT-HOPS repository <https://github.com/sao-eht/ehthops>`_ and install the Python environment locally:

.. code-block:: bash

   git clone https://github.com/sao-eht/ehthops.git
   cd ehthops
   uv sync --all-extras

The local virtual environment will be created in the repository root under ``.venv/`` and can be activated with

.. code-block:: bash

   source .venv/bin/activate

Updating the Python environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ensure that the ``uv`` environment is active in the shell before proceeding to install the editable dependencies.

The pipeline requires a local copy of the ``EAT`` package which can be obtained `here <https://github.com/sao-eht/eat>`_.
Change directory to a suitable location, clone the repository, and install it in editable mode:

.. code-block:: bash

   git clone https://github.com/sao-eht/eat.git
   uv pip install -e eat

For post-processing stages of the pipeline, an editable installation of ``eht-imaging`` is also required. Change to a suitable location,
clone the ``dev`` branch of ``eht-imaging``, and install it in editable mode:

.. code-block:: bash

   git clone --branch dev https://github.com/achael/eht-imaging.git
   uv pip install -e eht-imaging

Once the above steps are completed, the Python environment should be properly set up to run the EHT-HOPS pipeline.
All four bands can be processed with the same environment since the dependencies are shared across bands.

.. note::
   
   By default, the pipeline will create all the output data products in the same directory as the input data and code.
   The easiest way to recalibrate the same data with new settings or calibrate new data, is to clone ``ehthops``
   anew and set the Python environment up in the new clone.

