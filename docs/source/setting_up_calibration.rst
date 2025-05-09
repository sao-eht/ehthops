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

The last line above ensures that the submodules containing metadata and summary notebooks are updated to the latest version.

note::

    Only the publicly available metadata are imported by the above. These are expected to serve as a template for how metadata is expected to be
    organized. It is the responsibility of the user to ensure that their metadata are organized in the same way as the public metadata.

The code repository consists of four directories named **hops-bx** where **x** stands for the EHT "zoom" frequency band.
Conventionally, in order of increasing frequency, the bands are named 1, 2, 3, and 4.

.. note::

    The 2017 campaign has only two bands named "lo" and "hi". The shell scripts driving the calibration are aware of this
    and will make the appropriate substitutions for 2017 data, mapping "lo" -> "b3" and "hi" -> "b4".

The main pipeline script *ehthops/ehthops_pipeline.sh* takes the filename of a configuration file as argument and proceeds to
run the calibration. A sample configuration file *ehthops/settings.config* shows all the keywords that can be set to control the
calibration process. The user can create a copy of this file and modify it as needed. *ehthops_pipeline.sh* must be run from
within the **hops-bx** directories.

For this tutorial, we will use the "lo" band, so we will copy the driver script to **hops-b3**:

.. code-block:: bash

    cd hops-b3/
    cp ../ehthops_pipeline.sh .
    cp ../settings.config .

.. note::

    The script **scripts/cleanup.sh** helps to quickly delete all output files created during calibration, leaving the **hops-bx**
    directories in a clean state. Copy this to the **hops-b3** directory and run `source cleanup.sh` to clean up the 
    directory when necessary.

Updating the configuration file for calibration
-----------------------------------------------

The sample configuration file *ehthops/settings.config* contains the following keywords:

- **SET_SRCDIR**: Base directory containing the Mk4 data to be processed.
- **SET_CORRDAT**: List of paths (or simple directory names such as correlator data tags/releases) relative to SRCDIR separated by ':'.
- **SET_METADIR**: Directory where campaign metadata are to be found. Normally found under *ehthops/ehthops/meta*.
- **SET_EHTIMPATH**: Path to eht-imaging source code.
- **stages**: Stages to run (i.e. directory names found under *hops-bx*) as a space-separated string.
- **SET_OBSYEAR**: 4-letter code representing year of observation.
- **SET_MIXEDPOL**: Boolean value. Set this to true to request mixedpol calibration. This will assume that all ALMA data are in linear polarization basis while the rest are in circular polarization basis.
- **SET_HAXP**: Boolean value. Set this to true to indicate that ALMA linear polarization data are present in *-haxp* directories and must replace circularly polarized ALMA data originally linked from *-hops* directories. Setting this to true will automatically set MIXEDPOL=true.
- **SET_CAMPAIGN**: An EAT-recognizable code; currently EHT2017, EHT2018, EHT2021, EHT2022 are supported.
- **SET_INPUTDIR**: Input directory for post-processing stages. This is different for different stages and must be re-set for each post-processing stage. More details could be found in the sample *settings.config* file in the repository.

For this tutorial, we will assign the following values to the keywords:

  .. code-block:: bash

      SET_SRCDIR="/home/user/calibration/data/extracted"
      SET_CORRDAT="2016.1.01154.V"
      SET_METADIR="/home/user/calibration/ehthops/meta/eht2017/230GHz"
      SET_EHTIMPATH="/home/user/software/eht-imaging"
      stages="0.bootstrap 1.+flags+wins 2.+pcal 3.+adhoc 4.+delays 5.+close 6.uvfits"
      SET_YEAR="2017"
      SET_MIXEDPOL=true
      SET_HAXP=true
      SET_CAMPAIGN="EHT2017"
      SET_INPUTDIR=""

More information on how to determine the values of the command-line options can be found :ref:`here <command-line-options>`.

Submitting the calibration job to SLURM
---------------------------------------

A sample configuration file for submitting the job to SLURM follows (also found in **scripts/ehthops_slurm.job**):

.. code-block:: bash

    #!/bin/bash
    #SBATCH -c 48 # Number of cores requested
    #SBATCH -t 1-00:00:00 # Runtime
    #SBATCH -p blackhole # Partition
    #SBATCH --mem=64G # Memory per node in MB (--mem or --mem-per-cpu)
    #SBATCH -e slurm-%j.err
    #SBATCH -o slurm-%j.out

    # Set up env -- this may be different for different systems; the following are reasonable guidelines

    # source default bash settings from user's bashrc file.
    source $HOME/.bashrc

    # Activate the mamba environment with the necessary packages installed.
    mamba activate nseht310

    # Uncomment the following line if it is not present in your $HOME/.bashrc file or has not been run until now. In this case, the
    # bashrc file above contains this line, so it has been commented out. This is required to set up the HOPS environment properly.
    # source /n/holylfs05/LABS/bhi/Lab/doeleman_lab/inatarajan/software/installed/hops-3.24/bin/hops.bash

    # Set up HOPS environment once again with HOPS_SETUP=false (necessary to pick up all the HOPS environment variables properly).
    HOPS_SETUP=false source /n/holylfs05/LABS/bhi/Lab/doeleman_lab/inatarajan/software/installed/hops-3.24/bin/hops.bash

    # run script
    source ehthops_pipeline.sh -c settings.config

The environment setup lines may be different for different systems. The user should modify these lines as needed.
The correct python environment and HOPS setup must be activated before running the calibration script.
This config file can now be submitted to SLURM with **sbatch**:

.. code-block:: bash

    sbatch ehthops_slurm.job