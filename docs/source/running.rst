===============
Running ehthops
===============

The ehthops pipeline consists of multiple stages, each consisting of multiple steps. A detailed description of how the pipeline works can be found in 
`Blackburn et al. (2019) <https://ui.adsabs.harvard.edu/abs/2019ApJ...882...23B/abstract>`_.

Repository structure
-------------------

Stage 0 in band 1 (**hops-b1/0.bootstrap**) contains all the scripts that are common to all steps in each stage in each band.
Step-specific scripts are hosted in the corresponding directory under **hops-b1**. All other bands symlink to these scripts so that only one physical copy of this set of scripts is necessary.

The **meta** directory hosts the metadata and is structured as follows.

- meta
  - <telescope><year>
    - <frequency-in-GHz>GHz
      - cf
        - cf<stage>_b<bandno>_*
      - SEFD
        - b<bandno>
          - <HOPS-expt-no>
            - <source>_<two-letter-station-code>.txt
    - VEX
      - <track>.vex

Currently, the metadata include HOPS control files (**cf**), VEX files (**VEX**), station and source relevant SEFDs (**SEFD**) for each observing campaign.

The pipeline scripts pick the appropriate control files (from the **cf** subdirectory) and other relevant metadata during execution as long as the above directory organization and naming conventions
are followed.

Driver scripts
--------------

The **scripts** directory contains driver scripts required to run the pipeline in two different enivironments.

**driver_cannon.sh** and **driver_cloud.sh** are sample scripts that can be modified to run on any SLURM cluster (e.g. Harvard FASRC) and on the eht-cloud machines respectively.
For **driver_cloud.sh** the eht-cloud specific environment setup is done by scripts stored on the cloud.

The 

The driver scripts are run from within the **hops-b<bandno>** directories. They set the following environment variables that **must be** verified before each execution::

   SET_SRCDIR -- sets the parent directory containing the various revisions of the data
   SET_CORRDAT -- sets the revisions to be processed as a colon-separated list of directory names
   SET_EHTIMPATH -- sets the path to the source code of eht-imaging
   OBSFREQ -- sets the observing frequency in GHz (must match the frequency in the meta directory)
   TELESCOPE -- sets the telescope/facility name (must match the name in the meta directory)

.. note::
   At all stages from 0 to 5, SRCDIR points to the directory that hosts the archival data.
   At stage 6, SRCDIR must point to the directory '5.+close/data' in the current band.

**cleanup.sh** deletes all data generated as a result of a previous run and leaves the repo at the default state.

The pipeline can be executed by typing the following in a linux terminal or a screen session (or in the case of a SLURM cluster,
placing this line in the script submitted to SLURM)::

   source <script-name>

On a SLURM cluster, the above line is placed inside **ehthops.slurmconf** and the SLURM job can be submitted by running::

   sbatch ehthops.slurmconf

.. note::
   Instructions to run as a Docker image to be added.

.. note::
   The following instructions are EHT2021 campaign-specific and will be removed from repo documentation before release.

EHT2021 data specific instructions
----------------------------------

HOPS operates by assigning single letter codes to frequency channels, restricting the number of channels that can be represented.
Since the EHT 2021 campaign observed at two different frequency bands (230 GHz and 345 GHz), it is better to keep the reduction clean, by processing these data separately.

For 230 GHz data
----------------

The 2021 campaign observed at 345 GHz only on day 109 (expt_no 3769, track e21f19). Hence the preset flags corresponding to track e21f19 correspond only to 345 GHz observations.
While reducing 230 GHz data, replace the contents of *hops-b1/1.+flags_wins/cf1_flags_e21f19* with the following:

::
 
  * Flag all 345 GHz scans
  if scan > 109-000000
    skip true  * 109 is the day of the 345 GHz obs in 2021


For 345 GHz data
----------------

(1) *hops-b1/1.+flags_wins/cf1_flags_e21f19* is the only control file pertinent to 345 GHz data reduction.
Hence, the other control files containing the flags (prefixed *cf1_flags_*) can safely be deleted from the working copy of the repo if only 345 GHz data are being processed.

(2) Also, there is no need to symlink all the data from the archive. This can be accomplished by modifying the grep clause in *hops-b1/0.bootstrap/bin/2.link* as follows::

  grep "\/e21.*-$BAND-.*-hops\/" # before
  grep "\/e21f19.*-$BAND-.*-hops\/" # after

(3) Also, in stage 6, instead of looping over a date range from 3762 to 3769 in *1.convert* and *3.average*, loop only once over 3769.
