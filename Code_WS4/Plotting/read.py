#!/usr/bin/env python3

import re
import numpy as np
import glob
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from os.path import join
from itertools import combinations

deckSize = {"io": 0, "setup": 1, "compute": 2, "MPI": 3, "total":4}
sizes = [64, 512, 1024, 2048, 4096, 8192]
process = [8, 16, 32, 64]

DOMAIN = True
PROCESS = False

varList = {DOMAIN : sizes, PROCESS : process}
labelName = {DOMAIN : "Domain", PROCESS : "# proc"}
x_axisName = {DOMAIN : "Domain Size", PROCESS : "Num Processes"}
variableSaveName = {DOMAIN : "multdomain", PROCESS : "multproc"}
lineType = {"Baseline" : "-", "NB" : "-.", "OS" : "dotted", "Sandy" : "dotted", "Haswell" : "-", "Collective" : "dotted"}
architectures = ["Haswell", "Sandy"]
caseType = {"Baseline" : "Baseline", "NB" : "Non-Blocking", "OS" : "One-Sided", "Collective" : "Collective"}
colorType = ["blue", "red", "orange", "green", "brown", "purple"]

X, Y = np.meshgrid(process, sizes)

PIC_DIRECTORY = "./figures"

class OutputData:
	def __init__(self, fileName, case, architecture, isUpdated=False):
		self.case = case
		self.architecture = architecture
		if isUpdated:
			self.timeData = self.readOut(fileName[0])
			for name in fileName[1:]:
				self.timeData += self.readOut(name)
			self.timeData /= len(fileName)
			self.data = self.timeData
		else:
			self.timeData = self.readOut(fileName)
			self.data = self.timeData

		self.deckSize = self.data[0][0].shape[0]
		self.totalEntries = self.data.shape[0]
		self.sizes = 6
		self.numProc = 4
		self.dataTypes = {"IO" : self.IOData(), "Setup" : self.setupData(), "Compute" : self.computeData(), "MPI" : self.MPIData(), "Total" : self.totalData()}

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

			timeData.append(data)

		return np.array(timeData)

	def getArchitecture(self):
		return self.architecture

	def getCase(self):
		return self.case

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

	def getData(self, typeName):
		return self.dataTypes[typeName]

class plotClass:
	def __init__(self):
		Sandy = {}
		Haswell = {}
		self.dataSet = {"Sandy": Sandy, "Haswell" : Haswell}

	def addData(self, dataSet):
		for data in dataSet:
			self.dataSet[data.getArchitecture()][data.getCase()] = data

	def plot(self, cases, architecture, dataType, fixedVariable):
		fig = plt.figure(figsize=(14,9))
		plt.title("{} Time vs {}, {} & {}".format(dataType, x_axisName[not fixedVariable], caseType[cases[0]], caseType[cases[1]]))
		plt.xlabel(x_axisName[not fixedVariable])
		plt.ylabel("Time (s)")

		ax = plt.subplot(111)
		box = ax.get_position()
		ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
		
		for case in cases:
			dependentVariable = varList[not fixedVariable]
			dataSet = self.dataSet[architecture][case].getData(dataType)
			if fixedVariable == PROCESS:
				dataSet = np.transpose(dataSet)
			for i, var in enumerate(varList[fixedVariable]):
				label = "{}, {} = {}".format(caseType[case], labelName[fixedVariable], var)
				ls = lineType[case]
				color = colorType[i]
				plt.loglog(dependentVariable, dataSet[i,:], label=label, ls=ls, color=color)

		ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 12})
		saveFileName = "./{}_{}_{}_{}_{}.png".format(dataType.lower(), variableSaveName[fixedVariable], architecture.lower(), cases[1].lower(), cases[0].lower())
		print(saveFileName)
		plt.savefig(join(PIC_DIRECTORY, saveFileName))

	def plotBaseline(self, dataType, fixedVariable):
		fig = plt.figure(figsize=(14,9))
		case = "Baseline"
		plt.title("{} Time vs {}".format(dataType, x_axisName[not fixedVariable]))
		plt.xlabel(x_axisName[not fixedVariable])
		plt.ylabel("Time (s)")

		ax = plt.subplot(111)
		box = ax.get_position()
		ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

		for arch in architectures:
			dependentVariable = varList[not fixedVariable]
			dataSet = self.dataSet[arch][case].getData(dataType)
			if fixedVariable == PROCESS:
				dataSet = np.transpose(dataSet)
			for i, var in enumerate(varList[fixedVariable]):
				label = "{}, {} = {}".format(arch, labelName[fixedVariable], var)
				ls = lineType[arch]
				color = colorType[i]
				plt.loglog(dependentVariable, dataSet[i,:], label=label, ls=ls, color=color)

		ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 12})
		saveFileName = "./{}_{}_{}.png".format(dataType.lower(), variableSaveName[fixedVariable], "baseline")
		print(saveFileName)
		plt.savefig(join(PIC_DIRECTORY, saveFileName))

	def plotIO(self):
		fixedVariable = DOMAIN
		case = "Baseline"
		dataType = "IO"
		fig = plt.figure(figsize=(14,9))
		plt.title("{} Time vs {}".format("IO", x_axisName[fixedVariable]))
		plt.xlabel(x_axisName[fixedVariable])
		plt.ylabel("Time (s)")

		ax = plt.subplot(111)
		box = ax.get_position()
		ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
		dependentVariable = varList[fixedVariable]
		
		for i, arch in enumerate(architectures):
			dataSet = self.dataSet[arch][case].getData(dataType)
			label = "{}".format(arch)
			ls = lineType[arch]
			color = colorType[i]
			plt.plot(dependentVariable, dataSet, label=label, ls=ls, color=color)

		ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 12})
		saveFileName = "./{}_{}.png".format(dataType.lower(), "baseline")
		print(saveFileName)
		plt.savefig(join(PIC_DIRECTORY, saveFileName))


def readNames(tagName):
	return glob.glob("*" + tagName + "*")

if __name__ == '__main__':

	manager = plt.get_current_fig_manager()
	manager.resize(*manager.window.maxsize())

	collectiveFileNames = readNames("collective")
	baselineFileNames = readNames("baseline")
	# baselineFileNames = "baseline_out_gauss_64_intel_957068.out"

	dataHaswellCollective = OutputData(collectiveFileNames, "Collective", "Haswell", isUpdated=True)
	dataHaswellBaseline = OutputData(baselineFileNames, "Baseline", "Haswell", isUpdated=True)

	# dataHaswellBaseline = OutputData(fileName, "Baseline", "Haswell", isUpdated=True)

	# dataHaswellCollective = OutputData(fileName, "Baseline", "Haswell", isUpdated=True)

	# fileName = "wm_baseline.out"
	# dataHaswellBaseline = OutputData(fileName, "Baseline", "Haswell", isUpdated=True)

	# fileName = "sb_baseline.out"
	# dataSandyBaseline = OutputData(fileName, "Baseline", "Sandy", isUpdated=True)

	# fileName = "wm_nb.out"
	# dataHaswellNB = OutputData(fileName, "NB", "Haswell", isUpdated=True)

	# fileName = "sb_nb.out"
	# dataSandyNB = OutputData(fileName, "NB", "Sandy", isUpdated=True)

	# fileName = "wm_os.out"
	# dataHaswellOS = OutputData(fileName, "OS", "Haswell", isUpdated=True)

	# fileName = "sb_os.out"
	# dataSandyOS = OutputData(fileName, "OS", "Sandy", isUpdated=True)

	# dataFiles = (dataHaswellBaseline, dataSandyBaseline, dataHaswellNB, dataSandyNB, dataHaswellOS, dataSandyOS)

	dataFiles = [dataHaswellCollective, dataHaswellBaseline]

	plotting = plotClass()

	plotting.addData(dataFiles)


# ####### Plots all combinations present in casesToPlot ######################
# 	# casesToPlot = ["Baseline", "NB", "OS"]
	# casesToPlot = ["Baseline", "NB", "OS"]
	casesToPlot = ["Baseline", "Collective"]
	caseCombinations = combinations(casesToPlot, 2)
	dataToPlot = ["Compute", "MPI", "Total"]
	# architectureToPlot = ["Haswell", "Sandy"]
	architectureToPlot = ["Haswell"]
	variableToPlot = [DOMAIN, PROCESS]

	for cases in caseCombinations:
		for dataType in dataToPlot:
			for arch in architectureToPlot:
				for fvar in variableToPlot:
					plotting.plot(cases, arch, dataType, fvar)

# ####### Compares Sandy and Haswell nodes for Baseline data #####################
# 	dataToPlot = ["Setup", "Compute", "MPI", "Total"]
# 	for dataType in dataToPlot:
# 		for fvar in variableToPlot:
# 			plotting.plotBaseline(dataType, fvar)


# ####### Plots IO info #########################################################
	# plotting.plotIO()