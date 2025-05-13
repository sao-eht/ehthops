===============
Running ehthops
===============         

.. _command-line-options:

Command-line options
--------------------
Arguments are passed only to the launch script **0.launch**. The rest of the scripts are run without any arguments.
Some of the arguments define environment variables and are set using **SET_ENVVAR=VALUE** syntax.
The rest of the arguments are passed to the pipeline as command-line arguments.

The launch script can be run with the **-h** option to display the help message::

   source 0.bootstrap/bin/0.launch -h

   Usage: [SET_ENVVAR1=...] && [SET_ENVVAR2=...] && source 0.launch [options]

   Useful environment variables:
   =============================
   SET_CORRDAT     Correlation releases to use for SRC data, higher precedence comes first
   SET_WRKDIR      Working directory for pipeline process
   SET_TOPDIR      Top level dir for all stages
   SET_DATADIR     Input/output data location for HOPS
   SET_METADIR     Location of preset control files, META tables, ZBL flux estimates for netcal, etc
   SET_SRCDIR      Single input data location for correlator source data
   SET_SHRDIR      Location of shared resources (summary notebooks, etc)
   If these are not set, reasonable defaults are used (not always guaranteed to work).

   Command-line options:
   =====================
   -y <yyyy>       Campaign year"
   -m              Enable mixed polarization calibration"
   -x              Use HAXP data for ALMA (i.e. assume linearpol ALMA data present in -haxp directories)"
   -p <pattern>    Set the directory pattern for matching (regex); this is the parent directory of the <expt-no>/<scan> directories"
   -d <depth>      Set the directory depth for searching (integer); this is the distance between <CORRDAT> and <scan> directories"
   -S <dir>        Set the base data source directory (i.e. single input data location) "
   -C <colon-separated-list-of-dirs>    Set the correlation releases/tags to use in order of precedence"
   -M <dir>        Set the metadata directory (e.g. preset control files, META tables, ZBL flux estimates for netcal)"
   -h, --help      Display this help message and exit"

   Example:
   SET_SRCDIR=/path/to/srcdir && SET_CORRDAT="relativepath1:relativepath2" && SET_METADIR=/path/to/metadata && SET_OBSYEAR="2017" && SET_MIXEDPOL=false && SET_HAXP=false && source bin/0.launch

Some notes on the environment variables and running the stages manually:

- The 0.launch scripts attempt to set reasonable default values for the environment variables if they are not specified by the user. We recommend setting/verifying at least SRCDIR, CORRDAT, METADIR, and SHRDIR to ensure that the stages run correctly.
- At all stages from 0 to 5, SRCDIR points to the top level directory that hosts the archival data. At stage 6, SRCDIR must point to the directory *5.+close/data* in the current band.
- When running each stage/step manually, if stage 0 (**0.bootstrap**) is not required, the user must ensure that steps **0.launch** and **9.next** are run before running stage 1 (**1.+flags+wins**). This would copy all relevant scripts and control files necessary for running stage 1 (**1.+flags+wins**). This is automatically taken care of by the **ehthops_pipeline.sh** script when running in pipeline mode.
- The user can set SHRDIR to any directory containing runnable Jupyter notebooks (.ipynb files) to replace the default notebooks provided with the plots submodule.
- The METADIR is expected to contain the following subdirectories:

  - *cf/* -- contains the control files for the pipeline named according to the pattern **cf[0-9]_b[1|2|3|4|lo|hi]_\***, where the first number denotes the *stage* and the second number/character(s) denotes the *band*.
  - *antab/* -- contains the ANTAB files for all tracks and bands for the campaign.
  - *vex/* -- contains the observed VEX schedules for the campaign.

.. note::
   Instructions to run as Docker image to be added.

Helper scripts
--------------

- **ehthops/ehthops_pipeline.sh** is a script that runs all the stages of the pipeline, applicable to any band. It is a good starting point for learning to run the pipeline.
- **ehthops/settings.config** is a sample configuration file that shows all the keywords that can be passed to **ehthops_pipeline.sh**.
- **ehthops/scripts/ehthops_slurm.job** is a SLURM configuration file that can be used to submit the pipeline to a SLURM cluster.
- **ehthops/scripts/cleanup.sh** deletes all data generated as a result of a previous run and leaves the working area in a clean state.
