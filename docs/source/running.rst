===============
Running ehthops
===============

The ehthops pipeline consists of multiple stages, each consisting of multiple steps. A detailed description of the working of the pipeline can be found in 
`Blackburn et al. (2019) <https://ui.adsabs.harvard.edu/abs/2019ApJ...882...23B/abstract>`_.

Directory structure
-------------------

Stage 0 in band 1 (**hops-b1/0.bootstrap**) contains all the scripts that are common to all steps in each stage in each band.
Step-specific scripts are hosted in the corresponding directory under **hops-b1**. All other bands symlink to these scripts so that only one physical copy of these scripts are necessary.

Stages 0 and 1 in band 1 (**hops-b1/0.bootstrap** and **hops-b1/1.+flags+wins**) contain all the control files that are common to all steps in each stage in each band.
Other bands symlink to these control files where necessary. Band-specific control files can be found under the corresponding directories.

Running manually
----------------

Activate the conda environment created in the installation step and activate the HOPS shell environment::

   source /path/to/hops-3.24/bin/hops.bash

Checkout the ehthops pipeline (the version for calibrating EHT2021 data) from `https://github.com/eventhorizontelescope/2021-april <https://github.com/eventhorizontelescope/2021-april>`_.

The **dev-template** directory hosts the template directory structure, HOPS control files (prefixed **cf**), and source code for the pipeline. 
Data and scripts corresponding to each frequency band are contained in individual directories named **hops-bx** where **x** stands for the band number.

The source code consists of a collection of shell scripts which are run in sequence.
All scripts are run from within the corresponding **hops-bx** directory, by sourcing the scripts located in **hops-bx/<stage>/bin** in order. An example workflow looks like::

   cd dev-template/hops-bx
   cd <stage>
   source bin/<script>

This basic workflow is the same from stages 0 to 5. Stage 6 is the post-processing step which is run as follows::

   cd dev-template/hops-bx/6.uvfits
   source bin/0.launch
   source bin/1.uvfits
   source bin/2.import # optional step; ensure that path_ehtim is set appropriately in the code
   python bin/3.average

Running as a slurm job
----------------------

It is recommended to use system-specific driver shell scripts that set up the necessary environment to run the pipeline as a slurm job. This driver must

- Set up the appropriate conda environment.
- Set up the HOPS environment by running **source /path/to/hops-3.24/bin/hops.bash**.
- Run each step in each stage (in each band, if necessary) by sourcing the appropriate scripts.

.. note:: As of now, the post-processing stage (6.uvfits) will not run properly when submitted as a slurm job and must be run manually. This will be updated in a future version.

Running as a docker image
-------------------------

.. note:: TODO
