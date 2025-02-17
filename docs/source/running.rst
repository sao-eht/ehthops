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
   -y <yyyy>       Campaign year
   -m              Enable mixed polarization calibration
   -x              Use HAXP data for ALMA
   -p <pattern>    Set the pattern for searching (regex)
   -d <depth>      Set the directory depth for searching (integer)
   -h, --help      Display this help message and exit

   Example:
   SET_SRCDIR=/path/to/data/archive && SET_CORRDAT="Rev1-Cal:Rev1-Sci" && SET_METADIR=/path/to/metadata && source bin/0.launch -y 2021 -d 4 -p "e21f.*--.*.hops/"

Some notes on the environment variables:

- The pipeline attempts to set reasonable default values to these environment variables if they are not set. We recommend setting/verifying at least SRCDIR, CORRDAT, METADIR, and SHRDIR to ensure that the pipeline runs correctly.
- At all stages from 0 to 5, SRCDIR points to the top level directory that hosts the archival data. At stage 6, SRCDIR must point to the directory *5.+close/data* in the current band.
- The user can set SHRDIR to any directory containing runnable Jupyter notebooks (.ipynb files) to replace the default notebooks provided with the plots submodule.
- The METADIR is expected to contain the following subdirectories:

  - *cf/* -- contains the control files for the pipeline named according to the pattern **cf[0-9]_b[1234x]_\***, where the first number denotes the stage and the second number/character denotes the band.
  - *SEFD/* -- contains the station SEFD values for the campaign
  - *VEX/* -- contains the correlated VEX files for the campaign

Some notes on the command-line options:

- The **-y** option sets the year of the campaign and consists of 4 numbers in the format <yyyy>.
- The **-x** option is used to indicate that the linear polarization ALMA data in the archive must be linked from the *-haxp/* directories in the
  archive. When this option is set, **-m** is automatically set to indicate that mixedpol calibration is requested.
  Note that the pattern to match (**-p**) must be the directory containing ALMA data in circular polarization (usually *"-hops"*) and not *"-haxp"*.
- The **-m** option enables mixed polarization calibration. This option is used when the data are understood to be in hybrid polarization bases
  i.e. not all stations use the same polarization basis. It is possible for **-m** to be true and **-x** to be false, indicating that the mixed
  polarization data are all to be found under the *-hops/* directories in the archive.
- The **-p** option sets the pattern to match for the HOPS input directories in the archival data while linking.
  The default pattern is `e${OBSYEAR: -2}.*-$BAND-.*-hops/`.
- The **-d** option sets the directory depth (level) to look for the HOPS input files in the archival data while linking. The default depth is `4`.

The **-d** and **-p** options together determine the directory structure that will be created under **<stage>/data** by the pipeline and deserve
special care. The basic assumptions made by the pipeline about data organization are described :ref:`here <data-organization>`.
As noted there, the data are expected to be organized as *SRCDIR/CORRDAT/dir1/dir2/.../dirn/expt_no/scan_no/mk4_files*.

For instance, if the data organization looks like *SRCDIR/CORRDAT/dir1/dir2/expt_no/scan_no/mk4_files*, then **-d** should be set to **4** and
**-p** should be set to a pattern that matches the naming scheme of *dir2* (all directories at this level are expected to match this pattern).
The pipeline will then create a directory structure under **<stage>/data** corresponding to *expt_no/scan_no/mk4_files*.

These options exist to accommodate different data organization schemes for different data sets.

.. note::
   Instructions to run as Docker image to be added.

Helper scripts
--------------

Easy-to-use sample driver scripts that run the entire pipeline are provided under the directory **ehthops/scripts**.
These scripts are to be run from within the **ehthops/hops-b[1234]** directories:

- **driver_cannon.sh** is a script that runs all the stages of the pipeline, applicable to any band. It is a good starting point for learning to run the pipeline.
- **ehthops.slurmconf** is a SLURM configuration file that can be used to submit the pipeline to a SLURM cluster (e.g. **$** sbatch ehthops.slurmconf).
- **cleanup.sh** deletes all data generated as a result of a previous run and leaves the repo in a clean state.
