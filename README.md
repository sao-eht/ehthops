# ehthops
EHT-HOPS calibration pipeline for mm-VLBI observations

## Documentation

[![Documentation Status](https://readthedocs.org/projects/ehthops/badge/?version=latest)](https://ehthops.readthedocs.io/en/latest/?badge=latest)

## Quickstart

The entire pipeline can be run on a SLURM cluster as follows (we assume b4 data is being processed):

```bash
git clone https://github.com/sao-eht/ehthops.git
cd ehthops/scripts
cp ehthops_pipeline.sh settings.config ehthops_slurm_v2.job ../ehthops/hops-b4
cd ../ehthops/hops-b4
sbatch --export=EAT_SOURCE_CODE=/n/holylfs05/LABS/bhi/Lab/doeleman_lab/inatarajan/software/src/eat,EHTIM_SOURCE_CODE=/n/holylfs05/LABS/bhi/Lab/doeleman_lab/inatarajan/software/src/eht-imaging,CONFIG_FILE=settings.config ehthops_slurm_v2.job
```

Some points to note:

- Providing EAT_SOURCE_CODE to sbatch is mandatory since EAT contains all the calibration routines.
- Providing EHTIM_SOURCE_CODE is not mandatory, but required if post-processing (stages 6/7/8) is being requested.
- If CONFIG_FILE is not supplied, a configuration file named __settings.config__ is assumed to be present in the current directory.

For a complete description of the pipeline and tutorial, refer to the documentation linked above.
