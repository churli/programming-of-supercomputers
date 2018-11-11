#!/bin/bash

#if [[ $# -ne 1 || ! ( "$1" == "serial" || "$1" == "OMP" || "$1" == "MPI" || "$1" == "hybrid" ) ]]; then
if [[ $# -ne 1 ]]; then
	echo "You need to pass one of the following as argument:"
	echo "serial, OMP, MPI, hybrid"
	exit 1
fi

T="$1"

module unload mpi.ibm
module load mpi.intel

unlink Makefile
ln -s Makefile.d/Makefile.${T} Makefile
make clean
make
cp lulesh2.0 lulesh2.0.${T}

#eof

