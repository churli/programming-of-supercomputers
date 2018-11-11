import matplotlib.pyplot as plt

x = [1.0,2.0,3.0,4.0,5.0]
x_iter = iter(x)
basis = 126.02
data = [126.02, 78.25, 56.75, 45.91, 39.79]
data = [basis/value/next(x_iter) for value in data]

plt.plot(x,data, marker="o")
plt.title("Intel compiler, -unroll flag, 1 node, 8 processes, larger domain")
plt.xlabel("# OpenMP Threads")
plt.ylabel("Efficiency")
plt.show()

