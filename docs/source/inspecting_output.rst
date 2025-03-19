============
Output files
============

As the calibration proceeds, new directories will be created under each stage directory:

- **data** contains the symbolic links to the input files from the archive (created during the *2.link* step) and the calibrated output files (i.e. fringe files, alist files).
- **temp** contains the cumulative **cf_all** control file generated from cf's in metadata and all control commands generated in the previous stages.
- **log** contains various log files generated during calibration that can be used to verify and debug the calibration process.
- **tests** contains jupyter notebooks with summary plots and diagnostic information for further inspection of the data.

.. note::
    More details on inspecting the output to be added here.
