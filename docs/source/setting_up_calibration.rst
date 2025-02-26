==============================
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

The code repository consists of four directories named **hops-bx** where **x** stands for the EHT "zoom" band.
Conventionally, in order of increasing frequency, the bands are named 1, 2, 3, and 4.

.. note::

    The 2017 campaign has only two bands named "lo" and "hi". The shell scripts driving the calibration are aware of this
    and will make the appropriate substitutions for 2017 data, mapping "lo" -> "b3" and "hi" -> "b4".

The main driver script is run from within the **hops-bx** directories. Copy the driver script **scripts/driver_cannon.sh** to
the **hops-bx** directory of your choice. For this tutorial, we will use the "lo" band, so we will copy the driver script to
**hops-b3**:

.. code-block:: bash

    cd ehthops/hops-b3
    cp ../scripts/driver_cannon.sh .

.. note::

    The script **scripts/cleanup.sh** is also useful to quickly remove all output created during calibration, leaving the **hops-bx**
    directories in a clean state. Copy this to the **hops-b3** directory and run `source cleanup.sh` to clean up the 
    directory when necessary.

Updating command-line options and environment variables
-------------------------------------------------------

Here are a few things that the user should verify/modify in the driver script before running it:

- The first few lines of **driver_cannon.sh** are used to set the environment for the calibration run, by activating the relevant
  python environment (for running EAT) and setting the HOPS environment variables. Modify them as follows:

  .. code-block:: bash

      source $HOME/.bashrc # load the necessary environment variables
      mamba activate ehthops310 # activate the relevant mamba environment
      HOPS_SETUP=false source /path/to/installed/hops/bin/hops.bash # setting this to false ensures that the HOPS environment is set up anew for each run

  Note that **HOPS_SETUP=false** is necessary only if running via SLURM. If running from the terminal, do not set this environment variable.

- The script runs all the stages requested by the user, from **0.bootstrap** to **6.uvfits**.
  Ensure that only the necessary stages are included in this list. Here we run all the stages.

- The name of the band is extracted from the current working directory which is expected to be named **hops-bx**.
  Hence, ensure that this script is run from within the **hops-bx** directory.

- Each stage performs an additional calibration step that is specific to itself. At the end of each stage, the files
  necessary to run the following stage (such as shell scripts, existing and newly generated control files, the *adhoc*
  directory after stage 2) are copied to the next stage automatically during the step **9.next**.

- Each stage starts with the same command, **source 0.launch**, to which the stage-specific environment variables
  and command-line options are passed. Generally, stage-specific variables and options are the same for all the
  fringe-fitting stages:

  .. code-block:: bash

      SRCDIR=/home/user/calibration/data/extracted # top level directory that hosts the archival data
      CORRDAT="2016.1.01154.V" # correlation releases to use for SRC data, higher precedence comes first (multiple entries are colon-separated)
      METADIR=/home/user/calibration/ehthops/meta/eht2017/230GHz # location of metadata containing the cf directory; for post-processing, we need the SEFD and VEX directories as well

  As for the command-line options, set the year (**-y**) to **2017**, file search depth (**-d**) to **2** and the pattern to match (**-p**)
  to **"2016.1.01154.V"** to correspond to the directory organization of the downloaded EHT2017 data. This instructs the pipeline to create a
  directory structure under **<stage>/data**, mimicking the one that follows the pattern **2016.1.01154.V** in the archival data.
  The call to **0.launch** in the driver script then looks like this:

  .. code-block:: bash

      SET_SRCDIR=/home/user/calibration/data/extracted && SET_CORRDAT="2016.1.01154.V" && SET_METADIR=/home/user/calibration/ehthops/meta/eht2017/230GHz && source bin/0.launch -y 2017 -d 2 -p "2016.1.01154.V"

  More information on how to determine the values of the command-line options can be found :ref:`here <command-line-options>` section.

- At stage **6.uvfits**, SRCDIR should point to the directory **5.+close/data** in the current band.
  The environment variable EHTIMPATH should point to the eht-imaging library. Assume this is
  **/home/user/software/eht-imaging**. And there is only one command-line option **-c** which sets the campaign year
  in an EAT-recognizable format i.e. **EHT2017**. The call to **0.launch** in **6.uvfits** should look like this:

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