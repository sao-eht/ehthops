# ehthops
EHT-HOPS calibration pipeline for mm-VLBI observations

## Documentation

[![Documentation Status](https://readthedocs.org/projects/ehthops/badge/?version=latest)](https://ehthops.readthedocs.io/en/latest/?badge=latest)

## Quickstart

The EHT-HOPS pipeline is managed by the fast Python package manager `uv`. The best way to install uv on an HPC cluster is via `pipx`.
[Install pipx](https://pipx.pypa.io/stable/installation/) (alternatively, [from source](https://github.com/pypa/pipx)) and install `uv` via `pipx`:
```bash
pipx install uv
```

`uv` should now be available in `PATH`. The entire pipeline can be run on a `SLURM` cluster as follows (we assume b4 data are being processed):
```bash
git clone https://github.com/sao-eht/ehthops.git
cd ehthops/ehthops/scripts
cp ehthops_pipeline.sh settings.config ehthops_slurm_v2.job ../hops-b4
cd ../hops-b4
sbatch --export=EAT_SOURCE_CODE=/path/to/eat,EHTIM_SOURCE_CODE=/path/to/eht-imaging,CONFIG_FILE=/path/to/configfile ehthops_slurm_v2.job
```

Things to note:

- Providing `EAT_SOURCE_CODE` to `sbatch` is mandatory since `eat` contains all the calibration routines.
- Providing `EHTIM_SOURCE_CODE` is not mandatory, but required if post-processing (stages 6/7/8) is being requested.
- If `CONFIG_FILE` is not supplied, a configuration file named `settings.config` is assumed to be present in the current directory.

Always ensure that the values in `settings.config` are correct. For a complete description of the pipeline and tutorial, refer to the documentation linked above.
