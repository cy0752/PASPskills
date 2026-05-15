#!/bin/bash
#SBATCH --job-name=pasp
#SBATCH --partition=p1
#SBATCH --nodes=1
#SBATCH --ntasks=40
#SBATCH --cpus-per-task=1
#SBATCH --time=120:00:00
#SBATCH --output=pasp.%j.out
#SBATCH --error=pasp.%j.err

module purge
module load oneapi/2023.2

ulimit -s unlimited

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OMP_STACKSIZE=256M

BIN_DIR=/path/to/pasp/bin

mpirun -np $SLURM_NTASKS ${BIN_DIR}/PASP.x

exit 0
