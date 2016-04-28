#!/bin/tcsh
#
#$ -cwd
#$ -q ib1.q
#$ -N python_job
#$ -pe ib-hydra 1

date

module add mpich2-intel
module add software-2014

# For parallel python (not necesarilly GPAW)
# mpirun -np 8 gpaw-python dekode.py

# For non-parallel python
#nohup python dekode.py &
nohup python dekode.py 

date

exit 0
