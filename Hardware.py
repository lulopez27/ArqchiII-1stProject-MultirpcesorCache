import numpy as np


class Core:
    def __init__(self,l2cache,thr):
        self.cpu = CPU()
        self.l1cache = L1Cache()
        self.directory = Directory()
        self.l2cache = l2cache
        self.thr = thr

class CPU:
    def __init__(self):
        self.prob = np.random.poisson(1, 1000)
        self.curr=0
    def calc(self):
        pass
    def write(self,data,pos):
        pass
    def read(self,pos):
        pass
    def nextInst(self):
        # print("Curr = "+str(self.curr)+" Inst = "+str(self.prob[self.curr]))
        if (self.prob[self.curr] == 1):
            pass
        self.curr+=1

class L1Cache:
    pass

class Directory:
    pass

class L2Cache:
    pass
