import matplotlib.pyplot as plt 

with open("omp_gnu") as f:
	data = f.read().split("\n")
	time_data = []
	for x in data:
		try:
			time_data.append(float(x.split(",")[1]))
		except:
			pass

	speedup_data = [time_data[0]/x for x in time_data]
	# print(max(speedup_data))
	print(min(time_data))
	print(speedup_data.index(max(speedup_data)))

# with open("OMP GNU Compiler Results", "w") as f:
# 	for x in range(1,41):
# 		f.write("Test " + str(x) + "\nnode = srv03-ib\ntotal_tasks = 40\nOMP threads = " + str(x) + "\ntime = " + str(time_data[x-1]) + "\n\n")


# plt.plot(range(1,41), time_data)
# plt.title("GNU++ Compiler, -march=native -funroll-loops, srv03-ib")
# plt.xlabel("Time (s)")
# plt.ylabel("# of Processors")

# plt.show()

plt.plot(range(1,41), speedup_data, marker="o")
plt.title("GNU++ Compiler, -march=native -funroll-loops, srv03-ib")
plt.ylabel("Speedup")
plt.xlabel("# OpenMP Threads")

plt.show()