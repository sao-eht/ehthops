================================================
Meta-Environment Setup for the EHT-HOPS Pipeline
================================================

This page describes how to prepare the *meta environment* required to run the EHT-HOPS pipeline under SLURM.
The pipeline expects a mixed environment consisting of:

* An existing ``HOPS`` installation (required),
* A Python virtual environment managed with ``uv``,
* A local editable copy of ``EAT`` (required), and
* A local editable copy of ``eht-imaging`` (optional).

.. note::

   The SLURM script is designed to assemble this environment automatically at runtime, but the same requirements
   apply when preparing the installation manually. If running via SLURM, follow the procedure in ``README.md``
   to launch the pipeline. The manual ``HOPS`` installation is still required, but the ``uv`` environment and
   editable dependencies will be set up automatically by the SLURM script.

Installing HOPS
---------------

Pre-requisites
^^^^^^^^^^^^^^

On Ubuntu, some or all of the following packages may be necessary to be able to compile HOPS successfully.
Note that the exact names might differ on different systems

.. code-block:: bash

   sudo apt install gcc make gfortran libx11-dev ghostscript libfftw3-dev parallel
   sudo apt install gdb flex bison pkg-config autoconf automake gettext libtool

``FFTW`` is a pre-requisite for HOPS that should have been installed in the previous step. If not,
download `FFTW <https://fftw.org/>`_ manually and run the following commands to install it

.. code-block:: bash

   ./configure --prefix=</path/to/install/fftw> --enable-shared --enable-threads --enable-openmp
   make
   make install

If ``FFTW`` has been installed in a non-standard path, the following environment variables may be necessary.
Try this only if HOPS complains that FFTW3 is missing

.. code-block:: bash

   export FFTW3_LIBS="-L</path/to/fftw/lib>"
   export FFTW3_CFLAGS="-I</path/to/fftw/include>"

``PGPLOT`` is a pre-requisite for HOPS. Download `PGPLOT <https://sites.astro.caltech.edu/~tjp/pgplot/>`_ and
follow `these instructions <https://www.gnu.org/software/gnuastro/manual/html_node/PGPLOT.html>`_ to
install it. Note that the switch from ``g77`` to ``gfortran`` is necessary on any modern Linux system.

Define the following environment variables before compiling HOPS v3.24 so that ``PGPLOT`` and ``FFTW`` are
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
We have tested the following on both HOPS v3.24 and v3.26.

.. note::
   The public version of HOPS shown below does not contain some astronomy-specific utilities. Some parts of the pipeline
   (such as the *average* command) may not exist or work as expected. Please contact the EHT-HOPS pipeline developers for
   the customised version of HOPS. These utilities will be made available outside HOPS in a future release.

Download `HOPS <https://www.haystack.mit.edu/haystack-observatory-postprocessing-system-hops/>`_

.. code-block:: bash

   wget -nH https://web.mit.edu/haystack-www/hops/hops-3.24-3753.tar.gz

The -nH argument prevents the entire directory structure on the host from being recreated locally.
Regardless of whether you are using the public version of HOPS or the version provided by the
EHT-HOPS pipeline developers, the following steps are the same.

The HOPS developers recommend building HOPS in a separate directory from the source code
(this is separate from the install directory for HOPS). Untar HOPS version 3.24 (or 3.26)
to ``/path/to/parentdir`` and create a ``build`` directory under ``parentdir`` in which to compile HOPS.
The install location for HOPS binaries is specified using the ``--prefix`` option passed to configure

.. code-block:: bash

   tar -xvzf hops-3.24-3753.tar.gz
   mkdir bld-3.24 # at the same directory level as hops-3.24
   cd bld-3.24
   ../hops-3.24/configure --prefix=</path/to/install/hops-3.24> --enable-devel
   make all
   make install

.. note::
   Do not forget the ``\-\-enable-devel`` flag above! Without it, some necessary HOPS utilities will not be built.

The HOPS environment can be activated in the shell with

.. code-block:: bash

   source </path/to/hops-3.24/bin/hops.bash>

Installing EHT-HOPS Pipeline Environment
----------------------------------------

The EHT-HOPS pipeline is managed by the fast Python package manager ``uv``. The best way to install
``uv`` on an HPC cluster is via ``pipx``. Install ``pipx`` `via pip <https://pipx.pypa.io/stable/installation/>`_
or `from source <https://github.com/pypa/pipx>`_ and add it to ``PATH``. Then install ``uv`` via ``pipx``:

.. code-block:: bash

   pipx install uv

``uv`` should now be available as a command in the shell environment.

Optionally (recommended on HPC filesystems where hardlink behaviour may be noisy or unreliable),
suppress hardlink warnings by telling ``uv`` to copy files instead of linking them.

.. code-block:: bash

   export UV_LINK_MODE=copy

Clone the EHT-HOPS repository to a suitable location, drop into the root of the repo (where ``pyproject.toml`` lives)
and install the meta-environment for the pipeline with

.. code-block:: bash

   git clone https://github.com/sao-eht/ehthops.git
   cd ehthops
   uv sync --all-extras

The local virtual environment will be created in the repository root under ``.venv/`` with all the dependencies installed.
The virtual environment can now be activated with

.. code-block:: bash

   source .venv/bin/activate

Ensure that the ``uv`` environment is active in the shell before proceeding to install the editable dependencies.

The pipeline requires a local copy of the ``EAT`` package which can be obtained `here <https://github.com/sao-eht/eat>`_.
Change directory to a suitable location, clone the repository, and install in editable mode:

.. code-block:: bash

   git clone https://github.com/sao-eht/eat.git
   uv pip install -e eat

For post-processing stages of the pipeline, an editable installation of ``eht-imaging`` is also required. Change to a suitable location,
clone the ``dev`` branch of ``eht-imaging``, and install it in editable mode:

.. code-block:: bash

   git clone --branch dev https://github.com/achael/eht-imaging.git
   uv pip install -e eht-imaging
