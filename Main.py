from Hardware import *
import numpy as np
import matplotlib.pyplot as plt

pause = 0


# print(prob)
# count, bins, ignored = plt.hist(prob, 14, density=True)
# plt.show()

l2cache = L2Cache()
cores = []
for x in range(4): #Create the cores they're 4
    cores.append(Core(l2cache,x))
print(cores[x].thr)
for i in range(10):
    CPU.nextInst(cores[0].cpu)