from Hardware import Core,L1Cache,L2Cache,MainMem

mainMem = MainMem()
l2 = L2Cache(mainMem)
cores = []
cache = L1Cache(0,l2)
cores.append(Core(cache,0))
l2.addCache(cache)
print('Caches: ')
l2.printCaches()

cores[0].coreThread()

def createCaches(cores,l2):
    for i in range(4):
        print(i)
        cache = L1Cache(i,l2)
        cores.append(Core(cache,i))
        l2.addCache(cache)
