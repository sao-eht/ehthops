===============
Running ehthops
===============         

.. _launching-the-pipeline:

Launching the pipeline
------------------------
Arguments are passed only to the ``0.launch`` step which sets environment variables used by the other scripts.
Some of the arguments define environment variables and are set using ``SET_ENVVAR=VALUE`` syntax.
The rest of the arguments are passed to the pipeline as command-line arguments.

The launch script can be run with the ``-h`` option to display the help message::

   Usage: [SET_ENVVAR1=...] && [SET_ENVVAR2=...] && source bin/0.launch [options]

   Useful environment variables:
   =============================
   SET_CORRDAT     Correlation releases to use for SRC data, higher precedence comes first (colon-separated list)
   SET_WRKDIR      Working directory for pipeline process (default: PWD)
   SET_TOPDIR      Top level dir for all stages (default: WRKDIR/..)
   SET_DATADIR     Input/output data location for HOPS (default: WRKDIR/data)
   SET_METADIR     Location of preset control files, META tables, ZBL flux estimates for netcal, etc
   SET_SRCDIR      Single input data location for correlator source data
   SET_SHRDIR      Location of shared resources (summary notebooks, etc)
   SET_OBSYEAR     Campaign year
   SET_FILTERSTRING  Regex pattern to filter directories to process
   SET_MIXEDPOL    Enable mixed polarization calibration
   SET_HAXP        Use HAXP data for ALMA (i.e. assume linearpol ALMA data present in -haxp directories)

   If these are not set and no command-line options are given, then reasonable defaults are used (not always guaranteed to work!).

   Command-line options:
   =====================
   -y <yyyy>       Campaign year
   -m              Enable mixed polarization calibration
   -x              Use HAXP data for ALMA (i.e. assume linearpol ALMA data present in -haxp directories)
   -S <dir>        Set the base data source directory (i.e. single input data location) 
   -C <colon-separated-list-of-dirs>    Set the correlation releases/tags to use in order of precedence
   -M <dir>        Set the metadata directory (e.g. preset control files, META tables, ZBL flux estimates for netcal)
   -F <regex>      Set the filter string to select which directories to process
   -h, --help      Display this help message and exit

   Note:
   - The equivalent command-line options take precedence over the SET_* environment variables.
   - The SET_* environment variables take precedence over the default values.

   Example:
   SET_SRCDIR=/path/to/data/archive && SET_CORRDAT="Rev1-Cal:Rev1-Sci" && SET_METADIR=/path/to/metadata && SET_OBSYEAR=2021 source bin/0.launch

Some notes on the environment variables and running the stages manually (the following are taken care of automatically by ``scripts/ehthops_pipeline.sh``):

- ``0.launch`` attempts to set reasonable defaults for the environment variables if they are not specified. We recommend setting/verifying the values of at least ``SRCDIR``, ``CORRDAT``, ``METADIR``, and ``OBSYEAR`` every time ``0.launch`` is run.
- In stages 0 to 5, ``SRCDIR`` points to the top level directory that hosts the archival data. In stage 6, ``SRCDIR`` must point to the directory ``5.+close/data`` in the current band.
- If not starting from ``0.bootstrap``, ensure that ``0.launch`` and ``9.next`` are run before stage 1 (``1.+flags+wins``). This copies all relevant scripts and control files.
- The user can set ``SHRDIR`` to any directory containing runnable ``marimo`` notebooks to replace the default notebooks provided.
- The ``METADIR`` is expected to be organized according to the description given in the :ref:`metadata-organization` section.

.. todo::
   Instructions to run as Docker image to be added.

Helper scripts
--------------

The ``ehthops/scripts`` directory contains several helper scripts:

- ``ehthops_pipeline.sh`` runs all stages of the pipeline, applicable to any band. It is a good starting point to quickly start running the pipeline.
- ``settings.config`` provides a sample configuration that can be updated and passed to ``ehthops_pipeline.sh``.
- ``ehthops_slurm.job`` can be used to submit the pipeline to a SLURM cluster with appropriate modifications.
- ``cleanup.sh`` deletes all data generated during a previous run and leaves the working area in a clean state.
