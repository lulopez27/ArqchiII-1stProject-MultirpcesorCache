import numpy as np
from Main import isOdd,xor
run = True

class Core:
    def __init__(self,l1cache,l2cache,procNumb,control,directory): #create the core and hook it up
        self.prob = np.random.poisson(1, 1000)
        self.curr=0
        self.cpu = CPU()
        self.l1cache = l1cache
        self.l2cache = l2cache
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
    def __init__(self,memNum,directory): #,l2cache
        self.mem1={}
        self.mem1=[[0,0],[0,0]]
        # self.l2cache = l2cache
        self.memNum = memNum+1
        self.directory = directory

    def write(self,data,address):
        pass
        # self.checkAddress(address)

    def read(self,address):
        if not(self.checkAddress(address)): #readmiss
            self.removeAddress(address)
            #mutex start
            #mutex end
        else:
            #mutex start
            stat,_ = self.directory.getCacheBlock(self.memNum,address)
            stat = stat[self.memNum]
            pos = xor(isOdd(address),0x1)
            if(stat == 'M' or stat == 'S'): #its already in memory and has actual value
                pass #no need to do anything
            elif(stat == 'I'): #Current value is in memory but invalid
                self.mem1[pos] = self.directory.I2S(self.memNum,address)
            else: #the address is in some other state, an error
                self.errorprint()
                return [0,0]
            #mutex end
            return self.mem1[pos][0]
    
    def errorprint(self):
        print("ERRORR in cache")


    def checkAddress(self,address):
        if(isOdd(address)==1):
            return self.mem1[0][0] == address
        return  self.mem1[1][0] == address

    def removeAddress(self,address):#address is the new address thats desired
        oldAddress = self.getBlock(address)[0]# works because it is 1 way
        #mutex start
        stat,_ = self.directory.getCacheBlock(self.memNum,oldAddress)
        stat = stat[self.memNum]
        if('M' in stat):#if the block is in M it must be written to memory
            self.directory.M2I(self.memNum,oldAddress)#write the old block to memory and set is as I
        elif('S' in stat):#switch it to I in directory
            self.directory.S2I(self.memNum,oldAddress)#write the old block to memory and set is as I
        elif ('I' in stat):
            pass
        else:
            self.errorprint()
        block = self.directory.I2S(self.memNum,address)#get the memory block
        #mutex end
        pos = xor(isOdd(address),0x1)
        self.mem1[pos] = block #put new address into memory
    
    def getBlock(self,address): #returns block of mem specified by address
        if(isOdd(address)==1):
            return self.mem1[0]
        return self.mem1[1]

    
class Directory:
    def __init__(self,l2cache):
        self.directory = {}
        self.directory = [[0,'I','I','I','I'],[0,'I','I','I','I'],[0,'I','I','I','I'],[0,'I','I','I','I']] #Data and status, first two are for odds,MSI
        self.l2cache = l2cache

    def getCacheBlock(self,cacheNum,address): #CHECK IF IT RETURNS SHALLOW OR DEEP COPY, MUST BE SHALLOW COPY
        for i in range(4):
            if(address == self.directory[i][0]):
                return self.directory[i],i
        return 'N'

    def M2S(self,cacheNum,address): #M --> S, returns a whole block of memory
        cBlock,i = self.getCacheBlock(cacheNum,address)
        if cBlock == 'N':
            return self.notFound(address) #in case it is not in directory
        block = self.l2cache.getBlockl1(cacheNum,i,address)#put the block in l2, returns the block memory
        self.directory[i][cacheNum] = 'S'
        self.updatecache() #print current cache, DEBUG
        return block

    def M2I(self,cacheNum,address):#M --> I, returns a whole block of memory
        cBlock,i = self.getCacheBlock(cacheNum,address)
        if cBlock == 'N':
            return self.notFound(address) #in case it is not in directory
        block = self.l2cache.getBlockl1(cacheNum,i,address)#put the block in l2, returns the block memory
        self.directory[i][cacheNum] = 'I'
        self.updatecache() #print current cache, DEBUG
        return block

    # def S2M(self,cache,address):#M --> S, returns a whole block of memory

    def S2I(self,cacheNum,address):#S --> I, returns a whole block of memory
        cBlock,i = self.getCacheBlock(cacheNum,address)
        if cBlock == 'N':
            return self.notFound(address) #in case it is not in directory
        block = self.l2cache.getBlockl1(cacheNum,i,address)#put the block in l2, returns the block memory
        self.directory[i][cacheNum] = 'I'
        self.updatecache() #print current cache, DEBUG
        return block

    def I2S(self,cacheNum,address):#I --> S, returns a whole block of memory
        cBlock,i = self.getCacheBlock(cacheNum,address)
        if cBlock == 'N':
            return self.notFound(address) #in case it is not in directory
        elif ('M' in cBlock):#theres an M
            for j in range(1,5):
                if(self.directory[i][j] == 'M'): #check if there's an M, if so get mem and change it to S
                    block = self.M2S(j,address)
        else: #S or I, either way l2 is uptodate
            block = self.l2cache.getBlockl2(i)#get the block from l2
        self.directory[i][cacheNum] = 'S'
        self.updatecache() #print current cache, DEBUG
        return block


    # def I2M(self,cache,address):

    def notFound(self,address):
        print("didnt find address"+str(address))
    
    def updatecache(self):
        print(self.directory)

    # def contains(self,address):#check wether a position is already on L2, return bool
    #     if(isOdd(address)==1):
    #         return self.directory[0][0] == address or self.directory[1][0] == address 
    #     return self.directory[2][0] == address or self.directory[3][0] == address

    # def putAddrL2(self,address): #Put a new block in L2 from memory
    #     offset = np.random.randint(0,2)
    #     if(isOdd(address)==1):
    #         self.checkWT(offset,address) #Checks to write content to memory if needed
    #         self.changeL2Val(offset,address) #changes the value in L2
    #     offset +=2
    #     self.checkWT(offset,address) #Checks to write content to memory if needed
    #     self.changeL2Val(offset,address)
    
    # def changeL2Val(self,offset,address): #change the value of a block 
    #     self.l2cache.getAddrMainMem(offset,address)
    #     self.directory[offset][0] = address
    #     self.directory[offset][1] = self.directory[offset][2] = self.directory[offset][3] = self.directory[offset][4] = 'I'
    
    # def checkWT(self,offset,address):
    #     if('M' in self.directory):
    #         pos = self.directory.index('M')
    #         self.l1caches[pos]
    #     pass

class L2Cache:
    def __init__(self,mainmem,caches):
        self.mem2={}
        self.mem2=[[0,0],[0,0],[0,0],[0,0]]
        self.caches = caches
        self.mainmem=mainmem
    
    #Interactions with Main Memory
    def getAddrMainMem(self,pos,address): #get block from main memory
        self.mem2[pos][0] = address
        self.mem2[pos][1] = self.mainmem.getVal(address)

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

class Control:
    def __init__(self,directory):
        self.directory = directory
    
    def checkAddress(self,address): #check if an address is in directory, if it isnt add it to l2
        if(self.directory.contains(address)):
            return
        self.directory.putAddrL2(address)