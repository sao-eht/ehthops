===============
Running ehthops
===============         

.. _launching-the-pipeline:

Launching the pipeline
------------------------
Arguments are passed only to the ``0.launch`` step which sets environment variables used by the other scripts.
Some of the arguments define environment variables and are set using ``SET_ENVVAR=VALUE`` syntax.
The rest of the arguments are passed to the pipeline as command-line arguments.

The launch script can be run with the ``-h`` option to display all available options.

The fastest and the simplest way to launch the pipeline is to use the ``ehthops_pipeline.sh`` script which runs
all stages of the pipeline in sequence. This script can be used with a configuration file (e.g., ``settings.config``)
that defines the environment variables and command-line arguments for the launch stage. On a SLURM cluster,
the pipeline can be launched by submitting the ``ehthops_slurm.job`` script with appropriate modifications.

.. bash::
   sbatch ehthops_slurm.job

The maximum number of concurrent ``fourfit`` jobs can be set using ``SET_JOBARRAY_CAP`` in ``settings.config``.

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
