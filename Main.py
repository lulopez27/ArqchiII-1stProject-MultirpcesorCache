import threading
import time
from GUI import runGUI,updateWindow
from Hardware import Core,L1Cache,L2Cache,MainMem


def createAll():
    mainMem = MainMem()
    l2 = L2Cache(mainMem)
    createCores(l2)

# cache = L1Cache(0,l2)
# cores.append(Core(cache,0))
# l2.addCache(cache)
# print('Caches: ')
# print(l2.genPos(0))

def createCores(l2):
    cores = []
    for i in range(4):
        cache = L1Cache(i,l2)
        core = Core(cache,i)
        cores.append(core)
        l2.addCache(cache)
    mainloop(cores)

def mainloop(cores):
    while(True):
        # core1 = cores[0]
        # core2 = cores[1]
        # updateWindow(core1.l1cache.write(1,0),'C1V1')
        # updateWindow(core2.l1cache.write(4,0),'C2V1')
        # for i in range(4):
        #     core = cores[i]
        #     core.coreThread()
        threads = []
        for i in range(4):
            core = cores[i]
            thread = threading.Thread(target=core.coreThread, args=())
            threads.append(thread)
        for i in range(4):
            thr = threads[i]
            thr.start()
        for i in range(4):
            thr = threads[i]
            thr.join()
        time.sleep(5)
        print("done")

x = threading.Thread(target=runGUI, args=())
x.start()
time.sleep(1)
createAll()