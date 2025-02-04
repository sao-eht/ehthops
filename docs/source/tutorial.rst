====================
Calibration Tutorial
====================

This tutorial is meant to walk the user through the step-by-step process of calibrating data using
the EHT-HOPS pipeline, utlizing publicly available data from the EHT 2017 observing campaign.

We expect that the user has already installed the EHT-HOPS pipeline and will be using SLURM to schedule jobs on a compute cluster.
Please refer to the :doc:`installation guide <install>` for instructions on how to install the pipeline
and :ref:`this section <command-line-options>` in the running guide for information on the valid command-line options.

In the following we assume that the user operates out of a directory called **/home/user/calibration**.
All data will be stored under **data/** and the EHT-HOPS repository will be cloned to **ehthops/** (by default).

Preparing the data
==================

The output of the DiFX software correlator ("Level 1" or L1 data) converted to mk4 format is the standard input to HOPS.
We will calibrate the publicly available L1 data from the EHT 2017 observing campaign for this tutorial.
These data can be downloaded either from the `ALMA Science Portal <https://almascience.nrao.edu/almadata/ec/eht/>`_ or `CyVerse Data Commons (DOI: 10.25739/kat4-na03) <https://datacommons.cyverse.org/browse/iplant/home/shared/commons_repo/curated/EHTC_2017L1_May2022>`_.

For this tutorial, we will download the data from the directory **2016.1.01154.V**:

.. code-block:: bash

    cd /home/user/calibration/data
    wget -r -np -nH --cut-dirs=3 -A "*-hops.tgz,*-haxp.tgz" https://almascience.nrao.edu/almadata/ec/eht/2016.1.01154.V/

The "-hops.tgz" files consist of the final correlated data (in which ALMA correlations have been converted to circular
polarization basis), while the "-haxp.tgz" files contain the mixedpol ALMA-only data.

.. note::

    If the '-x' option is passed to **0.launch**, the "-haxp" ALMA data will replace the "-hops" data during calibration.
    In this tutorial, we concern ourselves only with the "-hops" data.
    
Unpack the data with the following command:

.. code-block:: bash

    mkdir -p extracted/2016.1.01154.V
    find 2016.1.01154.V -name "*.tgz" -exec tar -xvzf {} -C "extracted/2016.1.01154.V" \;

The untarred directories can be found in the directory **/home/user/calibration/data/extracted/2016.1.01154.V**.

Setting up the calibration run
==============================

The EHT-HOPS pipeline is driven by a series of shell scripts that execute the various stages of the calibration process step-by-step.
Sample driver scripts for running the entire pipeline are provided in the **scripts** directory of the EHT-HOPS repository.

Setting up the repository
-------------------------

Clone the public git repository for the EHT-HOPS pipeline.
All the calibrated output files will be created within this directory:

.. code-block:: bash

    cd /home/user/calibration
    git clone https://github.com/sao-eht/ehthops.git
    cd ehthops
    git submodule update --init --remote

The last line above ensures that the submodules are updated to the latest version.

The code repository consists of four directories named**hops-bx** where *x* stands for the EHT "zoom" band.
Conventionally, in order of increasing frequency, the bands are named 1, 2, 3, and 4.

.. note::

    The 2017 campaign has only two bands named "lo" and "hi". The shell scripts driving the calibration are aware of this
    and will make the appropriate substitutions for 2017 data, mapping "lo" -> "b3" and "hi" -> "b4".

The main driver script is run from within the **hops-bx** directories. Copy the driver script **scripts/driver_cannon.sh** to
the **hops-bx** directory of your choice. For this tutorial, we will use the "lo" band, so we will copy the driver script to
**hops-b3**:

.. code-block:: bash

    cd ehthops/hops-b3
    cp scripts/driver_cannon.sh .

.. note::

    The script **scripts/cleanup.sh** is also useful to quickly remove all output created during calibration, leaving the **hops-bx**
    directories in a clean state. Copy this to the **hops-b3** directory and `source` it to clean up the directory when necessary.

Updating command-line options and environment variables
-------------------------------------------------------

Here are a few things that the user should verify/modify in the driver script before running it:

- The first few lines of **driver_cannon.sh** are used to
set the environment for the calibration run, by activating the relevant python environment
(for running EAT) and setting the HOPS environment variables. Update these to reflect the settings
of your system.

- The script runs all the stages requested by the user, from **0.bootstrap** to **6.uvfits**.
Ensure that only the necessary stages are included in this list.

- The name of the band is extracted from the current working directory which is expected to be named **hops-bx**.
Hence, it is important to run the script from within the **hops-bx** directory.

- Each stage performs an additional calibration step that no other stage does. At the end of
these steps, relevant files from the current stage (scripts, cfs, adhoc directory) are copied to the next stage.

- Each stage starts with the same command, **source 0.launch**, which sets the environment variables
and passes the command-line options to the current stage.

Set the following values to the environment variables passed to **0.launch** in the driver script:

.. code-block:: bash

    SRCDIR=/home/user/calibration/data/extracted # top level directory that hosts the archival data
    CORRDAT="2016.1.01154.V" # correlation releases to use for SRC data, higher precedence comes first (multiple entries are colon-separated)
    METADIR=/home/user/calibration/ehthops/meta/eht2017/230GHz # location of metadata containing the cf directory; for post-processing, we need the SEFD and VEX directories as well

Using the command-line options, set the year to 2017, file search depth to 3 and the pattern to "*.ec_eht.e17.*-$band-.*-hops/" to match the file naming
convention of the EHT 2017 data that we downloaded. Putting it all together, the call to **0.launch** in the driver script should look like this:

.. code-block:: bash

    SET_SRCDIR=/home/user/calibration/data/extracted && SET_CORRDAT="2016.1.01154.V" && SET_METADIR=/home/user/calibration/ehthops/meta/eht2017/230GHz && source bin/0.launch -y 2017 -d 3 -p "*.ec_eht.e17.*-$band-.*-hops/"

These settings are the same from stages **0.launch** to **5.+close**.
At stage **6.uvfits**, the SRCDIR should point to the directory **5.+close/data** in the current band.
The environment variable EHTIMPATH should point to the eht-imaging library. Assume this is **/home/user/software/eht-imaging**.
And there is only one option **-c** to set the campaign year (**EHT2017**) for the uvfits generation (this is an EAT-recognizable code).

Putting it all together, the call to **0.launch** in **6.uvfits** should look like this:

.. code-block:: bash

    SET_EHTIMPATH="/home/user/software/eht-imaging" && SET_SRCDIR=$workdir/5.+close/data && SET_METADIR=/home/user/calibration/ehthops/meta/eht2017/230GHz && source bin/0.launch -c EHT2017

With the above changes, the driver script is ready to be submitted to SLURM.
Here is a sample configuration file for the SLURM job (can be found in **scripts/ehthops.slurmconf**):

.. code-block:: bash

    #!/bin/bash
    #SBATCH -c 48 # Number of cores requested
    #SBATCH -t 3-00:00:00 # Runtime
    #SBATCH -p partition-name # Partition
    #SBATCH --mem-per-cpu=2048 # Memory per node in MB (--mem or --mem-per-cpu)
    #SBATCH -e slurm-%j.err
    #SBATCH -o slurm-%j.out

    # run script
    source driver_cannon.sh

This config file can now be submitted with **sbatch**:

.. code-block:: bash

    sbatch ehthops.slurmconf


Output files
------------

As the calibration proceeds, new directories will be created under each stage directory:

- **temp** contains the cumulative **cf_all** control file generated from cf's in metadata and those generated during the previous stages.
- **data** contains the symbolic links to the input files from the archive and the calibrated output files (i.e. fringe files).
- **log** contains various log files generated during calibration.
- **tests** contains jupyter notebooks with summary plots and diagnostic information for further inspection.

