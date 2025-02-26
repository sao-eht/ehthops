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

.. toctree::
   :maxdepth: 2
   :caption: Contents

   preparing_data
   setting_up_calibration
   inspecting_output
