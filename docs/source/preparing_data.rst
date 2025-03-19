==================
Preparing the data
==================

The output of the DiFX software correlator ("Level 1" or L1 data) converted to mk4 format is the standard input to HOPS.
These data are usually organized such that each scan has its own directory and multiple scan directories are grouped together in a
single directory corresponding to an epoch/track/HOPS expt number.

We will calibrate the publicly available L1 data from the EHT 2017 observing campaign for this tutorial.
These data can be downloaded either from the `ALMA Science Portal <https://almascience.nrao.edu/almadata/ec/eht/>`_ or `CyVerse Data Commons (DOI: 10.25739/kat4-na03) <https://datacommons.cyverse.org/browse/iplant/home/shared/commons_repo/curated/EHTC_2017L1_May2022>`_.

For this tutorial, we will download the data from the directory **2016.1.01154.V**:

.. code-block:: bash

    cd /home/user/calibration/data
    wget -r -np -nH --cut-dirs=3 -A "*-hops.tgz,*-haxp.tgz" https://almascience.nrao.edu/almadata/ec/eht/2016.1.01154.V/

The **\*-hops.tgz** files consist of the final correlated data (in which ALMA correlations have been converted to circular
polarization basis), while the **\*-haxp.tgz** files contain the mixedpol ALMA-only data.

.. note::

    If the **-x** option is passed to **0.launch**, the ALMA data in the **-haxp** directories will replace the polconverted
    **-hops** ALMA data during calibration. In this tutorial, we concern ourselves only with the polconverted data in **-hops**.
    
Untar the data to the destination directory **/home/user/calibration/data/extracted/2016.1.01154.V** using the following script:

.. code-block:: bash

    SRCDIR=/home/user/calibration/data/2016.1.01154.V
    DESTDIR=/home/user/calibration/data/extracted/2016.1.01154.V

    # Get a list of all .tgz files in the current directory
    for file in $SRCDIR/*.tgz; do
            # Create a directory named after the file (without the .tgz extension)
            fname_without_ext=$(basename "${file%.tgz}")
            destdir_full="$DESTDIR/$fname_without_ext"
            mkdir -p $destdir_full

            # Extract the contents of the .tgz file into the newly created directory
            tar -xvzf "$file" -C "$destdir_full"
    done

The extracted data will be organized as follows:

.. code-block:: bash

    /home/user/calibration/data/extracted/2016.1.01154.V
    ├── group.uid___A001_X11a7_X37.ec_eht.e17b06-7-hi-m87-3C273-hops
    │   ├── 3598
    │   │   ├── 096-0046
    │   │   ├── 096-0122
    │   │   ├── 096-0158
    │   │   ├── 096-0218
    │   │   ├── 096-0254
    │   │   └── 096-0332
    │   │   └── <more scan directories>
    │   ├── <more expt directories>
    ├── <more top level directories by group>

The data are now ready for calibration.