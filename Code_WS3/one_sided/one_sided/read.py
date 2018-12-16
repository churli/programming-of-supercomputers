import re
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from os.path import join

deckSize = {"io": 0, "setup": 1, "compute": 2, "MPI": 3, "total":4}
sizes = [64, 512, 1024, 2048, 4096, 8192]
process = [8, 16, 32, 64]

X, Y = np.meshgrid(process, sizes)

PIC_DIRECTORY = "/home/keefe/Documents/TUM/Sem3/IN2190/Assignment3/one_sided_figure"

class OutputData:
	def __init__(self, fileName, isUpdated=False, entries=5):
		self.timeData = self.readOut(fileName)

		if isUpdated:
			temp = None
			self.data = []
			for i in range(24):
				temp = self.timeData[i*entries] + self.timeData[i*entries + 1] + self.timeData[i*entries + 2] + self.timeData[i*entries + 3] + self.timeData[i*entries + 4]
				temp /= entries
				self.data.append(temp)
			self.data = np.array(self.data)
		else:
			self.data = self.timeData

		self.deckSize = self.data[0][0].shape[0]
		self.totalEntries = self.data.shape[0]
		self.sizes = 6
		self.numProc = 4

	def readOut(self, fileName):
		with open(fileName) as f:
			data = f.readlines()
			tickets = []
			ticketStarted = False
			for line in data:
				if ticketStarted:
					if "Solving the" in line:
						tickets.append(ticket)
						ticket = line
					else:
						ticket += line
				else:
					if "Solving the" in line:
						ticket = line
						ticketStarted = True
					else:
						continue
			tickets.append(ticket)

		patternSetup = re.compile("IO.*(?=;)")
		timeData = []
		for ticket in tickets:
			data = None
			for line in ticket.split("\n"):
				rawLineData = re.search(patternSetup, line)
				try:
					lineData = np.array([float(re.split(";|:", rawLineData.group(0))[i]) for i in (1,3,5,7,9)])
					lineData[2] = lineData[2] - lineData[3]
					lineData = lineData.reshape((1,-1))
					if data is None:
						data = lineData
					else:
						data = np.append(data, lineData, axis=0)
				except:
					pass			

			# print(data.shape)
			timeData.append(data)


		return np.array(timeData)

	def IOData(self):
		loc = deckSize["io"]
		ioData = np.zeros((self.totalEntries,))
		for i, data in enumerate(self.data):
			ioData[i] = data[-1][loc]

		s = None
		for i in range(4):
			if s is None:
				s = ioData[i::4]
			else:				
				s = s + ioData[i::4]
		ioData = s/4

		return ioData

	def setupData(self):
		loc = deckSize["setup"]
		setupData = np.zeros((self.sizes, self.numProc))
		for i in range(self.sizes):
			for j in range(self.numProc):
				# print(np.max(self.data[i*self.numProc + j][:,loc]))
				setupData[i, j] = np.max(self.data[i*self.numProc + j][:,loc])

		return setupData

	def computeData(self):
		loc = deckSize["compute"]
		computeData = np.zeros((self.sizes, self.numProc))
		for i in range(self.sizes):
			for j in range(self.numProc):
				# print(np.max(self.data[i*self.numProc + j][:,loc]))
				computeData[i, j] = np.average(self.data[i*self.numProc + j][:,loc])

		return computeData

	def MPIData(self):
		loc = deckSize["MPI"]
		MPIData = np.zeros((self.sizes, self.numProc))
		for i in range(self.sizes):
			for j in range(self.numProc):
				# print(np.max(self.data[i*self.numProc + j][:,loc]))
				MPIData[i, j] = np.max(self.data[i*self.numProc + j][:,loc])
		return MPIData

	def MPIData_min(self):
		loc = deckSize["MPI"]
		MPIData = np.zeros((self.sizes, self.numProc))
		for i in range(self.sizes):
			for j in range(self.numProc):
				# print(np.max(self.data[i*self.numProc + j][:,loc]))
				MPIData[i, j] = np.min(self.data[i*self.numProc + j][:,loc])
		return MPIData	

	def MPIData_max(self):
		loc = deckSize["MPI"]
		MPIData = np.zeros((self.sizes, self.numProc))
		for i in range(self.sizes):
			for j in range(self.numProc):
				# print(np.max(self.data[i*self.numProc + j][:,loc]))
				MPIData[i, j] = np.max(self.data[i*self.numProc + j][:,loc])
		return MPIData	

	def totalData(self):
		loc = deckSize["total"]
		TotalData = np.zeros((self.sizes, self.numProc))
		for i in range(self.sizes):
			for j in range(self.numProc):
				# print(np.max(self.data[i*self.numProc + j][:,loc]))
				TotalData[i, j] = np.average(self.data[i*self.numProc + j][:,loc])
		return TotalData

if __name__ == '__main__':

	manager = plt.get_current_fig_manager()
	manager.resize(*manager.window.maxsize())

	fileName = "wm_baseline.out"
	dataHaswellBaseline = OutputData(fileName, isUpdated=True)

	fileName = "sb_baseline.out"
	dataSandyBaseline = OutputData(fileName, isUpdated=True)

	fileName = "wm_nb.out"
	dataHaswellNB = OutputData(fileName, isUpdated=True)

	fileName = "sb_nb.out"
	dataSandyNB = OutputData(fileName, isUpdated=True)

	fileName = "wm_os.out"
	dataHaswellOS = OutputData(fileName, isUpdated=True)

	fileName = "sb_os.out"
	dataSandyOS = OutputData(fileName, isUpdated=True)

	# plt.title("IO Time vs Size of Domain")
	# plt.xlabel("Domain (# Cells in Domain Length)")
	# plt.ylabel("Time (s)")
	
	# plt.plot(sizes, IOdataHaswellNB, label="Haswell", ls="-.")
	# plt.plot(sizes, IOdataSandyNB, label="Sandy Bridge")
	# plt.legend()
	# plt.savefig(join(PIC_DIRECTORY, "./IO.png"))
	# plt.show()
	# fig = plt.figure()
	# ax = Axes3D(fig)
	# ax = plt.gca(projection='3d')
	# ax.set_title("Setup Time vs Size of Domain vs Num Processes for Haswell")
	# ax.set_xlabel("Num Processes")
	# ax.set_ylabel("Domain")
	# ax.set_zlabel("Time (s)")

	# ax.contour3D(X, Y, setupDataHaswell, label="Haswell")
	# ax.contour3D(X, Y, setupdataHaswellNB, label="Averaged Haswell")
	# ax.contour3D(X, Y, setupDataSandy, label="Sandy Bridge")
	# ax.contour3D(X, Y, setupdataSandyNB, label="Averaged Sandy Bridge")
	# ax.plot_surface(X, Y, setupDataHaswell)
	# ax.plot(X, Y, setupdataHaswellNB, label="Haswell")
	# ax.plot(X, Y, setupdataSandyNB, label="Sandy Bridge")
	# ax.plot_surface(X, Y, setupdataHaswellNB)	
	# ax.plot_surface(X, Y, setupdataSandyNB)
	# plt.show()
	# plt.savefig(join(PIC_DIRECTORY, "./setup.png"))

	# ax.legend()
	# ax.savefig(join(PIC_DIRECTORY, "./setup.png"))
	


	# fig = plt.figure(figsize=(14,9))
	# plt.title("Setup Time vs. Num Processes, Non-blocking Comm")
	# plt.xlabel("Processes")
	# plt.ylabel("Time (s)")

	# ax = plt.subplot(111)
	# box = ax.get_position()
	# ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	
	# plt.loglog(process, dataHaswellNB.setupData()[0,:], label="Non-Blocking, Domain = 64", ls="-.", color="blue")
	# plt.loglog(process, dataHaswellNB.setupData()[1,:], label="Non-Blocking, Domain = 512", ls="-.", color="red")
	# plt.loglog(process, dataHaswellNB.setupData()[2,:], label="Non-Blocking, Domain = 1024", ls="-.", color="orange")
	# plt.loglog(process, dataHaswellNB.setupData()[3,:], label="Non-Blocking, Domain = 2048", ls="-.", color="green")
	# plt.loglog(process, dataHaswellNB.setupData()[4,:], label="Non-Blocking, Domain = 4096", ls="-.", color="brown")
	# plt.loglog(process, dataHaswellNB.setupData()[-1,:], label="Non-Blocking, Domain = 8192", ls="-.", color="purple")


	# plt.loglog(process, dataHaswellBaseline.setupData()[0,:], label="Baseline, Domain = 64", ls="-.", color="blue")
	# plt.loglog(process, dataHaswellBaseline.setupData()[1,:], label="Baseline, Domain = 512", ls="-.", color="red")
	# plt.loglog(process, dataHaswellBaseline.setupData()[2,:], label="Baseline, Domain = 1024", ls="-.", color="orange")
	# plt.loglog(process, dataHaswellBaseline.setupData()[3,:], label="Baseline, Domain = 2048", ls="-.", color="green")
	# plt.loglog(process, dataHaswellBaseline.setupData()[4,:], label="Baseline, Domain = 4096", ls="-.", color="brown")
	# plt.loglog(process, dataHaswellBaseline.setupData()[-1,:], label="Baseline, Domain = 8192", ls="-.", color="purple")


	# plt.loglog(process, dataSandyNB.setupData()[0,:], label="Sandy Bridge, Domain = 64", color="blue")
	# plt.loglog(process, dataSandyNB.setupData()[1,:], label="Sandy Bridge, Domain = 512", color="red")
	# plt.loglog(process, dataSandyNB.setupData()[2,:], label="Sandy Bridge, Domain = 1024", color="orange")
	# plt.loglog(process, dataSandyNB.setupData()[3,:], label="Sandy Bridge, Domain = 2048", color="green")
	# plt.loglog(process, dataSandyNB.setupData()[4,:], label="Sandy Bridge, Domain = 4096", color="brown")
	# plt.loglog(process, dataSandyNB.setupData()[-1,:], label="Sandy Bridge, Domain = 8192", color="purple")

	# plt.loglog(process, dataSandyBaseline.setupData()[0,:], label="Sandy Bridge, Domain = 64", color="blue")
	# plt.loglog(process, dataSandyBaseline.setupData()[1,:], label="Sandy Bridge, Domain = 512", color="red")
	# plt.loglog(process, dataSandyBaseline.setupData()[2,:], label="Sandy Bridge, Domain = 1024", color="orange")
	# plt.loglog(process, dataSandyBaseline.setupData()[3,:], label="Sandy Bridge, Domain = 2048", color="green")
	# plt.loglog(process, dataSandyBaseline.setupData()[4,:], label="Sandy Bridge, Domain = 4096", color="brown")
	# plt.loglog(process, dataSandyBaseline.setupData()[-1,:], label="Sandy Bridge, Domain = 8192", color="purple")

	# ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	# plt.savefig(join(PIC_DIRECTORY, "./setup_multidomain_mpi.png"))


	# fig = plt.figure(figsize=(14,9))
	# plt.title("Setup Time vs. Domain Size")
	# plt.xlabel("Domain Size")
	# plt.ylabel("Time (s)")
	# ax = plt.subplot(111)
	# box = ax.get_position()
	# ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

	# plt.plot(sizes, dataHaswellNB.setupData()[:,0], label="Haswell, # proc = 8", ls="-.", color="blue")
	# plt.plot(sizes, dataHaswellNB.setupData()[:,1], label="Haswell, # proc = 16", ls="-.", color="red")
	# plt.plot(sizes, dataHaswellNB.setupData()[:,2], label="Haswell, # proc = 32", ls="-.", color="orange")
	# plt.plot(sizes, dataHaswellNB.setupData()[:,3], label="Haswell, # proc = 64", ls="-.", color="green")
	
	# plt.plot(sizes, dataSandyNB.setupData()[:,0], label="Sandy Bridge, # proc = 8", color="blue")
	# plt.plot(sizes, dataSandyNB.setupData()[:,1], label="Sandy Bridge, # proc = 16", color="red")
	# plt.plot(sizes, dataSandyNB.setupData()[:,2], label="Sandy Bridge, # proc = 32", color="orange")
	# plt.plot(sizes, dataSandyNB.setupData()[:,3], label="Sandy Bridge, # proc = 64", color="green")
	# # plt.axis(ymin=0, ymax=20)
	# ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

	# # plt.show()
	# plt.savefig(join(PIC_DIRECTORY, "./setup_multiproc.png"))
	

	# fig = plt.figure(figsize=(14,9))
	# plt.title("Compute Time vs. Num Processes, Non-Blocking & One-Sided")
	# plt.xlabel("Processes")
	# plt.ylabel("Time (s)")

	# ax = plt.subplot(111)
	# box = ax.get_position()
	# ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

	# # plt.loglog(process, dataHaswellBaseline.computeData()[0,:], label="Baseline, Domain = 64", color="blue")	
	# # plt.loglog(process, dataHaswellBaseline.computeData()[1,:], label="Baseline, Domain = 512", color="red")
	# # plt.loglog(process, dataHaswellBaseline.computeData()[2,:], label="Baseline, Domain = 1024", color="orange")
	# # plt.loglog(process, dataHaswellBaseline.computeData()[3,:], label="Baseline, Domain = 2048", color="green")
	# # plt.loglog(process, dataHaswellBaseline.computeData()[4,:], label="Baseline, Domain = 4096", color="brown")
	# # plt.loglog(process, dataHaswellBaseline.computeData()[5,:], label="Baseline, Domain = 8192", color="purple")

	# # plt.loglog(process, dataHaswellNB.computeData()[0,:], label="Non-blocking, Domain = 64", ls="-.", color="blue")
	# # plt.loglog(process, dataHaswellNB.computeData()[1,:], label="Non-blocking, Domain = 512", ls="-.", color="red")
	# # plt.loglog(process, dataHaswellNB.computeData()[2,:], label="Non-blocking, Domain = 1024", ls="-.", color="orange")
	# # plt.loglog(process, dataHaswellNB.computeData()[3,:], label="Non-blocking, Domain = 2048", ls="-.", color="green")
	# # plt.loglog(process, dataHaswellNB.computeData()[4,:], label="Non-blocking, Domain = 4096", ls="-.", color="brown")
	# # plt.loglog(process, dataHaswellNB.computeData()[5,:], label="Non-blocking, Domain = 8192", ls="-.", color="purple")

	# # plt.loglog(process, dataHaswellOS.computeData()[0,:], label="One-Sided, Domain = 64", ls="dotted", color="blue")	
	# # plt.loglog(process, dataHaswellOS.computeData()[1,:], label="One-Sided, Domain = 512", ls="dotted", color="red")
	# # plt.loglog(process, dataHaswellOS.computeData()[2,:], label="One-Sided, Domain = 1024", ls="dotted", color="orange")
	# # plt.loglog(process, dataHaswellOS.computeData()[3,:], label="One-Sided, Domain = 2048", ls="dotted", color="green")
	# # plt.loglog(process, dataHaswellOS.computeData()[4,:], label="One-Sided, Domain = 4096", ls="dotted", color="brown")
	# # plt.loglog(process, dataHaswellOS.computeData()[5,:], label="One-Sided, Domain = 8192", ls="dotted", color="purple")



	# plt.loglog(process, dataSandyNB.computeData()[0,:], label="Non-Blocking, Domain = 64", ls="-.", color="blue")
	# plt.loglog(process, dataSandyNB.computeData()[1,:], label="Non-Blocking, Domain = 512", ls="-.", color="red")
	# plt.loglog(process, dataSandyNB.computeData()[2,:], label="Non-Blocking, Domain = 1024", ls="-.", color="orange")
	# plt.loglog(process, dataSandyNB.computeData()[3,:], label="Non-Blocking, Domain = 2048", ls="-.",color="green")
	# plt.loglog(process, dataSandyNB.computeData()[4,:], label="Non-Blocking, Domain = 4096", ls="-.",color="brown")
	# plt.loglog(process, dataSandyNB.computeData()[5,:], label="Non-Blocking, Domain = 8192", ls="-.",color="purple")

	# # plt.loglog(process, dataSandyBaseline.computeData()[0,:], label="Baseline, Domain = 64", color="blue")	
	# # plt.loglog(process, dataSandyBaseline.computeData()[1,:], label="Baseline, Domain = 512", color="red")
	# # plt.loglog(process, dataSandyBaseline.computeData()[2,:], label="Baseline, Domain = 1024", color="orange")
	# # plt.loglog(process, dataSandyBaseline.computeData()[3,:], label="Baseline, Domain = 2048", color="green")
	# # plt.loglog(process, dataSandyBaseline.computeData()[4,:], label="Baseline, Domain = 4096", color="brown")
	# # plt.loglog(process, dataSandyBaseline.computeData()[5,:], label="Baseline, Domain = 8192", color="purple")


	# plt.loglog(process, dataSandyOS.computeData()[0,:], label="One-Sided, Domain = 64", ls="dotted", color="blue")	
	# plt.loglog(process, dataSandyOS.computeData()[1,:], label="One-Sided, Domain = 512", ls="dotted", color="red")
	# plt.loglog(process, dataSandyOS.computeData()[2,:], label="One-Sided, Domain = 1024", ls="dotted", color="orange")
	# plt.loglog(process, dataSandyOS.computeData()[3,:], label="One-Sided, Domain = 2048", ls="dotted", color="green")
	# plt.loglog(process, dataSandyOS.computeData()[4,:], label="One-Sided, Domain = 4096", ls="dotted", color="brown")
	# plt.loglog(process, dataSandyOS.computeData()[5,:], label="One-Sided, Domain = 8192", ls="dotted", color="purple")

	# # plt.axis(ymin=0, ymax=20)
	# ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	# plt.savefig(join(PIC_DIRECTORY, "./compute_multdomain_sandy_os_nb.png"), bbox_inches="tight")


	# fig = plt.figure(figsize=(14,9))
	# plt.title("Compute Time vs. Domain Size, Baseline & One-Sided")
	# plt.xlabel("Domain Size")
	# plt.ylabel("Time (s)")


	# ax = plt.subplot(111)
	# box = ax.get_position()
	# ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
	
	# # plt.loglog(sizes, dataHaswellNB.computeData()[:,0], label="Non-blocking, # proc = 8", ls="-.", color="blue")
	# # plt.loglog(sizes, dataHaswellNB.computeData()[:,1], label="Non-blocking, # proc = 16", ls="-.", color="red")
	# # plt.loglog(sizes, dataHaswellNB.computeData()[:,2], label="Non-blocking, # proc = 32", ls="-.", color="orange")
	# # plt.loglog(sizes, dataHaswellNB.computeData()[:,3], label="Non-blocking, # proc = 64", ls="-.", color="green")

	# # plt.loglog(sizes, dataHaswellBaseline.computeData()[:,0], label="Baseline, # proc = 8", color="blue")
	# # plt.loglog(sizes, dataHaswellBaseline.computeData()[:,1], label="Baseline, # proc = 16", color="red")
	# # plt.loglog(sizes, dataHaswellBaseline.computeData()[:,2], label="Baseline, # proc = 32", color="orange")
	# # plt.loglog(sizes, dataHaswellBaseline.computeData()[:,3], label="Baseline, # proc = 64", color="green")

	# # plt.loglog(sizes, dataHaswellOS.computeData()[:,0], label="One-Sided, # proc = 8", ls="dotted", color="blue")
	# # plt.loglog(sizes, dataHaswellOS.computeData()[:,1], label="One-Sided, # proc = 16", ls="dotted", color="red")
	# # plt.loglog(sizes, dataHaswellOS.computeData()[:,2], label="One-Sided, # proc = 32", ls="dotted", color="orange")
	# # plt.loglog(sizes, dataHaswellOS.computeData()[:,3], label="One-Sided, # proc = 64", ls="dotted", color="green")
	
	
	# # plt.loglog(sizes, dataSandyNB.computeData()[:,0], label="Non-Blocking, # proc = 8", ls="-.", color="blue")
	# # plt.loglog(sizes, dataSandyNB.computeData()[:,1], label="Non-Blocking, # proc = 16", ls="-.", color="red")
	# # plt.loglog(sizes, dataSandyNB.computeData()[:,2], label="Non-Blocking, # proc = 32", ls="-.", color="orange")
	# # plt.loglog(sizes, dataSandyNB.computeData()[:,3], label="Non-Blocking, # proc = 64", ls="-.", color="green")
	
	# plt.loglog(sizes, dataSandyBaseline.computeData()[:,0], label="Baseline, # proc = 8", color="blue")
	# plt.loglog(sizes, dataSandyBaseline.computeData()[:,1], label="Baseline, # proc = 16", color="red")
	# plt.loglog(sizes, dataSandyBaseline.computeData()[:,2], label="Baseline, # proc = 32", color="orange")
	# plt.loglog(sizes, dataSandyBaseline.computeData()[:,3], label="Baseline, # proc = 64", color="green")


	# plt.loglog(sizes, dataSandyOS.computeData()[:,0], label="One-Sided, # proc = 8", ls="dotted", color="blue")
	# plt.loglog(sizes, dataSandyOS.computeData()[:,1], label="One-Sided, # proc = 16", ls="dotted", color="red")
	# plt.loglog(sizes, dataSandyOS.computeData()[:,2], label="One-Sided, # proc = 32", ls="dotted", color="orange")
	# plt.loglog(sizes, dataSandyOS.computeData()[:,3], label="One-Sided, # proc = 64", ls="dotted", color="green")

	# ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	# plt.savefig(join(PIC_DIRECTORY, "./compute_multiproc_sandy_os_baseline.png"))
	# # plt.show()
	
	

	# fig = plt.figure(figsize=(14,9))
	# plt.title("MPI Time vs. Domain Size, Non-Blocking & One-Sided")
	# plt.xlabel("Domain Size")
	# plt.ylabel("Time (s)")
	# ax = plt.subplot(111)
	# box = ax.get_position()
	# ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

	
	# # plt.loglog(sizes, dataHaswellNB.MPIData()[:,0], label="Non-Blocking, # proc = 8", ls="-.", color="blue")
	# # # plt.loglog(sizes, dataHaswellNB.MPIData_min()[:,0], color="blue", ls="-.")
	# # # ax.fill_between(sizes,dataHaswellNB.MPIData()[:,0],dataHaswellNB.MPIData_min()[:,0], color="powderblue")

	# # plt.loglog(sizes, dataHaswellNB.MPIData()[:,1], label="Non-Blocking, # proc = 16", ls="-.", color="red")
	# # # plt.loglog(sizes, dataHaswellNB.MPIData_min()[:,1], color="red", ls="-.")
	# # # ax.fill_between(sizes,dataHaswellNB.MPIData()[:,1],dataHaswellNB.MPIData_min()[:,1], color="mistyrose")

	# # plt.loglog(sizes, dataHaswellNB.MPIData()[:,2], label="Non-Blocking, # proc = 32", ls="-.", color="orange")
	# # # plt.loglog(sizes, dataHaswellNB.MPIData_min()[:,2], color="orange", ls="-.")
	# # # ax.fill_between(sizes,dataHaswellNB.MPIData()[:,2],dataHaswellNB.MPIData_min()[:,2], color="peachpuff")

	# # plt.loglog(sizes, dataHaswellNB.MPIData()[:,3], label="Non-Blocking, # proc = 64", ls="-.", color="green")
	# # # plt.loglog(sizes, dataHaswellNB.MPIData_min()[:,3], color="green", ls="-.")
	# # ax.fill_between(sizes,dataHaswellNB.MPIData()[:,3],dataHaswellNB.MPIData_min()[:,3], color="lightgreen")

	
	# # plt.loglog(sizes, dataHaswellBaseline.MPIData()[:,0], label="Baseline, # proc = 8", color="blue")

	# # plt.loglog(sizes, dataHaswellBaseline.MPIData()[:,1], label="Baseline, # proc = 16", color="red")

	# # plt.loglog(sizes, dataHaswellBaseline.MPIData()[:,2], label="Baseline, # proc = 32", color="orange")

	# # plt.loglog(sizes, dataHaswellBaseline.MPIData()[:,3], label="Baseline, # proc = 64", color="green")


	# # plt.loglog(sizes, dataHaswellOS.MPIData()[:,0], label="One-Sided # proc = 8", ls="dotted", color="blue")

	# # plt.loglog(sizes, dataHaswellOS.MPIData()[:,1], label="One-Sided # proc = 16", ls="dotted", color="red")

	# # plt.loglog(sizes, dataHaswellOS.MPIData()[:,2], label="One-Sided # proc = 32", ls="dotted", color="orange")

	# # plt.loglog(sizes, dataHaswellOS.MPIData()[:,3], label="One-Sided # proc = 64", ls="dotted", color="green")

	# plt.loglog(sizes, dataSandyNB.MPIData()[:,0], label="Non-Blocking, # proc = 8", ls="-.", color="blue")
	# # plt.loglog(sizes, dataSandyNB.MPIData_min()[:,0], color="blue")
	# # ax.fill_between(sizes,dataSandyNB.MPIData()[:,0],dataSandyNB.MPIData_min()[:,0], color="powderblue")
	# plt.loglog(sizes, dataSandyNB.MPIData()[:,1], label="Non-Blocking, # proc = 16", ls="-.", color="red")
	# # plt.loglog(sizes, dataSandyNB.MPIData_min()[:,1], color="red")
	# # ax.fill_between(sizes,dataSandyNB.MPIData()[:,1],dataSandyNB.MPIData_min()[:,1], color="mistyrose")
	# plt.loglog(sizes, dataSandyNB.MPIData()[:,2], label="Non-Blocking, # proc = 32", ls="-.", color="orange")
	# # plt.loglog(sizes, dataSandyNB.MPIData_min()[:,2], color="brown")
	# # ax.fill_between(sizes,dataSandyNB.MPIData()[:,2],dataSandyNB.MPIData_min()[:,2], color="wheat")
	# plt.loglog(sizes, dataSandyNB.MPIData()[:,3], label="Non-Blocking, # proc = 64", ls="-.", color="green")
	# # plt.loglog(sizes, dataSandyNB.MPIData_min()[:,3], color="green")
	# # ax.fill_between(sizes,dataSandyNB.MPIData()[:,3],dataSandyNB.MPIData_min()[:,3], color="lightgreen")


	# # plt.loglog(sizes, dataSandyBaseline.MPIData()[:,0], label="Baseline, # proc = 8", color="blue")

	# # plt.loglog(sizes, dataSandyBaseline.MPIData()[:,1], label="Baseline, # proc = 16", color="red")

	# # plt.loglog(sizes, dataSandyBaseline.MPIData()[:,2], label="Baseline, # proc = 32", color="orange")

	# # plt.loglog(sizes, dataSandyBaseline.MPIData()[:,3], label="Baseline, # proc = 64", color="green")


	# plt.loglog(sizes, dataSandyOS.MPIData()[:,0], label="One-Sided, # proc = 8", ls="dotted", color="blue")

	# plt.loglog(sizes, dataSandyOS.MPIData()[:,1], label="One-Sided, # proc = 16", ls="dotted", color="red")

	# plt.loglog(sizes, dataSandyOS.MPIData()[:,2], label="One-Sided, # proc = 32", ls="dotted", color="orange")

	# plt.loglog(sizes, dataSandyOS.MPIData()[:,3], label="One-Sided, # proc = 64", ls="dotted", color="green")

	# ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	# plt.savefig(join(PIC_DIRECTORY, "./mpi_multproc_sandy_os_nb.png"))
	

	# fig = plt.figure(figsize=(14,9))s.png"))
	

	# fig = plt.figure(figsize=(14,9))
	# plt.title("Total Time vs. Domain Size, Non-Blocking & One-Sided")
	# plt.xlabel("Domain Size")
	# plt.ylabel("Time (s)")

	# ax = plt.subplot(111)
	# box = ax.get_position()
	# ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

	
	# # plt.plot(sizes, dataHaswellNB.totalData()[:,0], label="Non-Blocking, # proc = 8", color="blue", ls="-.")
	# # # plt.loglog(sizes, dataHaswellNB.totalData_min()[:,0], color="blue")
	# # # ax.fill_between(sizes,dataHaswellNB.totalData()[:,0],dataHaswellNB.totalData_min()[0,:], color="powderblue")

	# # plt.plot(sizes, dataHaswellNB.totalData()[:,1], label="Non-Blocking, # proc = 16", color="red", ls="-.")
	# # # plt.loglog(sizes, dataHaswellNB.totalData_min()[:,1], color="red")
	# # # ax.fill_between(sizes,dataHaswellNB.totalData()[:,1],dataHaswellNB.totalData_min()[1,:], color="mistyrose")
	
	# # plt.loglog(sizes, dataHaswellNB.totalData()[:,2], label="Non-Blocking, # proc = 32", color="orange", ls="-.")
	# # # plt.loglog(sizes, dataHaswellNB.totalData_min()[:,2], color="brown")
	# # # ax.fill_between(sizes,dataHaswellNB.totalData()[:,2],dataHaswellNB.totalData_min()[2,:], color="wheat")
	
	# # plt.loglog(sizes, dataHaswellNB.totalData()[:,3], label="Non-Blocking, # proc = 64", color="green", ls="-.")
	# # # plt.loglog(sizes, dataHaswellNB.totalData_min()[:,3], color="purple")
	# # # ax.fill_between(sizes,dataHaswellNB.totalData()[:,3],dataHaswellNB.totalData_min()[3,:], color="thistle")
	
	# # plt.plot(sizes, dataHaswellBaseline.totalData()[:,0], label="Baseline, # proc = 8", color="blue")

	# # plt.plot(sizes, dataHaswellBaseline.totalData()[:,1], label="Baseline, # proc = 16", color="red")

	# # plt.loglog(sizes, dataHaswellBaseline.totalData()[:,2], label="Baseline, # proc = 32", color="orange")

	# # plt.loglog(sizes, dataHaswellBaseline.totalData()[:,3], label="Baseline, # proc = 64", color="green")


	# # plt.plot(sizes, dataHaswellOS.totalData()[:,0], label="One-Sided, # proc = 8", color="blue", ls="dotted")

	# # plt.plot(sizes, dataHaswellOS.totalData()[:,1], label="One-Sided, # proc = 16", color="red", ls="dotted")

	# # plt.loglog(sizes, dataHaswellOS.totalData()[:,2], label="One-Sided, # proc = 32", color="orange", ls="dotted")

	# # plt.loglog(sizes, dataHaswellOS.totalData()[:,3], label="One-Sided, # proc = 64", color="green", ls="dotted")

	
	# plt.loglog(sizes, dataSandyNB.totalData()[:,0], label="Non-Blocking, # proc = 8", color="blue", ls="-.")
	# plt.loglog(sizes, dataSandyNB.totalData()[:,1], label="Non-Blocking, # proc = 16", color="red", ls="-.")
	# plt.loglog(sizes, dataSandyNB.totalData()[:,2], label="Non-Blocking, # proc = 32", color="orange", ls="-.")
	# plt.loglog(sizes, dataSandyNB.totalData()[:,3], label="Non-Blocking, # proc = 64", color="green", ls="-.")
	

	# # plt.loglog(sizes, dataSandyBaseline.totalData()[:,0], label="Baseline, # proc = 8", color="blue")

	# # plt.loglog(sizes, dataSandyBaseline.totalData()[:,1], label="Baseline, # proc = 16", color="red")

	# # plt.loglog(sizes, dataSandyBaseline.totalData()[:,2], label="Baseline, # proc = 32", color="orange")

	# # plt.loglog(sizes, dataSandyBaseline.totalData()[:,3], label="Baseline, # proc = 64", color="green")


	# plt.plot(sizes, dataSandyOS.totalData()[:,0], label="One-Sided, # proc = 8", color="blue", ls="dotted")

	# plt.plot(sizes, dataSandyOS.totalData()[:,1], label="One-Sided, # proc = 16", color="red", ls="dotted")

	# plt.loglog(sizes, dataSandyOS.totalData()[:,2], label="One-Sided, # proc = 32", color="orange", ls="dotted")

	# plt.loglog(sizes, dataSandyOS.totalData()[:,3], label="One-Sided, # proc = 64", color="green", ls="dotted")



	# # plt.axis(ymin=0, ymax=20)
	# ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	# # plt.show()
	# plt.savefig(join(PIC_DIRECTORY, "./total_multprocess_sandy_os_nb.png"))



	fig = plt.figure(figsize=(14,9))
	# plt.title("Total Time vs. Num Process, Baseline & Non-Blocking")
	# plt.title("Total Time vs. Num Process, Baseline & One-Sided")
	plt.title("Total Time vs. Num Process, Non-Blocking & One-Sided")
	plt.xlabel("Num Process")
	plt.ylabel("Time (s)")

	ax = plt.subplot(111)
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

	
	# plt.loglog(process, dataHaswellNB.totalData()[0,:], label="Non-blocking, Domain Size = 64", color="blue", ls="-.")
	# # plt.loglog(process, dataHaswellNB.totalData_min()[0,:], color="blue")
	# # ax.fill_between(process,dataHaswellNB.totalData()[:,0],dataHaswellNB.totalData_min()[0,:], color="powderblue")

	# plt.loglog(process, dataHaswellNB.totalData()[1,:], label="Non-blocking, Domain Size = 512", color="red", ls="-.")
	# # plt.loglog(process, dataHaswellNB.totalData_min()[:,1], color="red")
	# # ax.fill_between(process,dataHaswellNB.totalData()[:,1],dataHaswellNB.totalData_min()[1,:], color="mistyrose")
	
	# plt.loglog(process, dataHaswellNB.totalData()[2,:], label="Non-blocking, Domain Size = 1024", color="orange", ls="-.")
	# # plt.loglog(process, dataHaswellNB.totalData_min()[:,2], color="brown")
	# # ax.fill_between(process,dataHaswellNB.totalData()[:,2],dataHaswellNB.totalData_min()[2,:], color="wheat")
	
	# plt.loglog(process, dataHaswellNB.totalData()[3,:], label="Non-blocking, Domain Size = 2048", color="green", ls="-.")
	# # plt.loglog(process, dataHaswellNB.totalData_min()[:,3], color="purple")
	# # ax.fill_between(process,dataHaswellNB.totalData()[:,3],dataHaswellNB.totalData_min()[3,:], color="thistle")

	# plt.loglog(process, dataHaswellNB.totalData()[4,:], label="Non-blocking, Domain Size = 4096", color="brown", ls="-.")
	# # plt.loglog(process, dataHaswellNB.totalData_min()[:,3], color="purple")
	# # ax.fill_between(process,dataHaswellNB.totalData()[:,3],dataHaswellNB.totalData_min()[3,:], color="thistle")

	# plt.loglog(process, dataHaswellNB.totalData()[5,:], label="Non-blocking, Domain Size = 8192", color="purple", ls="-.")
	# # plt.loglog(process, dataHaswellNB.totalData_min()[:,3], color="purple")
	# # ax.fill_between(process,dataHaswellNB.totalData()[:,3],dataHaswellNB.totalData_min()[3,:], color="thistle")



	# plt.loglog(process, dataHaswellBaseline.totalData()[0,:], label="Baseline, Domain Size = 64", color="blue")
	# # plt.loglog(process, dataHaswellBaseline.totalData_min()[0,:], color="blue")
	# # ax.fill_between(process,dataHaswellBaseline.totalData()[:,0],dataHaswellBaseline.totalData_min()[0,:], color="powderblue")

	# plt.loglog(process, dataHaswellBaseline.totalData()[1,:], label="Baseline, Domain Size = 512", color="red")
	# # plt.loglog(process, dataHaswellBaseline.totalData_min()[:,1], color="red")
	# # ax.fill_between(process,dataHaswellBaseline.totalData()[:,1],dataHaswellBaseline.totalData_min()[1,:], color="mistyrose")
	
	# plt.loglog(process, dataHaswellBaseline.totalData()[2,:], label="Baseline, Domain Size = 1024", color="orange")
	# # plt.loglog(process, dataHaswellBaseline.totalData_min()[:,2], color="brown")
	# # ax.fill_between(process,dataHaswellBaseline.totalData()[:,2],dataHaswellBaseline.totalData_min()[2,:], color="wheat")
	
	# plt.loglog(process, dataHaswellBaseline.totalData()[3,:], label="Baseline, Domain Size = 2048", color="green")
	# # plt.loglog(process, dataHaswellBaseline.totalData_min()[:,3], color="purple")
	# # ax.fill_between(process,dataHaswellBaseline.totalData()[:,3],dataHaswellBaseline.totalData_min()[3,:], color="thistle")

	# plt.loglog(process, dataHaswellBaseline.totalData()[4,:], label="Baseline, Domain Size = 4096", color="brown")
	# # plt.loglog(process, dataHaswellBaseline.totalData_min()[:,3], color="purple")
	# # ax.fill_between(process,dataHaswellBaseline.totalData()[:,3],dataHaswellBaseline.totalData_min()[3,:], color="thistle")

	# plt.loglog(process, dataHaswellBaseline.totalData()[5,:], label="Baseline, Domain Size = 8192", color="purple")
	# plt.loglog(process, dataHaswellBaseline.totalData_min()[:,3], color="purple")
	# ax.fill_between(process,dataHaswellBaseline.totalData()[:,3],dataHaswellBaseline.totalData_min()[3,:], color="thistle")

	# plt.loglog(process, dataHaswellOS.totalData()[0,:], label="One-Sided, Domain Size = 64", color="blue", ls="dotted")

	# plt.loglog(process, dataHaswellOS.totalData()[1,:], label="One-Sided, Domain Size = 512", color="red", ls="dotted")

	# plt.loglog(process, dataHaswellOS.totalData()[2,:], label="One-Sided, Domain Size = 1024", color="orange", ls="dotted")

	# plt.loglog(process, dataHaswellOS.totalData()[3,:], label="One-Sided, Domain Size = 2048", color="green", ls="dotted")

	# plt.loglog(process, dataHaswellOS.totalData()[4,:], label="One-Sided, Domain Size = 4096", color="brown", ls="dotted")

	# plt.loglog(process, dataHaswellOS.totalData()[5,:], label="One-Sided, Domain Size = 8192", color="purple", ls="dotted")

	
	
	plt.loglog(process, dataSandyNB.totalData()[0,:], label="Non-Blocking, Domain = 64", color="blue", ls="-.")
	plt.loglog(process, dataSandyNB.totalData()[1,:], label="Non-Blocking, Domain = 512", color="red", ls="-.")
	plt.loglog(process, dataSandyNB.totalData()[2,:], label="Non-Blocking, Domain = 1024", color="orange", ls="-.")
	plt.loglog(process, dataSandyNB.totalData()[3,:], label="Non-Blocking, Domain = 2048", color="green", ls="-.")
	plt.plot(process, dataSandyNB.totalData()[4,:], label="Non-Blocking, Domain = 4096", color="brown", ls="-.")
	plt.plot(process, dataSandyNB.totalData()[5,:], label="Non-Blocking, Domain = 8192", color="purple", ls="-.")
	
	# plt.loglog(process, dataSandyBaseline.totalData()[0,:], label="Baseline, Domain Size = 64", color="blue")

	# plt.loglog(process, dataSandyBaseline.totalData()[1,:], label="Baseline, Domain Size = 512", color="red")

	# plt.loglog(process, dataSandyBaseline.totalData()[2,:], label="Baseline, Domain Size = 1024", color="orange")

	# plt.loglog(process, dataSandyBaseline.totalData()[3,:], label="Baseline, Domain Size = 2048", color="green")

	# plt.loglog(process, dataSandyBaseline.totalData()[4,:], label="Baseline, Domain Size = 4096", color="brown")

	# plt.loglog(process, dataSandyBaseline.totalData()[5,:], label="Baseline, Domain Size = 8192", color="purple")




	plt.loglog(process, dataSandyOS.totalData()[0,:], label="One-Sided, Domain Size = 64", color="blue", ls="dotted")

	plt.loglog(process, dataSandyOS.totalData()[1,:], label="One-Sided, Domain Size = 512", color="red", ls="dotted")

	plt.loglog(process, dataSandyOS.totalData()[2,:], label="One-Sided, Domain Size = 1024", color="orange", ls="dotted")

	plt.loglog(process, dataSandyOS.totalData()[3,:], label="One-Sided, Domain Size = 2048", color="green", ls="dotted")

	plt.loglog(process, dataSandyOS.totalData()[4,:], label="One-Sided, Domain Size = 4096", color="brown", ls="dotted")

	plt.loglog(process, dataSandyOS.totalData()[5,:], label="One-Sided, Domain Size = 8192", color="purple", ls="dotted")



	# plt.axis(ymin=0, ymax=20)
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	# plt.show()
	plt.savefig(join(PIC_DIRECTORY, "./total_multdomain_sandy_os_nb.png"))