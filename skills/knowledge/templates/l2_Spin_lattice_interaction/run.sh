#!/bin/bash
#SBATCH --job-name=NiI2_MC_CG
#SBATCH -p p1
#SBATCH --output=slurm-%x-%j.o
#SBATCH --error=slurm-%x-%j.e
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32

module load oneapi/2023.2

ulimit -s unlimited

cd "$SLURM_SUBMIT_DIR" || exit
NP=$SLURM_NTASKS

echo "start" "$(date)"

mpirun -np "$NP" "/data/app/sh2025/pasp/bin/PASP.x" >log.out
mkdir node_data
mv T_* *node* Each* final* node_data

echo "finished" "$(date)"
