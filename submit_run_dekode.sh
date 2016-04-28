#!/bin/tcsh
#
#$ -cwd
#$ -q ib1.q
#$ -N all_dekode_jobs
#$ -pe ib-hydra 8

date

module add mpich2-intel
module add software-2014

nohup python run_dekode_for.py 

date

exit 0
