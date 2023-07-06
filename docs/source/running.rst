===============
Running ehthops
===============

The ehthops pipeline consists of multiple stages, each consisting of multiple steps. A detailed description of the working of the pipeline can be found in 
`Blackburn et al. (2019) <https://ui.adsabs.harvard.edu/abs/2019ApJ...882...23B/abstract>`_.

Directory structure
-------------------

Stage 0 in band 1 (**hops-b1/0.bootstrap**) contains all the scripts that are common to all steps in each stage in each band.
Step-specific scripts are hosted in the corresponding directory under **hops-b1**. All other bands symlink to these scripts so that only one physical copy of this set of scripts is necessary.

Stages 0 and 1 in band 1 (**hops-b1/0.bootstrap** and **hops-b1/1.+flags+wins**) host the preset control files and flags.
Other bands symlink to these control files where necessary, aside from hosting band-specific control files and flags at the corersponding stages.

Driver scripts
--------------

The *dev-template/scripts* directory contains driver scripts to run the pipeline in two different enivironments.

*driver_cannon.sh* and *hops2021.slurm* are sample scripts that can be modified to run on any SLURM cluster (e.g. the Harvard FAS cluster).

*driver_cloud.sh* is a sample script tailored to run on eht-cloud. The environment setup lines are hidden inside another script hosted on eht-cloud.

The driver scripts must be run from the *dev-template/hops-bx* directories. They set the following environment variables that **must be** verified before each execution::

   SET_SRCDIR -- sets the parent directory containing the various revisions of the data
   SET_CORRDAT -- sets the revisions to be processed as a colon-separated list of directory names
   SET_EHTIMPATH -- sets the path to the source code of eht-imaging

.. note::
   At all stages from 0 to 5, SRCDIR points to the directory that hosts the archival data.
   At stage 6, SRCDIR must point to the directory '5.+close/data' in the current band.

*cleanup.sh* deletes all data generated as a result of a previous run and leaves the repo at the default state.

The pipeline can be executed by typing the following in a linux terminal or a screen session (or in the case of a SLURM cluster,
placing this line in the script submitted to SLURM)::

   source <script-name>

On a SLURM cluster, the above line is placed inside *hops2021.slurm* and the SLURM job can be submitted by::

   sbatch hops2021.slurm

.. note::
   Instructions to run as a Docker image to be added.

EHT2021 data specific instructions
----------------------------------

HOPS operates by assigning single letter codes to frequency channels, restricting the number of channels that can be represented.
Since the EHT 2021 campaign observed at two different frequency bands (230 GHz and 345 GHz), it is better to keep the reduction clean, by processing these data separately.

The 2021 campaign observed at 345 GHz only on day 109 (expt_no 3769, track e21f19). Hence the preset flags corresponding to track e21f19 correspond only to 345 GHz observations.
While reducing 230 GHz data, replace the contents of *hops-b1/1.+flags_wins/cf1_flags_e21f19* with the following:

::
 
  * Flag all 345 GHz scans
  if scan > 109-000000
    skip true  * 109 is the day of the 345 GHz obs in 2021

*hops-b1/1.+flags_wins/cf1_flags_e21f19* is the only control file pertinent to 345 GHz data reduction.
Hence, the other control files containing the flags (prefixed *cf1_flags_*) can safely be deleted from the working copy of the repo if only 345 GHz data are being processed.

Also, there is no need to symlink all the data from the archive. This can be accomplished by changing the grep clause in *hops-b1/0.bootstrap/bin/2.link* must be modified as follows::

  grep "\/e21.*-$BAND-.*-hops\/" # before
  grep "\/e21f19.*-$BAND-.*-hops\/" # after
