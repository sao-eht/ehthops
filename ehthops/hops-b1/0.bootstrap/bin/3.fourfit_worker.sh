#!/usr/bin/env bash
# fourfit_worker.sh — single fourfit array task
#
# Called by 3.fourfit via: sbatch --array=1-N%CAP ... --export=ALL,WRKDIR=...,FILELIST=...
#
# Each SLURM_ARRAY_TASK_ID maps to one line of FILELIST, which is a path to
# a HOPS root file (e.g. .../data/3597/094-2242/OJ287.0COHFB).
#
# Required env vars (all provided by the sbatch call in 3.fourfit):
#   WRKDIR            — stage working directory (not exported by 0.launch, passed explicitly)
#   FILELIST          — path to log/filelist.txt written by 3.fourfit
#   HOPS_SETUP_SCRIPT — path to hops.bash (exported by ehthops_slurm.job)

# Source bashrc, as in the main slurm job script.
source "$HOME/.bashrc"

# Also set up HOPS environment as it runs in a fresh environment where HOPS is not yet set up.
HOPS_SETUP=false source "$HOPS_SETUP_SCRIPT"

# uv venv not sourced since fourfit is a C binary and does not need Python

# Look up this task's root file (array is 1-indexed to match filelist line numbers)
ROOTFILE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$FILELIST")

if [[ -z "$ROOTFILE" ]]; then
    echo "ERROR: no entry for task $SLURM_ARRAY_TASK_ID in $FILELIST" >&2
    exit 1
fi

fourfit -c "$WRKDIR/temp/cf_all" "$ROOTFILE" \
    > "$ROOTFILE.out" \
    2> "$ROOTFILE.err"
