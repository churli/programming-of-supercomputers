#!/bin/bash
#@ notification = complete
#@ notify_user = bianucci@in.tum.de
#@ wall_clock_limit = 02:30:00
#@ job_name = pos-lulesh-testFlags-<compiler>
#@ job_type = MPICH
#@ class = fat
#@ output = pos_lulesh_testFlags_$(jobid).out
#@ error = pos_lulesh_testFlags_$(jobid).out
#@ node = 1
#@ total_tasks = 40
#@ node_usage = not_shared
#@ energy_policy_tag = lulesh
#@ minimize_time_to_solution = yes
#@ island_count = 1
#@ queue

../etc/profile
/etc/profile.d/modules.sh

# The below are replaced automatically with the actual number of binaries to run!
flags=<flags>
compiler=<compiler>
###

csv="results_${compiler}.csv"

numFlags=${#flags[@]}
numComb=$[2**numFlags]

touch ${csv}
# Write results header
flagsStr=$(echo ${flags[@]} | sed s/" "/","/g)
echo "k,${flagsStr},CumulativeTimeSec,Speedup" > ${csv}

baseline=0
speedup=1
flagMask=()
for (( k=0; k<numComb; k++ )); do
	bin="lulesh2.0.testFlags.${compiler}.${k}"
	elapsedTimeSec=$(./${bin} | grep "Elapsed time" | grep -o "[0-9.]\+")
	# cp gmon.out gmon.testFlags.out.${compiler}.${k}
	# cumulativeTimeSec=$(gprof -b -p ${bin} gmon.out \
	# 	| tee gprof.testFlags.out.${compiler}.${k} \
	# 	| tail -n 1 \
	# 	| awk '{print $2}')
	cumulativeTimeSec=${elapsedTimeSec}
	
	# Compute the speedup
	if [[ k -eq 0 ]]; then
		baseline=${cumulativeTimeSec}
		speedup=1
	else
		speedup=$(echo "scale=3; ${baseline} / ${cumulativeTimeSec}" | bc)
	fi
	# Now compute the flag mask
	for (( i=0; i<numFlags; i++ )); do
		flagSwitch=$[k>>i&1]
		flagMask[i]=${flagSwitch}
	done
	flagMaskStr=$(echo ${flagMask[@]} | sed s/" "/","/g)
	# Now write the csv entry
	csvEntry="${k},${flagMaskStr},${cumulativeTimeSec},${speedup}"
	echo "${csvEntry}" >> ${csv}
done

#eof
