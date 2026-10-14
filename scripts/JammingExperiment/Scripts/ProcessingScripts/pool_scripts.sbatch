#!/bin/bash 
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1   # only start 1 task via srun because Python multiprocessing starts more tasks internally
#SBATCH --cpus-per-task=128  
#SBATCH --time 24:00:00

#SBATCH --output=/viper/u1/amoger/bat-swarm-model/slurm_logs/jammingexperiment_14_10_%j.out
#SBATCH --error=/viper/u1/amoger/bat-swarm-model/slurm_logs/jammingexperiment_14_10_%j.err

#SBATCH --job-name=dynamic_model
#SBATCH --mail-type=ALL
#SBATCH --mail-user=aditya.moger@uni-konstanz.de


# Recommended: prevent nested threading inside each worker process
# export OMP_NUM_THREADS=1
# export MKL_NUM_THREADS=1
# export OPENBLAS_NUM_THREADS=1
# export NUMEXPR_NUM_THREADS=1


module load anaconda/3/2023.03

conda init bash
source ~/.bashrc
conda activate /u/amoger/conda-envs/dynamic_model

# Use srun inside allocations (good Slurm hygiene)
srun --ntasks=1 --cpus-per-task="${SLURM_CPUS_PER_TASK}" \
  python -u \
  scripts/JammingExperiment/Scripts/ProcessingScripts/run_sweep.py \
  -m \
    bat.CALL_RATE_FAST=10,20 \
    bat.CALL_DIRECTIONALITY=4,7,10 \
    bat.EMITTED_SPL=80,100,140 \
    bat.HEARING_THRESHOLD=20,40,60,80 \
    bat.BAT_RADIAL_RESOLUTION=0.002,0.004,0.006 \
    bat.BAT_ANGULAR_RESOLUTION=15,30,60 \
    bat.BAT_FRONTAL_RANGE=30,60,90 \
    bat.CONSISTENCY_TIME_DELAY_CAP=0.008,0.011,0.014,0.026 \
    bat.MEMORY_WINDOW_FOR_CONSISTENCY=1,3,5,7 \
    arena.seed=55,89,144,233,377