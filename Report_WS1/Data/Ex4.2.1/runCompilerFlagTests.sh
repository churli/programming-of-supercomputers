#!/bin/bash

# Idea is to first build all the binaries with all the combinations, 
# on the login node, then we schedule one big job which runs them all.
#
# We should be able to safely assume that 2h30m are ok for the entire task.

# To enable flags we uncomment an append instruction in the makefile

module load gcc/4.9
module load intel/17.0

# Enable GCC set of variables
#compiler="gcc"
# #flags=( "march=native" ) #test
#flags=( "march=native" "fomit-frame-pointer" "floop-block" "floop-interchange" "floop-strip-mine" "funroll-loops" "flto" ) #gcc

# Enable ICC set of variables
compiler="icc"
flags=( "march=native" "xHost" "unroll" "ipo" ) #icc

sandbox="Sandboxes/FlagTest/${compiler}"
template="${compiler}.serial.testFlags"
target="${compiler}.serial.testFlags.tmp"
makefile="Makefile.d/Makefile.${target}"
mkdir -p ${sandbox}

numFlags=${#flags[@]}
numComb=$[2**numFlags]

# Now customize the submission script
cp ll-job-testFlags.template.sh ${sandbox}/ll-job-testFlags.sh
sed -i s/"<compiler>"/"${compiler}"/ ${sandbox}/ll-job-testFlags.sh
fstr="${flags[@]}"
sed -i s/"<flags>"/"( ${fstr} )"/ ${sandbox}/ll-job-testFlags.sh
chmod +x ${sandbox}/ll-job-testFlags.sh

# Now build all the combinations
for (( k=0; k<numComb; k++ )); do
    # Every time reset the makefile to the template one!
    cp Makefile.d/Makefile.${template} ${makefile}
    # Now check what flag to add
    for (( i=0; i<numFlags; i++ )); do
        # Here select the flags according to the combination number
        flagSwitch=$[k>>i&1]
        if [[ $flagSwitch -eq 1 ]]; then
            curFlag="${flags[i]}"
            # Add flag to makefile
            sed -i s/"# <addFlagsHere>"/"# <addFlagsHere>\nCXXFLAGS += -${curFlag}\nLDFLAGS += -${curFlag}"/ ${makefile}
        fi
    done
    ### If you want to enable gmon.out, uncomment the below
    # sed -i s/"# <addFlagsHere>"/"# <addFlagsHere>\nCXXFLAGS += -pg"/ ${makefile}
    # sed -i s/"# <addFlagsHere>"/"# <addFlagsHere>\nLDFLAGS += -pg"/ ${makefile}
    
    # Build
    ./build.sh ${target}
    mv lulesh2.0.${target} ${sandbox}/lulesh2.0.testFlags.${compiler}.${k} # Each build has its own binary
    cp ${makefile} ${sandbox}/Makefile.testFlags.${compiler}.${k}
done

pushd ${sandbox}
    llsubmit ll-job-testFlags.sh
    #./ll-job-testFlags.sh
popd

#eof

