============
Output files
============

As the calibration proceeds, new directories will be created under each stage directory:

- ``data/`` contains the symbolic links to the input files from the archive (created during the ``2.link`` step) and the calibrated output files (i.e. fringe files, ``alist`` files).
- ``temp/`` contains the cumulative ``cf_all`` control file generated from cf's in metadata and all control commands generated in the previous stages and the ``fourfit_worker.sh`` script created by ``3.fourfit``. Note that the worker script is created only if using SLURM.
- ``log/`` contains various log files generated during calibration that can be used to verify and debug the calibration process.
- ``tests/`` contains executed ``html`` versions of ``marimo`` notebooks with summary plots and diagnostic information for further inspection of the data.

.. todo::
    More details on inspecting the output to be added here.
