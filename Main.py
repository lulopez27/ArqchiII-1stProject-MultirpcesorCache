from threading import Thread
import time
from GUI import runGUI,updateWindow
import GUI
from Hardware import Core,L1Cache,L2Cache,MainMem


def createAll():
    time.sleep(1)
    mainMem = MainMem()
    l2 = L2Cache(mainMem)
    createCores(l2)


def createCores(l2):
    cores = []
    for i in range(4):
        cache = L1Cache(i,l2)
        core = Core(cache,i)
        cores.append(core)
        l2.addCache(cache)
    mainloop(cores)

def mainloop(cores):
    time.sleep(0.5)
    GUI.step_mutex.acquire()
    GUI.step_wait = True
    GUI.step_mutex.release()
    while (GUI.step_wait):
        updateWindow('','running')
        if(GUI.dead):
                return
        elif(len(GUI.inst) > 0):
            updateWindow('*','running')
            GUI.step_mutex.acquire()
            cache = GUI.inst[0]
            read = GUI.inst[1]
            addr = GUI.inst[2]
            if(read):
                cores[cache].setInstread(addr)
            else:
                val = GUI.inst[3]
                cores[cache].setInstwrit(addr,val)
            GUI.inst = []
            GUI.step_mutex.release()
    while(True):
        updateWindow('','running')
        threads = []
        if(GUI.single_thread):
            updateWindow('*','running')
            for i in range(4):
                core = cores[i]
                core.coreThread()
        else:
            updateWindow('*','running')
            for i in range(4):
                core = cores[i]
                thread = Thread(target=core.coreThread, args=())
                threads.append(thread)
            for i in range(4):
                thr = threads[i]
                thr.start()
            for i in range(4):
                thr = threads[i]
                thr.join()
        if(GUI.step):
            GUI.step_mutex.acquire()
            GUI.step_wait = True
            GUI.step_mutex.release()
            while (GUI.step_wait):
                updateWindow('','running')
                if(GUI.dead):
                    return
                elif(len(GUI.inst) > 0):
                    updateWindow('*','running')
                    GUI.step_mutex.acquire()
                    cache = GUI.inst[0]
                    read = GUI.inst[1]
                    addr = GUI.inst[2]
                    if(read):
                        cores[cache].setInstread(addr)
                    else:
                        val = GUI.inst[3]
                        cores[cache].setInstwrit(addr,val)
                    GUI.inst = []
                    GUI.step_mutex.release()
        if(GUI.dead):
                return
        print("done")

x = Thread(target=createAll, args=())
x.start()
runGUI()