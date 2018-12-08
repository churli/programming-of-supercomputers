import re
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from os.path import join

deckSize = {"io": 0, "setup": 1, "compute": 2, "MPI": 3, "total":4}
sizes = [64, 512, 1024, 2048, 4096, 8192]
process = [8, 16, 32, 64]

X, Y = np.meshgrid(process, sizes)

PIC_DIRECTORY = "/home/keefe/Documents/TUM/Sem3/IN2190/Assignment3/Figure"

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

	def TotalData(self):
		loc = deckSize["total"]
		TotalData = np.zeros((self.sizes, self.numProc))
		for i in range(self.sizes):
			for j in range(self.numProc):
				# print(np.max(self.data[i*self.numProc + j][:,loc]))
				TotalData[i, j] = np.average(self.data[i*self.numProc + j][:,loc])
		return TotalData

if __name__ == '__main__':
	fileName = "out_gauss_64_intel_2533289.out"
	dataHaswell = OutputData(fileName)
	IODataHaswell = dataHaswell.IOData()
	setupDataHaswell = dataHaswell.setupData()
	computeDataHaswell = dataHaswell.computeData()
	MPIDataHaswell = dataHaswell.MPIData()

	fileName = "out_gauss_64_intel_2533290.out"
	dataHaswellUpdated = OutputData(fileName, isUpdated=True)
	IODataHaswellUpdated = dataHaswellUpdated.IOData()
	setupDataHaswellUpdated = dataHaswellUpdated.setupData()
	computeDataHaswellUpdated = dataHaswellUpdated.computeData()
	MPIDataHaswellUpdated = dataHaswellUpdated.MPIData()

	fileName = "sb_out_gauss_64_intel_2533291.out"
	dataSandy = OutputData(fileName)
	IODataSandy = dataSandy.IOData()
	setupDataSandy = dataSandy.setupData()
	computeDataSandy = dataSandy.computeData()
	MPIDataSandy = dataSandy.MPIData()

	fileName = "sb_updated_out_gauss_64_intel_2508781.out"
	dataSandyUpdated = OutputData(fileName, isUpdated=True)
	IODataSandyUpdated = dataSandyUpdated.IOData()
	setupDataSandyUpdated = dataSandyUpdated.setupData()
	computeDataSandyUpdated = dataSandyUpdated.computeData()
	MPIDataSandyUpdated = dataSandyUpdated.MPIData()

	# plt.title("IO Time vs Size of Domain")
	# plt.xlabel("Domain Size (# Cells in Domain Length)")
	# plt.ylabel("Time (s)")
	
	# plt.plot(sizes, IODataHaswell, label="Haswell")
	# plt.plot(sizes, IODataHaswellUpdated, label="Averaged Haswell")
	# plt.plot(sizes, IODataSandy, label="Sandy Bridge")
	# plt.plot(sizes, IODataSandyUpdated, label="Averaged Sandy Bridge")
	# plt.legend()
	# # plt.savefig(join(PIC_DIRECTORY, "./IO.png"))
	# plt.show()
	# fig = plt.figure()
	# ax = Axes3D(fig)
	# ax = plt.gca(projection='3d')
	# ax.set_title("Setup Time vs Size of Domain vs Num Processes for Haswell")
	# ax.set_xlabel("Num Processes")
	# ax.set_ylabel("Domain Size")
	# ax.set_zlabel("Time (s)")

	# ax.contour3D(X, Y, setupDataHaswell, label="Haswell")
	# ax.contour3D(X, Y, setupDataHaswellUpdated, label="Averaged Haswell")
	# ax.contour3D(X, Y, setupDataSandy, label="Sandy Bridge")
	# ax.contour3D(X, Y, setupDataSandyUpdated, label="Averaged Sandy Bridge")
	# ax.plot_surface(X, Y, setupDataHaswell)
	# ax.plot(X, Y, setupDataHaswellUpdated, label="Averaged Haswell")
	# ax.plot(X, Y, setupDataSandyUpdated, label="Averaged Sandy Bridge")
	# ax.plot_surface(X, Y, setupDataHaswellUpdated)	
	# ax.plot_surface(X, Y, setupDataSandyUpdated)
	# plt.savefig(join(PIC_DIRECTORY, "./setup.png"))

	# ax.legend()
	# ax.savefig(join(PIC_DIRECTORY, "./setup.png"))
	# plt.show()

	# print(setupDataHaswellUpdated[0,0])
	# plt.title("Setup Time vs. Processes")
	# plt.xlabel("Processes")
	# plt.ylabel("Time (s)")
	
	# plt.plot(process, setupDataHaswellUpdated[3,:], label="Haswell, Domain Size = 2048")
	# plt.plot(process, setupDataSandyUpdated[3,:], label="Sandy Bridge, Domain Size = 2048")
	# plt.plot(process, setupDataHaswellUpdated[-1,:], label="Haswell, Domain Size = 8192")
	# plt.plot(process, setupDataSandyUpdated[-1,:], label="Sandy Bridge, Domain Size = 8192")
	# plt.axis(ymin=0, ymax=20)
	# plt.legend()
	# plt.savefig(join(PIC_DIRECTORY, "./setup_multdomain.png"))
	# plt.show()


	# plt.title("Compute Time vs. Num Processes")
	# plt.xlabel("Processes")
	# plt.ylabel("Time (s)")
	
	# plt.plot(process, computeDataHaswellUpdated[0,:], label="Haswell, Domain Size = 64")
	# plt.plot(process, computeDataSandyUpdated[0,:], label="Sandy Bridge, Domain Size = 64")
	# plt.plot(process, computeDataHaswellUpdated[-2,:], label="Haswell, Domain Size = 4096")
	# plt.plot(process, computeDataSandyUpdated[-2,:], label="Sandy Bridge, Domain Size = 4096")
	# # plt.plot(process, setupDataHaswellUpdated[-1,:], label="Haswell, Domain Size = 8192")
	# # plt.plot(process, setupDataSandyUpdated[-1,:], label="Sandy Bridge, Domain Size = 8192")
	# # plt.axis(ymin=0, ymax=20)
	# plt.legend()
	# plt.savefig(join(PIC_DIRECTORY, "./compute_multdomain.png"))
	# plt.show()


	# plt.title("MPI Time vs. Domain Size")
	# plt.xlabel("Domain Size")
	# plt.ylabel("Time (s)")
	
	# plt.plot(sizes, MPIDataHaswellUpdated[:,0], label="Haswell, Processes = 8")
	# plt.plot(sizes, MPIDataSandyUpdated[:,0], label="Sandy Bridge, Processes = 8")
	# plt.plot(sizes, MPIDataHaswellUpdated[:,-2], label="Haswell, Processes = 32")
	# plt.plot(sizes, MPIDataSandyUpdated[:,-2], label="Sandy Bridge, Processes = 32")
	# # plt.plot(process, setupDataHaswellUpdated[-1,:], label="Haswell, Domain Size = 8192")
	# # plt.plot(process, setupDataSandyUpdated[-1,:], label="Sandy Bridge, Domain Size = 8192")
	# # plt.axis(ymin=0, ymax=20)
	# plt.legend()
	# plt.savefig(join(PIC_DIRECTORY, "./mpi_multproc_2.png"))
	# plt.show()


	plt.title("MPI Time vs. Num Processes")
	plt.xlabel("Num Processes")
	plt.ylabel("Time (s)")
	
	plt.plot(process, MPIDataHaswellUpdated[0,:], label="Haswell, Domain Size = 64")
	plt.plot(process, MPIDataSandyUpdated[0,:], label="Sandy Bridge, Domain Size = 64")
	plt.plot(process, MPIDataHaswellUpdated[-2,:], label="Haswell, Domain Size = 4096")
	plt.plot(process, MPIDataSandyUpdated[-2,:], label="Sandy Bridge, Domain Size = 4096")
	# plt.plot(process, setupDataHaswellUpdated[-1,:], label="Haswell, Domain Size = 8192")
	# plt.plot(process, setupDataSandyUpdated[-1,:], label="Sandy Bridge, Domain Size = 8192")
	# plt.axis(ymin=0, ymax=20)
	plt.legend()
	plt.savefig(join(PIC_DIRECTORY, "./mpi_multdomain.png"))
	plt.show()


	# plt.title("Total Time vs. Domain Size")
	# plt.xlabel("Domain Size")
	# plt.ylabel("Time (s)")
	
	# plt.plot(sizes, dataHaswellUpdated.TotalData()[:,0], label="Haswell, Processes = 8")
	# plt.plot(sizes, dataSandyUpdated.TotalData()[:,0], label="Sandy Bridge, Processes = 8")
	# plt.plot(sizes, dataHaswellUpdated.TotalData()[:,-1], label="Haswell, Processes = 64")
	# plt.plot(sizes, dataSandyUpdated.TotalData()[:,-1], label="Sandy Bridge, Processes = 64")
	# # plt.plot(process, setupDataHaswellUpdated[-1,:], label="Haswell, Domain Size = 8192")
	# # plt.plot(process, setupDataSandyUpdated[-1,:], label="Sandy Bridge, Domain Size = 8192")
	# # plt.axis(ymin=0, ymax=20)
	# plt.legend()
	# plt.savefig(join(PIC_DIRECTORY, "./total_multproc.png"))
	# plt.show()