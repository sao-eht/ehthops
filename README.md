# ehthops
EHT-HOPS calibration pipeline for mm-VLBI observations

## Documentation

[![Documentation Status](https://readthedocs.org/projects/ehthops/badge/?version=latest)](https://ehthops.readthedocs.io/en/latest/?badge=latest)

## Quickstart

The EHT-HOPS pipeline is managed by the fast Python package manager `uv`. The best way to install `uv` on an HPC cluster is via `pipx`.
Install pipx [via pip](https://pipx.pypa.io/stable/installation/) or [from source](https://github.com/pypa/pipx) and ensure it is in your `PATH`.
Then install `uv` via `pipx`:
```bash
pipx install uv
```

`uv` should now be available in `PATH`. Clone `ehthops` from GitHub and set up the uv environment:
```bash
git clone https://github.com/sao-eht/ehthops.git
cd ehthops
uv sync --all-extras
source .venv/bin/activate
uv pip install -e </path/to/eat/source/code>    # mandatory
uv pip install -e </path/to/eht-imaging/source/code>   # optional -- necessary only for post-processing (including stage 6)
```
`EAT` can be obtained [here](https://github.com/sao-eht/eat)), while `eht-imaging` can be obtained [here](https://github.com/achael/eht-imaging/)).
Ensure that you clone the `dev` branch of `eht-imaging` locally.

Once the above environment is set up and activated, `ehthops` stages can either be run manually or as a pipeline using the default script
`scripts/ehthops_pipeline.sh`. The SLURM script `scripts/ehthops_slurm.job` can be used to run the pipeline on a SLURM cluster.
```bash
cd ehthops/scripts
cp ehthops_pipeline.sh settings.config ehthops_slurm.job ../hops-b4 # assuming we are reducing band 4 data
cd ../hops-b4
sbatch --export=CONFIG_FILE=/path/to/setting.config ehthops_slurm.job
```
Note that if `CONFIG_FILE` is not supplied, a configuration file named `settings.config` is assumed to be present in the current directory.

Always ensure that the values in `settings.config` are correct. For a complete description of the pipeline and tutorial, refer to the documentation linked above.
