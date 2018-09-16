import simulator
from simulator import Simulator
from utility import *
import time
import math
import random
simulator.USING_WIDTH32 = True    # decide 4 bytes or 1 byte save	

# execute stage
if __name__ == '__main__':
    print("Test my diy code \n")
    start_time=time.time()
    filter_asmCode('./Code/convolution_k.s','./Code/filter_asmcode.s')
    S = Simulator(AsmCodeInit=["./Code/filter_asmcode.s", "_StartUp.S"], DMemInit="./TestVector/initialize.mif", log="./Log/Mycode.dat", verbose=True)
    S.Initialize()
    PC = S.LabelToPC('main')
    S.RunAsm(PC=PC)
    S.DumpDataMem("./MemDump/resultMemory.mif")
    S.Report("./Log/Mycode.rpt")
    print("Test Done")
    end_time=time.time()
    all_time=math.floor(end_time-start_time)
    print('the simulation need %d hours ,%d minutes,%dseconds'%(all_time//3600,(all_time%3600)//60,all_time%60))
file_output = open('./Result/actually_result.data', 'a')
file_input = open('./MemDump/resultMemory.mif')
result = file_input.readlines()
address = 8791
for i in range(9):
    address = address + 1
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', result[address])
    file_output.write(m1.group(4) + '\n')
file_input.close()
file_output.close()