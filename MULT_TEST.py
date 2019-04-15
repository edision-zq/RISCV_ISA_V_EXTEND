import simulator
from simulator import Simulator
from utility import *
import time
import math
import random
simulator.USING_WIDTH32 = True    # decide 4 bytes or 1 byte save

# execute stage
if __name__ == '__main__':
    print("测试乘法代码\n")
    start_time = time.time()
    filter_asmCode('./Code/MIPS_MULT.s', './Code/filter_asmcode.s')
    S = Simulator(AsmCodeInit=["./Code/MIPS_MULT_t.s", "_StartUp.S"],
                  DMemInit="./TestVector/initialize.mif", log="./Log/MIPS_MULT.dat", verbose=True)
    S.Initialize()
    PC = S.LabelToPC('main')
    S.RunAsm(PC=PC)
    # S.DumpDataMem("./MemDump/MIPS_MULT_MEM.mif")
    # S.Report("./Log/MIPS_MULT.rpt")
    print("测试完成")
    end_time = time.time()
    all_time = math.floor(end_time-start_time)
    print('the simulation need %d hours ,%d minutes,%dseconds' %
          (all_time//3600, (all_time % 3600)//60, all_time % 60))
