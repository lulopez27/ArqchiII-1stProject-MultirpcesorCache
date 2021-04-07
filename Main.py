import numpy as np
import matplotlib.pyplot as plt

pause = 0


def isOdd(num):
    return num & 0x1

def xor(a, b):
    return (a and not b) or (not a and b)


mem = [[334,'I','I','M','I'],[5,'I','I','I','I'],[3,'I','I','M','I'],[2,'I','I','I','I']]
for x in range(5):
     print(x)

# def getmem():
#     return mem[3]

# print(mem[3])
# a = getmem()
# a[2] = 'P'
# print(mem[3])

# l2cache = L2Cache()
# directory = Directory()
# cores = []
# for x in range(4): #Create the cores they're 4
#     cores.append(Core(l2cache,directory,x))
# print(cores[x].thr)
# for i in range(10):
#     CPU.nextInst(cores[0].cpu)

