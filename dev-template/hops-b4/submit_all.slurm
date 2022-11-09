#!/bin/bash
#SBATCH -c 48 # Number of cores requested
#SBATCH -t 20:00:00 # Runtime
#SBATCH -p shared # Partition
#SBATCH --mem-per-cpu=2048 # Memory per node in MB (--mem or --mem-per-cpu)
#SBATCH -e slurm-%j.err
#SBATCH -o slurm-%j.out

# run script
./run_all.sh
