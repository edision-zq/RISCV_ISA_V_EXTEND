# ---------------------------------------------------------------------------------------------------
# Cryptography Processor Simula   tor
# Version : 1.0
# Date    : 2015-9-1
# Copyright@fudan.edu.cn
# ----------------------------------------------------------------------------------------------------
from bitarray import bitarray
import numpy as np
import sys
import os
import re
import fileinput
import time
from utility import *
import Crypto
import copy
import pdb

USING_WIDTH32=True
class CryptoExecutor:
    def __init__(self, AsmCodeInit=None, DMemInit=None, IMemInit=None, log=None, verbose=False):

        # Hardware modeling
        self._RF       = CryptoRegFiles()
        self._AsmCode  = CryptoAsmCode(InitFiles=AsmCodeInit)
        self._DataMem  = CryptoDataMemory(InitFile=DMemInit)
        self._PCStack  = CryptoPCStack()
        self._InstrSet = CryptoInstrSet()
        # InstrMem = CryptoInstrMemory(InitFile=IMemInit) # Not implemented yet

        # Executable information
        # Performance evaluation
        self._IC          = {}    # Count of each instruction
        self._Cycles      = {}    # Clock cycles of each instruction
        self._BeginSP     = None  # Begin stack pointer of the program
        self._EndSP       = None  # End stack pointer of the program

        # Function Calling
        self._FuncLabel = []
        self._FuncBeginPC = []
        self._FuncBeginCycle = []
        self._FuncEndCycle = []
        self._FuncCycles = []

        # For Debug
        self._LogFileName = log
        self._verbose = verbose
        self._Log = None

        # Set the behaviour of each instructions
        self._InstrSet.SetExec(Instr = "BLANK",    Func = self._ExecBLANK    )
        self._InstrSet.SetExec(Instr = "COMMENT",  Func = self._ExecCOMMENT  )
        self._InstrSet.SetExec(Instr = "LABEL",    Func = self._ExecLABEL    )
        self._InstrSet.SetExec(Instr = "setvl",    Func = self._Execsetvl    )
        self._InstrSet.SetExec(Instr = "add",      Func = self._Execadd      )
        self._InstrSet.SetExec(Instr = "sub",      Func = self._Execsub      )
        self._InstrSet.SetExec(Instr = "ret",      Func = self._Execret      )
        self._InstrSet.SetExec(Instr = "bnez",     Func = self._Execbnez     )
        self._InstrSet.SetExec(Instr = "bneq",     Func = self._Execbneq     )
        self._InstrSet.SetExec(Instr = "srli",     Func = self._Execsrli     )
        self._InstrSet.SetExec(Instr = "slli",     Func = self._Execslli     )
        self._InstrSet.SetExec(Instr = "ld",       Func = self._Execld       )
#        self._InstrSet.SetExec(Instr = "sw",       Func = self._Execsw       )
        self._InstrSet.SetExec(Instr = "li",       Func = self._Execli       )
        self._InstrSet.SetExec(Instr = "liv",      Func = self._Execliv      )
        self._InstrSet.SetExec(Instr = "mv",       Func = self._Execmv       )
        self._InstrSet.SetExec(Instr = "mul",      Func = self._Execmul      )
        self._InstrSet.SetExec(Instr = "subi",     Func = self._Execsubi     )
        self._InstrSet.SetExec(Instr = "call",     Func = self._Execcall     )
#        self._InstrSet.SetExec(Instr = "vcfg",     Func = self._Execvcfg     )
        # Instruction Set of RISC-V Vector
#        self._InstrSet.SetExec(Instr = "vmadd",    Func = self._Execvmadd    )
#        self._InstrSet.SetExec(Instr = "vnmadd",   Func = self._Execvnmadd   )
#        self._InstrSet.SetExec(Instr = "vmsub",    Func = self._Execvmsub    )
#        self._InstrSet.SetExec(Instr = "vnmsub",   Func = self._Execvnmsub   )
        self._InstrSet.SetExec(Instr = "vadd",     Func = self._Execvadd     )
#        self._InstrSet.SetExec(Instr = "vaddi",    Func = self._Execvaddi    )
#        self._InstrSet.SetExec(Instr = "vsub",     Func = self._Execvsub     )
#        self._InstrSet.SetExec(Instr = "vsubi",    Func = self._Execvsubi    )
#        self._InstrSet.SetExec(Instr = "vand",     Func = self._Execvand     )
#        self._InstrSet.SetExec(Instr = "vandi",    Func = self._Execvandi    )
#        self._InstrSet.SetExec(Instr = "vdiv",     Func = self._Execvdiv     )
#        self._InstrSet.SetExec(Instr = "vsge",     Func = self._Execvsge     )
#        self._InstrSet.SetExec(Instr = "vsne",     Func = self._Execvsne     )
#        self._InstrSet.SetExec(Instr = "vslt",     Func = self._Execvslt     )
#        self._InstrSet.SetExec(Instr = "vmax",     Func = self._Execvmax     )
#        self._InstrSet.SetExec(Instr = "vmin",     Func = self._Execvmin     )
        self._InstrSet.SetExec(Instr = "vmul",     Func = self._Execvmul     )
#        self._InstrSet.SetExec(Instr = "vmulh",    Func = self._Execvmulh    )
#        self._InstrSet.SetExec(Instr = "vor",      Func = self._Execvor      )
#        self._InstrSet.SetExec(Instr = "vori",     Func = self._Execvori     )
#        self._InstrSet.SetExec(Instr = "vrem",     Func = self._Execvrem     )
#        self._InstrSet.SetExec(Instr = "vsll",     Func = self._Execvsll     )
#        self._InstrSet.SetExec(Instr = "vslli",    Func = self._Execvslli    )
#        self._InstrSet.SetExec(Instr = "vsra",     Func = self._Execvsra     )
#        self._InstrSet.SetExec(Instr = "vsrai",    Func = self._Execvsrai    )
#        self._InstrSet.SetExec(Instr = "vsrl",     Func = self._Execvsrl     )
#        self._InstrSet.SetExec(Instr = "vsrli",    Func = self._Execvsrli    )
#        self._InstrSet.SetExec(Instr = "vxor",     Func = self._Execvxor     )
#        self._InstrSet.SetExec(Instr = "vxori",    Func = self._Execvxori    )
#        self._InstrSet.SetExec(Instr = "vclass",   Func = self._Execvclass   )
#        self._InstrSet.SetExec(Instr = "vsgnj",    Func = self._Execvsgnj    )
#        self._InstrSet.SetExec(Instr = "vsgnjn",   Func = self._Execvsgnjn   )
#        self._InstrSet.SetExec(Instr = "vsgnjx",   Func = self._Execvsgnjx   )
#        self._InstrSet.SetExec(Instr = "vsqrt",    Func = self._Execvsqrt    )
#        self._InstrSet.SetExec(Instr = "vcvt",     Func = self._Execvcvt     )
#        self._InstrSet.SetExec(Instr = "vmv",      Func = self._Execvmv      )
        self._InstrSet.SetExec(Instr = "vld",      Func = self._Execvld      )
        self._InstrSet.SetExec(Instr = "vst",      Func = self._Execvst      )
#        self._InstrSet.SetExec(Instr = "vlds",     Func = self._Execvlds     )
#        self._InstrSet.SetExec(Instr = "vsts",     Func = self._Execvsts     )
        self._InstrSet.SetExec(Instr = "vldx",     Func = self._Execvldx     )
#        self._InstrSet.SetExec(Instr = "vstx",     Func = self._Execvstx     )
#        self._InstrSet.SetExec(Instr = "vamoswap", Func = self._Execvamoswap )
#        self._InstrSet.SetExec(Instr = "vamoadd",  Func = self._Execvamoadd  )
#        self._InstrSet.SetExec(Instr = "vamand",   Func = self._Execvamoand  )
#        self._InstrSet.SetExec(Instr = "vamoor",   Func = self._Execvamoor   )
#        self._InstrSet.SetExec(Instr = "vamoxor",  Func = self._Execvamoxor  )
#        self._InstrSet.SetExec(Instr = "vamomax",  Func = self._Execvamomax  )
#        self._InstrSet.SetExec(Instr = "vamomin",  Func = self._Execvamomin  )
        # 添加MIPS指令集
        self._InstrSet.SetExec(Instr = "move",     Func = self._Execmv     )
        self._InstrSet.SetExec(Instr = "addi",     Func = self._Execaddi     )
        self._InstrSet.SetExec(Instr = "addiu",     Func = self._Execaddi     )
        self._InstrSet.SetExec(Instr = "addu",     Func = self._Execadd     )
        self._InstrSet.SetExec(Instr = "add",     Func = self._Execadd     )
        self._InstrSet.SetExec(Instr = "beq",     Func = self._Execbeq     )
        self._InstrSet.SetExec(Instr = "bne",     Func = self._Execbneq     )
        self._InstrSet.SetExec(Instr = "bgt",     Func = self._Execbgt     )
        self._InstrSet.SetExec(Instr = "andi",     Func = self._Execandi     )
        self._InstrSet.SetExec(Instr = "srl",     Func = self._Execsrli     )
        self._InstrSet.SetExec(Instr = "sll",     Func = self._Execslli     )
        self._InstrSet.SetExec(Instr = "sltu",     Func = self._Execsltu     )
        self._InstrSet.SetExec(Instr = "jal",     Func = self._Execjal     )
        self._InstrSet.SetExec(Instr = "j",     Func = self._Execcall     )
        self._InstrSet.SetExec(Instr = "jr",     Func = self._Execjr     )
        self._InstrSet.SetExec(Instr = "lw",       Func = self._Execlw       )
        self._InstrSet.SetExec(Instr = "sw",       Func = self._Execsw2       )
        self._InstrSet.SetExec(Instr = "div",      Func = self._Execdiv2      )
        self._InstrSet.SetExec(Instr = "mfhi",      Func = self._Execmfhi      )



    def SaveSelf(self):
        return copy.deepcopy(self)

    def RecoverSelf(self, Saved):
        # Recover internal state from the saved state
        self._RF          = Saved._RF
        self._AsmCode     = Saved._AsmCode
        self._DataMem     = Saved._DataMem
        self._PCStack     = Saved._PCStack
        self._InstrSet    = Saved._InstrSet
        self._IC          = Saved._IC
        self._Cycles      = Saved._Cycles
        self._BeginSP     = Saved._BeginSP
        self._EndSP       = Saved._EndSP
        self._LogFileName = Saved._LogFileName
        self._Log         = Saved._Log
        self._verbose     = Saved._verbose

    def IncreaseIC(self, Instr):
        if Instr in self._IC.keys():
            self._IC[Instr] = self._IC[Instr] + 1
        else :
            self._IC[Instr] = 1

    def IncreaseCycles(self, Instr, key, value):
        assert (key=="Serial") or (key=="Parallel"), "Wrong Parameters\n"
        if Instr in self._Cycles.keys():
            if key in self._Cycles[Instr].keys():
                self._Cycles[Instr][key] = self._Cycles[Instr][key] + value
            else:
                self._Cycles[Instr][key] = value
        else:
            if key == "Serial":
                self._Cycles[Instr] = {"Serial" : value}
            else:
                self._Cycles[Instr] = {"Parallel" : value}

    # Used to calculate total instruction count
    def GetTotalIC(self):
        TotalIC = 0
        for instr in self._IC.keys():
            TotalIC = TotalIC + self._IC[instr]
        return TotalIC

    # Used to calculte total clock cycles
    # Set InstrParallel=True to analysis total clock cycles with instruction parallelism considered
    def GetTotalCycles(self, InstrParallel=False):
        TotalCycles = 0
        for instr in self._Cycles.keys():
            if InstrParallel==True :
                TotalCycles = TotalCycles + self._Cycles[instr]["Parallel"]
            else :
                TotalCycles = TotalCycles + self._Cycles[instr]["Serial"]
        return TotalCycles

    # CPI = TotalCycles / TotalIC
    # Set InstrParallel=True to analysis CPI with instruction parallelism considered
    def GetCPI(self, InstrParallel=False):
        return float(self.GetTotalCycles(InstrParallel)) / float(self.GetTotalIC())

    def ReportFunc(self, FuncLabel):
        if(not FuncLabel in self._FuncLabel):
            self._FuncLabel.append(FuncLabel)
            self._FuncBeginPC.append(None)
            self._FuncBeginCycle.append(None)
            self._FuncEndCycle.append(None)
            self._FuncCycles.append(0)

    # Report information about the whole program
    # Used to analysis performance of the whole system
    def Report(self, File):
        HFile = open(File, "w")
        print("#=================================================================================================", sep="", end='\n', file=HFile, flush=False)
        print("#                                 Report of the whole program                                     ", sep="", end='\n', file=HFile, flush=False)
        print("#   Simulator : Cryptography Processor Simulator V1.0                                             ", sep="", end='\n', file=HFile, flush=False)
        print("#   Date      : %s                                 "%time.strftime("%Y-%m-%d %X", time.localtime()), sep="", end='\n', file=HFile, flush=False)
        print("#=================================================================================================", sep="", end='\n', file=HFile, flush=False)
        # CPI
        print("%-20s    | %-20s    | %-20s"%("Instruction Count", "Cycles-Serial", "Cycles-Parallel"), sep="", end='\n', file=HFile, flush=False)
        for instr in self._IC.keys():
            print("%-10s : %-10s |    %-20s |    %-20s"%(instr,self._IC[instr], self._Cycles[instr]["Serial"], self._Cycles[instr]["Parallel"]), sep="", end="\n", file=HFile, flush=False)
        print("%-10s : %-10s |    %-20s |    %-20s"%("total", str(self.GetTotalIC()), str(self.GetTotalCycles(InstrParallel=False)), str(self.GetTotalCycles(InstrParallel=True))), sep="", end="\n", file=HFile, flush=False)
        print("%-10s : %-10s"%("CPI-Serial",   str(self.GetCPI(InstrParallel=False))), sep="", end="\n", file=HFile, flush=False)
        print("%-10s : %-10s"%("CPI-Parallel", str(self.GetCPI(InstrParallel=True))),  sep="", end="\n", file=HFile, flush=False)

 #       # Stack
        print("\n\n#====================================Stack Usage Report========================================", sep="", end='\n', file=HFile, flush=False)
        print("%-30s : %-10s"%("Begin Stack", str(self._BeginSP)), sep="", end="\n", file=HFile, flush=False)
        print("%-30s : %-10s"%("End Stack", str(self._EndSP)), sep="", end="\n", file=HFile, flush=False)
        print("%-30s : %-10s"%("End Stack-Begin Stack", str(self._EndSP - self._BeginSP)), sep="", end="\n", file=HFile, flush=False)


        # Function cycles
        print("\n\n#====================================Function Cycles========================================", sep="", end='\n', file=HFile, flush=False)
        for index in range(0, len(self._FuncLabel)):
            print("%-30s : %-10s"%("Function Label", str(self._FuncLabel[index])), sep="", end="\n", file=HFile, flush=False)
            print("%-30s : %-10s"%("Cycles Totally", str(self._FuncCycles[index])), sep="", end="\n", file=HFile, flush=False)
            print("\n")



        HFile.close()

    def LabelToPC(self, Label):
        return self._AsmCode.LabelToPC(Label)

    def DumpDataMem(self, File):
        self._DataMem.DumpMem(File)

    # initialize internal state
    def Initialize(self):
        BeginPC = self._AsmCode.LabelToPC("_InitBegin")
        EndPC   = self._AsmCode.LabelToPC("_InitEnd")
        CurrentPC = BeginPC
        if self._verbose:
            print("Initializing internal state \n")
            self._Log = open(self._LogFileName, "w")
        while CurrentPC <= EndPC:
            ExecStatus, NextPC = self.StepAsm(PC=CurrentPC)
            CurrentPC = NextPC
            assert ExecStatus, "Run Failed\n"

    # Use assembly code to simulate hardware behaviour
    def StepAsm(self, PC=None):
        assert PC != None, "Wrong Parameters\n"
        ExecStatus = False
        Asm = self._AsmCode[PC]
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        if Matched:
            Exec  = self._InstrSet.GetExec(Instr)
            self._RF["PC"] = PC   # Set current PC
            self._Log.write("\n%s (PC = %d)\n"%(Asm, PC))

            # Info for some function
            if (PC-1 in self._FuncBeginPC):
                index = self._FuncBeginPC.index(PC-1)
                self._FuncEndCycle[index] = self.GetTotalCycles()
                self._FuncCycles[index] = self._FuncCycles[index] + self._FuncEndCycle[index] - self._FuncBeginCycle[index]

            ExecStatus, PC = Exec(Asm, PC)
            self._RF["PC"] = PC   # Update PC
            return ExecStatus, PC
        else:
            print("Unknown Instruction or Instructions Matched Twice "+Asm+"\n")
            print("Exiting...\n")
            sys.exit("Run Failed\n")

    def RunAsm(self, PC=None):
        assert PC != None, "Wrong Parameters\n"
        if self._verbose:
            print("Running Asm. Start PC = " + str(PC))
        end_PC = self._AsmCode.LabelToPC('end')
        while self._RF["PC"] != None and (PC != end_PC):
            self._RF["PC"] = PC   # Set current PC
            ExecStatus, PC = self.StepAsm(PC)
            self._RF["PC"] = PC   # Update PC
            assert ExecStatus, "Run Failed\n"
        self._Log.close()

	# Modeling Behaviour of each instructions
    def _ExecBLANK  (self, Asm="", PC=None):
        return True, PC+1

    def _ExecCOMMENT(self, Asm="", PC=None):
        return True, PC+1

    def _ExecLABEL  (self, Asm="", PC=None):
        if self._verbose:
            print("label:"+Asm)
        return True, PC+1

    def _Execsetvl    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(ret) or self._RF.IsLocked(r1):
            return False, PC
        else:
            s1 = self._RF[r1]
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, s1))
            if s1>= self._RF["mvl"]:
                result = self._RF["vl"] = self._RF[ret] = self._RF["mvl"]
            elif s1<(self._RF["mvl"]):
                result = self._RF["vl"] = self._RF[ret] = s1
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result 1 : %s = %x \n"%(ret, result))
            return True, PC+1

    def _Execvld    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(ret) or self._RF.IsLocked(r1):
            return False, PC
        else:
            Offset = self._RF[r1]
            Addr   = self._RF["sp"] + Offset
            self._Log.write("offset : %s = %x  \nstack pointer : %s = %x"%(r1, Offset, "sp", self._RF["sp"]))
            result = 0
            for i in range(self._RF["mvl"]):
                if i<self._RF["vl"]:
                    result = result + (self._DataMem[Addr+i]<<(32*i))
            self._RF[ret] = result
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result 1 : %s = %x \n"%(ret, result))
            return True, PC+1

    def _Execvmul    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or self._RF.IsLocked(ret):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = 0
            for i in range(self._RF["vl"]):
                tempt1 = (s1>>(i*32)) & 0xffffffff
                tempt2 = (s2>>(i*32)) & 0xffffffff
                tempt = tempt1 * tempt2
                result = result + (tempt<<(i*32))
            self._RF[ret] = result
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret, result))
            return True, PC+1

    def _Execvst    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r1, r2 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(r2) or self._RF.IsLocked(r1):
            return False, PC
        else:
            Offset = self._RF[r2]
            Addr   = self._RF["sp"] + Offset
            self._Log.write("Store  From Memory Reg: %s to Address %x, Value is %x \n" % (r1, Addr, self._RF[r1]))
            for i in range(self._RF["vl"]):
                tempt = (self._RF[r1]>>(32*i)) & 0xffffffff
                self._DataMem[Addr + i] = tempt
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            # information about Stack
            if (self._BeginSP == None) and (self._EndSP == None):
                self._BeginSP = Addr
                self._EndSP = Addr
            if Addr > self._EndSP:
                self._EndSP = Addr
            return True, PC+1

    def _Execadd    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or self._RF.IsLocked(ret):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = (s1 + s2)
            self._RF[ret] = result
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret, result))
            return True, PC+1

    def _Execsltu    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or self._RF.IsLocked(ret):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = 1 if (s1 < s2) else 0
            self._RF[ret] = result
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret, result))
            return True, PC+1

    def _Execandi    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1  = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        if self._RF.IsLocked(r1) or self._RF.IsLocked(ret):
            return False, PC
        else:
            s1 = self._RF[r1]
            self._Log.write("Source Reg 1 : %s = %x  \nImm : %x  \n"%(r1, s1, imm))
            result = s1 & imm
            self._RF[ret] = result
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret, result))
            return True, PC+1

    def _Execsub    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or self._RF.IsLocked(ret):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = (s1 - s2)
            self._RF[ret] = result
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret, result))
            return True, PC+1

    def _Execli(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret = Match.group(1)
        if re.match('-?0x', Match.group(2)):
            imm = int(Match.group(2), 16)
        else:
            imm = int(Match.group(2))
        self._Log.write("Imm = %x  \n" % (imm))
        self._RF[ret] = imm
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execmv(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r0 = Match.group(1), Match.group(2)
        self._Log.write("Source Reg 0 : %s = %x  \n" % (r0, self._RF[r0]))
        self._RF[ret] = self._RF[r0]
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execmfhi(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r0 = Match.group(1)
        self._Log.write("Source Reg : %s = %x  \nTarget Reg : %s = %x  \n" % ("Hi",self._RF["Hi"] , r0, self._RF[r0]))
        self._RF[r0] = self._RF["Hi"]
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (r0, self._RF[r0]))
        return True, PC + 1

    def _Execbnez   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r1, label = Match.group(1), Match.group(2)
        if self._RF.IsLocked(r1):
            return False, PC
        else:
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            if self._RF[r1] != 0:
                return True, self._AsmCode.LabelToPC(label)
            else:
                return True, PC+1

    def _Execbneq   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r1, r2, label = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r1):
            return False, PC
        else:
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            if self._RF[r1] != self._RF[r2]:
                return True, self._AsmCode.LabelToPC(label)
            else:
                return True, PC+1

    def _Execbgt   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r1, r2, label = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r1):
            return False, PC
        else:
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            if self._RF[r1] > self._RF[r2]:
                return True, self._AsmCode.LabelToPC(label)
            else:
                return True, PC+1

    def _Execbeq   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r1, r2, label = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r1):
            return False, PC
        else:
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            if self._RF[r1] == self._RF[r2]:
                return True, self._AsmCode.LabelToPC(label)
            else:
                return True, PC+1

    def _Execret   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        return True, self._RF["ra"]

    def _Execvadd    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or self._RF.IsLocked(ret):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = 0
            for i in range(self._RF["vl"]):
                tempt1 = (s1>>(i*32)) & 0xffffffff
                tempt2 = (s2>>(i*32)) & 0xffffffff
                tempt = tempt1 + tempt2
                result = result + (tempt<<(32*i))
            self._RF[ret] = result
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret, result))
            return True, PC+1

    def _Execvstx    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r1, r2 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            self._Log.write("Store  From Memory Reg: %s to Address %x, Value is %x \n" % (r1, Addr, self._RF[r1]))
            for i in range(self._RF["vl"]):
                Offset = (self._RF[r2]>>(32*i)) & 0xffffffff
                Addr   = self._RF[sp] + Offset
                self._DataMem[Addr] = (self._RF[r1]>>(32*i)) & 0xffffffff
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            # information about Stack
            if (self._BeginSP == None) and (self._EndSP == None):
                self._BeginSP = Addr
                self._EndSP = Addr
            if Addr > self._EndSP:
                self._EndSP = Addr
            return True, PC+1

    def _Execvldx    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r1, r2 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            result = 0
#            self._Log.write("load  From Address: %s to Mmeory Reg : %x, Value is %x \n" % (Addr, r2, self._RF[r2]))
            for i in range(self._RF["vl"]):
                Offset = (self._RF[r2]>>(32*i)) & 0xffffffff
                Addr   = self._RF["sp"] + Offset
                result = result + (self._DataMem[Addr]<<(32*i))
            self._RF[r1] = result
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            return True, PC+1

    def _Execsw(self, Asm="", PC=None):
        # Instruction behaviour
        Match = self._InstrSet.Match(Asm)
        Mem = Match.group(2)
        Reg = Match.group(1)
        MemSplit = (re.match(r'(-?\w+)(\((\w+)\))?', Mem))
        Offset = int(MemSplit.group(1))
        Pt = (MemSplit.group(3))
        Addr = self._RF[Pt] + Offset
        self._Log.write("LOAD  From Memory Address: %x From Reg %s, Value is %x \n" % (Addr, Reg, self._DataMem[Addr]))
        self._DataMem[Addr] = self._RF[Reg]
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        # Information about Stack
        if (self._BeginSP == None) and (self._EndSP == None):
            self._BeginSP = Addr
            self._EndSP = Addr
        if Addr > self._EndSP:
            self._EndSP = Addr
        return True, PC + 1

    def _Execsw2(self, Asm="", PC=None):
        # Instruction behaviour
        Match = self._InstrSet.Match(Asm)
        Mem = Match.group(2)
        Reg = Match.group(1)
        MemSplit = (re.match(r'(-?\w+)(\((\$\w+)\))?', Mem))
        Offset = int(MemSplit.group(1))
        Pt = (MemSplit.group(3))
        Addr = self._RF[Pt] + Offset
        self._Log.write("LOAD  From Memory Address: %x From Reg %s, Value is %x \n" % (Addr, Reg, self._DataMem[Addr]))
        self._DataMem[Addr] = self._RF[Reg]
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        # Information about Stack
        if (self._BeginSP == None) and (self._EndSP == None):
            self._BeginSP = Addr
            self._EndSP = Addr
        if Addr > self._EndSP:
            self._EndSP = Addr
        return True, PC + 1

    def _Execsrli(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        self._Log.write("Source Reg 0 : %s = %x  \nImm: %x  \n" % (r1, self._RF[r1], imm))
        s1 = self._RF[r1]
        result = s1>>imm
        self._RF[ret] = result
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execslli(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        self._Log.write("Source Reg 0 : %s = %x  \nImm: %x  \n" % (r1, self._RF[r1], imm))
        s1 = self._RF[r1]
        result = (s1<<imm) & 0xffffffff
        self._RF[ret] = result
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execaddi(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        self._Log.write("Source Reg 0 : %s = %x  \nImm: %x  \n" % (r1, self._RF[r1], imm))
        s1 = self._RF[r1]
        result = s1 + imm
        self._RF[ret] = result
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execsubi(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        self._Log.write("Source Reg 0 : %s = %x  \nImm: %x  \n" % (r1, self._RF[r1], imm))
        s1 = self._RF[r1]
        result = s1 - imm
        self._RF[ret] = result
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execld(self, Asm="", PC=None):
        # Instruction behaviour
        Match = self._InstrSet.Match(Asm)
        Mem = Match.group(2)
        Reg = Match.group(1)
        MemSplit = (re.match(r'(-?\w+)(\((\w+)\))?', Mem))
        Offset = int(MemSplit.group(1))
        Pt = (MemSplit.group(3))
        Addr = self._RF[Pt] + Offset
        self._Log.write("LOAD  From Memory Address: %x From Reg %s, Value is %x \n" % (Addr, Reg, self._DataMem[Addr]))
        self._RF[Reg] = self._DataMem[Addr]
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        # Information about Stack
        if (self._BeginSP == None) and (self._EndSP == None):
            self._BeginSP = Addr
            self._EndSP = Addr
        if Addr > self._EndSP:
            self._EndSP = Addr
        return True, PC + 1

    def _Execlw(self, Asm="", PC=None):
        # Instruction behaviour
        Match = self._InstrSet.Match(Asm)
        Mem = Match.group(2)
        Reg = Match.group(1)
        MemSplit = (re.match(r'(-?\w+)(\((\$\w+)\))?', Mem))
        Offset = int(MemSplit.group(1))
        Pt = (MemSplit.group(3))
        Addr = self._RF[Pt] + Offset
        self._Log.write("LOAD  From Memory Address: %x From Reg %s, Value is %x \n" % (Addr, Reg, self._DataMem[Addr]))
        self._RF[Reg] = self._DataMem[Addr]
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        # Information about Stack
        if (self._BeginSP == None) and (self._EndSP == None):
            self._BeginSP = Addr
            self._EndSP = Addr
        if Addr > self._EndSP:
            self._EndSP = Addr
        return True, PC + 1

    def _Execliv(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret = Match.group(1)
        if re.match('-?0x', Match.group(2)):
            imm = int(Match.group(2), 16)
        else:
            imm = int(Match.group(2))
        self._Log.write("Imm = %x  \n" % (imm))
        self._RF[ret] = imm
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execmul    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or self._RF.IsLocked(ret):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = (s1 * s2) & 0xffffffff
            self._RF[ret] = result
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret, result))
            return True, PC+1

    def _Execdiv    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r1, r2 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            self._RF[r1] = s1//s2
            self._RF[r2] = s1%s2
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result 1 : %s = %x \nResult 2 : %s = %x"%(r1, self._RF[r1], r2, self._RF[r2]))
            return True, PC+1

    def _Execdiv2    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r1, r2 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            self._RF["Lo"] = s1//s2
            self._RF["Hi"] = s1%s2
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result 1 : %s = %x \nResult 2 : %s = %x"%(r1, self._RF[r1], r2, self._RF[r2]))
            return True, PC+1

    def _Execcall  (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        label = Match.group(1)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self._Log.write("Jump to label: %s" % (label))
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        return True, self._AsmCode.LabelToPC(label)

    def _Execjal  (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        label = Match.group(1)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self._Log.write("Jump to label: %s, and link: %d" % (label, PC+1))
        self._RF["$ra"] = PC + 1
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        return True, self._AsmCode.LabelToPC(label)

    def _Execjr  (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        addr_reg = Match.group(1)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self._Log.write("Jump to $ra: %d" % (self._RF[addr_reg]))
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        return True, self._RF[addr_reg]

class CryptoDataMemory:
    # Mif file is used to initialize data memory
    def __init__(self, InitFile=None):
        if InitFile:
            self._Mem = read_mif(InitFile)
        else:
            # Memory looks like the following expression
            # Mem = {  0 : 123,
            #          1 : 456,
            #          2 : 789}
            self._Mem = {}

    def __getitem__(self, addr):
        assert addr in self._Mem.keys(), "Read memory without initilization \n"
        return self._Mem[addr]

    def __setitem__(self, addr, data):
        self._Mem[addr] = data

    def DumpMem(self, MifFile):
        write_mif(MifFile, self._Mem, data_width=256)


class CryptoInstrMemory:
    # Mif file is used to initilized instruction memroy
    def __init__(self, InitFile=None):
        """ Not implemented yet """
        pass

class CryptoPCStack:
    # Program Stack. Width : 32 bits
    def __init__(self):
        self._Stack = [None]
    def __getitem__(self, Index):
        return self._Stack[Index]
    def __setitem__(self, Index, Value):
        self._Stack[Index] = Value

    def Push(self, PC):
        self._Stack.append(PC)

    def Pop(self):
        PC = self._Stack[-1]
        del self._Stack[-1]
        return PC
    def CurrentValue(self):
        return self._Stack[-1]


class CryptoAsmCode:
    # Mif file is used to initlized CryptoAsmCode
    def __init__(self, InitFiles=[]):
        self._AsmCode=[]
        for AsmFile in InitFiles:
            if re.match(r".*/?_startUp_filter\.S", AsmFile):
                for line in fileinput.input(AsmFile):
                    self._AsmCode.append(line.strip("\n,\r"))

        for AsmFile in InitFiles:
            if not re.match(r".*_startUp_filter\.S", AsmFile):
                for line in fileinput.input(AsmFile):
                    self._AsmCode.append(line.strip("\n,\r"))


    def LabelToPC(self, Label):

        assert self._AsmCode.count(Label+":")==1, "Label Error, multiple label found in asm code\n"
        return self._AsmCode.index(Label+":")


    def __getitem__(self, index):
        return self._AsmCode[index]

    def __setitem__(self, index, value):
        self._AsmCoe[index] = value

    # Since the asm code is read only, it is not to deepcoy this class to save current state
    # The __deepcopy__ simply return reference to this class, which will improve performance of the simulator
    def __deepcopy__(self, Memo):
        return self



class CryptoRegFiles:
    def __init__(self):
        # Control register. Width : 32 bits
        # Assuming the initialized value is 0, be careful
        CSR = {"CY" : {"Value": 0, "Locked": False},
               "mvl" : {"Value": 8, "Locked": False},
               "vl" : {"Value": 0, "Locked": False},
        }

        # Scalar registers. Width : 32 bits. The total sum is 32.
        # Assuming the initialized value is 0, be careful.
        Scalar ={
		        "s0" : {"Value" : 0, "Locked" : False},
		        "s1" : {"Value" : 0, "Locked" : False},
		        "s2" : {"Value" : 0, "Locked" : False},
		        "s3" : {"Value" : 0, "Locked" : False},
		        "s4" : {"Value" : 0, "Locked" : False},
		        "s5" : {"Value" : 0, "Locked" : False},
		        "s6" : {"Value" : 0, "Locked" : False},
		        "s7" : {"Value" : 0, "Locked" : False},
		        "s8" : {"Value" : 0, "Locked" : False},
		        "s9" : {"Value" : 0, "Locked" : False},
		        "s10" : {"Value" : 0, "Locked" : False},
		        "s11" : {"Value" : 0, "Locked" : False},
		        "s12" : {"Value" : 0, "Locked" : False},
		        "s13" : {"Value" : 0, "Locked" : False},
		        "s14" : {"Value" : 0, "Locked" : False},
		        "s15" : {"Value" : 0, "Locked" : False},
		        "s16" : {"Value" : 0, "Locked" : False},
		        "s17" : {"Value" : 0, "Locked" : False},
		        "s18" : {"Value" : 0, "Locked" : False},
		        "s19" : {"Value" : 0, "Locked" : False},
		        "s20" : {"Value" : 0, "Locked" : False},
		        "s21" : {"Value" : 0, "Locked" : False},
		        "s22" : {"Value" : 0, "Locked" : False},
		        "s23" : {"Value" : 0, "Locked" : False},
		        "s24" : {"Value" : 0, "Locked" : False},
		        "s25" : {"Value" : 0, "Locked" : False},
		        "s26" : {"Value" : 0, "Locked" : False},
		        "s27" : {"Value" : 0, "Locked" : False},
		        "s28" : {"Value" : 0, "Locked" : False},
		        "s29" : {"Value" : 0, "Locked" : False},
		        "s30" : {"Value" : 0, "Locked" : False},
                "s31" : {"Value" : 0, "Locked" : False},
                "$0" : {"Value" : 0, "Locked" : False},  # 添加MIPS寄存器
                "$s0" : {"Value" : 0, "Locked" : False},
                "$s1" : {"Value" : 0, "Locked" : False},
                "$s2" : {"Value" : 0, "Locked" : False},
                "$s3" : {"Value" : 0, "Locked" : False},
                "$s4" : {"Value" : 0, "Locked" : False},


                "$v0" : {"Value" : 0, "Locked" : False},
                "$v1" : {"Value" : 0, "Locked" : False},
                "$v2" : {"Value" : 0, "Locked" : False},
                "$v3" : {"Value" : 0, "Locked" : False},
                "$v4" : {"Value" : 0, "Locked" : False},
                "$v5" : {"Value" : 0, "Locked" : False},
                "Hi" : {"Value" : 0, "Locked" : False},
                "Lo" : {"Value" : 0, "Locked" : False},
                }

		# Vector registers. Width : 8 * 32 = 256 bits. The total sum is 32.
		# Assuming the initialized value is 0, be careful

        Vector ={
		        "v0" :  {"Value" : 0, "Locked" : False},
                "v1" :  {"Value" : 0, "Locked" : False},
                "v2" :  {"Value" : 0, "Locked" : False},
                "v3" :  {"Value" : 0, "Locked" : False},
                "v4" :  {"Value" : 0, "Locked" : False},
                "v5" :  {"Value" : 0, "Locked" : False},
                "v6" :  {"Value" : 0, "Locked" : False},
                "v7" :  {"Value" : 0, "Locked" : False},
                "v8" :  {"Value" : 0, "Locked" : False},
                "v9" :  {"Value" : 0, "Locked" : False},
                "v10" : {"Value" : 0, "Locked" : False},
                "v11" : {"Value" : 0, "Locked" : False},
                "v12" : {"Value" : 0, "Locked" : False},
                "v13" : {"Value" : 0, "Locked" : False},
                "v14" : {"Value" : 0, "Locked" : False},
                "v15" : {"Value" : 0, "Locked" : False},
                "v16" : {"Value" : 0, "Locked" : False},
                "v17" : {"Value" : 0, "Locked" : False},
                "v18" : {"Value" : 0, "Locked" : False},
                "v19" : {"Value" : 0, "Locked" : False},
                "v20" : {"Value" : 0, "Locked" : False},
                "v21" : {"Value" : 0, "Locked" : False},
                "v22" : {"Value" : 0, "Locked" : False},
                "v23" : {"Value" : 0, "Locked" : False},
                "v24" : {"Value" : 0, "Locked" : False},
                "v25" : {"Value" : 0, "Locked" : False},
                "v26" : {"Value" : 0, "Locked" : False},
                "v27" : {"Value" : 0, "Locked" : False},
                "v28" : {"Value" : 0, "Locked" : False},
                "v29" : {"Value" : 0, "Locked" : False},
                "v30" : {"Value" : 0, "Locked" : False},
                "v31" : {"Value" : 0, "Locked" : False},}

        # Address registers. Width : 32 bits. The total sum is 6.
        # Assuming the initialized value is 0, be careful.
        Address ={
		        "a0" : {"Value" : 0, "Locked" : False},
		        "a1" : {"Value" : 0, "Locked" : False},
		        "a2" : {"Value" : 0, "Locked" : False},
		        "a3" : {"Value" : 0, "Locked" : False},
		        "a4" : {"Value" : 0, "Locked" : False},
		        "a5" : {"Value" : 0, "Locked" : False},
                "$a0" : {"Value" : 0, "Locked" : False},
                "$a1" : {"Value" : 0, "Locked" : False},
                "$a2" : {"Value" : 0, "Locked" : False},
                "$a3" : {"Value" : 0, "Locked" : False},
                "$a4" : {"Value" : 0, "Locked" : False},
                "$a5" : {"Value" : 0, "Locked" : False},}

		# Tempt Register. Width : 256 bits
        # Assuming the initialized value is 0, be careful
        Tempt = { "t0" : {"Value" : 0, "Locked" : False},
                  "t1" : {"Value" : 0, "Locked" : False},
                  "$t0" : {"Value" : 0, "Locked" : False},
                  "$t1" : {"Value" : 0, "Locked" : False},
                  "$t2" : {"Value" : 0, "Locked" : False},
                  "$t3" : {"Value" : 0, "Locked" : False},
                  "$t4" : {"Value" : 0, "Locked" : False},}

		# Return Address Register. Width : 256 bits
        # Assuming the initialized value is 0, be careful
        RA = {
            "ra" : {"Value" : 0, "Locked" : False},
            "$ra" : {"Value" : 0, "Locked" : False}
            }

		# Link Register. Width : 256 bits
        # Assuming the initialized value is 0, be careful
        LR = { "lr" : {"Value" : 0, "Locked" : False} }

        # Frame Pointer register. Width : 256 bits
        # Assuming the initialized value is 0, be careful
        FP = { "fp" : {"Value" : 0, "Locked" : False} }

        # Stack Pointer. Width : 256 bits
        # Assuming the initialized value is 0, be careful
        SP = { 
            "sp" : {"Value" : 0, "Locked" : False},
            "$sp" : {"Value" : 0, "Locked" : False}
        }

        # General purpose pointer, Width : 256 bits
        # Assuming the initialized value is 0, be careful
        GP = { "GP" : {"Value" : 0, "Locked" : False} }

        # Program Counter. Width : 256 bits
        # Assuming the initialized value is 0, be careful
        PC = { "PC" : {"Value" : 0, "Locked" : False} }

        self._RF = {}
        self._RF.update(CSR)
        self._RF.update(Scalar)
        self._RF.update(Vector)
        self._RF.update(Address)
        self._RF.update(Tempt)
        self._RF.update(SP)
        self._RF.update(LR)
        self._RF.update(FP)
        self._RF.update(GP)
        self._RF.update(PC)
        self._RF.update(RA)



        # Performance Evaluation
        self._BeginSP = None
        self._EndSP = None

    def __getitem__(self, RegName):
        assert RegName in self._RF.keys(), "Error Register Name\n"
        return self._RF[RegName]["Value"]

    def __setitem__(self, RegName, Value):
        assert RegName in self._RF.keys(), "Error Register Name\n"
        self._RF[RegName]["Value"] = Value

    def IsLocked(self, RegName):
        return self._RF[RegName]["Locked"]

    def Lock(self, RegName):
        self._RF[RegName]["Locked"] = True

    def Unlock(self, RegName):
        self._RF[RegName]["Locked"] = False

    def UpdataPC(self, PC):
        self._RF["PC"] = PC

    def GetCurPC(self):
        return self._RF["PC"]

class CryptoInstrSet:
    def __init__(self):
        # Parameters for each instructions, including clock cycles to run each instruction
        # hardware hehaviour and regular expression patterns required to intepret asm code
        self._InstrParams = {
                # Used to intepret blank line in asm code
                "BLANK"      :  { "Cycles"  : 0                                           ,
                                  "Exec"    : None                                        ,
                                  "Pattern" : re.compile("^\s*$")                         ,
                                  "Params"  : 0}                                          ,
                # Used to intepret comment line in asm code
                "COMMENT"    :  { "Cycles"  : 0                                           ,
                                  "Exec"    : None                                        ,
                                  "Pattern" : re.compile("^#")                            ,
                                  "Params"  : 0}                                          ,
                # Pseudo insturctions
                "LABEL"      :  { "Cycles"  : 0                                           ,
                                  "Exec"    : None                                        ,
                                  "Pattern" : re.compile("[^#].+?:")                      ,
                                  "Params"  : 0},
                "setvl": { "Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+setvl\s+(\w+)\,\s+(\w+)"),
                    "Params": 0},
                "vld": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+vld\s+(\w+)\,\s+(\w+)"),
                    "Params": 0},
                "vmul": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+vmul\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                    "Params": 0},
                "vst": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+vst\s+(\w+)\,\s+(\w+)"),
                    "Params": 0}						,
                "add": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+add\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                    "Params": 0},
                "sub": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+sub\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                    "Params": 0},
                "bnez": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+bnez\s+(\w+)\,\s+(\w+)"),
                    "Params": 0},
                "bneq": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+bneq\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                    "Params": 0},
                "beq": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*beq\s+(\$\w+)\,\s+(\$\w+)\,\s+(\w+)"),
                    "Params": 0},
                "bgt": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*bgt\s+(\$\w+)\,\s+(\$\w+)\,\s+(\w+)"),
                    "Params": 0},
                "bne": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*bne\s+(\$\w+)\,\s+(\$\w+)\,\s+(\w+)"),
                    "Params": 0},
                "ret": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+ret"),
                    "Params": 0},
                "vadd": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+vadd\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                    "Params": 0},
                "vldx": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+vldx\s+(\w+)\,\s+(\w+)"),
                    "Params": 0},
                "vst": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+vst\s+(\w+)\,\s+(\w+)"),
                    "Params": 0},
                "sltu": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*sltu\s+(\$\w+)\,\s+(\$\w+)\,\s+(\$\w+)"),
                    "Params": 0},
                "srli": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+srli\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)"),
                    "Params": 0},
                "srl": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*srl\s+(\$\w+)\,\s+(\$\w+)\,\s+(-?\w+)"),
                    "Params": 0},
                "slli": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+slli\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)"),
                    "Params": 0},
                "sll": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*sll\s+(\$\w+)\,\s+(\$\w+)\,\s+(-?\w+)"),
                    "Params": 0},
                "ld": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+ld\s+(\w+)\,\s+(.+)"),
                    "Params": 0},
                "lw": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*lw\s+(\$\w+)\,\s+(.+)"),
                    "Params": 0},
                "sw": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*sw\s+(\$\w+)\,\s+(.+)"),
                    "Params": 0},
                "li": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+li\s+(\w+)\,\s+(-?\w+)"),
                   "Params": 0},
                "liv": {"Cycles": 8,
                   "Exec": None,
                   "Pattern": re.compile("\s+liv\s+(\w+)\,\s+(-?\w+)"),
                   "Params": 0},
                "mul": {"Cycles": 3,
                   "Exec": None,
                   "Pattern": re.compile("\s+mul\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                   "Params": 0},
                "div": {"Cycles": 4,
                   "Exec": None,
                   "Pattern": re.compile("\s*div\s+(\$\w+)\,\s+(\$\w+)"),
                   "Params": 0},
                "mv": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+mv\s+(\w+)\,\s+(\w+)"),
                   "Params": 0},
                "move": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s*move\s+(\$\w+)\,\s+(\$\w+)"),
                   "Params": 0},
                "addi": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*addi\s+(\$\w+)\,\s+(\$\w+)\,\s+(-?\w+)"),
                    "Params": 0},
                "addiu": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*addiu\s+(\$\w+)\,\s+(\$\w+)\,\s+(-?\w+)"),
                    "Params": 0},
                "addu": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*addu\s+(\$\w+)\,\s+(\$\w+)\,\s+(\$\w+)"),
                    "Params": 0},
                "add": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*add\s+(\$\w+)\,\s+(\$\w+)\,\s+(\$\w+)"),
                    "Params": 0},
                "andi": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*andi\s+(\$\w+)\,\s+(\$\w+)\,\s+(-?\w+)"),
                    "Params": 0},
                "subi": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+subi\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)"),
                    "Params": 0},
                "call": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+call\s+(\w+)"),
                    "Params": 0},
                "j": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*j\s+(\w+)"),
                    "Params": 0},
                "jr": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*jr\s+(\$\w+)"),
                    "Params": 0},
                "jal": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*jal\s+(\w+)"),
                    "Params": 0},
                "mfhi": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s*mfhi\s+(\$\w+)"),
                    "Params": 0},
        }

    # Set the behaviour of given instruction
    def SetExec(self, Instr, Func):
        assert Instr in self._InstrParams.keys(), "Unable to find coresponding instructions\n"+Instr
        self._InstrParams[Instr]["Exec"] = Func

    # Get the behaviour of given instruction
    def GetExec(self, Instr):
        assert Instr in self._InstrParams.keys(), "Unable to find coresponding instructions\n"+Instr
        return self._InstrParams[Instr]["Exec"]

    def SetCycles(self, Instr, NumCycles):
        assert Instr in self._InstrParams.keys(), "Unable to find coresponding instructions\n"+Instr
        self._InstrParams[Instr]["Cycles"] = NumCycles

    def GetCycles(self, Instr):
        assert Instr in self._InstrParams.keys(), "Unable to find coresponding instructions\n"+Instr
        return self._InstrParams[Instr]["Cycles"]

    def SetRePattern(self, Instr, ReParrten):
        assert Instr in self._InstrParams.keys(), "Unable to find coresponding instructions\n"+Instr
        self._InstrParams[Instr]["Pattern"] = ReParrten

    def GetRePattern(self, Instr):
        assert Instr in self._InstrParams.keys(), "Unable to find coresponding instructions\n"+Instr
        return self._InstrParams[Instr]["Pattern"]

    def MatchedOnce(self, Asm):
        Matched = False
        MatchedInstr = None
        for Instr in  self._InstrParams.keys():
            if Matched and self._InstrParams[Instr]["Pattern"].match(Asm):
                return False # Match twice
            elif self._InstrParams[Instr]["Pattern"].match(Asm):
                Matched = True
                MatchedInstr = Instr
        return Matched, MatchedInstr

    def MatchedInstrs(self, Asm):
        Instructions = []
        for Instr in self._InstrParams.keys():
            if self._InstrParams[Instr]["Pattern"].match(Asm):
                Instructions.append(Instr)
        return Instructions

    def Match(self, Asm):
        if self.MatchedOnce(Asm):
            for Instr in self._InstrParams.keys():
                m = self._InstrParams[Instr]["Pattern"].match(Asm)
                if m:
                    return m
        else:
            return None


    def __getitem__(self, Instr):
        return self._InstrParams[Instr]

    def __setitem__(self, Instr, Params):
        self._InstrParams[Instr] = Params


    # Since Regular expression pattern is not supported by copy.deepcopy, __deepcopy__ needs to be implemented manually
    # Since it is not necessary to save the InstructionSet class, the __deepcopy__ simply return reference to this class
    def __deepcopy__(self, Memo):
        return self


class Simulator(CryptoExecutor):
    def __init__(self, AsmCodeInit=None, DMemInit=None, IMemInit=None, log=None, verbose=False):
        CryptoExecutor.__init__(self, AsmCodeInit=AsmCodeInit, DMemInit=DMemInit, IMemInit=IMemInit, log=log, verbose=verbose)

if __name__=='__main__':
    print("Simulator for cyrptography processor\n")

