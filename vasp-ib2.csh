#!/bin/tcsh
#

#$ -q ib2.q
#$ -N log-ib2
#$ -pe ib-hydra 16
#$ -cwd

date
module add mvapich2-intel

source /cluster/caml/intel/bin/compilervars.csh intel64

echo $LD_LIBRARY_PATH

/cluster/caml/mvapich2-intel/bin/mpiexec /cluster/caml/vasp-5.3-intel/vasp.ib.5.3.3


date

exit 0
