============
Output files
============

As the calibration proceeds, new directories will be created under each stage directory:

- **temp** contains the cumulative **cf_all** control file generated from cf's in metadata and those generated during the previous stages.
- **data** contains the symbolic links to the input files from the archive and the calibrated output files (i.e. fringe files).
- **log** contains various log files generated during calibration.
- **tests** contains jupyter notebooks with summary plots and diagnostic information for further inspection.

.. note::
    More details on inspecting the output to be added here.
