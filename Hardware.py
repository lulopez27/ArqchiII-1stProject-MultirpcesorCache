import numpy as np
import time
from threading import Lock
from GUI import updateWindow


def isOdd(num):
    return num & 0x1

def xor(a, b):
    return (a and not b) or (not a and b)

def updateGUI(block,key):
    updateWindow(block,key)

run = True
stop = True
semaphore = 4
mutex = Lock()

class Core:
    def __init__(self,l1cache,procNumb): #create the core and hook it up
        self.prob = np.random.poisson(1, 1000)
        self.curr=0
        self.cpu = CPU()
        self.l1cache = l1cache
        self.procNumb = procNumb+1
        self.prevInst = '::::'


    def coreThread(self):
        self.nextInst()

    def setInstread(self,addr):
        updateGUI('Core:'+str(self.procNumb)+'-Read: '+str(addr),'C'+str(self.procNumb)+'I')
        updateGUI(self.prevInst,'C'+str(self.procNumb)+'IA')
        self.prevInst = 'PrevInst: Core:'+str(self.procNumb)+'-Read: '+str(addr)
        block = self.l1cache.read(addr)
        self.updateGUICore(block)

    def setInstwrit(self,addr,val):
        print("Write: "+str(addr)+" = "+str(val) +" ------- cache : "+str(self.procNumb)+"\n")
        updateGUI('Core:'+str(self.procNumb)+'-Write : '+str(val)+' on '+str(addr),'C'+str(self.procNumb)+'I')
        updateGUI(self.prevInst,'C'+str(self.procNumb)+'IA')
        self.prevInst = 'PrevInst: Core:'+str(self.procNumb)+'-Write : '+str(val)+' on '+str(addr)
        block = self.l1cache.write(val,addr) 
        self.updateGUICore(block)

    def nextInst(self):
        if (self.prob[self.curr] == 1): #1 is for calc
            updateGUI('Core:'+str(self.procNumb)+'-Calc','C'+str(self.procNumb)+'I')
            updateGUI(self.prevInst,'C'+str(self.procNumb)+'IA')
            self.prevInst = 'PrevInst: Core:'+str(self.procNumb)+'-Calc'
            self.cpu.calc()
            time.sleep(1)
            print("Calc:  -------------------------- cache : "+str(self.procNumb)+"\n")
        elif(self.prob[self.curr] == 0): #0 is for read
            addr = self.cpu.genAddress() #get a random address from mem
            print("Read: "+str(addr) +" ---------------------- cache : "+str(self.procNumb)+"\n")
            updateGUI('Core:'+str(self.procNumb)+'-Read: '+str(addr),'C'+str(self.procNumb)+'I')
            updateGUI(self.prevInst,'C'+str(self.procNumb)+'IA')
            self.prevInst = 'PrevInst: Core:'+str(self.procNumb)+'-Read: '+str(addr)
            block = self.l1cache.read(addr)
            self.updateGUICore(block)
        else: #anything else will be a write
            addr = self.cpu.genAddress() #get an address from mem
            val  = self.cpu.genValue()   #get a random value to be writen at address
            print("Write: "+str(addr)+" = "+str(val) +" ------- cache : "+str(self.procNumb)+"\n")
            updateGUI('Core:'+str(self.procNumb)+'-Write : '+str(val)+' on '+str(addr),'C'+str(self.procNumb)+'I')
            updateGUI(self.prevInst,'C'+str(self.procNumb)+'IA')
            self.prevInst = 'PrevInst: Core:'+str(self.procNumb)+'-Write : '+str(val)+' on '+str(addr)
            block = self.l1cache.write(val,addr) 
            self.updateGUICore(block)
        self.curr+=1
        if (self.curr>999):
            self.curr = 0
        
    def updateGUIL1(self,block):
        blockstr = str(block[0])+') '+block[1] +' Addr:' +str("{0:b}".format(block[2]))+' Val:'+str("{0:x}".format(block[3]))
        print(blockstr)
        return blockstr
    
    def updateGUICore(self,block):
        if(isOdd(block[2])==1):
            updateGUI(self.updateGUIL1(block),'C'+str(self.procNumb)+'V0')
        else:
            updateGUI(self.updateGUIL1(block),'C'+str(self.procNumb)+'V1')

class CPU:
    def __init__(self):
        self.probaddr = np.random.poisson(7, 1000)
        self.curr = 0
         
    def calc(self): 
        #must call waiting function
        return 0
    def genAddress(self):
        self.curr+=1
        if (self.curr>999):
            self.curr = 0
        curradrr = self.probaddr[self.curr]
        if(curradrr >= 8):
            return 7
        return curradrr
    
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
        return block

    def read(self,address):
        if not(self.checkAddress(address)): #it isnt in memory
            self.removeAddress(address)#readmiss
        # its in memory
        block = self.getBlock(address)
        if (block[1] == 'M'): # its in L1
            return block
        elif (block[1] == 'S'):# its in L1
            return block
        elif (block[1] == 'I'):# readMiss
            time.sleep(4)
            block[3] = self.l2cache.readMiss(self.memNum,address)
            block[1] = 'S'
        return block

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
    
    def getAddress(self,address):
        block = self.getBlock(address)
        if(block[2] == address):
            return block
        return 0

    def M2S(self,address): #sets a block to S and returns the value
        block = self.getAddress(address)
        if (block != 0):
            block[1] = 'S'
            self.updateGUIL1(block, 'C'+str(self.memNum)+'V'+str(block[0]))
            return block[3]
        return 0

    def M2I(self,address):
        block = self.getAddress(address)
        if (block != 0):
            block[1] = 'I'
            self.updateGUIL1(block, 'C'+str(self.memNum)+'V'+str(block[0]))
            return block[3]
        return 0

    def S2I(self,address):
        block = self.getAddress(address)
        if (block != 0):
            block[1] = 'I'
            self.updateGUIL1(block, 'C'+str(self.memNum)+'V'+str(block[0]))
        return 0
    
    def updateGUIL1(self,block,key):
        blockstr = str(block[0])+') '+block[1] +' Addr:' +str("{0:b}".format(block[2]))+' Val:'+str("{0:x}".format(block[3]))
        updateGUI(blockstr,key)

class L2Cache:
    def __init__(self,mainMem):
        self.mem2={}
        self.mem2=[[0,'DI',0,[],0,0,0],[1,'DI',0,[],0,0,0],[2,'DI',0,[],0,0,0],[3,'DI',0,[],0,0,0]]
                  #0blockNum, 1State, 2owner, 3sharers, 4address, 5value, 6semaphore
        self.caches = []
        self.mainMem=mainMem
    
    def addCache(self,cache):
        self.caches.append(cache)

    def readMiss(self,cacheNum,address): #a readmiss is called from cacheNum with address
        block = self.getblock(address)
        if (block[1] == 'DI'):
            block[1] = 'DS'
        block[3].append(cacheNum)
        self.updateGUIL2(block,'L2V'+str(block[0]))
        time.sleep(1)
        block[6] = 0
        return block[5]

    def writeMiss(self,cacheNum,address):
        block = self.getblock(address)
        if (block[1] == 'DS'):
            for i in block[3]:
                self.caches[i-1].S2I(address) #change all 'S' status to 'I'
        block[1]  = 'DM' #put it as DM
        block[2] = cacheNum #set the current cache as owner
        block[3] = [] #remove all sharers
        self.updateGUIL2(block,'L2V'+str(block[0]))
        time.sleep(2)
        block[6] = 0 #release the block

    def getblock(self,address):
        block = 0
        for i in range(4): 
            if(self.mem2[i][4] == address):
                if(address == 0 and i<2):
                    block = 0
                else:
                    block = self.mem2[i]
                    return self.accessBlock(block)
        if (block == 0):
            pos = self.genPos(address) #generate random position based on address
            block = self.mem2[pos] #the block to be replaced 
        block = self.accessBlock(block)
        #default values
        block[1] = 'DI'
        block[2] = 0
        block[3] = []
        block[4] = address
        block[5] = self.mainMem.getVal(address) #value in the memory
        time.sleep(1)
        return block
    
    def accessBlock(self,block):
        while(block[6] == 1):#busy waiting
            pass
        mutex.acquire()
        block[6] = 1
        mutex.release()
        if(block[1] == 'DM'): 
            owner = block[2]
            getval = self.caches[owner-1].M2S(block[4])
            if (getval != 0 ):
                block[5] = self.caches[owner-1].M2S(block[4]) #change owner status to 'S'
            block[3].append(owner)
            time.sleep(6)
            self.mainMem.setVal(block[4],block[5])
            block[1] = 'DS'
            time.sleep(2)
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
        time.sleep(6)
        self.mainMem.setVal(address,val)
        block[6] = 0
        self.updateGUIL2(block,'L2V'+str(block[0]))
        

    def S2I(self,cacheNum,address):
        block = self.getblock(address)
        if (len(block[3]) == 1): #if only one cache has it
            block[1] = 'DI'
            block[3] = []
        elif(len(block[3]) == 0):
            pass #CHECK
        else: #if more than one has it
            block[3].remove(cacheNum)
        block[6] = 0
        self.updateGUIL2(block,'L2V'+str(block[0]))

    def updateGUIL2(self,block,key):
        blockstr = str(block[0])+') '+block[1] + ' O:' + str(block[2]) + ' Shar:'+'-'.join([str(elem) for elem in block[3]]) + ' Addr:' +str("{0:b}".format(block[4]))+' Val:'+str("{0:x}".format(block[5]))
        updateGUI(blockstr,key)

class MainMem:  
    def __init__(self):
        self.mem=[[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0]]
    
    def getVal(self,addr):
        return self.mem[addr][1]

    def setVal(self,addr,val):
        self.mem[addr][1] = val
        updateGUI(str("{0:b}".format(addr)) +" - " + str("{0:x}".format(val)),'MV'+str(addr))

