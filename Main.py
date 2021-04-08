from Hardware import Core,L1Cache,L2Cache,MainMem
pause = 0




mainMem = MainMem 
l2 = L2Cache(mainMem)
cores = []
for i in range(4):
    print(i)
    cache = L1Cache(i,l2)
    cores.append(Core(cache,i))
    l2.addCache(cache)
print('Caches: ')
l2.printCaches()
# cores = []
# for x in range(4): #Create the cores they're 4
#     cores.append(Core(l2cache,directory,x))
# print(cores[x].thr)
# for i in range(10):
#     CPU.nextInst(cores[0].cpu)

