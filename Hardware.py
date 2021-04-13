import numpy as np
from threading import Thread, Lock


def isOdd(num):
    return num & 0x1

def xor(a, b):
    return (a and not b) or (not a and b)

run = True
stop = False
mutex = Lock()

class Core:
    def __init__(self,l1cache,procNumb): #create the core and hook it up
        self.prob = np.random.poisson(1, 1000)
        self.curr=0
        self.cpu = CPU()
        self.l1cache = l1cache
        self.procNumb = procNumb+1


    def coreThread(self):
        while(run):
            if stop:
                pass
            else:
                self.nextInst()

    def nextInst(self):
        if (self.prob[self.curr] == 1): #1 is for calc
            self.cpu.calc()
        elif(self.prob[self.curr] == 0): #0 is for read
            addr = self.cpu.genAddress() #get a random address from mem
            print("Read: "+str(addr) +" ---------------------- cache : "+str(self.procNumb))
            self.l1cache.read(addr)
        else: #anything else will be a write
            addr = self.cpu.genAddress() #get an address from mem
            val  = self.cpu.genValue()   #get a random value to be writen at address
            print("Write: "+str(addr)+" = "+str(val) +" ------- cache : "+str(self.procNumb))
            self.l1cache.write(val,addr) 
        self.curr+=1

class CPU:
    def calc(self):#must call waiting function
        return 0
    def genAddress(self):
        return np.random.randint(0,8)
    def genValue(self):
        return np.random.randint(0,65536)

class L1Cache:
    def __init__(self,memNum,l2cache): #,l2cache
        self.mem1={}
        self.mem1=[[0,'I',0,0],[1,'I',0,0]] 
                  #0blocknum, 1state, 2address, 3value
        self.memNum = memNum+1
        self.l2cache = l2cache

    def write(self,data,address):
        if not(self.checkAddress(address)): #it isnt in memory
            self.removeAddress(address) #writemiss
        # its in memory
        block = self.getBlock(address)
        block[3] = data
        if (block[1] == 'M'): # its in L1, and most current
            pass
        elif (block[1] == 'S'):# its in L1, but not most current
            self.l2cache.writeMiss(self.memNum,address)
        elif (block[1] == 'I'):#invalid
            self.l2cache.writeMiss(self.memNum,address)
        block[1] = 'M'

    def read(self,address):
        if not(self.checkAddress(address)): #it isnt in memory
            self.removeAddress(address)#readmiss
        # its in memory
        block = self.getBlock(address)
        if (block[1] == 'M'): # its in L1
            return
        elif (block[1] == 'S'):# its in L1
            return
        elif (block[1] == 'I'):# readMiss
            block[3] = self.l2cache.readMiss(self.memNum,address)
            block[1] = 'S'

    def errorprint(self):
        print("ERRORR in cache")

    def checkAddress(self,address):
        if(isOdd(address)==1):
            return self.mem1[0][2] == address
        return  self.mem1[1][2] == address

    def removeAddress(self,address):#address is the new address thats desired
        oldBlock = self.getBlock(address)# works because it is 1 way
        stat = oldBlock[1]
        oldAddress = oldBlock[2]

        if('M' in stat):#if the block is in M it must be written to memory
            self.l2cache.M2I(self.memNum,oldAddress,oldBlock[3])#write the old block to memory and set is as I
        elif('S' in stat):#switch it to I in directory
            self.l2cache.S2I(self.memNum,oldAddress)#write the old block to memory and set is as I
        elif ('I' in stat):# doesnt matter
            pass
        #default cache values
        oldBlock[1] = 'I'
        oldBlock[2] = address

    
    def getBlock(self,address): #returns block of mem specified by address
        if(isOdd(address)==1):
            return self.mem1[0]
        return self.mem1[1]

    def M2S(self,address):
        block = self.getBlock(address)
        block[1] = 'S'

    def M2I(self,address):
        block = self.getBlock(address)
        block[1] = 'I'

    def S2I(self,address):
        block = self.getBlock(address)
        block[1] = 'I'
    

class L2Cache:
    def __init__(self,mainMem):
        self.mem2={}
        self.mem2=[[0,'DI',0,[],0,0,0],[1,'DI',0,[],0,0,0],[2,'DI',0,[],0,0,0],[3,'DI',0,[],0,0,0]]
                  #0blockNum, 1State, 2owner, 3sharers, 4address, 5value, 6semaphore
        self.caches = []
        self.mainMem=mainMem
    
    def addCache(self,cache):
        self.caches.append(cache)

    def printCaches(self):
        for i in self.caches:
            print(i.memNum)
        print("Done")

    def readMiss(self,cacheNum,address): #a readmiss is called from cacheNum with address
        block = self.getblock(address)
        if (block[1] == 'DM'):
            block[1] = 'DS'
            owner = block[2]
            self.caches[owner-1].M2S(address) #change owner status to 'S'
            block[5] = self.caches[owner-1].getBlock(address)[3] #get the value that the owner has and set it as current l2 value
            self.mainMem.setVal(address,block[5])
        elif (block[1] == 'DI'):
            block[1] = 'DS'
        block[3].append(cacheNum)
        block[6] = 0
        return block[5]

    def writeMiss(self,cacheNum,address):
        block = self.getblock(address)
        if (block[1] == 'DM'):
            owner = block[2]
            self.caches[owner-1].M2I(address) #change owner status to 'I'
        elif (block[1] == 'DS'):
            for i in block[3]:
                self.caches[i-1].S2I(address) #change all 'S' status to 'I'
        block[1]  = 'DM' #put it as DM
        block[2] = cacheNum #set the current cache as owner
        block[3] = [] #remove all sharers
        block[6] = 0 #release the block

    def getblock(self,address):
        block = 0
        for i in range(4):
            if(self.mem2[i][4] == address):
                block = self.mem2[i]
                return self.accessBlock(block)
        if (block == 0):
            pos = self.genPos(address) #generate random position based on address
            block = self.mem2[pos] #the block to be replaced 
        block = self.accessBlock(block)
        #default values
        if(block[1] == 'DM'):
            self.mainMem.setVal(block[4],block[5])
            block[1] = 'DI'
        block[1] = 'DI'
        block[2] = 0
        block[3] = []
        block[4] = address
        block[5] = self.mainMem.getVal(address) #value in the memory
        return block
    
    def accessBlock(self,block):
        while(block[6] == 1):#busy waiting
            pass
        mutex.acquire()
        block[6] = 1
        mutex.release()
        if(block[1] == 'DM'):
            self.mainMem.setVal(block[4],block[5])
            block[1] = 'DI'
        return block
        
    def genPos(self,address):
        if(isOdd(address)==1):
            pos = 0
        else:
            pos = 2
        pos += np.random.randint(0,2)
        return pos

    def M2I(self,cacheNum,address,val):#invalidate a block in DM state
        block = self.getblock(address)
        block[1] = 'DI'
        block[2] = 0
        block[3] = []
        block[5] = val #value it used to have
        self.mainMem.setVal(address,val)
        block[6] = 0

    def S2I(self,cacheNum,address):
        block = self.getblock(address)
        if (len(block[3]) == 1): #if only one cache has it
            block[1] = 'DI'
            block[3] = []
        else: #if more than one has it
            block[3].remove(cacheNum)
        block[6] = 0

class MainMem:  
    def __init__(self):
        self.mem=[[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0]]
    
    def getVal(self,addr):
        return self.mem[addr][1]

    def setVal(self,addr,val):
        self.mem[addr][1] = val
