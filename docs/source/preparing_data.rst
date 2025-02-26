==================
Preparing the data
==================

The output of the DiFX software correlator ("Level 1" or L1 data) converted to mk4 format is the standard input to HOPS.
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
    
Untar the data to the directory **/home/user/calibration/data/extracted/2016.1.01154.V**:

.. code-block:: bash

    mkdir -p extracted/2016.1.01154.V
    find 2016.1.01154.V -name "*.tgz" -exec tar -xvzf {} -C "extracted/2016.1.01154.V" \;