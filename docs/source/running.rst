===============
Running ehthops
===============
This repository describes the scripts that drive the EHT-HOPS pipeline execution. Running these scripts in sequence will execute
all stages of the pipeline.

.. note::
   Instructions to run as a Docker image to be added.


The driver scripts are run from within the **hops-b<bandno>** directories.
They set the following environment variables that **must be** verified before each execution::

   WRKDIR=${SET_WRKDIR:-"$PWD"}                  # working directory for pipeline process
   TOPDIR=${SET_TOPDIR:-"$WRKDIR/.."}            # top level dir for all stages
   DATADIR=${SET_DATADIR:-"$WRKDIR/data"}        # input/output data location for HOPS

   SRCDIR=${SET_SRCDIR:-"/data/2018-april/corr"} # single input data location for correlator source data
   SHRDIR=${SET_SHRDIR:-"$TOPDIR/../share"}      # location of shared resources (summary notebooks, etc)
   METADIR=${SET_METADIR:-"$TOPDIR/../meta"}     # location of META tables, ZBL flux estimates for netcal, etc

In addition, the following variables are set via command-line arguments to the **0.launch** script::

   OBSFREQ -- (`-f`) sets the observing frequency in GHz (must match the numerical value of the directory with the observing frequency in its name in *ehthops/meta/*); default is `230`.
   TELESCOPE -- (`-t`) sets the telescope/facility name (must match the telescope/facility name in *ehthops/meta/*); default is `eht`.
   OBSYEAR -- (`-y`) sets the year of observation (must match the year of the experiment that follows the telescope name in*ehthops/meta/*); default is `2021`.
   MIXEDPOL -- (`-m`) set to true if the `-m` option is given to indicate that the data contain mixed polarizations; `false` by default.
   HAXP -- (`-x`) set to true if the `-h` option is given to indicate that the mixed polarization data for ALMA must be linked from the *-haxp* directories in the archive; `false` by default.
   PATTERN -- (`-p`) sets the pattern to match for the HOPS input directories/files in the archival data while linking; default is `e${OBSYEAR: -2}.*-$BAND-.*-hops/`.
   DEPTH -- (`-d`) sets the directory depth (level) to look for `HOPS` input files in the archival data while linking; default is `4`.

A valid call to the **0.launch** script would look like::

   SET_SRCDIR=/n/holylfs05/LABS/bhi/Lab/doeleman_lab/archive/prod-extracted/2018April && SET_CORRDAT="Rev7-Cal:Rev7-Sci" && source bin/0.launch -t eht -f 230 -y 2018 -d 4 -p "e18.*-$band-.*.hops/"

.. note::
   At all stages from 0 to 5, SRCDIR points to the directory that hosts the archival data.
   At stage 6, SRCDIR must point to the directory *5.+close/data* in the current band.

**cleanup.sh** deletes all data generated as a result of a previous run and leaves the repo at the default state.

The pipeline can be executed by typing the following in a linux terminal or a screen session (or in the case of a SLURM cluster,
placing this line in the script submitted to SLURM)::

   source <script-name>

On a SLURM cluster, the above line is placed inside **ehthops.slurmconf** and the SLURM job can be submitted by running::

   sbatch ehthops.slurmconf