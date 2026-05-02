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

1. On Ubuntu, some or all of the following packages may be necessary for HOPS compilation to succeed.
Note that the exact names might differ on different systems.

.. code-block:: bash

   sudo apt install gcc make gfortran libx11-dev ghostscript libfftw3-dev parallel
   sudo apt install gdb flex bison pkg-config autoconf automake gettext libtool

2. Ensure that the above step has installed ``FFTW3``. If not, `install it manually from the 
official page <https://fftw.org/>`_. *If* HOPS complains ``FFTW3`` is missing (e.g. ``FFTW3`` is
installed in a non-standard path), ensure that the following environment variables are set.

.. code-block:: bash

   export FFTW3_LIBS="-L</path/to/fftw/lib>"
   export FFTW3_CFLAGS="-I</path/to/fftw/include>"

3. Download `PGPLOT <https://sites.astro.caltech.edu/~tjp/pgplot/>`_ and follow
`these instructions <https://www.gnu.org/software/gnuastro/manual/html_node/PGPLOT.html>`_
to install it. Note that the recommended switch from ``g77`` to ``gfortran`` is necessary
on any modern Linux system.

4. Define the following environment variables before compiling HOPS so that ``PGPLOT`` and ``FFTW`` are
discoverable by HOPS during compilation

.. code-block:: bash

   export PGPLOT_DIR="</path/to/pgplot>"
   export LD_LIBRARY_PATH="</path/to/pgplot>":"</path/to/fftw/lib>":$LD_LIBRARY_PATH
   export LDFLAGS="-L</path/to/fftw/lib>"
   export CFLAGS="-I</path/to/fftw/include>"
   export CPPFLAGS="-I</path/to/fftw/include>"
   export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:"</path/to/fftw/lib/pkgconfig>"

Downloading and installing HOPS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The `public release of HOPS <https://www.haystack.mit.edu/haystack-observatory-postprocessing-system-hops/>`_
does not contain some astronomy-specific utilities. Some parts of the pipeline (such as the ``average`` command)
may not exist or work as expected. **Please contact the EHT-HOPS pipeline developers** to obtain the correct version
of HOPS compatible with ``ehthops``.

.. note::
   The missing utilities will be made available as part of the ``EAT`` library in a future release,
   at which point the public release of HOPS will be sufficient for the pipeline:

   .. code-block:: bash

      wget -nH https://web.mit.edu/haystack-www/hops/<hops-version-number>.tar.gz

   Until then, the correct way to obtain HOPS is to contact the EHT-HOPS pipeline developers.

Developers of HOPS recommend building the software in an isolated ``build`` directory and installing it in
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

Note that 

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
