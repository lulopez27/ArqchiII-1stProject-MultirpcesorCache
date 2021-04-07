import numpy as np
from Main import isOdd,xor
from threading import Thread, Lock

run = True
mutex = Lock()

class Core:
    def __init__(self,l1cache,l2cache,procNumb,control,directory): #create the core and hook it up
        self.prob = np.random.poisson(1, 1000)
        self.curr=0
        self.cpu = CPU()
        self.l1cache = l1cache
        self.controller = controller
        self.procNumb = procNumb
        self.control = control
        self.directory = directory


    def coreThread(self):
        while(run):
            self.nextInst()

    def nextInst(self):
        print("Curr = "+str(self.curr)+" Inst = "+str(self.prob[self.curr]))

        if (self.prob[self.curr] == 1): #1 is for calc
            self.cpu.calc()
        elif(self.prob[self.curr] == 0): #0 is for read
            addr = self.cpu.genAddress() #get a random address from mem
            self.l1cache.read(addr)
        else: #anything else will be a write
            addr = self.cpu.genAddress() #get an address from mem
            val  = self.cpu.genValue()   #get a random value to be writen at address
            self.l1cache.write(val,addr) #
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
        else:# its in memory
            block = self.getBlock(address)
            block[3] = data
            if (block[1] == 'M'): # its in L1
                pass
            elif (block[1] == 'S'):# its in L1
                self.l2cache.writeMiss(self.memNum,address)
            elif (block[1] == 'I'):# readMiss
                self.l2cache.writeMiss(self.memNum,address)

    def read(self,address):
        if not(self.checkAddress(address)): #it isnt in memory
            self.removeAddress(address)#readmiss
        else:# its in memory
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
            return self.mem1[0][0] == address
        return  self.mem1[1][0] == address

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
        else:
            self.errorprint()
        
        return xor(isOdd(address),0x1)
    
    def getBlock(self,address): #returns block of mem specified by address
        if(isOdd(address)==1):
            return self.mem1[0]
        return self.mem1[1]

    def M2S(self,address):
        block = self.getBlock(address)
        block[1] = 'S'
    

class L2Cache:
    def __init__(self,mainMem,caches,directory):
        self.mem2={}
        self.mem2=[[0,'DI',0,[0],0,0,0],[1,'DI',0,[0],0,0,0],[2,'DI',0,[0],0,0,0],[3,'DI',0,[0],0,0,0]]
                  #0blockNum, 1State, 2owner, 3sharers, 4address, 5value, 6semaphore
        self.new=[0,1,2,3,4,5,6,7]
        self.caches = caches
        self.directory = directory
        self.mainMem=mainMem
    
    def readMiss(self,cacheNum,address): #a readmiss is called from cacheNum with address
        block = self.getblock(address)
        while(block[6] == 1):#busy waiting
            pass
        mutex.acquire()
        block[6] = 1
        mutex.release()
        if (block[1] == 'DM'):
            block[1] = 'DS'
            owner = block[2]
            self.caches[owner-1].M2S(address) #change owner status to 'S'
            block[5] = self.caches[owner-1].getBlock(address)[3] #get the value that the owner has and se it as current l2 value
            self.mainMem.setVal(address,block[5])
        elif (block[1] == 'DI'):
            block[1] = 'DS'
        block[3].append(cacheNum)
        block[6] = 0
        return block[5]

    # def writeMiss(self,address):
    #     block = self.getblock(address)
    #     while(block[6] == 1):
    #     pass
    #     block[3].append(cacheNum)

    def getblock(self,address):
        for i in range(4):
            if(self.mem2[i][3] == address):
                return self.mem2[i]
        self.genPos(address)
        self.mainMem.getblock(address)

    #Interactions with Main Memory
    def getAddrMainMem(self,address,save): #get block from main memory
        pos = self.genPos(address)
        if(address in self.new): #remove it from new
            pass
        else:
            self.mainMem.save()
        self.mem2[pos][0] = address
        self.mem2[pos][1] = self.mainMem.getVal(address)

    def genPos(self,address):
        if(isOdd(address)==1):
            pos = 0
        else:
            pos = 2
        pos =+ np.random.randint(0,2)
        return pos

    #Interactions with L1cache
    def getBlockl1(self,cache,memline,addr):#remmember the cache is the number starting at 1
        newVal = self.caches[cache-1].getBlock(addr) #returns block of mem specified by address 
        self.mem2[memline] = newVal
        return self.mem2[memline]


    def rmBlock(self,addr):#addr corresponds to the new block that I want
        pass


    def getBlockl2(self,pos): #get the block of a position
        return self.mem2[pos]

class MainMem:  
    def __init__(self):
        self.mem=[[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0]]
    
    def getVal(self,addr):
        return self.mem[addr][1]

    def setVal(self,addr,val):
        self.mem[addr][1] = val

    def getblock(self,address):
        return self.mem[address]
