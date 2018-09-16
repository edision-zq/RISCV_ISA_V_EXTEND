# ---------------------------------------------------------------------------------------------------
# Cryptography Processor Simulator
# Version : 1.0
# Date    : 2015-9-1
# Copyright@fudan.edu.cn
# ----------------------------------------------------------------------------------------------------
from bitarray import bitarray
import sys
import os
import re
import fileinput
import time
from utility import read_mif
from utility import write_mif
import Crypto
import copy
import pdb

def gmul(a, b, m, order = 8):
    p = 0
    for i in range(0,order):
        if (b % 2 == 1):
            p ^= a
        if ((a >> (order-1)) == 1):
            a = ((a * 2)) ^ m
        else:
            a = (a * 2)
        b = b >> 1
    return p
def gmul8_2(a, b, m8, m8_2):
    a1 = (a >> 8) & 0xff
    a2 = a & 0xff
    b1 = (b >> 8) & 0xff
    b2 = b & 0xff
    a1b1 = gmul(a1, b1, m8)
    a1b2 = gmul(a1, b2, m8)
    a2b1 = gmul(a2, b1, m8)
    a2b2 = gmul(a2, b2, m8)
    part1 = ((a1b2 ^ a2b1) << 8) | a2b2
    part2_1 = 0
    part2_2 = 0
    if (m8_2 & 1) == 1:
        part2_1 = a1b1
    if (m8_2 & 0b10) == 2:
        part2_2 = (a1b1 << 8)
    part2 = part2_1 | part2_2
    return part1 ^ part2
def gmul8_3(a, b, m8, m8_3):
    a1 = (a >> 16) & 0xff
    a2 = (a >> 8)  & 0xff
    a3 = a & 0xff
    b1 = (b >> 16) & 0xff
    b2 = (b >> 8) & 0xff
    b3 = b & 0xff
    a1b1 = gmul(a1, b1, m8)
    a1b2 = gmul(a1, b2, m8)
    a1b3 = gmul(a1, b3, m8)
    a2b1 = gmul(a2, b1, m8)
    a2b2 = gmul(a2, b2, m8)
    a2b3 = gmul(a2, b3, m8)
    a3b1 = gmul(a3, b1, m8)
    a3b2 = gmul(a3, b2, m8)
    a3b3 = gmul(a3, b3, m8)
    part1 = ((a1b3 ^ a2b2 ^ a3b1) << 16) | ((a2b3 ^ a3b2) << 8) | a3b3
    part2_1 = 0
    part2_2 = 0
    part2_3 = 0
    if (m8_3 & 1) == 1:
        part2_1 = a1b2 ^ a2b1
    if (m8_3 & 0b10) == 2:
        part2_2 = ((a1b2 ^ a2b1) << 8)
    if (m8_3 & 0b100) == 4:
        part2_3 = ((a1b2 ^ a2b1) << 16)
    part2 = part2_1 | part2_2 | part2_3
    if m8_3 == 0b001:
        part3 = a1b1 << 8
    elif m8_3 == 0b010:
        part3 = a1b1 << 16
    elif m8_3 == 0b011:
        part3 = (a1b1 << 16) | (a1b1 << 8)
    elif m8_3 == 0b100:
        part3 = a1b1 << 16
    elif m8_3 == 0b101:
        part3 = (a1b1 << 16) | (a1b1 << 8) | a1b1
    elif m8_3 == 0b110:
        part3 = a1b1 << 8
    elif m8_3 == 0b111:
        part3 = a1b1
    else:
        part3 = 0
    return part1 ^ part2 ^ part3
def gmul8_4(a, b, m8, m8_4):
    a1 = (a >> 24) & 0xff
    a2 = (a >> 16) & 0xff
    a3 = (a >> 8)  & 0xff
    a4 = a & 0xff
    b1 = (b >> 24) & 0xff
    b2 = (b >> 16) & 0xff
    b3 = (b >> 8)  & 0xff
    b4 = b & 0xff
    a1b1 = gmul(a1, b1, m8)
    a1b2 = gmul(a1, b2, m8)
    a1b3 = gmul(a1, b3, m8)
    a1b4 = gmul(a1, b4, m8)
    a2b1 = gmul(a2, b1, m8)
    a2b2 = gmul(a2, b2, m8)
    a2b3 = gmul(a2, b3, m8)
    a2b4 = gmul(a2, b4, m8)
    a3b1 = gmul(a3, b1, m8)
    a3b2 = gmul(a3, b2, m8)
    a3b3 = gmul(a3, b3, m8)
    a3b4 = gmul(a3, b4, m8)
    a4b1 = gmul(a4, b1, m8)
    a4b2 = gmul(a4, b2, m8)
    a4b3 = gmul(a4, b3, m8)
    a4b4 = gmul(a4, b4, m8)
    part1 = ((a1b4 ^ a2b3 ^ a3b2 ^ a4b1) << 24) | ((a2b4 ^ a3b3 ^ a4b2) << 16) | ((a3b4 ^ a4b3) << 8) | a4b4
    part2_1 = 0
    part2_2 = 0
    part2_3 = 0
    part2_4 = 0
    if (m8_4 & 1) == 1:
        part2_1 = a1b3 ^ a2b2 ^ a3b1
    if (m8_4 & 0b10) == 2:
        part2_2 = ((a1b3 ^ a2b2 ^ a3b1) << 8)
    if (m8_4 & 0b100) == 4:
        part2_3 = ((a1b3 ^ a2b2 ^ a3b1) << 16)
    if (m8_4 & 0b1000) == 8:
        part2_4 = ((a1b3 ^ a2b2 ^ a3b1) << 24)
    part2 = part2_1 | part2_2 | part2_3 | part2_4
    if m8_4 == 0b0001:
        part3 = (a1b2 ^ a2b1) << 8
    elif m8_4 == 0b0010:
        part3 = (a1b2 ^ a2b1) << 16
    elif m8_4 == 0b0011:
        part3 = ((a1b2 ^ a2b1) << 16) | ((a1b2 ^ a2b1) << 8)
    elif m8_4 == 0b0100:
        part3 = (a1b2 ^ a2b1) << 24
    elif m8_4 == 0b0101:
        part3 = ((a1b2 ^ a2b1) << 24) | ((a1b2 ^ a2b1) << 8)
    elif m8_4 == 0b0110:
        part3 = ((a1b2 ^ a2b1) << 24) | ((a1b2 ^ a2b1) << 16)
    elif m8_4 == 0b0111:
        part3 = ((a1b2 ^ a2b1) << 24) | ((a1b2 ^ a2b1) << 16) | ((a1b2 ^ a2b1) << 8)
    elif m8_4 == 0b1000:
        part3 = (a1b2 ^ a2b1) << 24
    elif m8_4 == 0b1001:
        part3 = ((a1b2 ^ a2b1) << 24) | ((a1b2 ^ a2b1) << 8) | (a1b2 ^ a2b1)
    elif m8_4 == 0b1010:
        part3 = ((a1b2 ^ a2b1) << 24) | ((a1b2 ^ a2b1) << 16) | ((a1b2 ^ a2b1) << 8)
    elif m8_4 == 0b1011:
        part3 = ((a1b2 ^ a2b1) << 24) | ((a1b2 ^ a2b1) << 16) | (a1b2 ^ a2b1)
    elif m8_4 == 0b1100:
        part3 = ((a1b2 ^ a2b1) << 16)
    elif m8_4 == 0b1101:
        part3 = ((a1b2 ^ a2b1) << 16) | ((a1b2 ^ a2b1) << 8) | (a1b2 ^ a2b1)
    elif m8_4 == 0b1110:
        part3 = ((a1b2 ^ a2b1) << 8)
    elif m8_4 == 0b1111:
        part3 = a1b2 ^ a2b1
    else:
        part3 = 0
    if m8_4 == 0b0001:
        part4 = a1b1 << 16
    elif m8_4 == 0b0010:
        part4 = a1b1 << 24
    elif m8_4 == 0b0011:
        part4 = (a1b1 << 24) | (a1b1 << 16)
    elif m8_4 == 0b0100:
        part4 = a1b1 << 16
    elif m8_4 == 0b0101:
        part4 = 0
    elif m8_4 == 0b0110:
        part4 = (a1b1 << 24) | (a1b1 << 16) | (a1b1 << 8)
    elif m8_4 == 0b0111:
        part4 = (a1b1 << 24) | (a1b1 << 8) | a1b1
    elif m8_4 == 0b1000:
        part4 = a1b1 << 24
    elif m8_4 == 0b1001:
        part4 = (a1b1 << 24) | (a1b1 << 16) | (a1b1 << 8) | a1b1
    elif m8_4 == 0b1010:
        part4 = (a1b1 << 16) | (a1b1 << 8)
    elif m8_4 == 0b1011:
        part4 = a1b1
    elif m8_4 == 0b1100:
        part4 = a1b1 << 24
    elif m8_4 == 0b1101:
        part4 = (a1b1 << 24) | (a1b1 << 16) | (a1b1 << 8)
    elif m8_4 == 0b1110:
        part4 = a1b1 << 16
    elif m8_4 == 0b1111:
        part4 = a1b1 << 8
    else:
        part4 = 0
    return part1 ^ part2 ^ part3 ^ part4	

    #gf(2^8)_mul
def ex8(a, b, c):
    re = a % 4
    if re == 0:
        result = 0
    elif re == 1:
        result = b
    elif re == 2:
        s = b * 2
        if s>=256:
            result = (s - 256) ^ c
        else:
            result = s
    elif re == 3:
        s1 = b
        s2 = b*2
        if s2>=256:
            result = (s2 - 256) ^ c ^ s1
        else:
            result = s2 ^ s1
    return result			
	
    #gcd
def gcd(a, b):
    while a!=0:
        a,b = b%a, a
    return b
	
    #modreverse
def findModReverse(a,m):
    if gcd(a,m)!=1:
        return None
    u1,u2,u3 = 1,0,a
    v1,v2,v3 = 0,1,m
    while v3!=0:
        q = u3//v3
        v1,v2,v3,u1,u2,u3 = (u1-q*v1),(u2-q*v2),(u3-q*v3),v1,v2,v3
    return u1%m

	# integer to bitarray
def bit8 (data):
    tempt = ((bin(data)[2:])[::-1])+'00000000'
    result = bitarray(tempt)
    return result

def bit16 (data):
    tempt = ((bin(data)[2:])[::-1])+'0000000000000000'
    result = bitarray(tempt)
    return result
	
def bit32(data):
    tempt = ((bin(data)[2:])[::-1])+'00000000000000000000000000000000'
    result = bitarray(tempt)
    return result

def bit64(data):
    tempt = ((bin(data)[2:])[::-1])+'0000000000000000000000000000000000000000000000000000000000000000'
    result = bitarray(tempt)
    return result
	
def bit128(data):
    tempt = ((bin(data)[2:])[::-1])+'00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    result = bitarray(tempt)
    return result

    # 32bits data to other bits data(8, 16, 32, 64, 128)
def bit32_to_8 (data):
    if ((bin(data)[2:])[::-1])[24:32]=='':
        data_H_16_H_8 = 0
    else:
        data_H_16_H_8 = int((((bin(data)[2:])[::-1])[24:32])[::-1], 2)
    if ((bin(data)[2:])[::-1])[16:24]=='':
        data_H_16_L_8 = 0
    else:
        data_H_16_L_8 = int((((bin(data)[2:])[::-1])[16:24])[::-1], 2)
    if ((bin(data)[2:])[::-1])[8:16]=='':
        data_L_16_H_8 = 0
    else:
        data_L_16_H_8 = int((((bin(data)[2:])[::-1])[8:16])[::-1], 2)
    if ((bin(data)[2:])[::-1])[0:8]=='':
        data_L_16_L_8 = 0
    else:
        data_L_16_L_8 = int((((bin(data)[2:])[::-1])[0:8])[::-1], 2)
    return data_H_16_H_8, data_H_16_L_8, data_L_16_H_8, data_L_16_L_8
		
def bit32_to_16 (data):
    if ((bin(data)[2:])[::-1])[16:32]=='':
        data_H_16 = 0
    else:
        data_H_16 = int((((bin(data)[2:])[::-1])[16:32])[::-1], 2)
    if ((bin(data)[2:])[::-1])[0:16]=='':
        data_L_16 = 0
    else:
        data_L_16 = int((((bin(data)[2:])[::-1])[0:16])[::-1], 2)
    return data_H_16, data_L_16
		
def bit32_to_64 (r1, r2):
    result = (r1<<32) + r2
    return result        

def bit32_to_128(r1, r2, r3, r4):
    result = (r1<<96) + (r2<<64) + (r3<<32) + r4
    return result
	
def bit64_to_32 (data):
    r1 = (data % (1<<64) - data % (1<<32))>>32
    r2 = data % (1<<32)
    return r1, r2
		
def bit128_to_32 (data):
    r1 = (data % (1<<128) - data % (1<<96))>>96
    r2 = (data % (1<<96) - data % (1<<64))>>64
    r3 = (data % (1<<64) - data % (1<<32))>>32
    r4 = data % (1<<32)
    return r1, r2, r3, r4
	
def bit256_to_32 (data):
    r1 = (data % (1<<256) - data % (1<<224))>>224
    r2 = (data % (1<<224) - data % (1<<192))>>192
    r3 = (data % (1<<192) - data % (1<<160))>>160
    r4 = (data % (1<<160) - data % (1<<128))>>128
    r5 = (data % (1<<128) - data % (1<<96))>>96
    r6 = (data % (1<<96) - data % (1<<64))>>64
    r7 = (data % (1<<64) - data % (1<<32))>>32
    r8 = data % (1<<32)
    return r1, r2, r3, r4, r5, r6, r7, r8


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
        self._InstrSet.SetExec(Instr = "BLANK",   Func = self._ExecBLANK  )
        self._InstrSet.SetExec(Instr = "COMMENT", Func = self._ExecCOMMENT)
        self._InstrSet.SetExec(Instr = "LABEL",   Func = self._ExecLABEL  )
        # Instruction Set of Common Function
        self._InstrSet.SetExec(Instr = "add",     Func = self._Execadd)
        # Instruction Set of Memory Operation and Register Operation
        self._InstrSet.SetExec(Instr="sd",        Func=self._Execsd)
        self._InstrSet.SetExec(Instr="ld",        Func=self._Execld)
        self._InstrSet.SetExec(Instr="li",        Func=self._Execli)
        self._InstrSet.SetExec(Instr="liv",        Func=self._Execliv)
        self._InstrSet.SetExec(Instr="lw",        Func=self._Execlw)
        self._InstrSet.SetExec(Instr="sw",        Func=self._Execsw)
        self._InstrSet.SetExec(Instr="mv",        Func=self._Execmv)
        # Instruction Set of Branch
        self._InstrSet.SetExec(Instr="bjlab",      Func=self._Execbjlab)
        self._InstrSet.SetExec(Instr="bjr",        Func=self._Execbjr)
        self._InstrSet.SetExec(Instr="bne",        Func=self._Execbne)
        self._InstrSet.SetExec(Instr="beq",        Func=self._Execbeq)
        self._InstrSet.SetExec(Instr="bgt",        Func=self._Execbgt)
        self._InstrSet.SetExec(Instr="bge",        Func=self._Execbge)
        self._InstrSet.SetExec(Instr="blt",        Func=self._Execblt)
        self._InstrSet.SetExec(Instr="ble",        Func=self._Execble)
		# Instruction Set of Boolean Function
        self._InstrSet.SetExec(Instr="qand",                  Func=self._Execqand)
        self._InstrSet.SetExec(Instr="qand64",                Func=self._Execqand64)
        self._InstrSet.SetExec(Instr="qand128",               Func=self._Execqand128)
        self._InstrSet.SetExec(Instr="qor",                   Func=self._Execqor)
        self._InstrSet.SetExec(Instr="qor64",                 Func=self._Execqor64)
        self._InstrSet.SetExec(Instr="qor128",                Func=self._Execqor128)
        self._InstrSet.SetExec(Instr="qxor",                  Func=self._Execqxor)
        self._InstrSet.SetExec(Instr="qxor64",                Func=self._Execqxor64)
        self._InstrSet.SetExec(Instr="qxor128",               Func=self._Execqxor128)
        self._InstrSet.SetExec(Instr="qnot",                  Func=self._Execqnot)
        self._InstrSet.SetExec(Instr="qnot64",                Func=self._Execqnot64)
        self._InstrSet.SetExec(Instr="qnot128",               Func=self._Execqnot128)
        self._InstrSet.SetExec(Instr="qtli",                  Func=self._Execqtli)
        self._InstrSet.SetExec(Instr="qtl",                   Func=self._Execqtl)
        self._InstrSet.SetExec(Instr="qsxor",                   Func=self._Execqsxor)
        self._InstrSet.SetExec(Instr="qsxor64",                   Func=self._Execqsxor64)
        self._InstrSet.SetExec(Instr="qsxor128",                   Func=self._Execqsxor128)
        self._InstrSet.SetExec(Instr="qcmp",                  Func=self._Execqcmp)
        self._InstrSet.SetExec(Instr="qcmp64",                Func=self._Execqcmp64)
        self._InstrSet.SetExec(Instr="qcmp128",               Func=self._Execqcmp128)
        self._InstrSet.SetExec(Instr="qtest",                 Func=self._Execqtest)
        self._InstrSet.SetExec(Instr="qtest64",               Func=self._Execqtest64)        
        self._InstrSet.SetExec(Instr="qtest128",              Func=self._Execqtest128)
        self._InstrSet.SetExec(Instr="qtesti",                Func=self._Execqtesti)
        self._InstrSet.SetExec(Instr="qtesti64",              Func=self._Execqtesti64)
        self._InstrSet.SetExec(Instr="qtesti128",             Func=self._Execqtesti128)
        self._InstrSet.SetExec(Instr="qteq",                  Func=self._Execqteq)
        self._InstrSet.SetExec(Instr="qteq64",                Func=self._Execqteq64)		
        self._InstrSet.SetExec(Instr="qteq128",               Func=self._Execqteq128)		
        self._InstrSet.SetExec(Instr="qteqi",                 Func=self._Execqteqi)		
        self._InstrSet.SetExec(Instr="qteqi64",               Func=self._Execqteqi64)		
        self._InstrSet.SetExec(Instr="qteqi128",              Func=self._Execqteqi128)		
        self._InstrSet.SetExec(Instr="qadd",                  Func=self._Execqadd)		
        self._InstrSet.SetExec(Instr="qadd64",                  Func=self._Execqadd64)		
        self._InstrSet.SetExec(Instr="qadd128",                  Func=self._Execqadd128)		
        self._InstrSet.SetExec(Instr="qsub",                  Func=self._Execqsub)
        self._InstrSet.SetExec(Instr="qsub64",                  Func=self._Execqsub64)
        self._InstrSet.SetExec(Instr="qsub128",                  Func=self._Execqsub128)
        self._InstrSet.SetExec(Instr="qmodadd8",                  Func=self._Execqmodadd8)
        self._InstrSet.SetExec(Instr="qmodadd16",                  Func=self._Execqmodadd16)
        self._InstrSet.SetExec(Instr="qmodadd32",                  Func=self._Execqmodadd32)
        self._InstrSet.SetExec(Instr="qmodadd64",                  Func=self._Execqmodadd64)
        self._InstrSet.SetExec(Instr="qmodadd128",                  Func=self._Execqmodadd128)
        self._InstrSet.SetExec(Instr="qmodsub8",                  Func=self._Execqmodsub8)
        self._InstrSet.SetExec(Instr="qmodsub16",                  Func=self._Execqmodsub16)
        self._InstrSet.SetExec(Instr="qmodsub32",                  Func=self._Execqmodsub32)
        self._InstrSet.SetExec(Instr="qmodsub64",                  Func=self._Execqmodsub64)
        self._InstrSet.SetExec(Instr="qmodsub128",                  Func=self._Execqmodsub128)
        self._InstrSet.SetExec(Instr="qmul8l",                  Func=self._Execqmul8l)
        self._InstrSet.SetExec(Instr="qmul8h",                  Func=self._Execqmul8h)
        self._InstrSet.SetExec(Instr="qmul16l",                  Func=self._Execqmul16l)
        self._InstrSet.SetExec(Instr="qmul16h",                  Func=self._Execqmul16h)
        self._InstrSet.SetExec(Instr="qmul32l",                  Func=self._Execqmul32l)
        self._InstrSet.SetExec(Instr="qmul32h",                  Func=self._Execqmul32h)
        self._InstrSet.SetExec(Instr="qmodmul8",                  Func=self._Execqmodmul8)
        self._InstrSet.SetExec(Instr="qmodmul16",                  Func=self._Execqmodmul16)
        self._InstrSet.SetExec(Instr="qmodmul32",                  Func=self._Execqmodmul32)
        self._InstrSet.SetExec(Instr="qishl32",                  Func=self._Execqishl32)
        self._InstrSet.SetExec(Instr="qishl8",                  Func=self._Execqishl8)
        self._InstrSet.SetExec(Instr="qshl32",                  Func=self._Execqshl32)
        self._InstrSet.SetExec(Instr="qshl8",                  Func=self._Execqshl8)
        self._InstrSet.SetExec(Instr="qishr32",                  Func=self._Execqishr32)
        self._InstrSet.SetExec(Instr="qishr8",                  Func=self._Execqishr8)
        self._InstrSet.SetExec(Instr="qshr32",                  Func=self._Execqshr32)
        self._InstrSet.SetExec(Instr="qshr8",                  Func=self._Execqshr8)
        self._InstrSet.SetExec(Instr="qirol32",                  Func=self._Execqirol32)
        self._InstrSet.SetExec(Instr="qirol8",                  Func=self._Execqirol8)
        self._InstrSet.SetExec(Instr="qrol32",                  Func=self._Execqrol32)
        self._InstrSet.SetExec(Instr="qrol8",                  Func=self._Execqrol8)
        self._InstrSet.SetExec(Instr="qiror32",                  Func=self._Execqiror32)
        self._InstrSet.SetExec(Instr="qiror8",                  Func=self._Execqiror8)
        self._InstrSet.SetExec(Instr="qror32",                  Func=self._Execqror32)
        self._InstrSet.SetExec(Instr="qror8",                  Func=self._Execqror8)
        self._InstrSet.SetExec(Instr = "qsbitperm32",          Func=self._Execqsbitperm32)
        self._InstrSet.SetExec(Instr="qsbitperm64",            Func=self._Execqsbitperm64)
        self._InstrSet.SetExec(Instr="qsbitperm128",           Func=self._Execqsbitperm128)
        self._InstrSet.SetExec(Instr="qsbitperm8",             Func=self._Execqsbitperm8)
        self._InstrSet.SetExec(Instr="qdbitperm32",            Func=self._Execqdbitperm32)
        self._InstrSet.SetExec(Instr="qbyteperm32",            Func=self._Execqbyteperm32)
        self._InstrSet.SetExec(Instr="qbyteperm64",            Func=self._Execqbyteperm64)
        self._InstrSet.SetExec(Instr="qbyteperm128",           Func=self._Execqbyteperm128)
        self._InstrSet.SetExec(Instr="qbitsw",                 Func=self._Execqbitsw)
        self._InstrSet.SetExec(Instr="qbytesw",                Func=self._Execqbytesw)
        self._InstrSet.SetExec(Instr="qlut8m8",                Func=self._Execqlut8m8)
        self._InstrSet.SetExec(Instr="q4lut8m8",                Func=self._Execq4lut8m8)
        self._InstrSet.SetExec(Instr="qlut4m4",                Func=self._Execqlut4m4)
        self._InstrSet.SetExec(Instr="qlut6m4",                Func=self._Execqlut6m4)
        self._InstrSet.SetExec(Instr="qlut8m4",                Func=self._Execqlut8m4)
        self._InstrSet.SetExec(Instr="qlut8m32",               Func=self._Execqlut8m32)
        self._InstrSet.SetExec(Instr="q4lut8m32",              Func=self._Execq4lut8m32)
        self._InstrSet.SetExec(Instr="qlutsw",                 Func=self._Execqlutsw)
        self._InstrSet.SetExec(Instr="qgf8_2mulx",             Func=self._Execqgf8_2mulx)
        self._InstrSet.SetExec(Instr="qgf8_3mulx",             Func=self._Execqgf8_3mulx)
        self._InstrSet.SetExec(Instr="qgf8_4mulx",             Func=self._Execqgf8_4mulx)
        self._InstrSet.SetExec(Instr="qgf8_mulv",              Func=self._Execqgf8_mulv)
        self._InstrSet.SetExec(Instr="qgf8_2mulv",             Func=self._Execqgf8_2mulv)
        self._InstrSet.SetExec(Instr="qgf8_3mulv",             Func=self._Execqgf8_3mulv)
        self._InstrSet.SetExec(Instr="qgf8_4mulv",             Func=self._Execqgf8_4mulv)
        self._InstrSet.SetExec(Instr="qmds4",                  Func=self._Execqmds4)
        self._InstrSet.SetExec(Instr="qmds8",                  Func=self._Execqmds8)
        self._InstrSet.SetExec(Instr="qmds16",                  Func=self._Execqmds16)
        self._InstrSet.SetExec(Instr="qgfmulx",                  Func=self._Execqgfmulx)
        self._InstrSet.SetExec(Instr="qgfmul8x",                  Func=self._Execqgfmul8x)
        self._InstrSet.SetExec(Instr="qgfmulb",                  Func=self._Execqgfmulb)
        self._InstrSet.SetExec(Instr="qgfmulc",                  Func=self._Execqgfmulc)
        self._InstrSet.SetExec(Instr="qgf8_matc",                  Func=self._Execqgfmulc)
        self._InstrSet.SetExec(Instr="qgf8_mat",                  Func=self._Execqgf8_mat)
        self._InstrSet.SetExec(Instr="qgf8_matcv",                  Func=self._Execqgf8_matcv)
        self._InstrSet.SetExec(Instr="qgf8_matv",                  Func=self._Execqgf8_matv)
        self._InstrSet.SetExec(Instr="qbfmul32l",                  Func=self._Execqbfmul32l)
        self._InstrSet.SetExec(Instr="qbfmul32h",                  Func=self._Execqbfmul32h)
        self._InstrSet.SetExec(Instr="qgfinv",                  Func=self._Execqgfinv)
        self._InstrSet.SetExec(Instr="qslfsr128", Func=self._Execqslfsr128)
        self._InstrSet.SetExec(Instr="qslfsr256", Func=self._Execqslfsr256)
        self._InstrSet.SetExec(Instr="qslfsr512", Func=self._Execqslfsr512)
        self._InstrSet.SetExec(Instr="qdlfsr128", Func=self._Execqdlfsr128)
        self._InstrSet.SetExec(Instr="qdlfsr256", Func=self._Execqdlfsr256)
        self._InstrSet.SetExec(Instr="qdlfsr512", Func=self._Execqdlfsr512)
        self._InstrSet.SetExec(Instr="qnlfsr128", Func=self._Execqnlfsr128)
        self._InstrSet.SetExec(Instr="qnlfsr256", Func=self._Execqnlfsr256)
        self._InstrSet.SetExec(Instr="qnlfsr512", Func=self._Execqnlfsr512)
        self._InstrSet.SetExec(Instr="qsfcsr128", Func=self._Execqsfcsr128)
        self._InstrSet.SetExec(Instr="qsfcsr256", Func=self._Execqsfcsr256)
        self._InstrSet.SetExec(Instr="qsfcsr512", Func=self._Execqsfcsr512)

		
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
        while self._RF["PC"] != None and (PC != 160):
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

    def _Execadd(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r0 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        self._Log.write("Source Reg 0 : %s = %x  \nImm: %x  \n" % (r0, self._RF[r0], imm))
        self._RF[ret] = self._RF[r0] + imm
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
		
    def _Execliv(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret = Match.group(1)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret)
        front = split3.group(1) 
        if re.match('-?0x', Match.group(2)):
            imm = int(Match.group(2), 16)
        else:
            imm = int(Match.group(2))
        self._Log.write("Imm = %x  \n" % (imm))
        self._RF[front + '3'],  self._RF[front + '2'], self._RF[front + '1'], self._RF[front + '0'] = bit128_to_32(imm & 0xffffffffffffffffffffffffffffffff)
        self._RF[front + '7'],  self._RF[front + '6'], self._RF[front + '5'], self._RF[front + '4'] = bit128_to_32(imm>>128)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, imm))
        return True, PC + 1

    def _Execld(self, Asm="", PC=None):
        # Instruction behaviour
        Match = self._InstrSet.Match(Asm)
        Mem = Match.group(2)
        Reg = Match.group(1)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', Reg)
        code1 = int(split1.group(2), 10) 
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(2), 16)
        else:
            imm = int(Match.group(3))
        MemSplit = (re.match(r'(-?\w+)(\((\w+)\))?', Mem))
        Offset = int(MemSplit.group(1))
        Pt = (MemSplit.group(3))
        Addr = self._RF[Pt] + Offset
        self._Log.write("LOAD  From Memory Address: %x From Reg %s, Value is %x \n" % (Addr, Reg, self._DataMem[Addr]))
        for i in range(imm):
            self._RF[split1.group(1) + str(code1 - i)] = self._DataMem[Addr + i]
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

    def _Execsd(self, Asm="", PC=None):
        # Instruction behaviour
        Match = self._InstrSet.Match(Asm)
        Mem = Match.group(2)
        Reg = Match.group(1)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', Reg)
        code1 = int(split1.group(2), 10) 
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(2), 16)
        else:
            imm = int(Match.group(3))
        MemSplit = (re.match(r'(-?\w+)(\((\w+)\))?', Mem))
        Offset = int(MemSplit.group(1))
        Pt = (MemSplit.group(3))
        Addr = self._RF[Pt] + Offset
        self._Log.write("LOAD  From Memory Address: %x From Reg %s, Value is %x \n" % (Addr, Reg, self._DataMem[Addr]))
        for i in range(imm):
            self._DataMem[Addr + i] = self._RF[split1.group(1) + str(code1 - i)]
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
        MemSplit = (re.match(r'(0+)(\((\w+)\))?', Mem))
        Offset = 0
        Pt = (MemSplit.group(3))
        Addr = self._RF[Pt]
        self._Log.write("LOAD  From Memory Address: %x From Reg %s, Value is %x \n" % (Addr, Reg, self._DataMem[Addr]))
        self._RF[Reg] = self._DataMem[Addr]
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        return True, PC + 1

    def _Execsw(self, Asm="", PC=None):
        # Instruction behaviour
        Match = self._InstrSet.Match(Asm)
        Mem = Match.group(2)
        Reg = Match.group(1)
        MemSplit = (re.match(r'(\d+)(\((\w+)\))?', Mem))
        Offset = int(MemSplit.group(1))
        Pt = (MemSplit.group(3))
        Addr = self._RF[Pt]
        self._Log.write("LOAD  From Memory Address: %x From Reg %s, Value is %x \n" % (Addr, Reg, self._DataMem[Addr]))
        self._DataMem[Addr] = self._RF[Reg]
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        return True, PC + 1
		
    def _Execbjlab  (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        label = Match.group(1), Match.group(2)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        return True, self._AsmCode.LabelToPC(label)

    def _Execbjr   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r0 = Match.group(1)
        if self._RF.IsLocked(r0):
            return False, PC
        else:
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            new_PC = self._RF[r0]
            return True, new_PC

    def _Execbne   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r0, r1, label = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r0) or self._RF.IsLocked(r1):
            return False, PC
        else:
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            if self._RF[r0] != self._RF[r1]:
                return True, self._AsmCode.LabelToPC(label)
            else:
                return True, PC+1
				
    def _Execbeq   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r0, r1, label = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r0) or self._RF.IsLocked(r1):
            return False, PC
        else:
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            if self._RF[r0] == self._RF[r1]:
                return True, self._AsmCode.LabelToPC(label)
            else:
                return True, PC+1
				
    def _Execbgt   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r0, r1, label = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r0) or self._RF.IsLocked(r1):
            return False, PC
        else:
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            if self._RF[r0] > self._RF[r1]:
                return True, self._AsmCode.LabelToPC(label)
            else:
                return True, PC+1

    def _Execbge   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r0, r1, label = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r0) or self._RF.IsLocked(r1):
            return False, PC
        else:
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            if self._RF[r0] >= self._RF[r1]:
                return True, self._AsmCode.LabelToPC(label)
            else:
                return True, PC+1

    def _Execblt   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r0, r1, label = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r0) or self._RF.IsLocked(r1):
            return False, PC
        else:
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            if self._RF[r0] < self._RF[r1]:
                return True, self._AsmCode.LabelToPC(label)
            else:
                return True, PC+1

    def _Execble   (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        r0, r1, label = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(r0) or self._RF.IsLocked(r1):
            return False, PC
        else:
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            if self._RF[r0] <= self._RF[r1]:
                return True, self._AsmCode.LabelToPC(label)
            else:
                return True, PC+1

    def _Execqand    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            self._RF[ret1] = s1 & s2
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqand64    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1) or (code3<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            s2 = (self._RF[r2]<<32) + self._RF[split2.group(1) + str(code2 - 1)]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = s1 & s2
            self._RF[ret1], self._RF[split3.group(1) + str(code3 - 1)] = bit64_to_32(s1 & s2)
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result 1: %s = %x \n"%(ret1, result))
            return True, PC+1
			
    def _Execqand128    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2)  or (code1<3) or (code2<3) or (code3<3):
            return False, PC
        else:
            s1 =( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + 
             (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            s2 =( (self._RF[r2]<<96) + (self._RF[split2.group(1) + str(code2 - 1)]<<64) + 
             (self._RF[split2.group(1) + str(code2 - 2)]<<32) + self._RF[split2.group(1) + str(code2 - 3)] )
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = s1 & s2
            self._RF[ret1], self._RF[split3.group(1)+str(code3-1)], self._RF[split3.group(1)+str(code3-2)], self._RF[split3.group(1)+str(code3-3)] = bit128_to_32(s1 & s2)
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result 1: %s = %x \n"%(ret1, result))
            return True, PC+1
			
    def _Execqor    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            self._RF[ret1] = s1 | s2
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqor64    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1) or (code3<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            s2 = (self._RF[r2]<<32) + self._RF[split2.group(1) + str(code2 - 1)]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = s1 | s2
            self._RF[ret1], self._RF[split3.group(1) + str(code3 - 1)] = bit64_to_32(s1 | s2)
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result 1: %s = %x \n"%(ret1, result))
            return True, PC+1
			
    def _Execqor128    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2)  or (code1<3) or (code2<3) or (code3<3):
            return False, PC
        else:
            s1 = ( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + 
             (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            s2 = ( (self._RF[r2]<<96) + (self._RF[split2.group(1) + str(code2 - 1)]<<64) + 
             (self._RF[split2.group(1) + str(code2 - 2)]<<32) + self._RF[split2.group(1) + str(code2 - 3)] )
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = s1 | s2
            self._RF[ret1], self._RF[split3.group(1)+str(code3-1)], self._RF[split3.group(1)+str(code3-2)], self._RF[split3.group(1)+str(code3-3)] = bit128_to_32(s1 | s2)
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result 1: %s = %x \n"%(ret1, result))
            return True, PC+1
			
    def _Execqxor    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            self._RF[ret1] = s1 ^ s2
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqxor64    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1) or (code3<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            s2 = (self._RF[r2]<<32) + self._RF[split2.group(1) + str(code2 - 1)]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = s1 ^ s2
            self._RF[ret1], self._RF[split3.group(1) + str(code3 - 1)] = bit64_to_32(s1 ^ s2)
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result 1: %s = %x \n"%(ret1, result))
            return True, PC+1
			
    def _Execqxor128    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2)  or (code1<3) or (code2<3) or (code3<3):
            return False, PC
        else:
            s1 = ( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + 
             (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            s2 = ( (self._RF[r2]<<96) + (self._RF[split2.group(1) + str(code2 - 1)]<<64) + 
             (self._RF[split2.group(1) + str(code2 - 2)]<<32) + self._RF[split2.group(1) + str(code2 - 3)] )
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            result = s1 ^ s2
            self._RF[ret1], self._RF[split3.group(1)+str(code3-1)], self._RF[split3.group(1)+str(code3-2)], self._RF[split3.group(1)+str(code3-3)] = bit128_to_32(s1 ^ s2)
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result 1: %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqnot    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1):
            return False, PC
        else:
            s1 = self._RF[r1]
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, s1))
            self._RF[ret1] = int("0xffffffff", 16) - s1
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqnot64    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or (code1<1) or (code3<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, s1))
            result = int("0xffffffffffffffff", 16) - s1
            self._RF[ret1], self._RF[split3.group(1) + str(code3 - 1)] = bit64_to_32(int("0xffffffffffffffff", 16) - s1)
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, result))
            return True, PC+1
	
    def _Execqnot128    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or (code1<3) or (code3<3):
            return False, PC
        else:
            s1 = ( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + 
             (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, s1))
            result = int("0xffffffffffffffffffffffffffffffff", 16) - s1
            self._RF[ret1], self._RF[split3.group(1)+str(code3-1)], self._RF[split3.group(1)+str(code3-2)], self._RF[split3.group(1)+str(code3-3)] = bit128_to_32(int("0xffffffffffffffffffffffffffffffff", 16) - s1)
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm) 
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, result))
            return True, PC+1

    def _Execqtli    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        code1 = int(split1.group(2), 10) 
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or (imm>255) or (code1<2):
            return False, PC
        else:
            log = bit8(imm)
            A = self._RF[split1.group(1) + str(code1 - 2)]
            B = self._RF[split1.group(1) + str(code1 - 1)]
            C = self._RF[r1]
            A_inv = int("0xffffffff", 16) - A
            B_inv = int("0xffffffff", 16) - B
            C_inv = int("0xffffffff", 16) - C
            self._RF[ret1] = ( (log[7] * (A & B & C)) | (log[6] * (A & B & C_inv)) |
		    (log[5] * (A & B_inv & C)) | (log[4] * (A & B_inv & C_inv)) | 
		    (log[3] * (A_inv & B & C)) | (log[2] * (A_inv & B & C_inv)) |
		    (log[1] * (A_inv & B_inv & C)) | (log[0] * (A_inv & B_inv & C_inv)) )
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1

    def _Execqtl    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        code1 = int(split1.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or (code1<3):
            return False, PC
        else:
            log = bit32(self._RF[split1.group(1) + str(code1 - 3)])
            A = self._RF[split1.group(1) + str(code1 - 2)]
            B = self._RF[split1.group(1) + str(code1 - 1)]
            C = self._RF[r1]
            A_inv = int("0xffffffff", 16) - A
            B_inv = int("0xffffffff", 16) - B
            C_inv = int("0xffffffff", 16) - C
            self._RF[ret1] = ( (log[7] * (A & B & C)) | (log[6] * (A & B & C_inv)) |
		    (log[5] * (A & B_inv & C)) | (log[4] * (A & B_inv & C_inv)) | 
		    (log[3] * (A_inv & B & C)) | (log[2] * (A_inv & B & C_inv)) |
		    (log[1] * (A_inv & B_inv & C)) | (log[0] * (A_inv & B_inv & C_inv)) )
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1			

    def _Execqsxor    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        s = Match.group(1)
        split = (re.match(r'(\w+)(\.(\w+))?', s))
        j = int(split.group(3), 10)
        rd = split.group(1)
        ret1, r1, r2 = rd, Match.group(2), Match.group(3)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            tempt = 0
            log2 = bit32(s2)
            log1 = bit32(s1)
            for i in range(32) :
                if log2[i]:
                    tempt = tempt ^ log1[i]
            self._RF[ret1] = tempt * pow(2, j)
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqsxor64    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        s = Match.group(1)
        split = (re.match(r'(\w+)(\.(\w+))?', s))
        j = int(split.group(3), 10)
        rd = split.group(1)
        ret1, r1, r2 = rd, Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1) or (code3<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            s2 = (self._RF[r2]<<32) + self._RF[split2.group(1) + str(code2 - 1)]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))	
            tempt = 0
            log2 = bit64(s2)
            log1 = bit64(s1)
            for i in range(64) :
                if log2[i]:
                    tempt = tempt ^ log1[i]
            result = tempt * pow(2, j)
            self._RF[ret1], self._RF[split3.group(1)+str(code3-1)] = bit64_to_32(tempt * pow(2, j))
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, result))
            return True, PC+1
			
    def _Execqsxor128    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        s = Match.group(1)
        split = (re.match(r'(\w+)(\.(\w+))?', s))
        j = int(split.group(3), 10)
        rd = split.group(1)
        ret1, r1, r2 = rd, Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2)  or (code1<3) or (code2<3) or (code3<3):
            return False, PC
        else:
            s1 = ( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + 
             (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            s2 = ( (self._RF[r2]<<96) + (self._RF[split2.group(1) + str(code2 - 1)]<<64) + 
             (self._RF[split2.group(1) + str(code2 - 2)]<<32) + self._RF[split2.group(1) + str(code2 - 3)] )
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            tempt = 0
            log2 = bit128(s2)
            log1 = bit128(s1)
            for i in range(128) :
                if log2[i]:
                    tempt = tempt ^ log1[i]
            result = tempt * pow(2, j)
            self._RF[ret1], self._RF[split3.group(1)+str(code3-1)], self._RF[split3.group(1)+str(code3-2)], self._RF[split3.group(1)+str(code3-3)] = bit128_to_32(tempt * pow(2, j))
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, result))
            return True, PC+1
			
    def _Execqcmp    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            if s1 < s2:
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqcmp64    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            s2 = (self._RF[r2]<<32) + self._RF[split2.group(1) + str(code2 - 1)]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            if s1 < s2:
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqcmp128    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2)  or (code1<3) or (code2<3):
            return False, PC
        else:
            s1 = ( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + 
             (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            s2 = ( (self._RF[r2]<<96) + (self._RF[split2.group(1) + str(code2 - 1)]<<64) + 
             (self._RF[split2.group(1) + str(code2 - 2)]<<32) + self._RF[split2.group(1) + str(code2 - 3)] )
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            if s1 < s2:
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqtest    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \n"%(r1, s1, r2, s2))
            if (s1 & s2):
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqtest64    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1) or (code3<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            s2 = (self._RF[r2]<<32) + self._RF[split2.group(1) + str(code2 - 1)]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))		
            if (s1 & s2):
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqtest128    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2)  or (code1<3) or (code2<3) or (code3<3):
            return False, PC
        else:
            s1 = ( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + 
             (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            s2 = ( (self._RF[r2]<<96) + (self._RF[split2.group(1) + str(code2 - 1)]<<64) + 
             (self._RF[split2.group(1) + str(code2 - 2)]<<32) + self._RF[split2.group(1) + str(code2 - 3)] )
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            if (s1 & s2):
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqtesti    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or imm>31:
            return False, PC
        else:
            s1 = self._RF[r1]
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, s1))
            if (s1 & (1<<imm)):
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqtesti64    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or imm>63 or (code1<1) or (code3<1):
            return False, PC
        else:
            s1 = ((self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)])
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, s1))
            if (s1 & (1<<imm)):
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqtesti128    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        code1 = int(split1.group(2), 10) 
        rs1 = split1.group(1) + str(code1)		
        rs2 = split1.group(1) + str(code1 - 1)	
        rs3 = split1.group(1) + str(code1 - 2)
        rs4 = split1.group(1) + str(code1 - 3)	
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or imm>127 or (code1<3):
            return False, PC
        else:
            s1 = ((self._RF[rs1]<<96) + (self._RF[rs2]<<64) + (self._RF[rs3]<<32) + self._RF[rs4])
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, s1))
            if (s1 & (1<<imm)):
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqteqi    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1):
            return False, PC
        else:
            s1 = self._RF[r1]
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, s1))
            if ((s1==0) & (imm==0)) or (s1==int("0xffffffff",16) & (imm==1)):
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqteqi64    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        code1 = int(split1.group(2), 10) 
        rs1 = split1.group(1) + str(code1)		
        rs2 = split1.group(1) + str(code1 - 1)		
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or (code1<1):
            return False, PC
        else:
            s1 = ((self._RF[rs1]<<32) + self._RF[rs2])
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, s1))
            if ((s1==0) & (imm==0)) or (s1==int("0xffffffffffffffff",16) & (imm==1)):
                result = self._RF[ret1] = 1
            else :
                result = self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, result))
            return True, PC+1
			
    def _Execqteqi128    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        code1 = int(split1.group(2), 10) 
        rs1 = split1.group(1) + str(code1)		
        rs2 = split1.group(1) + str(code1 - 1)		
        rs3 = split1.group(1) + str(code1 - 2)		
        rs4 = split1.group(1) + str(code1 - 3)	
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or (code1<3):
            return False, PC
        else:
            s1 = ((self._RF[rs1]<<96) + (self._RF[rs2]<<64) + (self._RF[rs3]<<32) + self._RF[rs4])
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, s1))
            if ((s1==0) & (imm==0)) or (s1==int("0xffffffffffffffffffffffffffffffff",16) & (imm==1)):
                result = self._RF[ret1] = 1
            else :
                result = self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, result))
            return True, PC+1

    def _Execqteq    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2, r3 = Match.group(1), Match.group(2), Match.group(3), Match.group(4)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or self._RF.IsLocked(r3):
            return False, PC
        else:
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            s3 = self._RF[r3]
            self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2, r3, s3))
            if ( (s1&(1<<s3)) == (s2&(1<<s3)) ):
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqteq64    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2, r3 = Match.group(1), Match.group(2), Match.group(3), Match.group(4)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            s2 = (self._RF[r2]<<32) + self._RF[split2.group(1) + str(code2 - 1)]
            s3 = self._RF[r3]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            if ( (s1&(1<<s3)) == (s2&(1<<s3)) ):
                self._RF[ret1] = 1
            else :
                self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqteq128    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2, r3 = Match.group(1), Match.group(2), Match.group(3), Match.group(4)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2)  or (code1<3) or (code2<3):
            return False, PC
        else:
            s1 = ( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + 
             (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            s2 = ( (self._RF[r2]<<96) + (self._RF[split2.group(1) + str(code2 - 1)]<<64) + 
             (self._RF[split2.group(1) + str(code2 - 2)]<<32) + self._RF[split2.group(1) + str(code2 - 3)] )
            s3 = self._RF[r3]
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \nReg 3 : %s = %x  \n"%(r1, s1, r2, s2, r3, s3))
            if ((s1&(1<<s3)) == (s2&(1<<s3)) ):
                result = self._RF[ret1] = 1
            else :
                result = self._RF[ret1] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, result))
            return True, PC+1
			
    def _Execqadd(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
        tempt = s1 + s2
        if tempt>=(1<<32):
            result = self._RF[ret] = tempt - (1<<32)
            self._RF['CY'] = 1
        else:
            result = self._RF[ret] = tempt
            self._RF['CY'] = 0
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, tempt))
        return True, PC + 1
		
    def _Execqadd64(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            s2 = (self._RF[r2]<<32) + self._RF[split2.group(1) + str(code2 - 1)]
            tempt = s1 + s2
            if tempt>=(1<<64):
                self._RF[ret], self,_RF[split3.group(1) + str(code3 - 1)] = bit64_to_32(tempt - (1<<64))
                self._RF['CY'] = 1
            else:
                self._RF[ret], self,_RF[split3.group(1) + str(code3 - 1)] = bit64_to_32(tempt)
                self._RF['CY'] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n" % (ret, tempt))
            return True, PC + 1
		
    def _Execqadd128(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if (code1<3) or (code2<3) or (code3<3):
            return False, PC
        else:
            s1 = ( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            s2 = ( (self._RF[r2]<<96) + (self._RF[split2.group(1) + str(code2 - 1)]<<64) + (self._RF[split2.group(1) + str(code2 - 2)]<<32) + self._RF[split2.group(1) + str(code2 - 3)] )
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            tempt = s1 + s2
            if tempt>=(1<<128):
                self._RF[ret], self._RF[split3.group(1) + str(code3-1)],  self._RF[split3.group(1) + str(code3-2)], self._RF[split3.group(1) + str(code3-3)] = bit128_to_32(tempt - (1<<128))
                self._RF['CY'] = 1
            else:
                self._RF[ret], self._RF[split3.group(1) + str(code3-1)],  self._RF[split3.group(1) + str(code3-2)], self._RF[split3.group(1) + str(code3-3)] = bit128_to_32(tempt)
                self._RF['CY'] = 0
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n" % (ret, tempt))
            return True, PC + 1
		
    def _Execqsub(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
        if s1>=s2:
            result = self._RF[ret] = s1 - s2
            self._RF['CY'] = 0
        else:
            result = self._RF[ret] = s1 + (1<<32) - s2
            self._RF['CY'] = 1
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, result))
        return True, PC + 1
		
    def _Execqsub64(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            s2 = (self._RF[r2]<<32) + self._RF[split2.group(1) + str(code2 - 1)]
            tempt = s1 - s2
            if s1>=s2:
                self._RF[ret], self,_RF[split3.group(1) + str(code3 - 1)] = s1 - s2
                self._RF['CY'] = 0
            else:
                self._RF[ret], self,_RF[split3.group(1) + str(code3 - 1)] = s1 + (1<<64) - s2
                self._RF['CY'] = 1
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n" % (ret, tempt))
            return True, PC + 1
		
    def _Execqsub128(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2)  or (code1<3) or (code2<3) or (code3<3):
            return False, PC
        else:
            s1 = ( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + 
             (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            s2 = ( (self._RF[r2]<<96) + (self._RF[split2.group(1) + str(code2 - 1)]<<64) + 
             (self._RF[split2.group(1) + str(code2 - 2)]<<32) + self._RF[split2.group(1) + str(code2 - 3)] )
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, s1, r2, s2))
            tempt = s1 - s2
            if s1>=s2:
                self._RF[ret], self._RF[split3 + str(code3-1)],  self._RF[split3 + str(code3-2)], self._RF[split3 + str(code3-3)] = s1 - s2
                self._RF['CY'] = 0
            else:
                self._RF[ret], self._RF[split3 + str(code3-1)],  self._RF[split3 + str(code3-2)], self._RF[split3 + str(code3-3)] = s1 + (1<<128) - s2
                self._RF['CY'] = 1
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n" % (ret, tempt))
            return True, PC + 1
	
    def _Execqmodadd8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        s1, s2, s3, s4 = bit32_to_8(self._RF[r1])
        s5, s6, s7, s8 = bit32_to_8(self._RF[r2])
        self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \nReg 2 : %s = %x  \nReg 3 : %s = %x  \n"%(r1, s4, r2, s8, r3, self._RF[r3], r4, self._RF[r4]))		
        self._RF[ret] = pow(s4+s8, 1, (1<<self._RF[r3])+self._RF[r4])
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
	
    def _Execqmodadd16(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        s1, s2 = bit32_to_16(self._RF[r1])
        s3, s4 = bit32_to_16(self._RF[r2])
        self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \nReg 2 : %s = %x  \nReg 3 : %s = %x  \n"%(r1, s2, r2, s4, r3, self._RF[r3], r4, self._RF[r4]))		
        self._RF[ret] = pow(s2+s4, 1, (1<<self._RF[r3])+self._RF[r4])
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmodadd32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \nReg 2 : %s = %x  \nReg 3 : %s = %x  \n"%(r1, s1, r2, s2, r3, self._RF[r3], r4, self._RF[r4]))
        self._RF[ret] = pow(s1+s2, 1, (1<<self._RF[r3])+self._RF[r4])
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmodadd64(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1) or (code3<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            s2 = (self._RF[r2]<<32) + self._RF[split2.group(1) + str(code2 - 1)]
            self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \nReg 2 : %s = %x  \nReg 3 : %s = %x  \n"%(r1, s1, r2, s2, r3, self._RF[r3], r4, self._RF[r4]))
            self._RF[ret], self._RF[split3 + str(code3-1)] = bit64_to_32(pow(s1+s2, 1, (1<<self._RF[r3])+self._RF[r4]))
            result = pow(s1+s2, 1, (1<<self._RF[r3])+self._RF[r4])
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n" % (ret, result))
            return True, PC + 1
		
    def _Execqmodadd128(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2)  or (code1<3) or (code2<3) or (code3<3):
            return False, PC
        else:
            s1 = ( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + 
             (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            s2 = ( (self._RF[r2]<<96) + (self._RF[split2.group(1) + str(code2 - 1)]<<64) + 
             (self._RF[split2.group(1) + str(code2 - 2)]<<32) + self._RF[split2.group(1) + str(code2 - 3)] )
            self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \nReg 2 : %s = %x  \nReg 3 : %s = %x  \n"%(r1, s1, r2, s2, r3, self._RF[r3], r4, self._RF[r4]))
            self._RF[ret], self._RF[split3 + str(code3-1)],  self._RF[split3 + str(code3-2)], self._RF[split3 + str(code3-3)] = bit128_to_32(pow(s1+s2, 1, (1<<self._RF[r3])+self._RF[r4]))
            result = pow(s1+s2, 1, (1<<self._RF[r3])+self._RF[r4])
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n" % (ret, result))
            return True, PC + 1
		
    def _Execqmodsub8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        s1, s2, s3, s4 = bit32_to_8(self._RF[r1])
        s5, s6, s7, s8 = bit32_to_8(self._RF[r2])
        self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \nReg 2 : %s = %x  \nReg 3 : %s = %x  \n"%(r1, s4, r2, s8, r3, self._RF[r3], r4, self._RF[r4]))
        self._RF[ret] = pow(s4-s8, 1, (1<<self._RF[r3])+self._RF[r4])
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmodsub16(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        s1, s2 = bit32_to_16(self._RF[r1])
        s3, s4 = bit32_to_16(self._RF[r2])
        self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \nReg 2 : %s = %x  \nReg 3 : %s = %x  \n"%(r1, s2, r2, s4, r3, self._RF[r3], r4, self._RF[r4]))
        self._RF[ret] = pow(s2-s4, 1, (1<<self._RF[r3])+self._RF[r4])
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmodsub32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \nReg 2 : %s = %x  \nReg 3 : %s = %x  \n"%(r1, s1, r2, s2, r3, self._RF[r3], r4, self._RF[r4]))
        self._RF[ret] = pow(s1-s2, 1, (1<<self._RF[r3])+self._RF[r4])
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmodsub64(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1) or (code3<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            s2 = (self._RF[r2]<<32) + self._RF[split2.group(1) + str(code2 - 1)]
            self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \nReg 2 : %s = %x  \nReg 3 : %s = %x  \n"%(r1, s1, r2, s2, r3, self._RF[r3], r4, self._RF[r4]))
            self._RF[ret], self._RF[split3 + str(code3-1)] = bit64_to_32(pow(s1-s2, 1, (1<<self._RF[r3])+self._RF[r4]))
            result = pow(s1-s2, 1, (1<<self._RF[r3])+self._RF[r4])
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n" % (ret, result))
            return True, PC + 1
		
    def _Execqmodsub128(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split2 = re.match(r'(\w+)(\w+)(\w+)?', r2)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code2 = int(split2.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2)  or (code1<3) or (code2<3) or (code3<3):
            return False, PC
        else:
            s1 = ( (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + 
             (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)] )
            s2 = ( (self._RF[r2]<<96) + (self._RF[split2.group(1) + str(code2 - 1)]<<64) + 
             (self._RF[split2.group(1) + str(code2 - 2)]<<32) + self._RF[split2.group(1) + str(code2 - 3)] )
            self._Log.write("Source Reg 0 : %s = %x  \nSource Reg 1 : %s = %x  \nReg 2 : %s = %x  \nReg 3 : %s = %x  \n"%(r1, s1, r2, s2, r3, self._RF[r3], r4, self._RF[r4]))
            self._RF[ret], self._RF[split3 + str(code3-1)],  self._RF[split3 + str(code3-2)], self._RF[split3 + str(code3-3)] = bit128_to_32(pow(s1-s2, 1, (1<<self._RF[r3])+self._RF[r4]))
            result = pow(s1-s2, 1, (1<<self._RF[r3])+self._RF[r4])
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n" % (ret, result))
            return True, PC + 1
		
    def _Execqmul8l(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1, s2, s3, s4 = bit32_to_8(self._RF[r1])
        s5, s6, s7, s8 = bit32_to_8(self._RF[r2])
        self._RF[ret] = (s3 * s7) * pow(2, 16) + (s4 * s8)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmul8h(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1, s2, s3, s4 = bit32_to_8(self._RF[r1])
        s5, s6, s7, s8 = bit32_to_8(self._RF[r2])
        self._RF[ret] = (s1 * s5) * pow(2, 16) + (s2 * s6)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmul16l(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2: %s = %x  \n" % (r1, self._RF[r1], r2, self._RF[r2]))
        s1, s2 = bit32_to_16(self._RF[r1])
        s3, s4 = bit32_to_16(self._RF[r2])
        self._RF[ret] = s2 * s4
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmul16h(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1, s2 = bit32_to_16(self._RF[r1])
        s3, s4 = bit32_to_16(self._RF[r2])
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2: %s = %x  \n" % (r1, s1, r2, s3))
        self._RF[ret] = s1 * s3
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqgfinv(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        s1 = self._RF[r1]
        self._Log.write("Source Reg 1 : %s = %x  \n" % (r1, s1))
        tempt = s1 % self._RF["range"]
        self._RF[ret] = findModReverse(tempt, self._RF['inv'])
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmul32l(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2: %s = %x  \n" % (r1, s1, r2, s2))
        tempt = s1 * s2
        s3, s4 = bit64_to_32(tempt)
        self._RF[ret] = s4
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmul32h(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2: %s = %x  \n" % (r1, s1, r2, s2))
        tempt = s1 * s2
        s3, s4 = bit64_to_32(tempt)
        self._RF[ret] = s3
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmodmul8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        s1, s2, s3, s4 = bit32_to_8(self._RF[r1])
        s5, s6, s7, s8 = bit32_to_8(self._RF[r2])
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2: %s = %x  \nReg 3 : %s = %x  \nReg 4: %s = %x  \n" % (r1, s4, r2, s8, r3, self._RF[r3], r4, self._RF[r4]))
        tempt = s4 * s8
        n = (1<<self._RF[r3]) + self._RF[r4]
        self._RF[ret] = pow(tempt, 1, n)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmodmul16(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        s1, s2 = bit32_to_16(self._RF[r1])
        s3, s4 = bit32_to_16(self._RF[r2])
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2: %s = %x  \nReg 3 : %s = %x  \nReg 4: %s = %x  \n" % (r1, s2, r2, s4, r3, self._RF[r3], r4, self._RF[r4]))
        tempt = s2 * s4
        n = (1<<self._RF[r3]) + self._RF[r4]
        self._RF[ret] = pow(tempt, 1, n)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmodmul32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2, r3, r4 = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2: %s = %x  \nReg 3 : %s = %x  \nReg 4: %s = %x  \n" % (r1, s1, r2, s2, r3, self._RF[r3], r4, self._RF[r4]))
        tempt = s1 * s2
        n = (1<<self._RF[r3]) + self._RF[r4]
        self._RF[ret] = pow(tempt, 1, n)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqishl32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        s1 = self._RF[r1]
        self._Log.write("Source Reg 1 : %s = %x  \nImm: %x  \n" % (r1, s1, imm))
        self._RF[ret] = int(((((bin(s1<<imm)[2:])[::-1])[0:32])[::-1]), 2)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqishl8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        s1 = self._RF[r1]
        self._Log.write("Source Reg 1 : %s = %x  \nimm : %x  \n" % (r1, s1, imm))
        if ((bin(s1)[2:])[::-1])[24:32]=='':
            r1_H_16_H_8 = 0
        else:
            r1_H_16_H_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[24:32])[::-1], 2)<<imm))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[16:24]=='':
            r1_H_16_L_8 = 0
        else:
            r1_H_16_L_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[16:24])[::-1], 2)<<imm))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[8:16]=='':
            r1_L_16_H_8 = 0
        else:
            r1_L_16_H_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[8:16])[::-1], 2)<<imm))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[0:8]=='':
            r1_L_16_L_8 = 0
        else:
            r1_L_16_L_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[0:8])[::-1], 2)<<imm))[2:])[::-1])[0:8])[::-1], 2)
        self._RF[ret] = (r1_H_16_H_8<<24) + (r1_H_16_L_8<<16) + (r1_L_16_H_8<<8) + (r1_L_16_L_8)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqshl32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2 : %s = %x  \n" % (r1, s1, r2, s2))
        shift = int((((bin(s2)[2:])[::-1])[0:5])[::-1], 2)
        self._RF[ret] = int(((((bin(s1<<shift)[2:])[::-1])[0:32])[::-1]), 2)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqshl8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2 : %s = %x  \n" % (r1, s1, r2, s2))
        shift = int((((bin(s2)[2:])[::-1])[0:3])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[24:32]=='':
            r1_H_16_H_8 = 0
        else:
            r1_H_16_H_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[24:32])[::-1], 2)<<shift))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[16:24]=='':
            r1_H_16_L_8 = 0
        else:
            r1_H_16_L_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[16:24])[::-1], 2)<<shift))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[8:16]=='':
            r1_L_16_H_8 = 0
        else:
            r1_L_16_H_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[8:16])[::-1], 2)<<shift))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[0:8]=='':
            r1_L_16_L_8 = 0
        else:
            r1_L_16_L_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[0:8])[::-1], 2)<<shift))[2:])[::-1])[0:8])[::-1], 2)
        self._RF[ret] = (r1_H_16_H_8<<24) + (r1_H_16_L_8<<16) + (r1_L_16_H_8<<8) + (r1_L_16_L_8)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqishr32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        s1 = self._RF[r1]
        self._Log.write("Source Reg 1 : %s = %x  \nImm: %x  \n" % (r1, s1, imm))
        self._RF[ret] = int(((((bin(s1>>imm)[2:])[::-1])[0:32])[::-1]), 2)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqishr8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        s1 = self._RF[r1]
        self._Log.write("Source Reg 1 : %s = %x  \nimm : %x  \n" % (r1, s1, imm))
        if ((bin(s1)[2:])[::-1])[24:32]=='':
            r1_H_16_H_8 = 0
        else:
            r1_H_16_H_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[24:32])[::-1], 2)>>imm))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[16:24]=='':
            r1_H_16_L_8 = 0
        else:
            r1_H_16_L_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[16:24])[::-1], 2)>>imm))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[8:16]=='':
            r1_L_16_H_8 = 0
        else:
            r1_L_16_H_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[8:16])[::-1], 2)>>imm))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[0:8]=='':
            r1_L_16_L_8 = 0
        else:
            r1_L_16_L_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[0:8])[::-1], 2)>>imm))[2:])[::-1])[0:8])[::-1], 2)
        self._RF[ret] = (r1_H_16_H_8<<24) + (r1_H_16_L_8<<16) + (r1_L_16_H_8<<8) + (r1_L_16_L_8)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqshr32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2 : %s = %x  \n" % (r1, s1, r2, s2))
        shift = int((((bin(s2)[2:])[::-1])[0:5])[::-1], 2)
        self._RF[ret] = int(((((bin(s1>>shift)[2:])[::-1])[0:32])[::-1]), 2)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqshr8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2 : %s = %x  \n" % (r1, s1, r2, s2))
        shift = int((((bin(s2)[2:])[::-1])[0:3])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[24:32]=='':
            r1_H_16_H_8 = 0
        else:
            r1_H_16_H_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[24:32])[::-1], 2)>>shift))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[16:24]=='':
            r1_H_16_L_8 = 0
        else:
            r1_H_16_L_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[16:24])[::-1], 2)>>shift))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[8:16]=='':
            r1_L_16_H_8 = 0
        else:
            r1_L_16_H_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[8:16])[::-1], 2)>>shift))[2:])[::-1])[0:8])[::-1], 2)
        if ((bin(s1)[2:])[::-1])[0:8]=='':
            r1_L_16_L_8 = 0
        else:
            r1_L_16_L_8 = int(((((bin(int((((bin(s1)[2:])[::-1])[0:8])[::-1], 2)>>shift))[2:])[::-1])[0:8])[::-1], 2)
        self._RF[ret] = (r1_H_16_H_8<<24) + (r1_H_16_L_8<<16) + (r1_L_16_H_8<<8) + (r1_L_16_L_8)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqirol32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        s1 = self._RF[r1]
        self._Log.write("Source Reg 1 : %s = %x  \nImm: %x  \n" % (r1, s1, imm))
        tempt = bin(s1)[2:][::-1] + '00000000000000000000000000000000'
        if imm == 0:
            self._RF[ret] = self._RF[r1]
        else:
            shift1 = int((tempt[(32-imm):32])[::-1], 2)
            shift2 = int((tempt[0:(32-imm)])[::-1], 2)
            self._RF[ret] = (shift2<<imm) + shift1
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqirol8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        s1 = self._RF[r1]
        self._Log.write("Source Reg 1 : %s = %x  \nImm: %x  \n" % (r1, s1, imm))
        t1, t2, t3, t4 = bit32_to_8(s1)
        tempt1 = bin(t1)[2:][::-1] + '00000000'
        tempt2 = bin(t2)[2:][::-1] + '00000000'
        tempt3 = bin(t3)[2:][::-1] + '00000000'
        tempt4 = bin(t4)[2:][::-1] + '00000000'
        if imm == 0:
            self._RF[ret] = self._RF[r1]
        else:
            r1_H_16_H_8_shift1 = int((tempt1[8-imm:8])[::-1], 2)
            r1_H_16_H_8_shift2 = int((tempt1[0:8-imm])[::-1], 2)
            r1_H_16_L_8_shift1 = int((tempt2[8-imm:8])[::-1], 2)
            r1_H_16_L_8_shift2 = int((tempt2[0:8-imm])[::-1], 2)
            r1_L_16_H_8_shift1 = int((tempt3[8-imm:8])[::-1], 2)
            r1_L_16_H_8_shift2 = int((tempt3[0:8-imm])[::-1], 2)
            r1_L_16_L_8_shift1 = int((tempt4[8-imm:8])[::-1], 2)
            r1_L_16_L_8_shift2 = int((tempt4[0:8-imm])[::-1], 2)
            r1_H_16_H_8 = (r1_H_16_H_8_shift2<<imm) + r1_H_16_H_8_shift1
            r1_H_16_L_8 = (r1_H_16_L_8_shift2<<imm) + r1_H_16_L_8_shift1
            r1_L_16_H_8 = (r1_L_16_H_8_shift2<<imm) + r1_L_16_H_8_shift1
            r1_L_16_L_8 = (r1_L_16_L_8_shift2<<imm) + r1_L_16_L_8_shift1
            self._RF[ret] = (r1_H_16_H_8<<24) + (r1_H_16_L_8<<16) + (r1_L_16_H_8<<8) + (r1_L_16_L_8)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqrol32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2 : %s = %x  \n" % (r1, s1, r2, s2))
        shift = s2 & 0x1f
        if (shift == 0):
            self._RF[ret] = s1
        else :
            shift1 = int((tempt[(32-shift):32])[::-1], 2)
            shift2 = int((tempt[0:(32-shift)])[::-1], 2)
            self._RF[ret] = (shift2<<shift) + shift1
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqrol8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2 : %s = %x  \n" % (r1, s1, r2, s2))
        shift = s2 & 0x7
        tempt1 = bin(t1)[2:][::-1] + '00000000'
        tempt2 = bin(t2)[2:][::-1] + '00000000'
        tempt3 = bin(t3)[2:][::-1] + '00000000'
        tempt4 = bin(t4)[2:][::-1] + '00000000'
        if shift == 0:
            self._RF[ret] = self._RF[r1]
        else:
            r1_H_16_H_8_shift1 = int((tempt1[8-shift:8])[::-1], 2)
            r1_H_16_H_8_shift2 = int((tempt1[0:8-shift])[::-1], 2)
            r1_H_16_L_8_shift1 = int((tempt2[8-shift:0])[::-1], 2)
            r1_H_16_L_8_shift2 = int((tempt2[0:8-shift])[::-1], 2)
            r1_L_16_H_8_shift1 = int((tempt3[8-shift:8])[::-1], 2)
            r1_L_16_H_8_shift2 = int((tempt3[0:8-shift])[::-1], 2)
            r1_L_16_L_8_shift1 = int((tempt4[8-shift:0])[::-1], 2)
            r1_L_16_L_8_shift2 = int((tempt4[0:8-shift])[::-1], 2)
            r1_H_16_H_8 = (r1_H_16_H_8_shift2<<shift) + r1_H_16_H_8_shift1
            r1_H_16_L_8 = (r1_H_16_L_8_shift2<<shift) + r1_H_16_L_8_shift1
            r1_L_16_H_8 = (r1_L_16_H_8_shift2<<shift) + r1_L_16_H_8_shift1
            r1_L_16_L_8 = (r1_L_16_L_8_shift2<<shift) + r1_L_16_L_8_shift1
            self._RF[ret] = (r1_H_16_H_8<<24) + (r1_H_16_L_8<<16) + (r1_L_16_H_8<<8) + (r1_L_16_L_8)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqiror32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        s1 = self._RF[r1]
        self._Log.write("Source Reg 1 : %s = %x  \nImm: %x  \n" % (r1, s1, imm))
        tempt = bin(s1)[2:][::-1] + '00000000000000000000000000000000'
        if imm == 0:
            self._RF[ret] = self._RF[r1]
        else:
            shift1 = int((tempt[imm:32])[::-1], 2)
            shift2 = int((tempt[0:imm])[::-1], 2)
            self._RF[ret] = (shift2<<(32-imm)) + shift1
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqiror8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        if re.match('-?0x', Match.group(3)):
            imm = int(Match.group(3), 16)
        else:
            imm = int(Match.group(3))
        s1 = self._RF[r1]
        self._Log.write("Source Reg 1 : %s = %x  \nImm: %x  \n" % (r1, s1, imm))
        t1, t2, t3, t4 = bit32_to_8(s1)
        tempt1 = bin(t1)[2:][::-1] + '00000000'
        tempt2 = bin(t2)[2:][::-1] + '00000000'
        tempt3 = bin(t3)[2:][::-1] + '00000000'
        tempt4 = bin(t4)[2:][::-1] + '00000000'
        if imm == 0:
            self._RF[ret] = self._RF[r1]
        else:
            r1_H_16_H_8_shift1 = int((tempt1[imm:8])[::-1], 2)
            r1_H_16_H_8_shift2 = int((tempt1[0:imm])[::-1], 2)
            r1_H_16_L_8_shift1 = int((tempt2[imm:8])[::-1], 2)
            r1_H_16_L_8_shift2 = int((tempt2[0:imm])[::-1], 2)
            r1_L_16_H_8_shift1 = int((tempt3[imm:8])[::-1], 2)
            r1_L_16_H_8_shift2 = int((tempt3[0:imm])[::-1], 2)
            r1_L_16_L_8_shift1 = int((tempt4[imm:8])[::-1], 2)
            r1_L_16_L_8_shift2 = int((tempt4[0:imm])[::-1], 2)
            r1_H_16_H_8 = (r1_H_16_H_8_shift2<<(8-imm)) + r1_H_16_H_8_shift1
            r1_H_16_L_8 = (r1_H_16_L_8_shift2<<(8-imm)) + r1_H_16_L_8_shift1
            r1_L_16_H_8 = (r1_L_16_H_8_shift2<<(8-imm)) + r1_L_16_H_8_shift1
            r1_L_16_L_8 = (r1_L_16_L_8_shift2<<(8-imm)) + r1_L_16_L_8_shift1
            self._RF[ret] = (r1_H_16_H_8<<24) + (r1_H_16_L_8<<16) + (r1_L_16_H_8<<8) + (r1_L_16_L_8)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqror32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2 : %s = %x  \n" % (r1, s1, r2, s2))
        shift = s2 & 0x1f
        if (shift == 0):
            self._RF[ret] = s1
        else :
            shift1 = int((tempt[shift:32])[::-1], 2)
            shift2 = int((tempt[0:shift])[::-1], 2)
            self._RF[ret] = (shift2<<(32 - shift)) + shift1
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqror8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2: %s = %x  \n" % (r1, self._RF[r1], r2, self._RF[r2]))
        s1 = self._RF[r1]
        s2 = self._RF[r2]
        self._Log.write("Source Reg 1 : %s = %x  \nReg 2 : %s = %x  \n" % (r1, s1, r2, s2))
        shift = s2 & 0x7
        tempt1 = bin(t1)[2:][::-1] + '00000000'
        tempt2 = bin(t2)[2:][::-1] + '00000000'
        tempt3 = bin(t3)[2:][::-1] + '00000000'
        tempt4 = bin(t4)[2:][::-1] + '00000000'
        if shift == 0:
            self._RF[ret] = self._RF[r1]
        else:
            r1_H_16_H_8_shift1 = int((tempt1[shift:8])[::-1], 2)
            r1_H_16_H_8_shift2 = int((tempt1[0:shift])[::-1], 2)
            r1_H_16_L_8_shift1 = int((tempt2[shift:8])[::-1], 2)
            r1_H_16_L_8_shift2 = int((tempt2[0:shift])[::-1], 2)
            r1_L_16_H_8_shift1 = int((tempt3[shift:8])[::-1], 2)
            r1_L_16_H_8_shift2 = int((tempt3[0:shift])[::-1], 2)
            r1_L_16_L_8_shift1 = int((tempt4[shift:8])[::-1], 2)
            r1_L_16_L_8_shift2 = int((tempt4[0:shift])[::-1], 2)
            r1_H_16_H_8 = (r1_H_16_H_8_shift2<<(8-shift)) + r1_H_16_H_8_shift1
            r1_H_16_L_8 = (r1_H_16_L_8_shift2<<(8-shift)) + r1_H_16_L_8_shift1
            r1_L_16_H_8 = (r1_L_16_H_8_shift2<<(8-shift)) + r1_L_16_H_8_shift1
            r1_L_16_L_8 = (r1_L_16_L_8_shift2<<(8-shift)) + r1_L_16_L_8_shift1
            self._RF[ret] = (r1_H_16_H_8<<24) + (r1_H_16_L_8<<16) + (r1_L_16_H_8<<8) + (r1_L_16_L_8)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqsbitperm32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r0= Match.group(1), Match.group(2)
        s0 = self._RF[r0]
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, s0))
        self._RF[ret] = (self._RF[r0] >> (self._RF["perm"] & 0x1f) & 0b1) | (
                (s0 >> ((self._RF["perm"] >> 5) & 0x1f) & 0b1) << 1) | (
                (s0 >> ((self._RF["perm"] >> 5*2) & 0x1f) & 0b1) << 2) | (
                (s0 >> ((self._RF["perm"] >> 5*3) & 0x1f) & 0b1) << 3) | (
                (s0 >> ((self._RF["perm"] >> 5*4) & 0x1f) & 0b1) << 4) | (
                (s0 >> ((self._RF["perm"] >> 5*5) & 0x1f) & 0b1) << 5) | (
                (s0 >> ((self._RF["perm"] >> 5 * 6) & 0x1f) & 0b1) << 6) | (
                (s0 >> ((self._RF["perm"] >> 5 * 7) & 0x1f) & 0b1) << 7) | (
                (s0 >> ((self._RF["perm"] >> 5*8) & 0x1f) & 0b1) << 8) | (
                (s0 >> ((self._RF["perm"] >> 5*9) & 0x1f) & 0b1) << 9) | (
                (s0 >> ((self._RF["perm"] >> 5 * 10) & 0x1f) & 0b1) << 10) | (
                (s0 >> ((self._RF["perm"] >> 5 * 11) & 0x1f) & 0b1) << 11) | (
                (s0 >> ((self._RF["perm"] >> 5*12) & 0x1f) & 0b1) << 12) | (
                (s0 >> ((self._RF["perm"] >> 5*13) & 0x1f) & 0b1) << 13) | (
                (s0 >> ((self._RF["perm"] >> 5 * 14) & 0x1f) & 0b1) << 14) | (
                (s0 >> ((self._RF["perm"] >> 5 * 15) & 0x1f) & 0b1) << 15) | (
                (s0 >> ((self._RF["perm"] >> 5*16) & 0x1f) & 0b1) << 16) | (
                (s0 >> ((self._RF["perm"] >> 5*17) & 0x1f) & 0b1) << 17) | (
                (s0 >> ((self._RF["perm"] >> 5 * 18) & 0x1f) & 0b1) << 18) | (
                (s0 >> ((self._RF["perm"] >> 5 * 19) & 0x1f) & 0b1) << 19) | (
                (s0 >> ((self._RF["perm"] >> 5*20) & 0x1f) & 0b1) << 20) | (
                (s0 >> ((self._RF["perm"] >> 5 * 21) & 0x1f) & 0b1) << 21) | (
                (s0 >> ((self._RF["perm"] >> 5 * 22) & 0x1f) & 0b1) << 22) | (
                (s0 >> ((self._RF["perm"] >> 5 * 23) & 0x1f) & 0b1) << 23) | (
                (s0 >> ((self._RF["perm"] >> 5 * 24) & 0x1f) & 0b1) << 24) | (
                (s0 >> ((self._RF["perm"] >> 5 * 25) & 0x1f) & 0b1) << 25) | (
                (s0 >> ((self._RF["perm"] >> 5 * 26) & 0x1f) & 0b1) << 26) | (
                (s0 >> ((self._RF["perm"] >> 5 * 27) & 0x1f) & 0b1) << 27) | (
                (s0 >> ((self._RF["perm"] >> 5 * 28) & 0x1f) & 0b1) << 28) | (
                (s0 >> ((self._RF["perm"] >> 5 * 29) & 0x1f) & 0b1) << 29) | (
                (s0 >> ((self._RF["perm"] >> 5 * 30) & 0x1f) & 0b1) << 30) | (
            (s0 >> ((self._RF["perm"] >> 5 * 31) & 0x1f) & 0b1) << 31)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqsbitperm64(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r0= Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code2<1) or (code3<1):
            return False, PC
        else:
            s0 = (self._RF[r0 + '_e1']<<32) + self._RF[r0 + '_e0']
            self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, s0))
            self._RF[ret] = (s0 >> (self._RF["perm"] & 0x1f) & 0b1) | (
                (s0 >> ((self._RF["perm"] >> 5) & 0x1f) & 0b1) << 1) | (
                (s0 >> ((self._RF["perm"] >> 5*2) & 0x1f) & 0b1) << 2) | (
                (s0 >> ((self._RF["perm"] >> 5*3) & 0x1f) & 0b1) << 3) | (
                (s0 >> ((self._RF["perm"] >> 5*4) & 0x1f) & 0b1) << 4) | (
                (s0 >> ((self._RF["perm"] >> 5*5) & 0x1f) & 0b1) << 5) | (
                (s0 >> ((self._RF["perm"] >> 5 * 6) & 0x1f) & 0b1) << 6) | (
                (s0 >> ((self._RF["perm"] >> 5 * 7) & 0x1f) & 0b1) << 7) | (
                (s0 >> ((self._RF["perm"] >> 5*8) & 0x1f) & 0b1) << 8) | (
                (s0 >> ((self._RF["perm"] >> 5*9) & 0x1f) & 0b1) << 9) | (
                (s0 >> ((self._RF["perm"] >> 5 * 10) & 0x1f) & 0b1) << 10) | (
                (s0 >> ((self._RF["perm"] >> 5 * 11) & 0x1f) & 0b1) << 11) | (
                (s0 >> ((self._RF["perm"] >> 5*12) & 0x1f) & 0b1) << 12) | (
                (s0 >> ((self._RF["perm"] >> 5*13) & 0x1f) & 0b1) << 13) | (
                (s0 >> ((self._RF["perm"] >> 5 * 14) & 0x1f) & 0b1) << 14) | (
                (s0 >> ((self._RF["perm"] >> 5 * 15) & 0x1f) & 0b1) << 15) | (
                (s0 >> ((self._RF["perm"] >> 5*16) & 0x1f) & 0b1) << 16) | (
                (s0 >> ((self._RF["perm"] >> 5*17) & 0x1f) & 0b1) << 17) | (
                (s0 >> ((self._RF["perm"] >> 5 * 18) & 0x1f) & 0b1) << 18) | (
                (s0 >> ((self._RF["perm"] >> 5 * 19) & 0x1f) & 0b1) << 19) | (
                (s0 >> ((self._RF["perm"] >> 5*20) & 0x1f) & 0b1) << 20) | (
                (s0 >> ((self._RF["perm"] >> 5 * 21) & 0x1f) & 0b1) << 21) | (
                (s0 >> ((self._RF["perm"] >> 5 * 22) & 0x1f) & 0b1) << 22) | (
                (s0 >> ((self._RF["perm"] >> 5 * 23) & 0x1f) & 0b1) << 23) | (
                (s0 >> ((self._RF["perm"] >> 5 * 24) & 0x1f) & 0b1) << 24) | (
                (s0 >> ((self._RF["perm"] >> 5 * 25) & 0x1f) & 0b1) << 25) | (
                (s0 >> ((self._RF["perm"] >> 5 * 26) & 0x1f) & 0b1) << 26) | (
                (s0 >> ((self._RF["perm"] >> 5 * 27) & 0x1f) & 0b1) << 27) | (
                (s0 >> ((self._RF["perm"] >> 5 * 28) & 0x1f) & 0b1) << 28) | (
                (s0 >> ((self._RF["perm"] >> 5 * 29) & 0x1f) & 0b1) << 29) | (
                (s0 >> ((self._RF["perm"] >> 5 * 30) & 0x1f) & 0b1) << 30) | (
                (s0 >> ((self._RF["perm"] >> 5 * 31) & 0x1f) & 0b1) << 31) | (
                (s0 >> ((self._RF["perm"] >> 5 * 32) & 0x1f) & 0b1) << 32) | (
                (s0 >> ((self._RF["perm"] >> 5 * 33) & 0x1f) & 0b1) << 33) | (
                (s0 >> ((self._RF["perm"] >> 5 * 34) & 0x1f) & 0b1) << 34) | (
                (s0 >> ((self._RF["perm"] >> 5 * 35) & 0x1f) & 0b1) << 35) | (
                (s0 >> ((self._RF["perm"] >> 5 * 36) & 0x1f) & 0b1) << 36) | (
                (s0 >> ((self._RF["perm"] >> 5 * 37) & 0x1f) & 0b1) << 37) | (
                (s0 >> ((self._RF["perm"] >> 5 * 38) & 0x1f) & 0b1) << 38) | (
                (s0 >> ((self._RF["perm"] >> 5 * 39) & 0x1f) & 0b1) << 39) | (
                (s0 >> ((self._RF["perm"] >> 5 * 40) & 0x1f) & 0b1) << 40) | (
                (s0 >> ((self._RF["perm"] >> 5 * 41) & 0x1f) & 0b1) << 41) | (
                (s0 >> ((self._RF["perm"] >> 5 * 42) & 0x1f) & 0b1) << 42) | (
                (s0 >> ((self._RF["perm"] >> 5 * 43) & 0x1f) & 0b1) << 43) | (
                (s0 >> ((self._RF["perm"] >> 5 * 44) & 0x1f) & 0b1) << 44) | (
                (s0 >> ((self._RF["perm"] >> 5 * 45) & 0x1f) & 0b1) << 45) | (
                (s0 >> ((self._RF["perm"] >> 5 * 46) & 0x1f) & 0b1) << 46) | (
                (s0 >> ((self._RF["perm"] >> 5 * 47) & 0x1f) & 0b1) << 47) | (
                (s0 >> ((self._RF["perm"] >> 5 * 48) & 0x1f) & 0b1) << 48) | (
                (s0 >> ((self._RF["perm"] >> 5 * 49) & 0x1f) & 0b1) << 49) | (
                (s0 >> ((self._RF["perm"] >> 5 * 50) & 0x1f) & 0b1) << 50) | (
                (s0 >> ((self._RF["perm"] >> 5 * 51) & 0x1f) & 0b1) << 51) | (
                (s0 >> ((self._RF["perm"] >> 5 * 52) & 0x1f) & 0b1) << 52) | (
                (s0 >> ((self._RF["perm"] >> 5 * 53) & 0x1f) & 0b1) << 53) | (
                (s0 >> ((self._RF["perm"] >> 5 * 54) & 0x1f) & 0b1) << 54) | (
                (s0 >> ((self._RF["perm"] >> 5 * 55) & 0x1f) & 0b1) << 55) | (
                (s0 >> ((self._RF["perm"] >> 5 * 56) & 0x1f) & 0b1) << 56) | (
                (s0 >> ((self._RF["perm"] >> 5 * 57) & 0x1f) & 0b1) << 57) | (
                (s0 >> ((self._RF["perm"] >> 5 * 58) & 0x1f) & 0b1) << 58) | (
                (s0 >> ((self._RF["perm"] >> 5 * 59) & 0x1f) & 0b1) << 59) | (
                (s0 >> ((self._RF["perm"] >> 5 * 60) & 0x1f) & 0b1) << 60) | (
                (s0 >> ((self._RF["perm"] >> 5 * 61) & 0x1f) & 0b1) << 61) | (
                (s0 >> ((self._RF["perm"] >> 5 * 62) & 0x1f) & 0b1) << 62) | (
                (s0 >> ((self._RF["perm"] >> 5 * 63) & 0x1f) & 0b1) << 63)
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
            return True, PC + 1

    def _Execqsbitperm128(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r0= Match.group(1), Match.group(2)
        s0 = (self._RF[r0 + '_e3']<<96) + (self._RF[r0 + '_e2']<<64) + (self._RF[r0 + '_e1']<<32) + self._RF[r0 + '_e0'] 
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, s0))
        self._RF[ret] = (s0 >> (self._RF["perm"] & 0x1f) & 0b1) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 1) & 0x1f) & 0b1) << 1) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 2) & 0x1f) & 0b1) << 2) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 3) & 0x1f) & 0b1) << 3) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 4) & 0x1f) & 0b1) << 4) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 5) & 0x1f) & 0b1) << 5) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 6) & 0x1f) & 0b1) << 6) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 7) & 0x1f) & 0b1) << 7) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 8) & 0x1f) & 0b1) << 8) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 9) & 0x1f) & 0b1) << 9) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 10) & 0x1f) & 0b1) << 10) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 11) & 0x1f) & 0b1) << 11) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 12) & 0x1f) & 0b1) << 12) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 13) & 0x1f) & 0b1) << 13) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 14) & 0x1f) & 0b1) << 14) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 15) & 0x1f) & 0b1) << 15) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 16) & 0x1f) & 0b1) << 16) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 17) & 0x1f) & 0b1) << 17) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 18) & 0x1f) & 0b1) << 18) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 19) & 0x1f) & 0b1) << 19) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 20) & 0x1f) & 0b1) << 20) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 21) & 0x1f) & 0b1) << 21) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 22) & 0x1f) & 0b1) << 22) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 23) & 0x1f) & 0b1) << 23) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 24) & 0x1f) & 0b1) << 24) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 25) & 0x1f) & 0b1) << 25) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 26) & 0x1f) & 0b1) << 26) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 27) & 0x1f) & 0b1) << 27) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 28) & 0x1f) & 0b1) << 28) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 29) & 0x1f) & 0b1) << 29) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 30) & 0x1f) & 0b1) << 30) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 31) & 0x1f) & 0b1) << 31) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 32) & 0x1f) & 0b1) << 32) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 33) & 0x1f) & 0b1) << 33) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 34) & 0x1f) & 0b1) << 34) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 35) & 0x1f) & 0b1) << 35) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 36) & 0x1f) & 0b1) << 36) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 37) & 0x1f) & 0b1) << 37) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 38) & 0x1f) & 0b1) << 38) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 39) & 0x1f) & 0b1) << 39) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 40) & 0x1f) & 0b1) << 40) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 41) & 0x1f) & 0b1) << 41) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 42) & 0x1f) & 0b1) << 42) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 43) & 0x1f) & 0b1) << 43) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 44) & 0x1f) & 0b1) << 44) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 45) & 0x1f) & 0b1) << 45) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 46) & 0x1f) & 0b1) << 46) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 47) & 0x1f) & 0b1) << 47) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 48) & 0x1f) & 0b1) << 48) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 49) & 0x1f) & 0b1) << 49) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 50) & 0x1f) & 0b1) << 50) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 51) & 0x1f) & 0b1) << 51) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 52) & 0x1f) & 0b1) << 52) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 53) & 0x1f) & 0b1) << 53) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 54) & 0x1f) & 0b1) << 54) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 55) & 0x1f) & 0b1) << 55) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 56) & 0x1f) & 0b1) << 56) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 57) & 0x1f) & 0b1) << 57) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 58) & 0x1f) & 0b1) << 58) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 59) & 0x1f) & 0b1) << 59) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 60) & 0x1f) & 0b1) << 60) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 61) & 0x1f) & 0b1) << 61) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 62) & 0x1f) & 0b1) << 62) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 63) & 0x1f) & 0b1) << 63) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 64) & 0x1f) & 0b1) << 64) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 65) & 0x1f) & 0b1) << 65) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 66) & 0x1f) & 0b1) << 66) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 67) & 0x1f) & 0b1) << 67) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 68) & 0x1f) & 0b1) << 68) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 69) & 0x1f) & 0b1) << 69) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 70) & 0x1f) & 0b1) << 70) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 71) & 0x1f) & 0b1) << 71) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 72) & 0x1f) & 0b1) << 72) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 73) & 0x1f) & 0b1) << 73) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 74) & 0x1f) & 0b1) << 74) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 75) & 0x1f) & 0b1) << 75) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 76) & 0x1f) & 0b1) << 76) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 77) & 0x1f) & 0b1) << 77) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 78) & 0x1f) & 0b1) << 78) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 79) & 0x1f) & 0b1) << 79) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 80) & 0x1f) & 0b1) << 80) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 81) & 0x1f) & 0b1) << 81) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 82) & 0x1f) & 0b1) << 82) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 83) & 0x1f) & 0b1) << 83) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 84) & 0x1f) & 0b1) << 84) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 85) & 0x1f) & 0b1) << 85) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 86) & 0x1f) & 0b1) << 86) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 87) & 0x1f) & 0b1) << 87) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 88) & 0x1f) & 0b1) << 88) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 89) & 0x1f) & 0b1) << 89) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 90) & 0x1f) & 0b1) << 90) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 91) & 0x1f) & 0b1) << 91) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 92) & 0x1f) & 0b1) << 92) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 93) & 0x1f) & 0b1) << 93) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 94) & 0x1f) & 0b1) << 94) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 95) & 0x1f) & 0b1) << 95) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 96) & 0x1f) & 0b1) << 96) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 97) & 0x1f) & 0b1) << 97) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 98) & 0x1f) & 0b1) << 98) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 99) & 0x1f) & 0b1) << 99) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 100) & 0x1f) & 0b1) << 100) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 101) & 0x1f) & 0b1) << 101) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 102) & 0x1f) & 0b1) << 102) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 103) & 0x1f) & 0b1) << 103) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 104) & 0x1f) & 0b1) << 104) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 105) & 0x1f) & 0b1) << 105) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 106) & 0x1f) & 0b1) << 106) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 107) & 0x1f) & 0b1) << 107) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 108) & 0x1f) & 0b1) << 108) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 109) & 0x1f) & 0b1) << 109) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 110) & 0x1f) & 0b1) << 110) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 111) & 0x1f) & 0b1) << 111) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 112) & 0x1f) & 0b1) << 112) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 113) & 0x1f) & 0b1) << 113) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 114) & 0x1f) & 0b1) << 114) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 115) & 0x1f) & 0b1) << 115) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 116) & 0x1f) & 0b1) << 116) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 117) & 0x1f) & 0b1) << 117) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 118) & 0x1f) & 0b1) << 118) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 119) & 0x1f) & 0b1) << 119) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 120) & 0x1f) & 0b1) << 120) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 121) & 0x1f) & 0b1) << 121) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 122) & 0x1f) & 0b1) << 122) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 123) & 0x1f) & 0b1) << 123) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 124) & 0x1f) & 0b1) << 124) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 125) & 0x1f) & 0b1) << 125) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 126) & 0x1f) & 0b1) << 126) | (
                    (s0 >> ((self._RF["perm"] >> 5 * 127) & 0x1f) & 0b1) << 127)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqsbitperm8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r0, r1, i, j = Match.group(1), Match.group(2), Match.group(3), Match.group(4), Match.group(5)
        self._Log.write(
            "Source Reg 0 : %s = 0x%x \nSource Reg 1 : %s = 0x%x  \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        targ = self._RF[r0] & (0xff << (int(i)*8))
        res =   (targ >> (self._RF[r1] & 0x7) & 1) | (
                (targ >> (self._RF[r1] >> 3 * 1 & 0x7) & 1) << 1) | (
                (targ >> (self._RF[r1] >> 3 * 2 & 0x7) & 1) << 2) | (
                (targ >> (self._RF[r1] >> 3 * 3 & 0x7) & 1) << 3) | (
                (targ >> (self._RF[r1] >> 3 * 4 & 0x7) & 1) << 4) | (
                (targ >> (self._RF[r1] >> 3 * 5 & 0x7) & 1) << 5) | (
                (targ >> (self._RF[r1] >> 3 * 6 & 0x7) & 1) << 6) | (
                (targ >> (self._RF[r1] >> 3 * 7 & 0x7) & 1) << 7)
        self._RF[ret] = self._RF[ret] & ~(0xff << int(j)) | (res << int(j))
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqdbitperm32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r0 = Match.group(1), Match.group(2)
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        targ = self._RF[r0] & 0xffffffff
        perm = self._RF[r0] >> 32
        self._RF[ret] = (targ >> (perm & 0x1f) & 0b1) | (
                (targ >> ((perm >> 5) & 0x1f) & 0b1) << 1) | (
                                (targ >> ((perm >> 5 * 2) & 0x1f) & 0b1) << 2) | (
                                (targ >> ((perm >> 5 * 3) & 0x1f) & 0b1) << 3) | (
                                (targ >> ((perm >> 5 * 4) & 0x1f) & 0b1) << 4) | (
                                (targ >> ((perm >> 5 * 5) & 0x1f) & 0b1) << 5) | (
                                (targ >> ((perm >> 5 * 6) & 0x1f) & 0b1) << 6) | (
                                (targ >> ((perm >> 5 * 7) & 0x1f) & 0b1) << 7) | (
                                (targ >> ((perm >> 5 * 8) & 0x1f) & 0b1) << 8) | (
                                (targ >> ((perm >> 5 * 9) & 0x1f) & 0b1) << 9) | (
                                (targ >> ((perm >> 5 * 10) & 0x1f) & 0b1) << 10) | (
                                (targ >> ((perm >> 5 * 11) & 0x1f) & 0b1) << 11) | (
                                (targ >> ((perm >> 5 * 12) & 0x1f) & 0b1) << 12) | (
                                (targ >> ((perm >> 5 * 13) & 0x1f) & 0b1) << 13) | (
                                (targ >> ((perm >> 5 * 14) & 0x1f) & 0b1) << 14) | (
                                (targ >> ((perm >> 5 * 15) & 0x1f) & 0b1) << 15) | (
                                (targ >> ((perm >> 5 * 16) & 0x1f) & 0b1) << 16) | (
                                (targ >> ((perm >> 5 * 17) & 0x1f) & 0b1) << 17) | (
                                (targ >> ((perm >> 5 * 18) & 0x1f) & 0b1) << 18) | (
                                (targ >> ((perm >> 5 * 19) & 0x1f) & 0b1) << 19) | (
                                (targ >> ((perm >> 5 * 20) & 0x1f) & 0b1) << 20) | (
                                (targ >> ((perm >> 5 * 21) & 0x1f) & 0b1) << 21) | (
                                (targ >> ((perm >> 5 * 22) & 0x1f) & 0b1) << 22) | (
                                (targ >> ((perm >> 5 * 23) & 0x1f) & 0b1) << 23) | (
                                (targ >> ((perm >> 5 * 24) & 0x1f) & 0b1) << 24) | (
                                (targ >> ((perm >> 5 * 25) & 0x1f) & 0b1) << 25) | (
                                (targ >> ((perm >> 5 * 26) & 0x1f) & 0b1) << 26) | (
                                (targ >> ((perm >> 5 * 27) & 0x1f) & 0b1) << 27) | (
                                (targ >> ((perm >> 5 * 28) & 0x1f) & 0b1) << 28) | (
                                (targ >> ((perm >> 5 * 29) & 0x1f) & 0b1) << 29) | (
                                (targ >> ((perm >> 5 * 30) & 0x1f) & 0b1) << 30) | (
                                (targ >> ((perm >> 5 * 31) & 0x1f) & 0b1) << 31)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqbyteperm32(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r0, r1= Match.group(1), Match.group(2), Match.group(3)
        self._Log.write("Source Reg 0 : %s = 0x%x \nSource Reg 1 : %s = 0x%x  \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        self._RF[ret] = (self._RF[r0] >> ((self._RF[r1] & 0b11) * 8) & 0xff) | (
                        (self._RF[r0] >> ((self._RF[r1] >> 2 & 0b11) * 8) & 0xff) << 8) | (
                        (self._RF[r0] >> ((self._RF[r1] >> 4 & 0b11) * 8) & 0xff) << 16) | (
                        (self._RF[r0] >> ((self._RF[r1] >> 6 & 0b11) * 8) & 0xff) << 24)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqbyteperm64(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r0, r1 = Match.group(1), Match.group(2), Match.group(3)
        s0 = self._RF[]
        self._Log.write(
            "Source Reg 0 : %s = 0x%x \nSource Reg 1 : %s = 0x%x  \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        self._RF[ret] = (self._RF[r0] >> ((self._RF[r1] & 0b111) * 8) & 0xff) | (
                (self._RF[r0] >> ((self._RF[r1] >> 3 & 0b111) * 8) & 0xff) << 8) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 6 & 0b111) * 8) & 0xff) << 16) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 9 & 0b111) * 8) & 0xff) << 24) | (
                (self._RF[r0] >> ((self._RF[r1] >> 12 & 0b111) * 8) & 0xff) << 32) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 15 & 0b111) * 8) & 0xff) << 40) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 18 & 0b111) * 8) & 0xff) << 48) | (
                (self._RF[r0] >> ((self._RF[r1] >> 21 & 0b111) * 8) & 0xff) << 56)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqbyteperm128(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r0, r1 = Match.group(1), Match.group(2), Match.group(3)
        self._Log.write(
            "Source Reg 0 : %s = 0x%x \nSource Reg 1 : %s = 0x%x  \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        self._RF[ret] = (self._RF[r0] >> ((self._RF[r1] & 0xf) * 8) & 0xff) | (
                (self._RF[r0] >> ((self._RF[r1] >> 4 * 1 & 0xf) * 8) & 0xff) << 8 * 1) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 2 & 0xf) * 8) & 0xff) << 8 * 2) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 3 & 0xf) * 8) & 0xff) << 8 * 3) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 4 & 0xf) * 8) & 0xff) << 8 * 4) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 5 & 0xf) * 8) & 0xff) << 8 * 5) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 6 & 0xf) * 8) & 0xff) << 8 * 6) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 7 & 0xf) * 8) & 0xff) << 8 * 7) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 8 & 0xf) * 8) & 0xff) << 8 * 8) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 9 & 0xf) * 8) & 0xff) << 8 * 9) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 10 & 0xf) * 8) & 0xff) << 8 * 10) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 11 & 0xf) * 8) & 0xff) << 8 * 11) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 12 & 0xf) * 8) & 0xff) << 8 * 12) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 13 & 0xf) * 8) & 0xff) << 8 * 13) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 14 & 0xf) * 8) & 0xff) << 8 * 14) | (
                                (self._RF[r0] >> ((self._RF[r1] >> 4 * 15 & 0xf) * 8) & 0xff) << 8 * 15)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqbitsw(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0, r1 = Match.group(1), Match.group(2), Match.group(3)
        self._Log.write(
            "Source Reg 0 : %s = 0x%x \nSource Reg 1 : %s = 0x%x  \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        temp1 = (self._RF[r0] >> (self._RF[r1] & 0x1f) & 1) << (self._RF[r1] >> 5 & 0x1f)
        temp2 = (self._RF[r0] >> (self._RF[r1] >> 5 & 0x1f) & 1) << (self._RF[r1] & 0x1f)
        self._RF[ret] = self._RF[r0] & ~(1 <<(self._RF[r1] & 0x1f)) & ~(1 << (self._RF[r1] >> 5 & 0x1f)) | (temp1 | temp2)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqbytesw(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0, r1 = Match.group(1), Match.group(2), Match.group(3)
        self._Log.write(
            "Source Reg 0 : %s = 0x%x \nSource Reg 1 : %s = 0x%x  \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        temp1 = (self._RF[r0] >> ((self._RF[r1] & 0b11) * 8) & 0xff) << ((self._RF[r1] >> 2 & 0b11) * 8)
        temp2 = (self._RF[r0] >> ((self._RF[r1] >> 2 & 0b11) * 8) & 0xff) << ((self._RF[r1] & 0b11) * 8)
        self._RF[ret] = self._RF[r0] & ~(0xff << ((self._RF[r1] & 0b11) * 8)) & ~(0xff << ((self._RF[r1] >> 2 & 0b11) * 8)) | (temp1 | temp2)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqlut8m8(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0= Match.group(1), Match.group(2)
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        s1, s2, s3, s4 = bit32_to_8(self._RF[r0])
        s1_s = self._RF['LUT8X8_'+str(s1)]
        s2_s = self._RF['LUT8X8_'+str(s2)]
        s3_s = self._RF['LUT8X8_'+str(s3)]
        s4_s = self._RF['LUT8X8_'+str(s4)]
        self._RF[ret] = (s1_s<<24) + (s2_s<<16) + (s3_s<<8) + (s4_s)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execq4lut8m8(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0= Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r0)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret)
        code1 = int(split1.group(2), 10) 
        code3 = int(split3.group(2), 10)
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        s11, s12, s13, s14 = bit32_to_8(self._RF[r0])
        s21, s22, s23, s24 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 1)])
        s31, s32, s33, s34 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 2)])
        s41, s42, s43, s44 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 3)])
        s11_s = self._RF['LUT8X8_'+str(s11)]
        s12_s = self._RF['LUT8X8_'+str(s12)]
        s13_s = self._RF['LUT8X8_'+str(s13)]
        s14_s = self._RF['LUT8X8_'+str(s14)]
        s21_s = self._RF['LUT8X8_'+str(s21)]
        s22_s = self._RF['LUT8X8_'+str(s22)]
        s23_s = self._RF['LUT8X8_'+str(s23)]
        s24_s = self._RF['LUT8X8_'+str(s24)]
        s31_s = self._RF['LUT8X8_'+str(s31)]
        s32_s = self._RF['LUT8X8_'+str(s32)]
        s33_s = self._RF['LUT8X8_'+str(s33)]
        s34_s = self._RF['LUT8X8_'+str(s34)]
        s41_s = self._RF['LUT8X8_'+str(s41)]
        s42_s = self._RF['LUT8X8_'+str(s42)]
        s43_s = self._RF['LUT8X8_'+str(s43)]
        s44_s = self._RF['LUT8X8_'+str(s44)]
        rd1 = self._RF[ret] = (s11_s<<24) + (s12_s<<16) + (s13_s<<8) + (s14_s)
        rd2 = self._RF[split1.group(1) + str(code1 - 1)] = (s21_s<<24) + (s22_s<<16) + (s23_s<<8) + (s24_s)
        rd3 = self._RF[split1.group(1) + str(code1 - 2)] = (s31_s<<24) + (s32_s<<16) + (s33_s<<8) + (s34_s)
        rd4 = self._RF[split1.group(1) + str(code1 - 3)] = (s41_s<<24) + (s42_s<<16) + (s43_s<<8) + (s44_s)
        tempt = (rd1<<96) + (rd2<<64) + (rd3<<32) + (rd4)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, tempt))
        return True, PC + 1

    def _Execqlut4m4(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0= Match.group(1), Match.group(2)
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        self._RF[ret] = self._RF["LUT4X4_"+str(self._RF[r0] & 0xf)] | (self._RF["LUT4X4_"+str(self._RF[r0] >> 4 & 0xf)] << 4) |\
                        (self._RF["LUT4X4_" + str(self._RF[r0] >> 8 & 0xf)] << 8) | (self._RF["LUT4X4_"+str(self._RF[r0] >> 12 & 0xf)] << 12) | \
                        (self._RF["LUT4X4_" + str(self._RF[r0] >> 16 & 0xf)] << 16) | (self._RF["LUT4X4_" + str(self._RF[r0] >> 20 & 0xf)] << 20) | \
                        (self._RF["LUT4X4_" + str(self._RF[r0] >> 24 & 0xf)] << 24) | (self._RF["LUT4X4_" + str(self._RF[r0] >> 28 & 0xf)] << 28)
            # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqlut6m4(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0= Match.group(1), Match.group(2)
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        self._RF[ret] = self._RF["LUT6X4_"+str(self._RF[r0] & 0x3f)] | (self._RF["LUT6X4_"+str(self._RF[r0] >> 6 & 0x3f)] << 4) |\
                        (self._RF["LUT6X4_" + str(self._RF[r0] >> 12 & 0x3f)] << 8) | (self._RF["LUT6X4_"+str(self._RF[r0] >> 18 & 0x3f)] << 12) | \
                        (self._RF["LUT6X4_" + str(self._RF[r0] >> 24 & 0x3f)] << 16) | (self._RF["LUT6X4_" + str(self._RF[r0] >> 30 & 0x3f)] << 20) | \
                        (self._RF["LUT6X4_" + str(self._RF[r0] >> 36 & 0x3f)] << 24) | (self._RF["LUT6X4_" + str(self._RF[r0] >> 42 & 0x3f)] << 28)
            # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqlut8m4(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0= Match.group(1), Match.group(2)
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        self._RF[ret] = self._RF["LUT8X4_"+str(self._RF[r0] & 0xff)] | (self._RF["LUT8X4_"+str(self._RF[r0] >> 8 & 0xff)] << 4) |\
                        (self._RF["LUT8X4_" + str(self._RF[r0] >> 16 & 0xff)] << 8) | (self._RF["LUT8X4_"+str(self._RF[r0] >> 24 & 0xff)] << 12) | \
                        (self._RF["LUT8X4_" + str(self._RF[r0] >> 32 & 0xff)] << 16) | (self._RF["LUT8X4_" + str(self._RF[r0] >> 40 & 0xff)] << 20) | \
                        (self._RF["LUT8X4_" + str(self._RF[r0] >> 48 & 0xff)] << 24) | (self._RF["LUT8X4_" + str(self._RF[r0] >> 56 & 0xff)] << 28)
            # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqlut8m32(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0, n= Match.group(1), Match.group(2), Match.group(3)
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        self._RF[ret] = self._RF["LUT8X32_"+str(self._RF[r0] >> (int(n)*8) & 0xff)]
            # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execq4lut8m32(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0= Match.group(1), Match.group(2)
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        self._RF[ret] = self._RF["LUT8X32_"+str(self._RF[r0] & 0xff)] | (self._RF["LUT8X32_"+str(self._RF[r0] >> 8 & 0xff)] << 32) |\
                        (self._RF["LUT8X32_" + str(self._RF[r0] >> 16 & 0xff)] << 64) | (self._RF["LUT8X32_"+str(self._RF[r0] >> 24 & 0xff)] << 96)
            # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqlutsw(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, r1, idx= Match.group(1), Match.group(2), int(Match.group(3))
        self._Log.write("Source Reg 0 : %s = 0x%x \nSource Reg 1 : %s = 0x%x  \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        if idx == 0:
            tmp = self._RF["LUT8X8_" + str(self._RF[r0] & 0xff)]
            self._RF["LUT8X8_" + str(self._RF[r0] & 0xff)] = self._RF["LUT8X8_" + str(self._RF[r1] & 0xff)]
            self._RF["LUT8X8_" + str(self._RF[r1] & 0xff)] = tmp
        elif idx == 1:
            tmp = self._RF["LUT4X4_" + str(self._RF[r0] & 0xf)]
            self._RF["LUT4X4_" + str(self._RF[r0] & 0xf)] = self._RF["LUT4X4_" + str(self._RF[r1] & 0xf)]
            self._RF["LUT4X4_" + str(self._RF[r1] & 0xf)] = tmp
        elif idx == 2:
            tmp = self._RF["LUT6X4_" + str(self._RF[r0] & 0x3f)]
            self._RF["LUT6X4_" + str(self._RF[r0] & 0x3f)] = self._RF["LUT6X4_" + str(self._RF[r1] & 0x3f)]
            self._RF["LUT6X4_" + str(self._RF[r1] & 0x3f)] = tmp
        elif idx == 3:
            tmp = self._RF["LUT8X4_" + str(self._RF[r0] & 0xff)]
            self._RF["LUT8X4_" + str(self._RF[r0] & 0xff)] = self._RF["LUT8X4_" + str(self._RF[r1] & 0xff)]
            self._RF["LUT8X4_" + str(self._RF[r1] & 0xff)] = tmp
        else:
            tmp = self._RF["LUT8X32_" + str(self._RF[r0] & 0xff)]
            self._RF["LUT8X32_" + str(self._RF[r0] & 0xff)] = self._RF["LUT8X32_" + str(self._RF[r1] & 0xff)]
            self._RF["LUT8X32_" + str(self._RF[r1] & 0xff)] = tmp
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        return True, PC + 1
		
    def _Execqgf8_2mulx(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0= Match.group(1), Match.group(2)
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        high_part = (self._RF[r0] & 0xffff0000) >> 16
        low_part  = self._RF[r0] & 0xffff
        if self._RF["gen_poly2_8_2"] == 0b01:
            tmp1 = high_part >> 8
        elif self._RF["gen_poly2_8_2"] == 0b10:
            tmp1 = high_part & 0xff00
        elif self._RF["gen_poly2_8_2"] == 0b11:
            tmp1 = (high_part & 0xff00) | (high_part >> 8)
        else:
            tmp1 = 0
        high_part_new = ((high_part & 0xff) << 8) ^ tmp1
        if self._RF["gen_poly2_8_2"] == 0b01:
            tmp2 = low_part >> 8
        elif self._RF["gen_poly2_8_2"] == 0b10:
            tmp2 = low_part & 0xff00
        elif self._RF["gen_poly2_8_2"] == 0b11:
            tmp2 = (low_part & 0xff00) | (low_part >> 8)
        else:
            tmp2 = 0
        low_part_new = ((low_part & 0xff) << 8) ^ tmp2
        self._RF[ret] = (high_part_new << 16) | low_part_new
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqgf8_3mulx(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0 = Match.group(1), Match.group(2)
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        op = (self._RF[r0] >> 16) & 0xff
        tmp1 = 0
        tmp2 = 0
        tmp3 = 0
        if (self._RF["gen_poly2_8_3"] & 1) == 1:
            tmp1 = op
        if (self._RF["gen_poly2_8_3"] & 0b010) == 2:
            tmp2 = op << 8
        if (self._RF["gen_poly2_8_3"] & 0b100) == 4:
            tmp3 = op << 16
        tmp = tmp1 | tmp2 | tmp3
        self._RF[ret] = ((self._RF[r0] & 0xffff) << 8) ^ tmp
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqgf8_4mulx(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0 = Match.group(1), Match.group(2)
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        op = (self._RF[r0] >> 24) & 0xff
        tmp1 = 0
        tmp2 = 0
        tmp3 = 0
        tmp4 = 0
        if (self._RF["gen_poly2_8_4"] & 1) == 1:
            tmp1 = op
        if (self._RF["gen_poly2_8_4"] & 0b010) == 2:
            tmp2 = op << 8
        if (self._RF["gen_poly2_8_4"] & 0b100) == 4:
            tmp3 = op << 16
        if (self._RF["gen_poly2_8_4"] & 0b1000) == 8:
            tmp4 = op << 24
        tmp = tmp1 | tmp2 | tmp3 | tmp4
        self._RF[ret] = ((self._RF[r0] & 0xffffff) << 8) ^ tmp
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqgf8_mulv(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0, r1 = Match.group(1), Match.group(2), Match.group(3)
        self._Log.write("Source Reg 0 : %s = 0x%x \nSource Reg 1 : %s = 0x%x  \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        res = 0
        for i in range(0,4):
            op1 = (self._RF[r0] >> (8 * i)) & 0xff
            op2 = (self._RF[r1] >> (8 * i)) & 0xff
            res = (gmul(op1, op2, self._RF["gen_poly2_8"] | (1<<8)) << (8 * i)) | res
        self._RF[ret] = res
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqgf8_2mulv(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0, r1 = Match.group(1), Match.group(2), Match.group(3)
        self._Log.write("Source Reg 0 : %s = 0x%x \nSource Reg 1 : %s = 0x%x  \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        tmp1 = gmul8_2((self._RF[r0] >> 16) & 0xffff, (self._RF[r1] >> 16) & 0xffff, self._RF["gen_poly2_8"] | (1<<8), self._RF["gen_poly2_8_2"])
        tmp2 = gmul8_2(self._RF[r0] & 0xffff, self._RF[r1] & 0xffff, self._RF["gen_poly2_8"] | (1<<8), self._RF["gen_poly2_8_2"])
        tmp3 = gmul8_2((self._RF[r0] >> 16) & 0xffff, 0x0100, self._RF["gen_poly2_8"] | (1<<8), self._RF["gen_poly2_8_2"])
        tmp4 = gmul8_2(self._RF[r0] & 0xffff, 0x0100, self._RF["gen_poly2_8"] | (1<<8), self._RF["gen_poly2_8_2"])
        self._RF[ret] = tmp2 | (tmp1 << 16) | (tmp4 << 32) | (tmp3 << 48)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqgf8_3mulv(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0, r1 = Match.group(1), Match.group(2), Match.group(3)
        self._Log.write("Source Reg 0 : %s = 0x%x \nSource Reg 1 : %s = 0x%x  \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        tmp1 = gmul8_3(self._RF[r0] & 0xffffff, self._RF[r1] & 0xffffff, self._RF["gen_poly2_8"] | (1<<8), self._RF["gen_poly2_8_3"])
        tmp2 = gmul8_3(self._RF[r0] & 0xffffff, 0x0100, self._RF["gen_poly2_8"] | (1<<8), self._RF["gen_poly2_8_3"])
        tmp3 = gmul8_3(self._RF[r0] & 0xffffff, 0x010000, self._RF["gen_poly2_8"] | (1<<8), self._RF["gen_poly2_8_3"])
        self._RF[ret] = tmp1 | (tmp2 << 32) | (tmp3 << 64)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqgf8_4mulv(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        ret, r0, r1 = Match.group(1), Match.group(2), Match.group(3)
        self._Log.write("Source Reg 0 : %s = 0x%x \nSource Reg 1 : %s = 0x%x  \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        tmp1 = gmul8_4(self._RF[r0], self._RF[r1], self._RF["gen_poly2_8"] | (1<<8), self._RF["gen_poly2_8_4"])
        tmp2 = gmul8_4(self._RF[r0], 0x0100, self._RF["gen_poly2_8"] | (1<<8), self._RF["gen_poly2_8_4"])
        tmp3 = gmul8_4(self._RF[r0], 0x010000, self._RF["gen_poly2_8"] | (1<<8), self._RF["gen_poly2_8_4"])
        tmp4 = gmul8_4(self._RF[r0], 0x01000000, self._RF["gen_poly2_8"] | (1<<8), self._RF["gen_poly2_8_4"])
        self._RF[ret] = tmp1 | (tmp2 << 32) | (tmp3 << 64) | (tmp4 << 96)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmds4(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret, r1 = Match.group(1), Match.group(2)
        d1 = self._RF[ret]
        s1 = self._RF[r1]
        self._Log.write("Source Reg 1 : %s = %x  \n" % (r1, s1))
        ret_H_16_H_8, ret_H_16_L_8, ret_L_16_H_8, ret_L_16_L_8 = bit32_to_8(d1)
        mds32 = bit32(s1)
        ret_H_16_H_8 = int((bin((ret_H_16_H_8 * mds32[31]) + (ret_H_16_L_8 * mds32[27]) + (ret_L_16_H_8 * mds32[23]) + (ret_L_16_L_8 * mds32[19]))[2:])[0:8], 2)
        ret_H_16_L_8 = int((bin((ret_H_16_H_8 * mds32[30]) + (ret_H_16_L_8 * mds32[26]) + (ret_L_16_H_8 * mds32[22]) + (ret_L_16_L_8 * mds32[18]))[2:])[0:8], 2)
        ret_L_16_H_8 = int((bin((ret_H_16_H_8 * mds32[29]) + (ret_H_16_L_8 * mds32[25]) + (ret_L_16_H_8 * mds32[21]) + (ret_L_16_L_8 * mds32[17]))[2:])[0:8], 2)
        ret_L_16_L_8 = int((bin((ret_H_16_H_8 * mds32[28]) + (ret_H_16_L_8 * mds32[24]) + (ret_L_16_H_8 * mds32[20]) + (ret_L_16_L_8 * mds32[16]))[2:])[0:8], 2)
        self._RF[ret] = (ret_H_16_H_8<<24) + (ret_H_16_L_8<<16) + (ret_L_16_H_8<<8) + (ret_L_16_L_8)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = %x \n" % (ret, self._RF[ret]))
        return True, PC + 1
		
    def _Execqmds8(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code3<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<32) + self._RF[split1.group(1) + str(code1 - 1)]
            d1 = (self._RF[ret1]<<32) + self._RF[split3.group(1) + str(code3 - 1)]
            self._Log.write("Source Reg 1 : %s = %x  \nRet 1 : %s = %x" % (r1, s1, ret1, d1))
            ret1_H_16_H_8, ret1_H_16_L_8, ret1_L_16_H_8, ret1_L_16_L_8 = bit32_to_8(self._RF[ret1])
            ret2_H_16_H_8, ret2_H_16_L_8, ret2_L_16_H_8, ret2_L_16_L_8 = bit32_to_8(self._RF[split3.group(1) + str(code3-1)])
            mds32_r1 = bit32(self._RF[r1])
            mds32_r2 = bit32(self._RF[split1.group(1) + str(code1 - 1)])
            ret1_H_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[31]) + (ret1_H_16_L_8 * mds32_r1[23]) + (ret1_L_16_H_8 * mds32_r1[15]) + (ret1_L_16_L_8 * mds32_r1[7]) + (ret2_H_16_H_8 * mds32_r2[31]) + (ret2_H_16_L_8 * mds32_r2[23]) + (ret2_L_16_H_8 * mds32_r2[15]) + (ret2_L_16_L_8 * mds32_r2[7]))[2:])[0:8], 2)
            ret1_H_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[30]) + (ret1_H_16_L_8 * mds32_r1[22]) + (ret1_L_16_H_8 * mds32_r1[14]) + (ret1_L_16_L_8 * mds32_r1[6]) + (ret2_H_16_H_8 * mds32_r2[30]) + (ret2_H_16_L_8 * mds32_r2[22]) + (ret2_L_16_H_8 * mds32_r2[14]) + (ret2_L_16_L_8 * mds32_r2[6]))[2:])[0:8], 2)
            ret1_L_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[29]) + (ret1_H_16_L_8 * mds32_r1[21]) + (ret1_L_16_H_8 * mds32_r1[13]) + (ret1_L_16_L_8 * mds32_r1[5]) + (ret2_H_16_H_8 * mds32_r2[29]) + (ret2_H_16_L_8 * mds32_r2[21]) + (ret2_L_16_H_8 * mds32_r2[13]) + (ret2_L_16_L_8 * mds32_r2[5]))[2:])[0:8], 2)
            ret1_L_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[28]) + (ret1_H_16_L_8 * mds32_r1[20]) + (ret1_L_16_H_8 * mds32_r1[12]) + (ret1_L_16_L_8 * mds32_r1[4]) + (ret2_H_16_H_8 * mds32_r2[28]) + (ret2_H_16_L_8 * mds32_r2[20]) + (ret2_L_16_H_8 * mds32_r2[12]) + (ret2_L_16_L_8 * mds32_r2[4]))[2:])[0:8], 2)
            ret2_H_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[27]) + (ret1_H_16_L_8 * mds32_r1[19]) + (ret1_L_16_H_8 * mds32_r1[11]) + (ret1_L_16_L_8 * mds32_r1[3]) + (ret2_H_16_H_8 * mds32_r2[27]) + (ret2_H_16_L_8 * mds32_r2[19]) + (ret2_L_16_H_8 * mds32_r2[11]) + (ret2_L_16_L_8 * mds32_r2[3]))[2:])[0:8], 2)
            ret2_H_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[26]) + (ret1_H_16_L_8 * mds32_r1[18]) + (ret1_L_16_H_8 * mds32_r1[10]) + (ret1_L_16_L_8 * mds32_r1[2]) + (ret2_H_16_H_8 * mds32_r2[26]) + (ret2_H_16_L_8 * mds32_r2[18]) + (ret2_L_16_H_8 * mds32_r2[10]) + (ret2_L_16_L_8 * mds32_r2[2]))[2:])[0:8], 2)
            ret2_L_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[25]) + (ret1_H_16_L_8 * mds32_r1[17]) + (ret1_L_16_H_8 * mds32_r1[9]) + (ret1_L_16_L_8 * mds32_r1[1]) + (ret2_H_16_H_8 * mds32_r2[25]) + (ret2_H_16_L_8 * mds32_r2[17]) + (ret2_L_16_H_8 * mds32_r2[9]) + (ret2_L_16_L_8 * mds32_r2[1]))[2:])[0:8], 2)
            ret2_L_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[24]) + (ret1_H_16_L_8 * mds32_r1[16]) + (ret1_L_16_H_8 * mds32_r1[8]) + (ret1_L_16_L_8 * mds32_r1[0]) + (ret2_H_16_H_8 * mds32_r2[24]) + (ret2_H_16_L_8 * mds32_r2[16]) + (ret2_L_16_H_8 * mds32_r2[8]) + (ret2_L_16_L_8 * mds32_r2[0]))[2:])[0:8], 2)
            self._RF[ret1] = (ret1_H_16_H_8<<24) + (ret1_H_16_L_8<<16) + (ret1_L_16_H_8<<8) + ret1_L_16_L_8
            self._RF[split3.group(1) + str(code3 - 1)] = (ret2_H_16_H_8<<24) + (ret2_H_16_L_8<<16) + (ret2_L_16_H_8<<8) + ret2_L_16_L_8
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result1 : %s = %x \nResult2 : %s = %x \n" % (ret1, self._RF[ret1]))
            return True, PC + 1
		
    def _Execqmds16(self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<1) or (code3<1):
            return False, PC
        else:
            s1 = (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)]
            d1 = (self._RF[ret1]<<96) + (self._RF[split3.group(1) + str(code3 - 1)]<<64) + (self._RF[split3.group(1) + str(code3 - 2)]<<32) + self._RF[split3.group(1) + str(code3 - 3)]
            self._Log.write("Source Reg 1 : %s = %x  \nRet 1 : %s = %x" % (r1, s1, ret1, d1))
            ret1_H_16_H_8, ret1_H_16_L_8, ret1_L_16_H_8, ret1_L_16_L_8 = bit32_to_8(self._RF[ret1])
            ret2_H_16_H_8, ret2_H_16_L_8, ret2_L_16_H_8, ret2_L_16_L_8 = bit32_to_8(self._RF[split3.group(1) + str(code3 - 1)])
            ret3_H_16_H_8, ret3_H_16_L_8, ret3_L_16_H_8, ret3_L_16_L_8 = bit32_to_8(self._RF[split3.group(1) + str(code3 - 2)])
            ret4_H_16_H_8, ret4_H_16_L_8, ret4_L_16_H_8, ret4_L_16_L_8 = bit32_to_8(self._RF[split3.group(1) + str(code3 - 3)])
            mds32_r1 = bit32(self._RF[r1])
            mds32_r2 = bit32(self._RF[split1.group(1) + str(code1 - 1)])
            mds32_r3 = bit32(self._RF[split1.group(1) + str(code1 - 2)])
            mds32_r4 = bit32(self._RF[split1.group(1) + str(code1 - 3)])
            ret1_H_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[31]) + (ret1_H_16_L_8 * mds32_r1[15]) + (ret1_L_16_H_8 * mds32_r2[31]) + (ret1_L_16_L_8 * mds32_r2[15]) + (ret2_H_16_H_8 * mds32_r3[31]) + (ret2_H_16_L_8 * mds32_r3[15]) + (ret2_L_16_H_8 * mds32_r4[31]) + (ret2_L_16_L_8 * mds32_r4[15]))[2:])[0:8], 2)
            ret1_H_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[30]) + (ret1_H_16_L_8 * mds32_r1[14]) + (ret1_L_16_H_8 * mds32_r2[30]) + (ret1_L_16_L_8 * mds32_r2[14]) + (ret2_H_16_H_8 * mds32_r3[30]) + (ret2_H_16_L_8 * mds32_r3[14]) + (ret2_L_16_H_8 * mds32_r4[30]) + (ret2_L_16_L_8 * mds32_r4[14]))[2:])[0:8], 2)
            ret1_L_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[29]) + (ret1_H_16_L_8 * mds32_r1[13]) + (ret1_L_16_H_8 * mds32_r2[29]) + (ret1_L_16_L_8 * mds32_r2[13]) + (ret2_H_16_H_8 * mds32_r3[29]) + (ret2_H_16_L_8 * mds32_r3[13]) + (ret2_L_16_H_8 * mds32_r4[29]) + (ret2_L_16_L_8 * mds32_r4[13]))[2:])[0:8], 2)
            ret1_L_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[28]) + (ret1_H_16_L_8 * mds32_r1[12]) + (ret1_L_16_H_8 * mds32_r2[28]) + (ret1_L_16_L_8 * mds32_r2[12]) + (ret2_H_16_H_8 * mds32_r3[28]) + (ret2_H_16_L_8 * mds32_r3[12]) + (ret2_L_16_H_8 * mds32_r4[28]) + (ret2_L_16_L_8 * mds32_r4[12]))[2:])[0:8], 2)
            ret2_H_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[27]) + (ret1_H_16_L_8 * mds32_r1[11]) + (ret1_L_16_H_8 * mds32_r2[27]) + (ret1_L_16_L_8 * mds32_r2[11]) + (ret2_H_16_H_8 * mds32_r3[27]) + (ret2_H_16_L_8 * mds32_r3[11]) + (ret2_L_16_H_8 * mds32_r4[27]) + (ret2_L_16_L_8 * mds32_r4[11]))[2:])[0:8], 2)
            ret2_H_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[26]) + (ret1_H_16_L_8 * mds32_r1[10]) + (ret1_L_16_H_8 * mds32_r2[26]) + (ret1_L_16_L_8 * mds32_r2[10]) + (ret2_H_16_H_8 * mds32_r3[26]) + (ret2_H_16_L_8 * mds32_r3[10]) + (ret2_L_16_H_8 * mds32_r4[26]) + (ret2_L_16_L_8 * mds32_r4[10]))[2:])[0:8], 2)
            ret2_L_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[25]) + (ret1_H_16_L_8 * mds32_r1[9]) + (ret1_L_16_H_8 * mds32_r2[25]) + (ret1_L_16_L_8 * mds32_r2[9]) + (ret2_H_16_H_8 * mds32_r3[25]) + (ret2_H_16_L_8 * mds32_r3[9]) + (ret2_L_16_H_8 * mds32_r4[25]) + (ret2_L_16_L_8 * mds32_r4[9]))[2:])[0:8], 2)
            ret2_L_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[24]) + (ret1_H_16_L_8 * mds32_r1[8]) + (ret1_L_16_H_8 * mds32_r2[24]) + (ret1_L_16_L_8 * mds32_r2[8]) + (ret2_H_16_H_8 * mds32_r3[24]) + (ret2_H_16_L_8 * mds32_r3[8]) + (ret2_L_16_H_8 * mds32_r4[24]) + (ret2_L_16_L_8 * mds32_r4[8]))[2:])[0:8], 2)
            ret3_H_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[23]) + (ret1_H_16_L_8 * mds32_r1[7]) + (ret1_L_16_H_8 * mds32_r2[23]) + (ret1_L_16_L_8 * mds32_r2[7]) + (ret2_H_16_H_8 * mds32_r3[23]) + (ret2_H_16_L_8 * mds32_r3[7]) + (ret2_L_16_H_8 * mds32_r4[23]) + (ret2_L_16_L_8 * mds32_r4[7]))[2:])[0:8], 2)
            ret3_H_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[22]) + (ret1_H_16_L_8 * mds32_r1[6]) + (ret1_L_16_H_8 * mds32_r2[22]) + (ret1_L_16_L_8 * mds32_r2[6]) + (ret2_H_16_H_8 * mds32_r3[22]) + (ret2_H_16_L_8 * mds32_r3[6]) + (ret2_L_16_H_8 * mds32_r4[22]) + (ret2_L_16_L_8 * mds32_r4[6]))[2:])[0:8], 2)
            ret3_L_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[21]) + (ret1_H_16_L_8 * mds32_r1[5]) + (ret1_L_16_H_8 * mds32_r2[21]) + (ret1_L_16_L_8 * mds32_r2[5]) + (ret2_H_16_H_8 * mds32_r3[21]) + (ret2_H_16_L_8 * mds32_r3[5]) + (ret2_L_16_H_8 * mds32_r4[21]) + (ret2_L_16_L_8 * mds32_r4[5]))[2:])[0:8], 2)
            ret3_L_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[20]) + (ret1_H_16_L_8 * mds32_r1[4]) + (ret1_L_16_H_8 * mds32_r2[20]) + (ret1_L_16_L_8 * mds32_r2[4]) + (ret2_H_16_H_8 * mds32_r3[20]) + (ret2_H_16_L_8 * mds32_r3[4]) + (ret2_L_16_H_8 * mds32_r4[20]) + (ret2_L_16_L_8 * mds32_r4[4]))[2:])[0:8], 2)
            ret4_H_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[19]) + (ret1_H_16_L_8 * mds32_r1[3]) + (ret1_L_16_H_8 * mds32_r2[19]) + (ret1_L_16_L_8 * mds32_r2[3]) + (ret2_H_16_H_8 * mds32_r3[19]) + (ret2_H_16_L_8 * mds32_r3[3]) + (ret2_L_16_H_8 * mds32_r4[19]) + (ret2_L_16_L_8 * mds32_r4[3]))[2:])[0:8], 2)
            ret4_H_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[18]) + (ret1_H_16_L_8 * mds32_r1[2]) + (ret1_L_16_H_8 * mds32_r2[18]) + (ret1_L_16_L_8 * mds32_r2[2]) + (ret2_H_16_H_8 * mds32_r3[18]) + (ret2_H_16_L_8 * mds32_r3[2]) + (ret2_L_16_H_8 * mds32_r4[18]) + (ret2_L_16_L_8 * mds32_r4[2]))[2:])[0:8], 2)
            ret4_L_16_H_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[17]) + (ret1_H_16_L_8 * mds32_r1[1]) + (ret1_L_16_H_8 * mds32_r2[17]) + (ret1_L_16_L_8 * mds32_r2[1]) + (ret2_H_16_H_8 * mds32_r3[17]) + (ret2_H_16_L_8 * mds32_r3[1]) + (ret2_L_16_H_8 * mds32_r4[17]) + (ret2_L_16_L_8 * mds32_r4[1]))[2:])[0:8], 2)
            ret4_L_16_L_8 = int((bin( (ret1_H_16_H_8 * mds32_r1[16]) + (ret1_H_16_L_8 * mds32_r1[0]) + (ret1_L_16_H_8 * mds32_r2[16]) + (ret1_L_16_L_8 * mds32_r2[0]) + (ret2_H_16_H_8 * mds32_r3[16]) + (ret2_H_16_L_8 * mds32_r3[0]) + (ret2_L_16_H_8 * mds32_r4[16]) + (ret2_L_16_L_8 * mds32_r4[0]))[2:])[0:8], 2)
            s1 = (ret1_H_16_H_8<<24) + (ret1_H_16_L_8<<16) + (ret1_L_16_H_8<<8) + (ret1_L_16_L_8)
            s2 = (ret2_H_16_H_8<<24) + (ret2_H_16_L_8<<16) + (ret2_L_16_H_8<<8) + (ret2_L_16_L_8)
            s3 = (ret3_H_16_H_8<<24) + (ret4_H_16_L_8<<16) + (ret3_L_16_H_8<<8) + (ret3_L_16_L_8)
            s4 = (ret4_H_16_H_8<<24) + (ret3_H_16_L_8<<16) + (ret4_L_16_H_8<<8) + (ret4_L_16_L_8)
            self._RF[ret1], self._RF[split3.group(1) + str(code1 - 1)], self._RF[split3.group(1) + str(code1 - 2)], self._RF[split3.group(1) + str(code1 - 3)] = bit128_to_32((s1<<96) + (s2<<64) + (s3<<32) + s4)
		    # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result1 : %s = %x \n" % (ret1, self._RF[ret1]))
            return True, PC + 1

    def _Execqgfmulx    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1):
            return False, PC
        else:
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, self._RF[r1]))
            coff = bit32(self._RF[r1])
            poly = (coff[31] * pow(self._RF['dim'], 31) + coff[30] * pow(self._RF['dim'], 30) + coff[29] * pow(self._RF['dim'], 29) + coff[28] * pow(self._RF['dim'], 28) + 
                    coff[27] * pow(self._RF['dim'], 27) + coff[26] * pow(self._RF['dim'], 26) + coff[25] * pow(self._RF['dim'], 25) + coff[24] * pow(self._RF['dim'], 24) + 
                    coff[23] * pow(self._RF['dim'], 23) + coff[22] * pow(self._RF['dim'], 22) + coff[21] * pow(self._RF['dim'], 21) + coff[20] * pow(self._RF['dim'], 20) + 
                    coff[19] * pow(self._RF['dim'], 19) + coff[18] * pow(self._RF['dim'], 18) + coff[17] * pow(self._RF['dim'], 17) + coff[16] * pow(self._RF['dim'], 16) + 
                    coff[15] * pow(self._RF['dim'], 15) + coff[14] * pow(self._RF['dim'], 14) + coff[13] * pow(self._RF['dim'], 13) + coff[12] * pow(self._RF['dim'], 12) + 
                    coff[11] * pow(self._RF['dim'], 11) + coff[10] * pow(self._RF['dim'], 10) + coff[9] * pow(self._RF['dim'], 9) + coff[8] * pow(self._RF['dim'], 8) + 
                    coff[7] * pow(self._RF['dim'], 7) + coff[6] * pow(self._RF['dim'], 6) + coff[5] * pow(self._RF['dim'], 5) + coff[4] * pow(self._RF['dim'], 4) + 
                    coff[3] * pow(self._RF['dim'], 3) + coff[2] * pow(self._RF['dim'], 2) + coff[1] * pow(self._RF['dim'], 1) + coff[0] * pow(self._RF['dim'], 0))
            self._RF[ret1] = (poly * self._RF['dim']) % self._RF['range']
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqgfmul8x    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1):
            return False, PC
        else:
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, self._RF[r1]))
            coff = bit32(self._RF[r1])
            poly = (coff[31] * pow(self._RF['dim'], 31) + coff[30] * pow(self._RF['dim'], 30) + coff[29] * pow(self._RF['dim'], 29) + coff[28] * pow(self._RF['dim'], 28) + 
                    coff[27] * pow(self._RF['dim'], 27) + coff[26] * pow(self._RF['dim'], 26) + coff[25] * pow(self._RF['dim'], 25) + coff[24] * pow(self._RF['dim'], 24) + 
                    coff[23] * pow(self._RF['dim'], 23) + coff[22] * pow(self._RF['dim'], 22) + coff[21] * pow(self._RF['dim'], 21) + coff[20] * pow(self._RF['dim'], 20) + 
                    coff[19] * pow(self._RF['dim'], 19) + coff[18] * pow(self._RF['dim'], 18) + coff[17] * pow(self._RF['dim'], 17) + coff[16] * pow(self._RF['dim'], 16) + 
                    coff[15] * pow(self._RF['dim'], 15) + coff[14] * pow(self._RF['dim'], 14) + coff[13] * pow(self._RF['dim'], 13) + coff[12] * pow(self._RF['dim'], 12) + 
                    coff[11] * pow(self._RF['dim'], 11) + coff[10] * pow(self._RF['dim'], 10) + coff[9] * pow(self._RF['dim'], 9) + coff[8] * pow(self._RF['dim'], 8) + 
                    coff[7] * pow(self._RF['dim'], 7) + coff[6] * pow(self._RF['dim'], 6) + coff[5] * pow(self._RF['dim'], 5) + coff[4] * pow(self._RF['dim'], 4) + 
                    coff[3] * pow(self._RF['dim'], 3) + coff[2] * pow(self._RF['dim'], 2) + coff[1] * pow(self._RF['dim'], 1) + coff[0] * pow(self._RF['dim'], 0))
            self._RF[ret1] = (poly * pow(self._RF['dim'], 8)) % self._RF['range']
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1

    def _Execqgfmulb    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        s = Match.group(3)
        split = (re.match(r'(\w+)(\.(\w+))?', s))
        j = int(split.group(3), 10)
        rs = split.group(1)
        ret1, r1, r2 = Match.group(1), Match.group(2), rs
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            self._Log.write("Source Reg 1 : %s = %x  \nSource Reg 2 : %s = %x  \n"%(r1, self._RF[r1], r2, self._RF[r2]))
            coff = bit32(self._RF[r1])
            poly = (coff[31] * pow(self._RF['dim'], 31) + coff[30] * pow(self._RF['dim'], 30) + coff[29] * pow(self._RF['dim'], 29) + coff[28] * pow(self._RF['dim'], 28) + 
                    coff[27] * pow(self._RF['dim'], 27) + coff[26] * pow(self._RF['dim'], 26) + coff[25] * pow(self._RF['dim'], 25) + coff[24] * pow(self._RF['dim'], 24) + 
                    coff[23] * pow(self._RF['dim'], 23) + coff[22] * pow(self._RF['dim'], 22) + coff[21] * pow(self._RF['dim'], 21) + coff[20] * pow(self._RF['dim'], 20) + 
                    coff[19] * pow(self._RF['dim'], 19) + coff[18] * pow(self._RF['dim'], 18) + coff[17] * pow(self._RF['dim'], 17) + coff[16] * pow(self._RF['dim'], 16) + 
                    coff[15] * pow(self._RF['dim'], 15) + coff[14] * pow(self._RF['dim'], 14) + coff[13] * pow(self._RF['dim'], 13) + coff[12] * pow(self._RF['dim'], 12) + 
                    coff[11] * pow(self._RF['dim'], 11) + coff[10] * pow(self._RF['dim'], 10) + coff[9] * pow(self._RF['dim'], 9) + coff[8] * pow(self._RF['dim'], 8) + 
                    coff[7] * pow(self._RF['dim'], 7) + coff[6] * pow(self._RF['dim'], 6) + coff[5] * pow(self._RF['dim'], 5) + coff[4] * pow(self._RF['dim'], 4) + 
                    coff[3] * pow(self._RF['dim'], 3) + coff[2] * pow(self._RF['dim'], 2) + coff[1] * pow(self._RF['dim'], 1) + coff[0] * pow(self._RF['dim'], 0))
            s1, s2, s3, s4 = bit32_to_8(self._RF[r2])
            byte = s1 * (j == 1) + s2 * (j == 2) + s3 * (j == 3) + s4 * (j == 4)  
            self._RF[ret1] = (poly * byte) % self._RF['range']
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1
			
    def _Execqgfmulc    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1):
            return False, PC
        else:
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, self._RF[r1]))
            coff = bit32(self._RF[r1])
            poly = (coff[31] * pow(self._RF['dim'], 31) + coff[30] * pow(self._RF['dim'], 30) + coff[29] * pow(self._RF['dim'], 29) + coff[28] * pow(self._RF['dim'], 28) + 
                    coff[27] * pow(self._RF['dim'], 27) + coff[26] * pow(self._RF['dim'], 26) + coff[25] * pow(self._RF['dim'], 25) + coff[24] * pow(self._RF['dim'], 24) + 
                    coff[23] * pow(self._RF['dim'], 23) + coff[22] * pow(self._RF['dim'], 22) + coff[21] * pow(self._RF['dim'], 21) + coff[20] * pow(self._RF['dim'], 20) + 
                    coff[19] * pow(self._RF['dim'], 19) + coff[18] * pow(self._RF['dim'], 18) + coff[17] * pow(self._RF['dim'], 17) + coff[16] * pow(self._RF['dim'], 16) + 
                    coff[15] * pow(self._RF['dim'], 15) + coff[14] * pow(self._RF['dim'], 14) + coff[13] * pow(self._RF['dim'], 13) + coff[12] * pow(self._RF['dim'], 12) + 
                    coff[11] * pow(self._RF['dim'], 11) + coff[10] * pow(self._RF['dim'], 10) + coff[9] * pow(self._RF['dim'], 9) + coff[8] * pow(self._RF['dim'], 8) + 
                    coff[7] * pow(self._RF['dim'], 7) + coff[6] * pow(self._RF['dim'], 6) + coff[5] * pow(self._RF['dim'], 5) + coff[4] * pow(self._RF['dim'], 4) + 
                    coff[3] * pow(self._RF['dim'], 3) + coff[2] * pow(self._RF['dim'], 2) + coff[1] * pow(self._RF['dim'], 1) + coff[0] * pow(self._RF['dim'], 0))
            self._RF[ret1] = (poly * self._RF['C']) % self._RF['range']
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1

    def _Execqgf8_matc    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1):
            return False, PC
        else:
            self._Log.write("Source Reg 1 : %s = %x  \n"%(r1, self._RF[r1]))
            s1, s2, s3, s4 = bit32_to_8(self._RF[r1])
            s11, s12, s13, s14 = bit32_to_8(self._RF['mat1'])
            s21, s22, s23, s24 = bit32_to_8(self._RF['mat2'])
            s31, s32, s33, s34 = bit32_to_8(self._RF['mat3'])
            s41, s42, s43, s44 = bit32_to_8(self._RF['mat4']) 
            s21 = int((((bin(s11 * s1 + s12 * s2 + s13 * s3 + s14 * s4)[2:])[::-1])[0:8])[::-1], 2) 
            s22 = int((((bin(s21 * s1 + s22 * s2 + s23 * s3 + s24 * s4)[2:])[::-1])[0:8])[::-1], 2) 
            s23 = int((((bin(s31 * s1 + s32 * s2 + s33 * s3 + s34 * s4)[2:])[::-1])[0:8])[::-1], 2) 
            s24 = int((((bin(s41 * s1 + s42 * s2 + s43 * s3 + s44 * s4)[2:])[::-1])[0:8])[::-1], 2)
            self._RF[ret1] = (s21<<24)	+ (s22<<16) + (s23<<8) + s24		
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1		

    def _Execqgf8_mat    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2) or (code1<3):
            return False, PC
        else:
            s1 = (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)]
            self._Log.write("Source Reg 1 : %s = %x  \nRet 1 : %s = %x" % (r1, s1, ret1, self._RF[ret1]))
            s1, s2, s3, s4 = bit32_to_8(self._RF[r1])
            s11, s21, s31, s41 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 4)])
            s12, s22, s32, s42 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 3)])
            s13, s23, s33, s43 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 2)])
            s14, s24, s34, s44 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 1)])
            s21 = int((((bin(s11 * s1 + s12 * s2 + s13 * s3 + s14 * s4)[2:])[::-1])[0:8])[::-1], 2) 
            s22 = int((((bin(s21 * s1 + s22 * s2 + s23 * s3 + s24 * s4)[2:])[::-1])[0:8])[::-1], 2) 
            s23 = int((((bin(s31 * s1 + s32 * s2 + s33 * s3 + s34 * s4)[2:])[::-1])[0:8])[::-1], 2) 
            s24 = int((((bin(s41 * s1 + s42 * s2 + s43 * s3 + s44 * s4)[2:])[::-1])[0:8])[::-1], 2)
            self._RF[ret1] = (s21<<24)	+ (s22<<16) + (s23<<8) + s24		
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1

    def _Execqgf8_matcv    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or (code1<3) or (code3<3):
            return False, PC
        else:
            s1 = (self._RF[r1]<<96) + (self._RF[split1.group(1) + str(code1 - 1)]<<64) + (self._RF[split1.group(1) + str(code1 - 2)]<<32) + self._RF[split1.group(1) + str(code1 - 3)]
            d1 = (self._RF[ret1]<<96) + (self._RF[split3.group(1) + str(code1 - 1)]<<64) + (self._RF[split3.group(1) + str(code1 - 2)]<<32) + self._RF[split3.group(1) + str(code1 - 3)]
            self._Log.write("Source Reg 1 : %s = %x  \nRet 1 : %s = %x" % (r1, s1, ret1, d1))
            c11, c12, c13, c14 = bit32_to_8(self._RF['mat1'])
            c21, c22, c23, c24 = bit32_to_8(self._RF['mat2'])
            c31, c32, c33, c34 = bit32_to_8(self._RF['mat3'])
            c41, c42, c43, c44 = bit32_to_8(self._RF['mat4'])
            s11, s21, s31, s41 = bit32_to_8(self._RF[r1])
            s12, s22, s32, s42 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 1)])
            s13, s23, s33, s43 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 2)])
            s14, s24, s34, s44 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 3)])
            d11 = ex8(c11,s11, self._RF['gen_poly2_8']) ^ ex8(c12,s21, self._RF['gen_poly2_8']) ^ ex8(c13,s31, self._RF['gen_poly2_8']) ^ ex8(c14,s41, self._RF['gen_poly2_8'])
            d12 = ex8(c11,s12, self._RF['gen_poly2_8']) ^ ex8(c12,s22, self._RF['gen_poly2_8']) ^ ex8(c13,s32, self._RF['gen_poly2_8']) ^ ex8(c14,s42, self._RF['gen_poly2_8'])
            d13 = ex8(c11,s13, self._RF['gen_poly2_8']) ^ ex8(c12,s23, self._RF['gen_poly2_8']) ^ ex8(c13,s33, self._RF['gen_poly2_8']) ^ ex8(c14,s43, self._RF['gen_poly2_8'])
            d14 = ex8(c11,s14, self._RF['gen_poly2_8']) ^ ex8(c12,s24, self._RF['gen_poly2_8']) ^ ex8(c13,s34, self._RF['gen_poly2_8']) ^ ex8(c14,s44, self._RF['gen_poly2_8'])
            d21 = ex8(c21,s11, self._RF['gen_poly2_8']) ^ ex8(c22,s21, self._RF['gen_poly2_8']) ^ ex8(c23,s31, self._RF['gen_poly2_8']) ^ ex8(c24,s41, self._RF['gen_poly2_8'])
            d22 = ex8(c21,s12, self._RF['gen_poly2_8']) ^ ex8(c22,s22, self._RF['gen_poly2_8']) ^ ex8(c23,s32, self._RF['gen_poly2_8']) ^ ex8(c24,s42, self._RF['gen_poly2_8'])
            d23 = ex8(c21,s13, self._RF['gen_poly2_8']) ^ ex8(c22,s23, self._RF['gen_poly2_8']) ^ ex8(c23,s33, self._RF['gen_poly2_8']) ^ ex8(c24,s43, self._RF['gen_poly2_8'])
            d24 = ex8(c21,s14, self._RF['gen_poly2_8']) ^ ex8(c22,s24, self._RF['gen_poly2_8']) ^ ex8(c23,s34, self._RF['gen_poly2_8']) ^ ex8(c24,s44, self._RF['gen_poly2_8'])
            d31 = ex8(c31,s11, self._RF['gen_poly2_8']) ^ ex8(c32,s21, self._RF['gen_poly2_8']) ^ ex8(c33,s31, self._RF['gen_poly2_8']) ^ ex8(c34,s41, self._RF['gen_poly2_8'])
            d32 = ex8(c31,s12, self._RF['gen_poly2_8']) ^ ex8(c32,s22, self._RF['gen_poly2_8']) ^ ex8(c33,s32, self._RF['gen_poly2_8']) ^ ex8(c34,s42, self._RF['gen_poly2_8'])
            d33 = ex8(c31,s13, self._RF['gen_poly2_8']) ^ ex8(c32,s23, self._RF['gen_poly2_8']) ^ ex8(c33,s33, self._RF['gen_poly2_8']) ^ ex8(c34,s43, self._RF['gen_poly2_8'])
            d34 = ex8(c31,s14, self._RF['gen_poly2_8']) ^ ex8(c32,s24, self._RF['gen_poly2_8']) ^ ex8(c33,s34, self._RF['gen_poly2_8']) ^ ex8(c34,s44, self._RF['gen_poly2_8'])
            d41 = ex8(c41,s11, self._RF['gen_poly2_8']) ^ ex8(c42,s21, self._RF['gen_poly2_8']) ^ ex8(c43,s31, self._RF['gen_poly2_8']) ^ ex8(c44,s41, self._RF['gen_poly2_8'])
            d42 = ex8(c41,s12, self._RF['gen_poly2_8']) ^ ex8(c42,s22, self._RF['gen_poly2_8']) ^ ex8(c43,s32, self._RF['gen_poly2_8']) ^ ex8(c44,s42, self._RF['gen_poly2_8'])
            d43 = ex8(c41,s13, self._RF['gen_poly2_8']) ^ ex8(c42,s23, self._RF['gen_poly2_8']) ^ ex8(c43,s33, self._RF['gen_poly2_8']) ^ ex8(c44,s43, self._RF['gen_poly2_8'])
            d44 = ex8(c41,s14, self._RF['gen_poly2_8']) ^ ex8(c42,s24, self._RF['gen_poly2_8']) ^ ex8(c43,s34, self._RF['gen_poly2_8']) ^ ex8(c44,s44, self._RF['gen_poly2_8'])
            s1 = (d11<<24)	+ (d21<<16) + (d31<<8) + d41		
            s2 = (d12<<24)	+ (d22<<16) + (d32<<8) + d42		
            s3 = (d13<<24)	+ (d23<<16) + (d33<<8) + d43		
            s4 = (d14<<24)	+ (d24<<16) + (d34<<8) + d44
            result = (s1<<96) + (s2<<64) + (s3<<32) + s4
            self._RF[ret1], self._RF[split3.group(1) + str(code3-1)], self._RF[split3.group(1) + str(code3-2)], self._RF[split3.group(1) + str(code3-3)] = bit128_to_32((s1<<96) + (s2<<64) + (s3<<32) + s4)			
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, result))
            return True, PC+1

    def _Execqgf8_matv    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1 = Match.group(1), Match.group(2)
        split1 = re.match(r'(\w+)(\w+)(\w+)?', r1)
        split3 = re.match(r'(\w+)(\w+)(\w+)?', ret1)
        code1 = int(split1.group(2), 10) 
        code3 = int(split3.group(2), 10) 
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or (code1<7) or (code3<3):
            return False, PC
        else:
            s1 = ((self._RF[r1]<<224) + (self._RF[split1.group(1) + str(code1 - 1)]<<192) + (self._RF[split1.group(1) + str(code1 - 2)]<<160) + 
			(self._RF[split1.group(1) + str(code1 - 3)]<<128) + (self._RF[split1.group(1) + str(code1 - 4)]<<96) + (self._RF[split1.group(1) + str(code1 - 5)]<<64) +
			(self._RF[split1.group(1) + str(code1 - 6)]<<32) + (self._RF[split1.group(1) + str(code1 - 7)]))
            d1 = (self._RF[ret1]<<96) + (self._RF[split3.group(1) + str(code1 - 1)]<<64) + (self._RF[split3.group(1) + str(code1 - 2)]<<32) + self._RF[split3.group(1) + str(code1 - 3)]
            self._Log.write("Source Reg 1 : %s = %x  \nRet 1 : %s = %x" % (r1, s1, ret1, d1))
            c11, c21, c31, c41 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 3)])
            c12, c22, c32, c42 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 2)])
            c13, c23, c33, c43 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 1)])
            c14, c24, c34, c44 = bit32_to_8(self._RF[r1])
            s11, s21, s31, s41 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 7)])
            s12, s22, s32, s42 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 6)])
            s13, s23, s33, s43 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 5)])
            s14, s24, s34, s44 = bit32_to_8(self._RF[split1.group(1) + str(code1 - 4)])
            d11 = ex8(c11,s11, self._RF['gen_poly2_8']) ^ ex8(c12,s21, self._RF['gen_poly2_8']) ^ ex8(c13,s31, self._RF['gen_poly2_8']) ^ ex8(c14,s41, self._RF['gen_poly2_8'])
            d12 = ex8(c11,s12, self._RF['gen_poly2_8']) ^ ex8(c12,s22, self._RF['gen_poly2_8']) ^ ex8(c13,s32, self._RF['gen_poly2_8']) ^ ex8(c14,s42, self._RF['gen_poly2_8'])
            d13 = ex8(c11,s13, self._RF['gen_poly2_8']) ^ ex8(c12,s23, self._RF['gen_poly2_8']) ^ ex8(c13,s33, self._RF['gen_poly2_8']) ^ ex8(c14,s43, self._RF['gen_poly2_8'])
            d14 = ex8(c11,s14, self._RF['gen_poly2_8']) ^ ex8(c12,s24, self._RF['gen_poly2_8']) ^ ex8(c13,s34, self._RF['gen_poly2_8']) ^ ex8(c14,s44, self._RF['gen_poly2_8'])
            d21 = ex8(c21,s11, self._RF['gen_poly2_8']) ^ ex8(c22,s21, self._RF['gen_poly2_8']) ^ ex8(c23,s31, self._RF['gen_poly2_8']) ^ ex8(c24,s41, self._RF['gen_poly2_8'])
            d22 = ex8(c21,s12, self._RF['gen_poly2_8']) ^ ex8(c22,s22, self._RF['gen_poly2_8']) ^ ex8(c23,s32, self._RF['gen_poly2_8']) ^ ex8(c24,s42, self._RF['gen_poly2_8'])
            d23 = ex8(c21,s13, self._RF['gen_poly2_8']) ^ ex8(c22,s23, self._RF['gen_poly2_8']) ^ ex8(c23,s33, self._RF['gen_poly2_8']) ^ ex8(c24,s43, self._RF['gen_poly2_8'])
            d24 = ex8(c21,s14, self._RF['gen_poly2_8']) ^ ex8(c22,s24, self._RF['gen_poly2_8']) ^ ex8(c23,s34, self._RF['gen_poly2_8']) ^ ex8(c24,s44, self._RF['gen_poly2_8'])
            d31 = ex8(c31,s11, self._RF['gen_poly2_8']) ^ ex8(c32,s21, self._RF['gen_poly2_8']) ^ ex8(c33,s31, self._RF['gen_poly2_8']) ^ ex8(c34,s41, self._RF['gen_poly2_8'])
            d32 = ex8(c31,s12, self._RF['gen_poly2_8']) ^ ex8(c32,s22, self._RF['gen_poly2_8']) ^ ex8(c33,s32, self._RF['gen_poly2_8']) ^ ex8(c34,s42, self._RF['gen_poly2_8'])
            d33 = ex8(c31,s13, self._RF['gen_poly2_8']) ^ ex8(c32,s23, self._RF['gen_poly2_8']) ^ ex8(c33,s33, self._RF['gen_poly2_8']) ^ ex8(c34,s43, self._RF['gen_poly2_8'])
            d34 = ex8(c31,s14, self._RF['gen_poly2_8']) ^ ex8(c32,s24, self._RF['gen_poly2_8']) ^ ex8(c33,s34, self._RF['gen_poly2_8']) ^ ex8(c34,s44, self._RF['gen_poly2_8'])
            d41 = ex8(c41,s11, self._RF['gen_poly2_8']) ^ ex8(c42,s21, self._RF['gen_poly2_8']) ^ ex8(c43,s31, self._RF['gen_poly2_8']) ^ ex8(c44,s41, self._RF['gen_poly2_8'])
            d42 = ex8(c41,s12, self._RF['gen_poly2_8']) ^ ex8(c42,s22, self._RF['gen_poly2_8']) ^ ex8(c43,s32, self._RF['gen_poly2_8']) ^ ex8(c44,s42, self._RF['gen_poly2_8'])
            d43 = ex8(c41,s13, self._RF['gen_poly2_8']) ^ ex8(c42,s23, self._RF['gen_poly2_8']) ^ ex8(c43,s33, self._RF['gen_poly2_8']) ^ ex8(c44,s43, self._RF['gen_poly2_8'])
            d44 = ex8(c41,s14, self._RF['gen_poly2_8']) ^ ex8(c42,s24, self._RF['gen_poly2_8']) ^ ex8(c43,s34, self._RF['gen_poly2_8']) ^ ex8(c44,s44, self._RF['gen_poly2_8'])      			
            s1 = (d11<<24)	+ (d21<<16) + (d31<<8) + d41		
            s2 = (d12<<24)	+ (d22<<16) + (d32<<8) + d42		
            s3 = (d13<<24)	+ (d23<<16) + (d33<<8) + d43		
            s4 = (d14<<24)	+ (d24<<16) + (d34<<8) + d44
            result = (s1<<96) + (s2<<64) + (s3<<32) + s4
            self._RF[ret1], self._RF[split3.group(1) + str(code3-1)], self._RF[split3.group(1) + str(code3-2)], self._RF[split3.group(1) + str(code3-3)] = bit128_to_32((s4<<96) + (s3<<64) + (s2<<32) + s1)			
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, result))
            return True, PC+1

    def _Execqbfmul32l    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            self._Log.write("Source Reg 1 : %s = %x  \nReg 2 : %s = %x  \n"%(r1, self._RF[r1], r2, self._RF[r2]))
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            result = s1 * s2
            d1, d2 = bit64_to_32(result)
            self._RF[ret1] = d2		
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1			
			
    def _Execqbfmul32h    (self, Asm="", PC=None):
        # Instruction Behaviour
        Match = self._InstrSet.Match(Asm)
        ret1, r1, r2 = Match.group(1), Match.group(2), Match.group(3)
        if self._RF.IsLocked(ret1) or self._RF.IsLocked(r1) or self._RF.IsLocked(r2):
            return False, PC
        else:
            self._Log.write("Source Reg 1 : %s = %x  \nReg 2 : %s = %x  \n"%(r1, self._RF[r1], r2, self._RF[r2]))
            s1 = self._RF[r1]
            s2 = self._RF[r2]
            result = s1 * s2
            d1, d2 = bit64_to_32(result)
            self._RF[ret1] = d1		
            # Information to be reported
            Matched, Instr = self._InstrSet.MatchedOnce(Asm)
            self.IncreaseIC(Instr)
            self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
            self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
            self._Log.write("Result : %s = %x \n"%(ret1, self._RF[ret1]))
            return True, PC+1

    def _Execqslfsr128(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, shift = Match.group(1), int(Match.group(2))
        ret = r0
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        for i in range(0, shift):
            bit = (self._RF[r0] >> 127) & 1
            for j in range(0,127):
                if ((self._RF["lfsr_xor"] >> j) & 1) == 1:
                    bit = bit ^ ((self._RF[r0] >> j) & 1)
            bit = bit ^ ((self._RF["rs"] >> i) & 1)
            self._RF[ret] = ((self._RF[r0] & ~(1 << 127)) << 1) | bit
			
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqslfsr256(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, shift = Match.group(1), int(Match.group(2))
        ret = r0
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        for i in range(0, shift):
            bit = (self._RF[r0] >> 255) & 1
            for j in range(0,255):
                if ((self._RF["lfsr_xor"] >> j) & 1) == 1:
                    bit = bit ^ ((self._RF[r0] >> j) & 1)
            bit = bit ^ ((self._RF["rs"] >> i) & 1)
            self._RF[ret] = ((self._RF[r0] & ~(1 << 255)) << 1) | bit
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqslfsr512(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, r1, shift = Match.group(1), Match.group(2), int(Match.group(3))
        ret0 = r0
        ret1 = r1
        s = (self._RF[r0]<<256) + self._RF[r1]
        self._Log.write("Source Reg 0 : %s = 0x%x \n Reg 1 : %s = %x \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        for i in range(0, shift):
            bit = (s >> 511) & 1
            for j in range(0,511):
                if ((self._RF["lfsr_xor"] >> j) & 1) == 1:
                    bit = (bit ^ (s >> j) & 1)
            bit = bit ^ ((self._RF["rs"] >> i) & 1)
            self._RF[ret0] = (((s & ~(1 << 511)) << 1) | bit)>>256
            self._RF[ret1] = (((s & ~(1 << 511)) << 1) | bit) & (pow(2, 256) - 1)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result0 : %s = 0x%x \n Result1 : %s = %x \n" % (ret0, self._RF[ret0], ret1, self._RF[ret1]))
        return True, PC + 1

    def _Execqdlfsr128(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, shift = Match.group(1), int(Match.group(2))
        ret = r0
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        for i in range(0, shift):
            if ((self._RF[r0] >> 127) & 1) == 1:
                tmp = ((self._RF[r0] ^ self._RF["lfsr_xor"]) & ~(1 << 127)) << 1
                self._RF[ret] = tmp | (((self._RF["rs"] >> i) & 1) ^ 1)
            else:
                self._RF[ret] = ((self._RF[r0] & ~(1 << 127)) << 1) | ((self._RF["rs"] >> i) & 1)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqdlfsr256(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, shift = Match.group(1), int(Match.group(2))
        ret = r0
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        for i in range(0, shift):
            if ((self._RF[r0] >> 255) & 1) == 1:
                tmp = ((self._RF[r0] ^ self._RF["lfsr_xor"]) & ~(1 << 255)) << 1
                self._RF[ret] = tmp | (((self._RF["rs"] >> i) & 1) ^ 1)
            else:
                self._RF[ret] = ((self._RF[r0] & ~(1 << 255)) << 1) | ((self._RF["rs"] >> i) & 1)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqdlfsr512(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, r1, shift = Match.group(1), Match.group(2), int(Match.group(3))
        ret0 = r0
        ret1 = r1
        s = (self._RF[r0]<<256) + self._RF[r1]
        self._Log.write("Source Reg 0 : %s = 0x%x \n Reg 1 : %s = %x \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        for i in range(0, shift):
            if ((s >> 511) & 1) == 1:
                tmp = ((s ^ self._RF["lfsr_xor"]) & ~(1 << 511)) << 1
                self._RF[ret0] = (tmp | (((self._RF["rs"] >> i) & 1) ^ 1))>>256
                self._RF[ret1] = (tmp | (((self._RF["rs"] >> i) & 1) ^ 1)) & (pow(2, 256) - 1)
            else:
                self._RF[ret0] = (((s & ~(1 << 511)) << 1) | ((self._RF["rs"] >> i) & 1))>>256
                self._RF[ret1] = (((s & ~(1 << 511)) << 1) | ((self._RF["rs"] >> i) & 1)) & (pow(2, 256) - 1)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result 0 : %s = 0x%x \n Result 1 : %s = %x \n" % (ret0, self._RF[ret0], ret1, self._RF[ret1]))
        return True, PC + 1
    # may not correct
    # first and, second xor.
    # fibonacci arch

    def _Execqnlfsr128(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, shift = Match.group(1), int(Match.group(2))
        ret = r0
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        for i in range(0, shift):
            bit = (self._RF[r0] >> 127) & 1
            for j in range(0,127):
                if ((self._RF["lfsr_and"] >> j) & 1) == 1:
                    bit = bit & ((self._RF[r0] >> j) & 1)
                if ((self._RF["lfsr_xor"] >> j) & 1) == 1:
                    bit = bit ^ ((self._RF[r0] >> j) & 1)
            bit = bit ^ ((self._RF["rs"] >> i) & 1)
            self._RF[ret] = ((self._RF[r0] & ~(1 << 127)) << 1) | bit
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqnlfsr256(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, shift = Match.group(1), int(Match.group(2))
        ret = r0
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        for i in range(0, shift):
            bit = (self._RF[r0] >> 255) & 1
            for j in range(0,255):
                if ((self._RF["lfsr_and"] >> j) & 1) == 1:
                    bit = bit & ((self._RF[r0] >> j) & 1)
                if ((self._RF["lfsr_xor"] >> j) & 1) == 1:
                    bit = bit ^ ((self._RF[r0] >> j) & 1)
            bit = bit ^ ((self._RF["rs"] >> i) & 1)
            self._RF[ret] = ((self._RF[r0] & ~(1 << 255)) << 1) | bit
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqnlfsr512(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, r1, shift = Match.group(1), Match.group(2), int(Match.group(3))
        ret0 = r0
        ret1 = r1
        s = (self._RF[r0]<<256) + self._RF[r1]
        self._Log.write("Source Reg 0 : %s = 0x%x \n Reg 1 : %s = %x \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        for i in range(0, shift):
            bit = (s >> 511) & 1
            for j in range(0,511):
                if ((self._RF["lfsr_and"] >> j) & 1) == 1:
                    bit = bit & ((s >> j) & 1)
                if ((self._RF["lfsr_xor"] >> j) & 1) == 1:
                    bit = bit ^ ((s >> j) & 1)
            bit = bit ^ ((self._RF["rs"] >> i) & 1)
            self._RF[ret0] = (((s & ~(1 << 511)) << 1) | bit)>>256
            self._RF[ret1] = (((s & ~(1 << 511)) << 1) | bit) & (pow(2, 256) - 1)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result 0 : %s = 0x%x \n Result 1 : %s = %x" % (ret0, self._RF[ret0], ret1, self._RF[ret1]))
        return True, PC + 1

    def _Execqsfcsr128(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, shift = Match.group(1), int(Match.group(2))
        ret = r0
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        for i in range(0, shift):
            bit = self._RF["m"]
            for j in range(0,128):
                if ((self._RF["fcsr"] >> j) & 1) == 1:
                    bit = bit + ((self._RF[r0] >> j) & 1)
            self._RF["m"] = bit // 2
            bit = (bit % 2) ^ ((self._RF["rs"] >> i) & 1)
            self._RF[ret] = ((self._RF[r0] & ~(1 << 127)) << 1) | bit
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqsfcsr256(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, shift = Match.group(1), int(Match.group(2))
        ret = r0
        self._Log.write("Source Reg 0 : %s = 0x%x \n" % (r0, self._RF[r0]))
        for i in range(0, shift):
            bit = self._RF["m"]
            for j in range(0,256):
                if ((self._RF["fcsr"] >> j) & 1) == 1:
                    bit = bit + ((self._RF[r0] >> j) & 1)
            self._RF["m"] = bit // 2
            bit = (bit % 2) ^ ((self._RF["rs"] >> i) & 1)
            self._RF[ret] = ((self._RF[r0] & ~(1 << 255)) << 1) | bit
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result : %s = 0x%x \n" % (ret, self._RF[ret]))
        return True, PC + 1

    def _Execqsfcsr512(self, Asm="", PC=None):
        Match = self._InstrSet.Match(Asm)
        r0, r1, shift = Match.group(1), Match.group(2), int(Match.group(3))
        ret0 = r0
        ret1 = r1
        s = (self._RF[r0]<<256) + self._RF[r1]
        self._Log.write("Source Reg 0 : %s = 0x%x \n Reg 1 : %s = %x \n" % (r0, self._RF[r0], r1, self._RF[r1]))
        for i in range(0, shift):
            bit = self._RF["m"]
            for j in range(0, 512):
                if ((self._RF["fcsr"] >> j) & 1) == 1:
                    bit = bit + ((s >> j) & 1)
            self._RF["m"] = bit // 2
            bit = (bit % 2) ^ ((self._RF["rs"] >> i) & 1)
            self._RF[ret0] = (((s & ~(1 << 511)) << 1) | bit)>>256
            self._RF[ret1] = (((s & ~(1 << 511)) << 1) | bit) & (pow(2, 256) - 1)
        # Information to be reported
        Matched, Instr = self._InstrSet.MatchedOnce(Asm)
        self.IncreaseIC(Instr)
        self.IncreaseCycles(Instr, "Serial", self._InstrSet.GetCycles(Instr))
        self.IncreaseCycles(Instr, "Parallel", self._InstrSet.GetCycles(Instr))
        self._Log.write("Result 0 : %s = 0x%x \n Result 1 : %s = %x \n" % (ret0, self._RF[ret0], ret1, self._RF[ret1]))
        return True, PC + 1			
			
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
        # Special purpose wide registers.  Width : 320 bits
        # Assuming the initialized value is 0, be careful
        SWR = { "swr0" : {"Value" : 0, "Locked" : False},
                "swr1" : {"Value" : 0, "Locked" : False},
                "swr2" : {"Value" : 0, "Locked" : False},
                "swr3" : {"Value" : 0, "Locked" : False},
                "swr4" : {"Value" : 0, "Locked" : False},
                }
				
        CSR = {"CY" : {"Value": 0, "Locked": False},
               "k" : {"Value": 0, "Locked": False},
               "v" : {"Value": 0, "Locked": False},
               "C" : {"Value": 8, "Locked": False},
               "Pi" : {"Value": 0, "Locked": False},
               "dim" : {"Value": 2, "Locked": False},
               "mat1" : {"Value": 0x02030101, "Locked": False},
               "mat2" : {"Value": 0x01020301, "Locked": False},
               "mat3" : {"Value": 0x01010203, "Locked": False},
               "mat4" : {"Value": 0x03010102, "Locked": False},
               "inv"  : {"Value": 17, "Locked": False},
               "range": {"Value": 200, "Locked": False},
               "perm"          : {"Value" : 0x443, "Locked" : False},  # 123
               "gen_poly2_8"   : {"Value" : 0x1b, "Locked" : False},   # same to AES
               "gen_poly2_8_2" : {"Value" : 0b01, "Locked": False},    # x^2 + 1
               "gen_poly2_8_3" : {"Value": 0b001, "Locked": False},  # x^3 + 1
               "gen_poly2_8_4": {"Value": 0b0001, "Locked": False},  # x^4 + 1
               "lfsr_xor": {"Value": 0b101, "Locked": False},
               "lfsr_and": {"Value": 0b010, "Locked": False},
               "fcsr": {"Value": 0b101, "Locked": False},
               "m": {"Value": 0b011, "Locked": False},
               "rs": {"Value": 0b101, "Locked": False},
        }

		# Vector registers. Width : 8 * 32 = 256 bits. The total sum is 32.
		# Assuming the initialized value is 0, be careful
        V0 ={
		        "V0_e0" : {"Value" : 0, "Locked" : False},
                "V0_e1" : {"Value" : 0, "Locked" : False},
                "V0_e2" : {"Value" : 0, "Locked" : False},
                "V0_e3" : {"Value" : 0, "Locked" : False},
                "V0_e4" : {"Value" : 0, "Locked" : False},
                "V0_e5" : {"Value" : 0, "Locked" : False},
                "V0_e6" : {"Value" : 0, "Locked" : False},
                "V0_e7" : {"Value" : 0, "Locked" : False},}
        V1 ={
                "V1_e0" : {"Value" : 0, "Locked" : False},
                "V1_e1" : {"Value" : 0, "Locked" : False},
                "V1_e2" : {"Value" : 0, "Locked" : False},
                "V1_e3" : {"Value" : 0, "Locked" : False},
                "V1_e4" : {"Value" : 0, "Locked" : False},
                "V1_e5" : {"Value" : 0, "Locked" : False},
                "V1_e6" : {"Value" : 0, "Locked" : False},
                "V1_e7" : {"Value" : 0, "Locked" : False},}
        V2 ={   
                "V2_e0" : {"Value" : 0, "Locked" : False},
                "V2_e1" : {"Value" : 0, "Locked" : False},
                "V2_e2" : {"Value" : 0, "Locked" : False},
                "V2_e3" : {"Value" : 0, "Locked" : False},
                "V2_e4" : {"Value" : 0, "Locked" : False},
                "V2_e5" : {"Value" : 0, "Locked" : False},
                "V2_e6" : {"Value" : 0, "Locked" : False},
                "V2_e7" : {"Value" : 0, "Locked" : False},}
        V3 ={
                "V3_e0" : {"Value" : 0, "Locked" : False},
                "V3_e1" : {"Value" : 0, "Locked" : False},
                "V3_e2" : {"Value" : 0, "Locked" : False},
                "V3_e3" : {"Value" : 0, "Locked" : False},
                "V3_e4" : {"Value" : 0, "Locked" : False},
                "V3_e5" : {"Value" : 0, "Locked" : False},
                "V3_e6" : {"Value" : 0, "Locked" : False},
                "V3_e7" : {"Value" : 0, "Locked" : False},}
        V4 ={
                "V4_e0" : {"Value" : 0, "Locked" : False},
                "V4_e1" : {"Value" : 0, "Locked" : False},
                "V4_e2" : {"Value" : 0, "Locked" : False},
                "V4_e3" : {"Value" : 0, "Locked" : False},
                "V4_e4" : {"Value" : 0, "Locked" : False},
                "V4_e5" : {"Value" : 0, "Locked" : False},
                "V4_e6" : {"Value" : 0, "Locked" : False},
                "V4_e7" : {"Value" : 0, "Locked" : False},}
        V5 ={
                "V5_e0" : {"Value" : 0, "Locked" : False},
                "V5_e1" : {"Value" : 0, "Locked" : False},
                "V5_e2" : {"Value" : 0, "Locked" : False},
                "V5_e3" : {"Value" : 0, "Locked" : False},
                "V5_e4" : {"Value" : 0, "Locked" : False},
                "V5_e5" : {"Value" : 0, "Locked" : False},
                "V5_e6" : {"Value" : 0, "Locked" : False},
                "V5_e7" : {"Value" : 0, "Locked" : False},}
        V6 ={
                "V6_e0" : {"Value" : 0, "Locked" : False},
                "V6_e1" : {"Value" : 0, "Locked" : False},
                "V6_e2" : {"Value" : 0, "Locked" : False},
                "V6_e3" : {"Value" : 0, "Locked" : False},
                "V6_e4" : {"Value" : 0, "Locked" : False},
                "V6_e5" : {"Value" : 0, "Locked" : False},
                "V6_e6" : {"Value" : 0, "Locked" : False},
                "V6_e7" : {"Value" : 0, "Locked" : False},}
        V7 ={
                "V7_e0" : {"Value" : 0, "Locked" : False},
                "V7_e1" : {"Value" : 0, "Locked" : False},
                "V7_e2" : {"Value" : 0, "Locked" : False},
                "V7_e3" : {"Value" : 0, "Locked" : False},
                "V7_e4" : {"Value" : 0, "Locked" : False},
                "V7_e5" : {"Value" : 0, "Locked" : False},
                "V7_e6" : {"Value" : 0, "Locked" : False},
                "V7_e7" : {"Value" : 0, "Locked" : False},}
        V8 ={
                "V8_e0" : {"Value" : 0, "Locked" : False},
                "V8_e1" : {"Value" : 0, "Locked" : False},
                "V8_e2" : {"Value" : 0, "Locked" : False},
                "V8_e3" : {"Value" : 0, "Locked" : False},
                "V8_e4" : {"Value" : 0, "Locked" : False},
                "V8_e5" : {"Value" : 0, "Locked" : False},
                "V8_e6" : {"Value" : 0, "Locked" : False},
                "V8_e7" : {"Value" : 0, "Locked" : False},}
        V9 ={
                "V9_e0" : {"Value" : 0, "Locked" : False},
                "V9_e1" : {"Value" : 0, "Locked" : False},
                "V9_e2" : {"Value" : 0, "Locked" : False},
                "V9_e3" : {"Value" : 0, "Locked" : False},
                "V9_e4" : {"Value" : 0, "Locked" : False},
                "V9_e5" : {"Value" : 0, "Locked" : False},
                "V9_e6" : {"Value" : 0, "Locked" : False},
                "V9_e7" : {"Value" : 0, "Locked" : False},}
        V10 ={
                "V10_e0" : {"Value" : 0, "Locked" : False},
                "V10_e1" : {"Value" : 0, "Locked" : False},
                "V10_e2" : {"Value" : 0, "Locked" : False},
                "V10_e3" : {"Value" : 0, "Locked" : False},
                "V10_e4" : {"Value" : 0, "Locked" : False},
                "V10_e5" : {"Value" : 0, "Locked" : False},
                "V10_e6" : {"Value" : 0, "Locked" : False},
                "V10_e7" : {"Value" : 0, "Locked" : False},}
        V11 ={
                "V11_e0" : {"Value" : 0, "Locked" : False},
                "V11_e1" : {"Value" : 0, "Locked" : False},
                "V11_e2" : {"Value" : 0, "Locked" : False},
                "V11_e3" : {"Value" : 0, "Locked" : False},
                "V11_e4" : {"Value" : 0, "Locked" : False},
                "V11_e5" : {"Value" : 0, "Locked" : False},
                "V11_e6" : {"Value" : 0, "Locked" : False},
                "V11_e7" : {"Value" : 0, "Locked" : False},}
        V12 ={  
                "V12_e0" : {"Value" : 0, "Locked" : False},
                "V12_e1" : {"Value" : 0, "Locked" : False},
                "V12_e2" : {"Value" : 0, "Locked" : False},
                "V12_e3" : {"Value" : 0, "Locked" : False},
                "V12_e4" : {"Value" : 0, "Locked" : False},
                "V12_e5" : {"Value" : 0, "Locked" : False},
                "V12_e6" : {"Value" : 0, "Locked" : False},
                "V12_e7" : {"Value" : 0, "Locked" : False},}
        V13 ={
                "V13_e0" : {"Value" : 0, "Locked" : False},
                "V13_e1" : {"Value" : 0, "Locked" : False},
                "V13_e2" : {"Value" : 0, "Locked" : False},
                "V13_e3" : {"Value" : 0, "Locked" : False},
                "V13_e4" : {"Value" : 0, "Locked" : False},
                "V13_e5" : {"Value" : 0, "Locked" : False},
                "V13_e6" : {"Value" : 0, "Locked" : False},
                "V13_e7" : {"Value" : 0, "Locked" : False},}
        V14 ={
                "V14_e0" : {"Value" : 0, "Locked" : False},
                "V14_e1" : {"Value" : 0, "Locked" : False},
                "V14_e2" : {"Value" : 0, "Locked" : False},
                "V14_e3" : {"Value" : 0, "Locked" : False},
                "V14_e4" : {"Value" : 0, "Locked" : False},
                "V14_e5" : {"Value" : 0, "Locked" : False},
                "V14_e6" : {"Value" : 0, "Locked" : False},
                "V14_e7" : {"Value" : 0, "Locked" : False},}
        V15 ={
                "V15_e0" : {"Value" : 0, "Locked" : False},
                "V15_e1" : {"Value" : 0, "Locked" : False},
                "V15_e2" : {"Value" : 0, "Locked" : False},
                "V15_e3" : {"Value" : 0, "Locked" : False},
                "V15_e4" : {"Value" : 0, "Locked" : False},
                "V15_e5" : {"Value" : 0, "Locked" : False},
                "V15_e6" : {"Value" : 0, "Locked" : False},
                "V15_e7" : {"Value" : 0, "Locked" : False},}
        V16 ={
                "V16_e0" : {"Value" : 0, "Locked" : False},
                "V16_e1" : {"Value" : 0, "Locked" : False},
                "V16_e2" : {"Value" : 0, "Locked" : False},
                "V16_e3" : {"Value" : 0, "Locked" : False},
                "V16_e4" : {"Value" : 0, "Locked" : False},
                "V16_e5" : {"Value" : 0, "Locked" : False},
                "V16_e6" : {"Value" : 0, "Locked" : False},
                "V16_e7" : {"Value" : 0, "Locked" : False},}
        V17 ={
                "V17_e0" : {"Value" : 0, "Locked" : False},
                "V17_e1" : {"Value" : 0, "Locked" : False},
                "V17_e2" : {"Value" : 0, "Locked" : False},
                "V17_e3" : {"Value" : 0, "Locked" : False},
                "V17_e4" : {"Value" : 0, "Locked" : False},
                "V17_e5" : {"Value" : 0, "Locked" : False},
                "V17_e6" : {"Value" : 0, "Locked" : False},
                "V17_e7" : {"Value" : 0, "Locked" : False},}
        V18 ={
                "V18_e0" : {"Value" : 0, "Locked" : False},
                "V18_e1" : {"Value" : 0, "Locked" : False},
                "V18_e2" : {"Value" : 0, "Locked" : False},
                "V18_e3" : {"Value" : 0, "Locked" : False},
                "V18_e4" : {"Value" : 0, "Locked" : False},
                "V18_e5" : {"Value" : 0, "Locked" : False},
                "V18_e6" : {"Value" : 0, "Locked" : False},
                "V18_e7" : {"Value" : 0, "Locked" : False},}
        V19 ={
                "V19_e0" : {"Value" : 0, "Locked" : False},
                "V19_e1" : {"Value" : 0, "Locked" : False},
                "V19_e2" : {"Value" : 0, "Locked" : False},
                "V19_e3" : {"Value" : 0, "Locked" : False},
                "V19_e4" : {"Value" : 0, "Locked" : False},
                "V19_e5" : {"Value" : 0, "Locked" : False},
                "V19_e6" : {"Value" : 0, "Locked" : False},
                "V19_e7" : {"Value" : 0, "Locked" : False},}
        V20 ={
                "V20_e0" : {"Value" : 0, "Locked" : False},
                "V20_e1" : {"Value" : 0, "Locked" : False},
                "V20_e2" : {"Value" : 0, "Locked" : False},
                "V20_e3" : {"Value" : 0, "Locked" : False},
                "V20_e4" : {"Value" : 0, "Locked" : False},
                "V20_e5" : {"Value" : 0, "Locked" : False},
                "V20_e6" : {"Value" : 0, "Locked" : False},
                "V20_e7" : {"Value" : 0, "Locked" : False},}
        V21 ={
                "V21_e0" : {"Value" : 0, "Locked" : False},
                "V21_e1" : {"Value" : 0, "Locked" : False},
                "V21_e2" : {"Value" : 0, "Locked" : False},
                "V21_e3" : {"Value" : 0, "Locked" : False},
                "V21_e4" : {"Value" : 0, "Locked" : False},
                "V21_e5" : {"Value" : 0, "Locked" : False},
                "V21_e6" : {"Value" : 0, "Locked" : False},
                "V21_e7" : {"Value" : 0, "Locked" : False},}
        V22 ={
                "V22_e0" : {"Value" : 0, "Locked" : False},
                "V22_e1" : {"Value" : 0, "Locked" : False},
                "V22_e2" : {"Value" : 0, "Locked" : False},
                "V22_e3" : {"Value" : 0, "Locked" : False},
                "V22_e4" : {"Value" : 0, "Locked" : False},
                "V22_e5" : {"Value" : 0, "Locked" : False},
                "V22_e6" : {"Value" : 0, "Locked" : False},
                "V22_e7" : {"Value" : 0, "Locked" : False},}
        V23 ={
                "V23_e0" : {"Value" : 0, "Locked" : False},
                "V23_e1" : {"Value" : 0, "Locked" : False},
                "V23_e2" : {"Value" : 0, "Locked" : False},
                "V23_e3" : {"Value" : 0, "Locked" : False},
                "V23_e4" : {"Value" : 0, "Locked" : False},
                "V23_e5" : {"Value" : 0, "Locked" : False},
                "V23_e6" : {"Value" : 0, "Locked" : False},
                "V23_e7" : {"Value" : 0, "Locked" : False},}
        V24 ={
                "V24_e0" : {"Value" : 0, "Locked" : False},
                "V24_e1" : {"Value" : 0, "Locked" : False},
                "V24_e2" : {"Value" : 0, "Locked" : False},
                "V24_e3" : {"Value" : 0, "Locked" : False},
                "V24_e4" : {"Value" : 0, "Locked" : False},
                "V24_e5" : {"Value" : 0, "Locked" : False},
                "V24_e6" : {"Value" : 0, "Locked" : False},
                "V24_e7" : {"Value" : 0, "Locked" : False},}
        V25 ={
                "V25_e0" : {"Value" : 0, "Locked" : False},
                "V25_e1" : {"Value" : 0, "Locked" : False},
                "V25_e2" : {"Value" : 0, "Locked" : False},
                "V25_e3" : {"Value" : 0, "Locked" : False},
                "V25_e4" : {"Value" : 0, "Locked" : False},
                "V25_e5" : {"Value" : 0, "Locked" : False},
                "V25_e6" : {"Value" : 0, "Locked" : False},
                "V25_e7" : {"Value" : 0, "Locked" : False},}
        V26 ={
                "V26_e0" : {"Value" : 0, "Locked" : False},
                "V26_e1" : {"Value" : 0, "Locked" : False},
                "V26_e2" : {"Value" : 0, "Locked" : False},
                "V26_e3" : {"Value" : 0, "Locked" : False},
                "V26_e4" : {"Value" : 0, "Locked" : False},
                "V26_e5" : {"Value" : 0, "Locked" : False},
                "V26_e6" : {"Value" : 0, "Locked" : False},
                "V26_e7" : {"Value" : 0, "Locked" : False},}
        V27 ={
                "V27_e0" : {"Value" : 0, "Locked" : False},
                "V27_e1" : {"Value" : 0, "Locked" : False},
                "V27_e2" : {"Value" : 0, "Locked" : False},
                "V27_e3" : {"Value" : 0, "Locked" : False},
                "V27_e4" : {"Value" : 0, "Locked" : False},
                "V27_e5" : {"Value" : 0, "Locked" : False},
                "V27_e6" : {"Value" : 0, "Locked" : False},
                "V27_e7" : {"Value" : 0, "Locked" : False},}
        V28 ={
                "V28_e0" : {"Value" : 0, "Locked" : False},
                "V28_e1" : {"Value" : 0, "Locked" : False},
                "V28_e2" : {"Value" : 0, "Locked" : False},
                "V28_e3" : {"Value" : 0, "Locked" : False},
                "V28_e4" : {"Value" : 0, "Locked" : False},
                "V28_e5" : {"Value" : 0, "Locked" : False},
                "V28_e6" : {"Value" : 0, "Locked" : False},
                "V28_e7" : {"Value" : 0, "Locked" : False},}
        V29 ={
                "V29_e0" : {"Value" : 0, "Locked" : False},
                "V29_e1" : {"Value" : 0, "Locked" : False},
                "V29_e2" : {"Value" : 0, "Locked" : False},
                "V29_e3" : {"Value" : 0, "Locked" : False},
                "V29_e4" : {"Value" : 0, "Locked" : False},
                "V29_e5" : {"Value" : 0, "Locked" : False},
                "V29_e6" : {"Value" : 0, "Locked" : False},
                "V29_e7" : {"Value" : 0, "Locked" : False},}
        V30 ={
                "V30_e0" : {"Value" : 0, "Locked" : False},
                "V30_e1" : {"Value" : 0, "Locked" : False},
                "V30_e2" : {"Value" : 0, "Locked" : False},
                "V30_e3" : {"Value" : 0, "Locked" : False},
                "V30_e4" : {"Value" : 0, "Locked" : False},
                "V30_e5" : {"Value" : 0, "Locked" : False},
                "V30_e6" : {"Value" : 0, "Locked" : False},
                "V30_e7" : {"Value" : 0, "Locked" : False},}
        V31 ={
                "V31_e0" : {"Value" : 0, "Locked" : False},
                "V31_e1" : {"Value" : 0, "Locked" : False},
                "V31_e2" : {"Value" : 0, "Locked" : False},
                "V31_e3" : {"Value" : 0, "Locked" : False},
                "V31_e4" : {"Value" : 0, "Locked" : False},
                "V31_e5" : {"Value" : 0, "Locked" : False},
                "V31_e6" : {"Value" : 0, "Locked" : False},
                "V31_e7" : {"Value" : 0, "Locked" : False},}

        LUT8X8 = {
            "LUT8X8_0": {"Value": 99, "Locked": False},
            "LUT8X8_1": {"Value": 124, "Locked": False},
            "LUT8X8_2": {"Value": 119, "Locked": False},
            "LUT8X8_3": {"Value": 123, "Locked": False},
            "LUT8X8_4": {"Value": 242, "Locked": False},
            "LUT8X8_5": {"Value": 107, "Locked": False},
            "LUT8X8_6": {"Value": 111, "Locked": False},
            "LUT8X8_7": {"Value": 197, "Locked": False},
            "LUT8X8_8": {"Value": 48, "Locked": False},
            "LUT8X8_9": {"Value": 1, "Locked": False},
            "LUT8X8_10": {"Value": 103, "Locked": False},
            "LUT8X8_11": {"Value": 43, "Locked": False},
            "LUT8X8_12": {"Value": 254, "Locked": False},
            "LUT8X8_13": {"Value": 215, "Locked": False},
            "LUT8X8_14": {"Value": 171, "Locked": False},
            "LUT8X8_15": {"Value": 118, "Locked": False},
            "LUT8X8_16": {"Value": 202, "Locked": False},
            "LUT8X8_17": {"Value": 130, "Locked": False},
            "LUT8X8_18": {"Value": 201, "Locked": False},
            "LUT8X8_19": {"Value": 125, "Locked": False},
            "LUT8X8_20": {"Value": 250, "Locked": False},
            "LUT8X8_21": {"Value": 89, "Locked": False},
            "LUT8X8_22": {"Value": 71, "Locked": False},
            "LUT8X8_23": {"Value": 240, "Locked": False},
            "LUT8X8_24": {"Value": 173, "Locked": False},
            "LUT8X8_25": {"Value": 212, "Locked": False},
            "LUT8X8_26": {"Value": 162, "Locked": False},
            "LUT8X8_27": {"Value": 175, "Locked": False},
            "LUT8X8_28": {"Value": 156, "Locked": False},
            "LUT8X8_29": {"Value": 164, "Locked": False},
            "LUT8X8_30": {"Value": 114, "Locked": False},
            "LUT8X8_31": {"Value": 192, "Locked": False},
            "LUT8X8_32": {"Value": 183, "Locked": False},
            "LUT8X8_33": {"Value": 253, "Locked": False},
            "LUT8X8_34": {"Value": 147, "Locked": False},
            "LUT8X8_35": {"Value": 38, "Locked": False},
            "LUT8X8_36": {"Value": 54, "Locked": False},
            "LUT8X8_37": {"Value": 63, "Locked": False},
            "LUT8X8_38": {"Value": 247, "Locked": False},
            "LUT8X8_39": {"Value": 204, "Locked": False},
            "LUT8X8_40": {"Value": 52, "Locked": False},
            "LUT8X8_41": {"Value": 165, "Locked": False},
            "LUT8X8_42": {"Value": 229, "Locked": False},
            "LUT8X8_43": {"Value": 241, "Locked": False},
            "LUT8X8_44": {"Value": 113, "Locked": False},
            "LUT8X8_45": {"Value": 216, "Locked": False},
            "LUT8X8_46": {"Value": 49, "Locked": False},
            "LUT8X8_47": {"Value": 21, "Locked": False},
            "LUT8X8_48": {"Value": 4, "Locked": False},
            "LUT8X8_49": {"Value": 199, "Locked": False},
            "LUT8X8_50": {"Value": 35, "Locked": False},
            "LUT8X8_51": {"Value": 195, "Locked": False},
            "LUT8X8_52": {"Value": 24, "Locked": False},
            "LUT8X8_53": {"Value": 150, "Locked": False},
            "LUT8X8_54": {"Value": 5, "Locked": False},
            "LUT8X8_55": {"Value": 154, "Locked": False},
            "LUT8X8_56": {"Value": 7, "Locked": False},
            "LUT8X8_57": {"Value": 18, "Locked": False},
            "LUT8X8_58": {"Value": 128, "Locked": False},
            "LUT8X8_59": {"Value": 226, "Locked": False},
            "LUT8X8_60": {"Value": 235, "Locked": False},
            "LUT8X8_61": {"Value": 39, "Locked": False},
            "LUT8X8_62": {"Value": 178, "Locked": False},
            "LUT8X8_63": {"Value": 117, "Locked": False},
            "LUT8X8_64": {"Value": 9, "Locked": False},
            "LUT8X8_65": {"Value": 131, "Locked": False},
            "LUT8X8_66": {"Value": 44, "Locked": False},
            "LUT8X8_67": {"Value": 26, "Locked": False},
            "LUT8X8_68": {"Value": 27, "Locked": False},
            "LUT8X8_69": {"Value": 110, "Locked": False},
            "LUT8X8_70": {"Value": 90, "Locked": False},
            "LUT8X8_71": {"Value": 160, "Locked": False},
            "LUT8X8_72": {"Value": 82, "Locked": False},
            "LUT8X8_73": {"Value": 59, "Locked": False},
            "LUT8X8_74": {"Value": 214, "Locked": False},
            "LUT8X8_75": {"Value": 179, "Locked": False},
            "LUT8X8_76": {"Value": 41, "Locked": False},
            "LUT8X8_77": {"Value": 227, "Locked": False},
            "LUT8X8_78": {"Value": 47, "Locked": False},
            "LUT8X8_79": {"Value": 132, "Locked": False},
            "LUT8X8_80": {"Value": 83, "Locked": False},
            "LUT8X8_81": {"Value": 209, "Locked": False},
            "LUT8X8_82": {"Value": 0, "Locked": False},
            "LUT8X8_83": {"Value": 237, "Locked": False},
            "LUT8X8_84": {"Value": 32, "Locked": False},
            "LUT8X8_85": {"Value": 252, "Locked": False},
            "LUT8X8_86": {"Value": 177, "Locked": False},
            "LUT8X8_87": {"Value": 91, "Locked": False},
            "LUT8X8_88": {"Value": 106, "Locked": False},
            "LUT8X8_89": {"Value": 203, "Locked": False},
            "LUT8X8_90": {"Value": 190, "Locked": False},
            "LUT8X8_91": {"Value": 57, "Locked": False},
            "LUT8X8_92": {"Value": 74, "Locked": False},
            "LUT8X8_93": {"Value": 76, "Locked": False},
            "LUT8X8_94": {"Value": 88, "Locked": False},
            "LUT8X8_95": {"Value": 207, "Locked": False},
            "LUT8X8_96": {"Value": 208, "Locked": False},
            "LUT8X8_97": {"Value": 239, "Locked": False},
            "LUT8X8_98": {"Value": 170, "Locked": False},
            "LUT8X8_99": {"Value": 251, "Locked": False},
            "LUT8X8_100": {"Value": 67, "Locked": False},
            "LUT8X8_101": {"Value": 77, "Locked": False},
            "LUT8X8_102": {"Value": 51, "Locked": False},
            "LUT8X8_103": {"Value": 131, "Locked": False},
            "LUT8X8_104": {"Value": 69, "Locked": False},
            "LUT8X8_105": {"Value": 249, "Locked": False},
            "LUT8X8_106": {"Value": 2, "Locked": False},
            "LUT8X8_107": {"Value": 127, "Locked": False},
            "LUT8X8_108": {"Value": 80, "Locked": False},
            "LUT8X8_109": {"Value": 60, "Locked": False},
            "LUT8X8_110": {"Value": 159, "Locked": False},
            "LUT8X8_111": {"Value": 168, "Locked": False},
            "LUT8X8_112": {"Value": 81, "Locked": False},
            "LUT8X8_113": {"Value": 163, "Locked": False},
            "LUT8X8_114": {"Value": 64, "Locked": False},
            "LUT8X8_115": {"Value": 143, "Locked": False},
            "LUT8X8_116": {"Value": 146, "Locked": False},
            "LUT8X8_117": {"Value": 157, "Locked": False},
            "LUT8X8_118": {"Value": 56, "Locked": False},
            "LUT8X8_119": {"Value": 245, "Locked": False},
            "LUT8X8_120": {"Value": 188, "Locked": False},
            "LUT8X8_121": {"Value": 182, "Locked": False},
            "LUT8X8_122": {"Value": 218, "Locked": False},
            "LUT8X8_123": {"Value": 33, "Locked": False},
            "LUT8X8_124": {"Value": 16, "Locked": False},
            "LUT8X8_125": {"Value": 255, "Locked": False},
            "LUT8X8_126": {"Value": 243, "Locked": False},
            "LUT8X8_127": {"Value": 210, "Locked": False},
            "LUT8X8_128": {"Value": 205, "Locked": False},
            "LUT8X8_129": {"Value": 12, "Locked": False},
            "LUT8X8_130": {"Value": 19, "Locked": False},
            "LUT8X8_131": {"Value": 236, "Locked": False},
            "LUT8X8_132": {"Value": 95, "Locked": False},
            "LUT8X8_133": {"Value": 151, "Locked": False},
            "LUT8X8_134": {"Value": 68, "Locked": False},
            "LUT8X8_135": {"Value": 23, "Locked": False},
            "LUT8X8_136": {"Value": 196, "Locked": False},
            "LUT8X8_137": {"Value": 167, "Locked": False},
            "LUT8X8_138": {"Value": 126, "Locked": False},
            "LUT8X8_139": {"Value": 61, "Locked": False},
            "LUT8X8_140": {"Value": 100, "Locked": False},
            "LUT8X8_141": {"Value": 93, "Locked": False},
            "LUT8X8_142": {"Value": 25, "Locked": False},
            "LUT8X8_143": {"Value": 115, "Locked": False},
            "LUT8X8_144": {"Value": 96, "Locked": False},
            "LUT8X8_145": {"Value": 129, "Locked": False},
            "LUT8X8_146": {"Value": 79, "Locked": False},
            "LUT8X8_147": {"Value": 220, "Locked": False},
            "LUT8X8_148": {"Value": 34, "Locked": False},
            "LUT8X8_149": {"Value": 42, "Locked": False},
            "LUT8X8_150": {"Value": 144, "Locked": False},
            "LUT8X8_151": {"Value": 136, "Locked": False},
            "LUT8X8_152": {"Value": 70, "Locked": False},
            "LUT8X8_153": {"Value": 238, "Locked": False},
            "LUT8X8_154": {"Value": 140, "Locked": False},
            "LUT8X8_155": {"Value": 20, "Locked": False},
            "LUT8X8_156": {"Value": 222, "Locked": False},
            "LUT8X8_157": {"Value": 94, "Locked": False},
            "LUT8X8_158": {"Value": 11, "Locked": False},
            "LUT8X8_159": {"Value": 219, "Locked": False},
            "LUT8X8_160": {"Value": 224, "Locked": False},
            "LUT8X8_161": {"Value": 50, "Locked": False},
            "LUT8X8_162": {"Value": 58, "Locked": False},
            "LUT8X8_163": {"Value": 10, "Locked": False},
            "LUT8X8_164": {"Value": 73, "Locked": False},
            "LUT8X8_165": {"Value": 6, "Locked": False},
            "LUT8X8_166": {"Value": 36, "Locked": False},
            "LUT8X8_167": {"Value": 92, "Locked": False},
            "LUT8X8_168": {"Value": 134, "Locked": False},
            "LUT8X8_169": {"Value": 211, "Locked": False},
            "LUT8X8_170": {"Value": 172, "Locked": False},
            "LUT8X8_171": {"Value": 98, "Locked": False},
            "LUT8X8_172": {"Value": 145, "Locked": False},
            "LUT8X8_173": {"Value": 149, "Locked": False},
            "LUT8X8_174": {"Value": 228, "Locked": False},
            "LUT8X8_175": {"Value": 121, "Locked": False},
            "LUT8X8_176": {"Value": 231, "Locked": False},
            "LUT8X8_177": {"Value": 200, "Locked": False},
            "LUT8X8_178": {"Value": 55, "Locked": False},
            "LUT8X8_179": {"Value": 109, "Locked": False},
            "LUT8X8_180": {"Value": 141, "Locked": False},
            "LUT8X8_181": {"Value": 213, "Locked": False},
            "LUT8X8_182": {"Value": 78, "Locked": False},
            "LUT8X8_183": {"Value": 169, "Locked": False},
            "LUT8X8_184": {"Value": 108, "Locked": False},
            "LUT8X8_185": {"Value": 86, "Locked": False},
            "LUT8X8_186": {"Value": 244, "Locked": False},
            "LUT8X8_187": {"Value": 234, "Locked": False},
            "LUT8X8_188": {"Value": 101, "Locked": False},
            "LUT8X8_189": {"Value": 122, "Locked": False},
            "LUT8X8_190": {"Value": 174, "Locked": False},
            "LUT8X8_191": {"Value": 8, "Locked": False},
            "LUT8X8_192": {"Value": 186, "Locked": False},
            "LUT8X8_193": {"Value": 120, "Locked": False},
            "LUT8X8_194": {"Value": 37, "Locked": False},
            "LUT8X8_195": {"Value": 46, "Locked": False},
            "LUT8X8_196": {"Value": 28, "Locked": False},
            "LUT8X8_197": {"Value": 166, "Locked": False},
            "LUT8X8_198": {"Value": 180, "Locked": False},
            "LUT8X8_199": {"Value": 198, "Locked": False},
            "LUT8X8_200": {"Value": 232, "Locked": False},
            "LUT8X8_201": {"Value": 221, "Locked": False},
            "LUT8X8_202": {"Value": 116, "Locked": False},
            "LUT8X8_203": {"Value": 31, "Locked": False},
            "LUT8X8_204": {"Value": 75, "Locked": False},
            "LUT8X8_205": {"Value": 189, "Locked": False},
            "LUT8X8_206": {"Value": 139, "Locked": False},
            "LUT8X8_207": {"Value": 138, "Locked": False},
            "LUT8X8_208": {"Value": 112, "Locked": False},
            "LUT8X8_209": {"Value": 62, "Locked": False},
            "LUT8X8_210": {"Value": 181, "Locked": False},
            "LUT8X8_211": {"Value": 102, "Locked": False},
            "LUT8X8_212": {"Value": 72, "Locked": False},
            "LUT8X8_213": {"Value": 3, "Locked": False},
            "LUT8X8_214": {"Value": 246, "Locked": False},
            "LUT8X8_215": {"Value": 14, "Locked": False},
            "LUT8X8_216": {"Value": 97, "Locked": False},
            "LUT8X8_217": {"Value": 53, "Locked": False},
            "LUT8X8_218": {"Value": 87, "Locked": False},
            "LUT8X8_219": {"Value": 185, "Locked": False},
            "LUT8X8_220": {"Value": 134, "Locked": False},
            "LUT8X8_221": {"Value": 193, "Locked": False},
            "LUT8X8_222": {"Value": 29, "Locked": False},
            "LUT8X8_223": {"Value": 158, "Locked": False},
            "LUT8X8_224": {"Value": 225, "Locked": False},
            "LUT8X8_225": {"Value": 248, "Locked": False},
            "LUT8X8_226": {"Value": 152, "Locked": False},
            "LUT8X8_227": {"Value": 17, "Locked": False},
            "LUT8X8_228": {"Value": 105, "Locked": False},
            "LUT8X8_229": {"Value": 217, "Locked": False},
            "LUT8X8_230": {"Value": 142, "Locked": False},
            "LUT8X8_231": {"Value": 148, "Locked": False},
            "LUT8X8_232": {"Value": 155, "Locked": False},
            "LUT8X8_233": {"Value": 30, "Locked": False},
            "LUT8X8_234": {"Value": 135, "Locked": False},
            "LUT8X8_235": {"Value": 233, "Locked": False},
            "LUT8X8_236": {"Value": 206, "Locked": False},
            "LUT8X8_237": {"Value": 85, "Locked": False},
            "LUT8X8_238": {"Value": 40, "Locked": False},
            "LUT8X8_239": {"Value": 223, "Locked": False},
            "LUT8X8_240": {"Value": 140, "Locked": False},
            "LUT8X8_241": {"Value": 161, "Locked": False},
            "LUT8X8_242": {"Value": 137, "Locked": False},
            "LUT8X8_243": {"Value": 13, "Locked": False},
            "LUT8X8_244": {"Value": 191, "Locked": False},
            "LUT8X8_245": {"Value": 230, "Locked": False},
            "LUT8X8_246": {"Value": 66, "Locked": False},
            "LUT8X8_247": {"Value": 104, "Locked": False},
            "LUT8X8_248": {"Value": 65, "Locked": False},
            "LUT8X8_249": {"Value": 153, "Locked": False},
            "LUT8X8_250": {"Value": 45, "Locked": False},
            "LUT8X8_251": {"Value": 15, "Locked": False},
            "LUT8X8_252": {"Value": 176, "Locked": False},
            "LUT8X8_253": {"Value": 84, "Locked": False},
            "LUT8X8_254": {"Value": 187, "Locked": False},
            "LUT8X8_255": {"Value": 22, "Locked": False},
        }
        LUT4X4 = {
            "LUT4X4_0": {"Value": 15, "Locked": False},
            "LUT4X4_1": {"Value": 14, "Locked": False},
            "LUT4X4_2": {"Value": 13, "Locked": False},
            "LUT4X4_3": {"Value": 12, "Locked": False},
            "LUT4X4_4": {"Value": 11, "Locked": False},
            "LUT4X4_5": {"Value": 10, "Locked": False},
            "LUT4X4_6": {"Value": 9, "Locked": False},
            "LUT4X4_7": {"Value": 8, "Locked": False},
            "LUT4X4_8": {"Value": 7, "Locked": False},
            "LUT4X4_9": {"Value": 6, "Locked": False},
            "LUT4X4_10": {"Value": 5, "Locked": False},
            "LUT4X4_11": {"Value": 4, "Locked": False},
            "LUT4X4_12": {"Value": 3, "Locked": False},
            "LUT4X4_13": {"Value": 2, "Locked": False},
            "LUT4X4_14": {"Value": 1, "Locked": False},
            "LUT4X4_15": {"Value": 0, "Locked": False},
        }
        LUT6X4 = {
            "LUT6X4_0": {"Value": 0, "Locked": False},
            "LUT6X4_1": {"Value": 1, "Locked": False},
            "LUT6X4_2": {"Value": 2, "Locked": False},
            "LUT6X4_3": {"Value": 3, "Locked": False},
            "LUT6X4_4": {"Value": 4, "Locked": False},
            "LUT6X4_5": {"Value": 5, "Locked": False},
            "LUT6X4_6": {"Value": 6, "Locked": False},
            "LUT6X4_7": {"Value": 7, "Locked": False},
            "LUT6X4_8": {"Value": 8, "Locked": False},
            "LUT6X4_9": {"Value": 9, "Locked": False},
            "LUT6X4_10": {"Value": 10, "Locked": False},
            "LUT6X4_11": {"Value": 11, "Locked": False},
            "LUT6X4_12": {"Value": 12, "Locked": False},
            "LUT6X4_13": {"Value": 13, "Locked": False},
            "LUT6X4_14": {"Value": 14, "Locked": False},
            "LUT6X4_15": {"Value": 15, "Locked": False},
            "LUT6X4_16": {"Value": 0, "Locked": False},
            "LUT6X4_17": {"Value": 1, "Locked": False},
            "LUT6X4_18": {"Value": 2, "Locked": False},
            "LUT6X4_19": {"Value": 3, "Locked": False},
            "LUT6X4_20": {"Value": 4, "Locked": False},
            "LUT6X4_21": {"Value": 5, "Locked": False},
            "LUT6X4_22": {"Value": 6, "Locked": False},
            "LUT6X4_23": {"Value": 7, "Locked": False},
            "LUT6X4_24": {"Value": 8, "Locked": False},
            "LUT6X4_25": {"Value": 9, "Locked": False},
            "LUT6X4_26": {"Value": 10, "Locked": False},
            "LUT6X4_27": {"Value": 11, "Locked": False},
            "LUT6X4_28": {"Value": 12, "Locked": False},
            "LUT6X4_29": {"Value": 13, "Locked": False},
            "LUT6X4_30": {"Value": 14, "Locked": False},
            "LUT6X4_31": {"Value": 15, "Locked": False},
            "LUT6X4_32": {"Value": 0, "Locked": False},
            "LUT6X4_33": {"Value": 1, "Locked": False},
            "LUT6X4_34": {"Value": 2, "Locked": False},
            "LUT6X4_35": {"Value": 3, "Locked": False},
            "LUT6X4_36": {"Value": 4, "Locked": False},
            "LUT6X4_37": {"Value": 5, "Locked": False},
            "LUT6X4_38": {"Value": 6, "Locked": False},
            "LUT6X4_39": {"Value": 7, "Locked": False},
            "LUT6X4_40": {"Value": 8, "Locked": False},
            "LUT6X4_41": {"Value": 9, "Locked": False},
            "LUT6X4_42": {"Value": 10, "Locked": False},
            "LUT6X4_43": {"Value": 11, "Locked": False},
            "LUT6X4_44": {"Value": 12, "Locked": False},
            "LUT6X4_45": {"Value": 13, "Locked": False},
            "LUT6X4_46": {"Value": 14, "Locked": False},
            "LUT6X4_47": {"Value": 15, "Locked": False},
            "LUT6X4_48": {"Value": 0, "Locked": False},
            "LUT6X4_49": {"Value": 1, "Locked": False},
            "LUT6X4_50": {"Value": 2, "Locked": False},
            "LUT6X4_51": {"Value": 3, "Locked": False},
            "LUT6X4_52": {"Value": 4, "Locked": False},
            "LUT6X4_53": {"Value": 5, "Locked": False},
            "LUT6X4_54": {"Value": 6, "Locked": False},
            "LUT6X4_55": {"Value": 7, "Locked": False},
            "LUT6X4_56": {"Value": 8, "Locked": False},
            "LUT6X4_57": {"Value": 9, "Locked": False},
            "LUT6X4_58": {"Value": 10, "Locked": False},
            "LUT6X4_59": {"Value": 11, "Locked": False},
            "LUT6X4_60": {"Value": 12, "Locked": False},
            "LUT6X4_61": {"Value": 13, "Locked": False},
            "LUT6X4_62": {"Value": 14, "Locked": False},
            "LUT6X4_63": {"Value": 15, "Locked": False},
        }
        LUT8X4 = {
            "LUT8X4_0": {"Value": 0, "Locked": False},
            "LUT8X4_1": {"Value": 1, "Locked": False},
            "LUT8X4_2": {"Value": 2, "Locked": False},
            "LUT8X4_3": {"Value": 3, "Locked": False},
            "LUT8X4_4": {"Value": 4, "Locked": False},
            "LUT8X4_5": {"Value": 5, "Locked": False},
            "LUT8X4_6": {"Value": 6, "Locked": False},
            "LUT8X4_7": {"Value": 7, "Locked": False},
            "LUT8X4_8": {"Value": 8, "Locked": False},
            "LUT8X4_9": {"Value": 9, "Locked": False},
            "LUT8X4_10": {"Value": 10, "Locked": False},
            "LUT8X4_11": {"Value": 11, "Locked": False},
            "LUT8X4_12": {"Value": 12, "Locked": False},
            "LUT8X4_13": {"Value": 13, "Locked": False},
            "LUT8X4_14": {"Value": 14, "Locked": False},
            "LUT8X4_15": {"Value": 15, "Locked": False},
            "LUT8X4_16": {"Value": 0, "Locked": False},
            "LUT8X4_17": {"Value": 1, "Locked": False},
            "LUT8X4_18": {"Value": 2, "Locked": False},
            "LUT8X4_19": {"Value": 3, "Locked": False},
            "LUT8X4_20": {"Value": 4, "Locked": False},
            "LUT8X4_21": {"Value": 5, "Locked": False},
            "LUT8X4_22": {"Value": 6, "Locked": False},
            "LUT8X4_23": {"Value": 7, "Locked": False},
            "LUT8X4_24": {"Value": 8, "Locked": False},
            "LUT8X4_25": {"Value": 9, "Locked": False},
            "LUT8X4_26": {"Value": 10, "Locked": False},
            "LUT8X4_27": {"Value": 11, "Locked": False},
            "LUT8X4_28": {"Value": 12, "Locked": False},
            "LUT8X4_29": {"Value": 13, "Locked": False},
            "LUT8X4_30": {"Value": 14, "Locked": False},
            "LUT8X4_31": {"Value": 15, "Locked": False},
            "LUT8X4_32": {"Value": 0, "Locked": False},
            "LUT8X4_33": {"Value": 1, "Locked": False},
            "LUT8X4_34": {"Value": 2, "Locked": False},
            "LUT8X4_35": {"Value": 3, "Locked": False},
            "LUT8X4_36": {"Value": 4, "Locked": False},
            "LUT8X4_37": {"Value": 5, "Locked": False},
            "LUT8X4_38": {"Value": 6, "Locked": False},
            "LUT8X4_39": {"Value": 7, "Locked": False},
            "LUT8X4_40": {"Value": 8, "Locked": False},
            "LUT8X4_41": {"Value": 9, "Locked": False},
            "LUT8X4_42": {"Value": 10, "Locked": False},
            "LUT8X4_43": {"Value": 11, "Locked": False},
            "LUT8X4_44": {"Value": 12, "Locked": False},
            "LUT8X4_45": {"Value": 13, "Locked": False},
            "LUT8X4_46": {"Value": 14, "Locked": False},
            "LUT8X4_47": {"Value": 15, "Locked": False},
            "LUT8X4_48": {"Value": 0, "Locked": False},
            "LUT8X4_49": {"Value": 1, "Locked": False},
            "LUT8X4_50": {"Value": 2, "Locked": False},
            "LUT8X4_51": {"Value": 3, "Locked": False},
            "LUT8X4_52": {"Value": 4, "Locked": False},
            "LUT8X4_53": {"Value": 5, "Locked": False},
            "LUT8X4_54": {"Value": 6, "Locked": False},
            "LUT8X4_55": {"Value": 7, "Locked": False},
            "LUT8X4_56": {"Value": 8, "Locked": False},
            "LUT8X4_57": {"Value": 9, "Locked": False},
            "LUT8X4_58": {"Value": 10, "Locked": False},
            "LUT8X4_59": {"Value": 11, "Locked": False},
            "LUT8X4_60": {"Value": 12, "Locked": False},
            "LUT8X4_61": {"Value": 13, "Locked": False},
            "LUT8X4_62": {"Value": 14, "Locked": False},
            "LUT8X4_63": {"Value": 15, "Locked": False},
            "LUT8X4_64": {"Value": 0, "Locked": False},
            "LUT8X4_65": {"Value": 1, "Locked": False},
            "LUT8X4_66": {"Value": 2, "Locked": False},
            "LUT8X4_67": {"Value": 3, "Locked": False},
            "LUT8X4_68": {"Value": 4, "Locked": False},
            "LUT8X4_69": {"Value": 5, "Locked": False},
            "LUT8X4_70": {"Value": 6, "Locked": False},
            "LUT8X4_71": {"Value": 7, "Locked": False},
            "LUT8X4_72": {"Value": 8, "Locked": False},
            "LUT8X4_73": {"Value": 9, "Locked": False},
            "LUT8X4_74": {"Value": 10, "Locked": False},
            "LUT8X4_75": {"Value": 11, "Locked": False},
            "LUT8X4_76": {"Value": 12, "Locked": False},
            "LUT8X4_77": {"Value": 13, "Locked": False},
            "LUT8X4_78": {"Value": 14, "Locked": False},
            "LUT8X4_79": {"Value": 15, "Locked": False},
            "LUT8X4_80": {"Value": 0, "Locked": False},
            "LUT8X4_81": {"Value": 1, "Locked": False},
            "LUT8X4_82": {"Value": 2, "Locked": False},
            "LUT8X4_83": {"Value": 3, "Locked": False},
            "LUT8X4_84": {"Value": 4, "Locked": False},
            "LUT8X4_85": {"Value": 5, "Locked": False},
            "LUT8X4_86": {"Value": 6, "Locked": False},
            "LUT8X4_87": {"Value": 7, "Locked": False},
            "LUT8X4_88": {"Value": 8, "Locked": False},
            "LUT8X4_89": {"Value": 9, "Locked": False},
            "LUT8X4_90": {"Value": 10, "Locked": False},
            "LUT8X4_91": {"Value": 11, "Locked": False},
            "LUT8X4_92": {"Value": 12, "Locked": False},
            "LUT8X4_93": {"Value": 13, "Locked": False},
            "LUT8X4_94": {"Value": 14, "Locked": False},
            "LUT8X4_95": {"Value": 15, "Locked": False},
            "LUT8X4_96": {"Value": 0, "Locked": False},
            "LUT8X4_97": {"Value": 1, "Locked": False},
            "LUT8X4_98": {"Value": 2, "Locked": False},
            "LUT8X4_99": {"Value": 3, "Locked": False},
            "LUT8X4_100": {"Value": 4, "Locked": False},
            "LUT8X4_101": {"Value": 5, "Locked": False},
            "LUT8X4_102": {"Value": 6, "Locked": False},
            "LUT8X4_103": {"Value": 7, "Locked": False},
            "LUT8X4_104": {"Value": 8, "Locked": False},
            "LUT8X4_105": {"Value": 9, "Locked": False},
            "LUT8X4_106": {"Value": 10, "Locked": False},
            "LUT8X4_107": {"Value": 11, "Locked": False},
            "LUT8X4_108": {"Value": 12, "Locked": False},
            "LUT8X4_109": {"Value": 13, "Locked": False},
            "LUT8X4_110": {"Value": 14, "Locked": False},
            "LUT8X4_111": {"Value": 15, "Locked": False},
            "LUT8X4_112": {"Value": 0, "Locked": False},
            "LUT8X4_113": {"Value": 1, "Locked": False},
            "LUT8X4_114": {"Value": 2, "Locked": False},
            "LUT8X4_115": {"Value": 3, "Locked": False},
            "LUT8X4_116": {"Value": 4, "Locked": False},
            "LUT8X4_117": {"Value": 5, "Locked": False},
            "LUT8X4_118": {"Value": 6, "Locked": False},
            "LUT8X4_119": {"Value": 7, "Locked": False},
            "LUT8X4_120": {"Value": 8, "Locked": False},
            "LUT8X4_121": {"Value": 9, "Locked": False},
            "LUT8X4_122": {"Value": 10, "Locked": False},
            "LUT8X4_123": {"Value": 11, "Locked": False},
            "LUT8X4_124": {"Value": 12, "Locked": False},
            "LUT8X4_125": {"Value": 13, "Locked": False},
            "LUT8X4_126": {"Value": 14, "Locked": False},
            "LUT8X4_127": {"Value": 15, "Locked": False},
            "LUT8X4_128": {"Value": 0, "Locked": False},
            "LUT8X4_129": {"Value": 1, "Locked": False},
            "LUT8X4_130": {"Value": 2, "Locked": False},
            "LUT8X4_131": {"Value": 3, "Locked": False},
            "LUT8X4_132": {"Value": 4, "Locked": False},
            "LUT8X4_133": {"Value": 5, "Locked": False},
            "LUT8X4_134": {"Value": 6, "Locked": False},
            "LUT8X4_135": {"Value": 7, "Locked": False},
            "LUT8X4_136": {"Value": 8, "Locked": False},
            "LUT8X4_137": {"Value": 9, "Locked": False},
            "LUT8X4_138": {"Value": 10, "Locked": False},
            "LUT8X4_139": {"Value": 11, "Locked": False},
            "LUT8X4_140": {"Value": 12, "Locked": False},
            "LUT8X4_141": {"Value": 13, "Locked": False},
            "LUT8X4_142": {"Value": 14, "Locked": False},
            "LUT8X4_143": {"Value": 15, "Locked": False},
            "LUT8X4_144": {"Value": 0, "Locked": False},
            "LUT8X4_145": {"Value": 1, "Locked": False},
            "LUT8X4_146": {"Value": 2, "Locked": False},
            "LUT8X4_147": {"Value": 3, "Locked": False},
            "LUT8X4_148": {"Value": 4, "Locked": False},
            "LUT8X4_149": {"Value": 5, "Locked": False},
            "LUT8X4_150": {"Value": 6, "Locked": False},
            "LUT8X4_151": {"Value": 7, "Locked": False},
            "LUT8X4_152": {"Value": 8, "Locked": False},
            "LUT8X4_153": {"Value": 9, "Locked": False},
            "LUT8X4_154": {"Value": 10, "Locked": False},
            "LUT8X4_155": {"Value": 11, "Locked": False},
            "LUT8X4_156": {"Value": 12, "Locked": False},
            "LUT8X4_157": {"Value": 13, "Locked": False},
            "LUT8X4_158": {"Value": 14, "Locked": False},
            "LUT8X4_159": {"Value": 15, "Locked": False},
            "LUT8X4_160": {"Value": 0, "Locked": False},
            "LUT8X4_161": {"Value": 1, "Locked": False},
            "LUT8X4_162": {"Value": 2, "Locked": False},
            "LUT8X4_163": {"Value": 3, "Locked": False},
            "LUT8X4_164": {"Value": 4, "Locked": False},
            "LUT8X4_165": {"Value": 5, "Locked": False},
            "LUT8X4_166": {"Value": 6, "Locked": False},
            "LUT8X4_167": {"Value": 7, "Locked": False},
            "LUT8X4_168": {"Value": 8, "Locked": False},
            "LUT8X4_169": {"Value": 9, "Locked": False},
            "LUT8X4_170": {"Value": 10, "Locked": False},
            "LUT8X4_171": {"Value": 11, "Locked": False},
            "LUT8X4_172": {"Value": 12, "Locked": False},
            "LUT8X4_173": {"Value": 13, "Locked": False},
            "LUT8X4_174": {"Value": 14, "Locked": False},
            "LUT8X4_175": {"Value": 15, "Locked": False},
            "LUT8X4_176": {"Value": 0, "Locked": False},
            "LUT8X4_177": {"Value": 1, "Locked": False},
            "LUT8X4_178": {"Value": 2, "Locked": False},
            "LUT8X4_179": {"Value": 3, "Locked": False},
            "LUT8X4_180": {"Value": 4, "Locked": False},
            "LUT8X4_181": {"Value": 5, "Locked": False},
            "LUT8X4_182": {"Value": 6, "Locked": False},
            "LUT8X4_183": {"Value": 7, "Locked": False},
            "LUT8X4_184": {"Value": 8, "Locked": False},
            "LUT8X4_185": {"Value": 9, "Locked": False},
            "LUT8X4_186": {"Value": 10, "Locked": False},
            "LUT8X4_187": {"Value": 11, "Locked": False},
            "LUT8X4_188": {"Value": 12, "Locked": False},
            "LUT8X4_189": {"Value": 13, "Locked": False},
            "LUT8X4_190": {"Value": 14, "Locked": False},
            "LUT8X4_191": {"Value": 15, "Locked": False},
            "LUT8X4_192": {"Value": 0, "Locked": False},
            "LUT8X4_193": {"Value": 1, "Locked": False},
            "LUT8X4_194": {"Value": 2, "Locked": False},
            "LUT8X4_195": {"Value": 3, "Locked": False},
            "LUT8X4_196": {"Value": 4, "Locked": False},
            "LUT8X4_197": {"Value": 5, "Locked": False},
            "LUT8X4_198": {"Value": 6, "Locked": False},
            "LUT8X4_199": {"Value": 7, "Locked": False},
            "LUT8X4_200": {"Value": 8, "Locked": False},
            "LUT8X4_201": {"Value": 9, "Locked": False},
            "LUT8X4_202": {"Value": 10, "Locked": False},
            "LUT8X4_203": {"Value": 11, "Locked": False},
            "LUT8X4_204": {"Value": 12, "Locked": False},
            "LUT8X4_205": {"Value": 13, "Locked": False},
            "LUT8X4_206": {"Value": 14, "Locked": False},
            "LUT8X4_207": {"Value": 15, "Locked": False},
            "LUT8X4_208": {"Value": 0, "Locked": False},
            "LUT8X4_209": {"Value": 1, "Locked": False},
            "LUT8X4_210": {"Value": 2, "Locked": False},
            "LUT8X4_211": {"Value": 3, "Locked": False},
            "LUT8X4_212": {"Value": 4, "Locked": False},
            "LUT8X4_213": {"Value": 5, "Locked": False},
            "LUT8X4_214": {"Value": 6, "Locked": False},
            "LUT8X4_215": {"Value": 7, "Locked": False},
            "LUT8X4_216": {"Value": 8, "Locked": False},
            "LUT8X4_217": {"Value": 9, "Locked": False},
            "LUT8X4_218": {"Value": 10, "Locked": False},
            "LUT8X4_219": {"Value": 11, "Locked": False},
            "LUT8X4_220": {"Value": 12, "Locked": False},
            "LUT8X4_221": {"Value": 13, "Locked": False},
            "LUT8X4_222": {"Value": 14, "Locked": False},
            "LUT8X4_223": {"Value": 15, "Locked": False},
            "LUT8X4_224": {"Value": 0, "Locked": False},
            "LUT8X4_225": {"Value": 1, "Locked": False},
            "LUT8X4_226": {"Value": 2, "Locked": False},
            "LUT8X4_227": {"Value": 3, "Locked": False},
            "LUT8X4_228": {"Value": 4, "Locked": False},
            "LUT8X4_229": {"Value": 5, "Locked": False},
            "LUT8X4_230": {"Value": 6, "Locked": False},
            "LUT8X4_231": {"Value": 7, "Locked": False},
            "LUT8X4_232": {"Value": 8, "Locked": False},
            "LUT8X4_233": {"Value": 9, "Locked": False},
            "LUT8X4_234": {"Value": 10, "Locked": False},
            "LUT8X4_235": {"Value": 11, "Locked": False},
            "LUT8X4_236": {"Value": 12, "Locked": False},
            "LUT8X4_237": {"Value": 13, "Locked": False},
            "LUT8X4_238": {"Value": 14, "Locked": False},
            "LUT8X4_239": {"Value": 15, "Locked": False},
            "LUT8X4_240": {"Value": 0, "Locked": False},
            "LUT8X4_241": {"Value": 1, "Locked": False},
            "LUT8X4_242": {"Value": 2, "Locked": False},
            "LUT8X4_243": {"Value": 3, "Locked": False},
            "LUT8X4_244": {"Value": 4, "Locked": False},
            "LUT8X4_245": {"Value": 5, "Locked": False},
            "LUT8X4_246": {"Value": 6, "Locked": False},
            "LUT8X4_247": {"Value": 7, "Locked": False},
            "LUT8X4_248": {"Value": 8, "Locked": False},
            "LUT8X4_249": {"Value": 9, "Locked": False},
            "LUT8X4_250": {"Value": 10, "Locked": False},
            "LUT8X4_251": {"Value": 11, "Locked": False},
            "LUT8X4_252": {"Value": 12, "Locked": False},
            "LUT8X4_253": {"Value": 13, "Locked": False},
            "LUT8X4_254": {"Value": 14, "Locked": False},
            "LUT8X4_255": {"Value": 15, "Locked": False},
        }
        LUT8X32 = {
            "LUT8X32_0": {"Value": 0, "Locked": False},
            "LUT8X32_1": {"Value": 16777216, "Locked": False},
            "LUT8X32_2": {"Value": 33554432, "Locked": False},
            "LUT8X32_3": {"Value": 50331648, "Locked": False},
            "LUT8X32_4": {"Value": 67108864, "Locked": False},
            "LUT8X32_5": {"Value": 83886080, "Locked": False},
            "LUT8X32_6": {"Value": 100663296, "Locked": False},
            "LUT8X32_7": {"Value": 117440512, "Locked": False},
            "LUT8X32_8": {"Value": 134217728, "Locked": False},
            "LUT8X32_9": {"Value": 150994944, "Locked": False},
            "LUT8X32_10": {"Value": 167772160, "Locked": False},
            "LUT8X32_11": {"Value": 184549376, "Locked": False},
            "LUT8X32_12": {"Value": 201326592, "Locked": False},
            "LUT8X32_13": {"Value": 218103808, "Locked": False},
            "LUT8X32_14": {"Value": 234881024, "Locked": False},
            "LUT8X32_15": {"Value": 251658240, "Locked": False},
            "LUT8X32_16": {"Value": 268435456, "Locked": False},
            "LUT8X32_17": {"Value": 285212672, "Locked": False},
            "LUT8X32_18": {"Value": 301989888, "Locked": False},
            "LUT8X32_19": {"Value": 318767104, "Locked": False},
            "LUT8X32_20": {"Value": 335544320, "Locked": False},
            "LUT8X32_21": {"Value": 352321536, "Locked": False},
            "LUT8X32_22": {"Value": 369098752, "Locked": False},
            "LUT8X32_23": {"Value": 385875968, "Locked": False},
            "LUT8X32_24": {"Value": 402653184, "Locked": False},
            "LUT8X32_25": {"Value": 419430400, "Locked": False},
            "LUT8X32_26": {"Value": 436207616, "Locked": False},
            "LUT8X32_27": {"Value": 452984832, "Locked": False},
            "LUT8X32_28": {"Value": 469762048, "Locked": False},
            "LUT8X32_29": {"Value": 486539264, "Locked": False},
            "LUT8X32_30": {"Value": 503316480, "Locked": False},
            "LUT8X32_31": {"Value": 520093696, "Locked": False},
            "LUT8X32_32": {"Value": 536870912, "Locked": False},
            "LUT8X32_33": {"Value": 553648128, "Locked": False},
            "LUT8X32_34": {"Value": 570425344, "Locked": False},
            "LUT8X32_35": {"Value": 587202560, "Locked": False},
            "LUT8X32_36": {"Value": 603979776, "Locked": False},
            "LUT8X32_37": {"Value": 620756992, "Locked": False},
            "LUT8X32_38": {"Value": 637534208, "Locked": False},
            "LUT8X32_39": {"Value": 654311424, "Locked": False},
            "LUT8X32_40": {"Value": 671088640, "Locked": False},
            "LUT8X32_41": {"Value": 687865856, "Locked": False},
            "LUT8X32_42": {"Value": 704643072, "Locked": False},
            "LUT8X32_43": {"Value": 721420288, "Locked": False},
            "LUT8X32_44": {"Value": 738197504, "Locked": False},
            "LUT8X32_45": {"Value": 754974720, "Locked": False},
            "LUT8X32_46": {"Value": 771751936, "Locked": False},
            "LUT8X32_47": {"Value": 788529152, "Locked": False},
            "LUT8X32_48": {"Value": 805306368, "Locked": False},
            "LUT8X32_49": {"Value": 822083584, "Locked": False},
            "LUT8X32_50": {"Value": 838860800, "Locked": False},
            "LUT8X32_51": {"Value": 855638016, "Locked": False},
            "LUT8X32_52": {"Value": 872415232, "Locked": False},
            "LUT8X32_53": {"Value": 889192448, "Locked": False},
            "LUT8X32_54": {"Value": 905969664, "Locked": False},
            "LUT8X32_55": {"Value": 922746880, "Locked": False},
            "LUT8X32_56": {"Value": 939524096, "Locked": False},
            "LUT8X32_57": {"Value": 956301312, "Locked": False},
            "LUT8X32_58": {"Value": 973078528, "Locked": False},
            "LUT8X32_59": {"Value": 989855744, "Locked": False},
            "LUT8X32_60": {"Value": 1006632960, "Locked": False},
            "LUT8X32_61": {"Value": 1023410176, "Locked": False},
            "LUT8X32_62": {"Value": 1040187392, "Locked": False},
            "LUT8X32_63": {"Value": 1056964608, "Locked": False},
            "LUT8X32_64": {"Value": 1073741824, "Locked": False},
            "LUT8X32_65": {"Value": 1090519040, "Locked": False},
            "LUT8X32_66": {"Value": 1107296256, "Locked": False},
            "LUT8X32_67": {"Value": 1124073472, "Locked": False},
            "LUT8X32_68": {"Value": 1140850688, "Locked": False},
            "LUT8X32_69": {"Value": 1157627904, "Locked": False},
            "LUT8X32_70": {"Value": 1174405120, "Locked": False},
            "LUT8X32_71": {"Value": 1191182336, "Locked": False},
            "LUT8X32_72": {"Value": 1207959552, "Locked": False},
            "LUT8X32_73": {"Value": 1224736768, "Locked": False},
            "LUT8X32_74": {"Value": 1241513984, "Locked": False},
            "LUT8X32_75": {"Value": 1258291200, "Locked": False},
            "LUT8X32_76": {"Value": 1275068416, "Locked": False},
            "LUT8X32_77": {"Value": 1291845632, "Locked": False},
            "LUT8X32_78": {"Value": 1308622848, "Locked": False},
            "LUT8X32_79": {"Value": 1325400064, "Locked": False},
            "LUT8X32_80": {"Value": 1342177280, "Locked": False},
            "LUT8X32_81": {"Value": 1358954496, "Locked": False},
            "LUT8X32_82": {"Value": 1375731712, "Locked": False},
            "LUT8X32_83": {"Value": 1392508928, "Locked": False},
            "LUT8X32_84": {"Value": 1409286144, "Locked": False},
            "LUT8X32_85": {"Value": 1426063360, "Locked": False},
            "LUT8X32_86": {"Value": 1442840576, "Locked": False},
            "LUT8X32_87": {"Value": 1459617792, "Locked": False},
            "LUT8X32_88": {"Value": 1476395008, "Locked": False},
            "LUT8X32_89": {"Value": 1493172224, "Locked": False},
            "LUT8X32_90": {"Value": 1509949440, "Locked": False},
            "LUT8X32_91": {"Value": 1526726656, "Locked": False},
            "LUT8X32_92": {"Value": 1543503872, "Locked": False},
            "LUT8X32_93": {"Value": 1560281088, "Locked": False},
            "LUT8X32_94": {"Value": 1577058304, "Locked": False},
            "LUT8X32_95": {"Value": 1593835520, "Locked": False},
            "LUT8X32_96": {"Value": 1610612736, "Locked": False},
            "LUT8X32_97": {"Value": 1627389952, "Locked": False},
            "LUT8X32_98": {"Value": 1644167168, "Locked": False},
            "LUT8X32_99": {"Value": 1660944384, "Locked": False},
            "LUT8X32_100": {"Value": 1677721600, "Locked": False},
            "LUT8X32_101": {"Value": 1694498816, "Locked": False},
            "LUT8X32_102": {"Value": 1711276032, "Locked": False},
            "LUT8X32_103": {"Value": 1728053248, "Locked": False},
            "LUT8X32_104": {"Value": 1744830464, "Locked": False},
            "LUT8X32_105": {"Value": 1761607680, "Locked": False},
            "LUT8X32_106": {"Value": 1778384896, "Locked": False},
            "LUT8X32_107": {"Value": 1795162112, "Locked": False},
            "LUT8X32_108": {"Value": 1811939328, "Locked": False},
            "LUT8X32_109": {"Value": 1828716544, "Locked": False},
            "LUT8X32_110": {"Value": 1845493760, "Locked": False},
            "LUT8X32_111": {"Value": 1862270976, "Locked": False},
            "LUT8X32_112": {"Value": 1879048192, "Locked": False},
            "LUT8X32_113": {"Value": 1895825408, "Locked": False},
            "LUT8X32_114": {"Value": 1912602624, "Locked": False},
            "LUT8X32_115": {"Value": 1929379840, "Locked": False},
            "LUT8X32_116": {"Value": 1946157056, "Locked": False},
            "LUT8X32_117": {"Value": 1962934272, "Locked": False},
            "LUT8X32_118": {"Value": 1979711488, "Locked": False},
            "LUT8X32_119": {"Value": 1996488704, "Locked": False},
            "LUT8X32_120": {"Value": 2013265920, "Locked": False},
            "LUT8X32_121": {"Value": 2030043136, "Locked": False},
            "LUT8X32_122": {"Value": 2046820352, "Locked": False},
            "LUT8X32_123": {"Value": 2063597568, "Locked": False},
            "LUT8X32_124": {"Value": 2080374784, "Locked": False},
            "LUT8X32_125": {"Value": 2097152000, "Locked": False},
            "LUT8X32_126": {"Value": 2113929216, "Locked": False},
            "LUT8X32_127": {"Value": 2130706432, "Locked": False},
            "LUT8X32_128": {"Value": 2147483648, "Locked": False},
            "LUT8X32_129": {"Value": 2164260864, "Locked": False},
            "LUT8X32_130": {"Value": 2181038080, "Locked": False},
            "LUT8X32_131": {"Value": 2197815296, "Locked": False},
            "LUT8X32_132": {"Value": 2214592512, "Locked": False},
            "LUT8X32_133": {"Value": 2231369728, "Locked": False},
            "LUT8X32_134": {"Value": 2248146944, "Locked": False},
            "LUT8X32_135": {"Value": 2264924160, "Locked": False},
            "LUT8X32_136": {"Value": 2281701376, "Locked": False},
            "LUT8X32_137": {"Value": 2298478592, "Locked": False},
            "LUT8X32_138": {"Value": 2315255808, "Locked": False},
            "LUT8X32_139": {"Value": 2332033024, "Locked": False},
            "LUT8X32_140": {"Value": 2348810240, "Locked": False},
            "LUT8X32_141": {"Value": 2365587456, "Locked": False},
            "LUT8X32_142": {"Value": 2382364672, "Locked": False},
            "LUT8X32_143": {"Value": 2399141888, "Locked": False},
            "LUT8X32_144": {"Value": 2415919104, "Locked": False},
            "LUT8X32_145": {"Value": 2432696320, "Locked": False},
            "LUT8X32_146": {"Value": 2449473536, "Locked": False},
            "LUT8X32_147": {"Value": 2466250752, "Locked": False},
            "LUT8X32_148": {"Value": 2483027968, "Locked": False},
            "LUT8X32_149": {"Value": 2499805184, "Locked": False},
            "LUT8X32_150": {"Value": 2516582400, "Locked": False},
            "LUT8X32_151": {"Value": 2533359616, "Locked": False},
            "LUT8X32_152": {"Value": 2550136832, "Locked": False},
            "LUT8X32_153": {"Value": 2566914048, "Locked": False},
            "LUT8X32_154": {"Value": 2583691264, "Locked": False},
            "LUT8X32_155": {"Value": 2600468480, "Locked": False},
            "LUT8X32_156": {"Value": 2617245696, "Locked": False},
            "LUT8X32_157": {"Value": 2634022912, "Locked": False},
            "LUT8X32_158": {"Value": 2650800128, "Locked": False},
            "LUT8X32_159": {"Value": 2667577344, "Locked": False},
            "LUT8X32_160": {"Value": 2684354560, "Locked": False},
            "LUT8X32_161": {"Value": 2701131776, "Locked": False},
            "LUT8X32_162": {"Value": 2717908992, "Locked": False},
            "LUT8X32_163": {"Value": 2734686208, "Locked": False},
            "LUT8X32_164": {"Value": 2751463424, "Locked": False},
            "LUT8X32_165": {"Value": 2768240640, "Locked": False},
            "LUT8X32_166": {"Value": 2785017856, "Locked": False},
            "LUT8X32_167": {"Value": 2801795072, "Locked": False},
            "LUT8X32_168": {"Value": 2818572288, "Locked": False},
            "LUT8X32_169": {"Value": 2835349504, "Locked": False},
            "LUT8X32_170": {"Value": 2852126720, "Locked": False},
            "LUT8X32_171": {"Value": 2868903936, "Locked": False},
            "LUT8X32_172": {"Value": 2885681152, "Locked": False},
            "LUT8X32_173": {"Value": 2902458368, "Locked": False},
            "LUT8X32_174": {"Value": 2919235584, "Locked": False},
            "LUT8X32_175": {"Value": 2936012800, "Locked": False},
            "LUT8X32_176": {"Value": 2952790016, "Locked": False},
            "LUT8X32_177": {"Value": 2969567232, "Locked": False},
            "LUT8X32_178": {"Value": 2986344448, "Locked": False},
            "LUT8X32_179": {"Value": 3003121664, "Locked": False},
            "LUT8X32_180": {"Value": 3019898880, "Locked": False},
            "LUT8X32_181": {"Value": 3036676096, "Locked": False},
            "LUT8X32_182": {"Value": 3053453312, "Locked": False},
            "LUT8X32_183": {"Value": 3070230528, "Locked": False},
            "LUT8X32_184": {"Value": 3087007744, "Locked": False},
            "LUT8X32_185": {"Value": 3103784960, "Locked": False},
            "LUT8X32_186": {"Value": 3120562176, "Locked": False},
            "LUT8X32_187": {"Value": 3137339392, "Locked": False},
            "LUT8X32_188": {"Value": 3154116608, "Locked": False},
            "LUT8X32_189": {"Value": 3170893824, "Locked": False},
            "LUT8X32_190": {"Value": 3187671040, "Locked": False},
            "LUT8X32_191": {"Value": 3204448256, "Locked": False},
            "LUT8X32_192": {"Value": 3221225472, "Locked": False},
            "LUT8X32_193": {"Value": 3238002688, "Locked": False},
            "LUT8X32_194": {"Value": 3254779904, "Locked": False},
            "LUT8X32_195": {"Value": 3271557120, "Locked": False},
            "LUT8X32_196": {"Value": 3288334336, "Locked": False},
            "LUT8X32_197": {"Value": 3305111552, "Locked": False},
            "LUT8X32_198": {"Value": 3321888768, "Locked": False},
            "LUT8X32_199": {"Value": 3338665984, "Locked": False},
            "LUT8X32_200": {"Value": 3355443200, "Locked": False},
            "LUT8X32_201": {"Value": 3372220416, "Locked": False},
            "LUT8X32_202": {"Value": 3388997632, "Locked": False},
            "LUT8X32_203": {"Value": 3405774848, "Locked": False},
            "LUT8X32_204": {"Value": 3422552064, "Locked": False},
            "LUT8X32_205": {"Value": 3439329280, "Locked": False},
            "LUT8X32_206": {"Value": 3456106496, "Locked": False},
            "LUT8X32_207": {"Value": 3472883712, "Locked": False},
            "LUT8X32_208": {"Value": 3489660928, "Locked": False},
            "LUT8X32_209": {"Value": 3506438144, "Locked": False},
            "LUT8X32_210": {"Value": 3523215360, "Locked": False},
            "LUT8X32_211": {"Value": 3539992576, "Locked": False},
            "LUT8X32_212": {"Value": 3556769792, "Locked": False},
            "LUT8X32_213": {"Value": 3573547008, "Locked": False},
            "LUT8X32_214": {"Value": 3590324224, "Locked": False},
            "LUT8X32_215": {"Value": 3607101440, "Locked": False},
            "LUT8X32_216": {"Value": 3623878656, "Locked": False},
            "LUT8X32_217": {"Value": 3640655872, "Locked": False},
            "LUT8X32_218": {"Value": 3657433088, "Locked": False},
            "LUT8X32_219": {"Value": 3674210304, "Locked": False},
            "LUT8X32_220": {"Value": 3690987520, "Locked": False},
            "LUT8X32_221": {"Value": 3707764736, "Locked": False},
            "LUT8X32_222": {"Value": 3724541952, "Locked": False},
            "LUT8X32_223": {"Value": 3741319168, "Locked": False},
            "LUT8X32_224": {"Value": 3758096384, "Locked": False},
            "LUT8X32_225": {"Value": 3774873600, "Locked": False},
            "LUT8X32_226": {"Value": 3791650816, "Locked": False},
            "LUT8X32_227": {"Value": 3808428032, "Locked": False},
            "LUT8X32_228": {"Value": 3825205248, "Locked": False},
            "LUT8X32_229": {"Value": 3841982464, "Locked": False},
            "LUT8X32_230": {"Value": 3858759680, "Locked": False},
            "LUT8X32_231": {"Value": 3875536896, "Locked": False},
            "LUT8X32_232": {"Value": 3892314112, "Locked": False},
            "LUT8X32_233": {"Value": 3909091328, "Locked": False},
            "LUT8X32_234": {"Value": 3925868544, "Locked": False},
            "LUT8X32_235": {"Value": 3942645760, "Locked": False},
            "LUT8X32_236": {"Value": 3959422976, "Locked": False},
            "LUT8X32_237": {"Value": 3976200192, "Locked": False},
            "LUT8X32_238": {"Value": 3992977408, "Locked": False},
            "LUT8X32_239": {"Value": 4009754624, "Locked": False},
            "LUT8X32_240": {"Value": 4026531840, "Locked": False},
            "LUT8X32_241": {"Value": 4043309056, "Locked": False},
            "LUT8X32_242": {"Value": 4060086272, "Locked": False},
            "LUT8X32_243": {"Value": 4076863488, "Locked": False},
            "LUT8X32_244": {"Value": 4093640704, "Locked": False},
            "LUT8X32_245": {"Value": 4110417920, "Locked": False},
            "LUT8X32_246": {"Value": 4127195136, "Locked": False},
            "LUT8X32_247": {"Value": 4143972352, "Locked": False},
            "LUT8X32_248": {"Value": 4160749568, "Locked": False},
            "LUT8X32_249": {"Value": 4177526784, "Locked": False},
            "LUT8X32_250": {"Value": 4194304000, "Locked": False},
            "LUT8X32_251": {"Value": 4211081216, "Locked": False},
            "LUT8X32_252": {"Value": 4227858432, "Locked": False},
            "LUT8X32_253": {"Value": 4244635648, "Locked": False},
            "LUT8X32_254": {"Value": 4261412864, "Locked": False},
            "LUT8X32_255": {"Value": 4278190080, "Locked": False},
        }


        # Link Register. Width : 256 bits
        # Assuming the initialized value is 0, be careful
        LR = { "lr" : {"Value" : 0, "Locked" : False} }

        # Frame Pointer register. Width : 256 bits
        # Assuming the initialized value is 0, be careful
        FP = { "fp" : {"Value" : 0, "Locked" : False} }

        # Stack Pointer. Width : 256 bits
        # Assuming the initialized value is 0, be careful
        SP = { "sp" : {"Value" : 0, "Locked" : False} }

        # General purpose pointer, Width : 256 bits
        # Assuming the initialized value is 0, be careful
        GP = { "GP" : {"Value" : 0, "Locked" : False} }

        # Program Counter. Width : 256 bits
        # Assuming the initialized value is 0, be careful
        PC = { "PC" : {"Value" : 0, "Locked" : False} }



        
        MMR = {
            "MMRet"         : {"Value" : None,                                                                             "Locked" : False} ,
            "Modular"       : {"Value" : 82434016654578246444830763105245969129603161266935169637912592173415460324733,                                                                            "Locked" : False} ,    # Todo : FixThis
           #Modular*2^(RADIX+2)=ModularMont  
            "ModularMont"   : {"Value" : 0x2d90000000a8e9bc7580ead3fd63b1d1487ca4d2c69ebbb6f95be6c9f8d4515f4000000,        "Locked" : False} ,
            "N"             : {"Value" : 12,                                                                               "Locked" : False} ,
            "RADIX"         : {"Value" : 24,                                                                               "Locked" : False} ,
            "M2"            : {"Value" : 0x8ba8749723f55d2e60d42fb6381632bf813e76937ea8ac4a5e991bfde3b66f01,              "Locked" : False} ,
            "M1"            : {"Value" : 0x2161ef9cc07bc231a0e1e2ff8f1cc936e1246f366c6349dae53154d1196ec20d,               "Locked" : False}  }


        self._RF = {}
        self._RF.update(SWR)
        self._RF.update(V0)
        self._RF.update(V1)
        self._RF.update(V2)
        self._RF.update(V3)
        self._RF.update(V4)
        self._RF.update(V5)
        self._RF.update(V6)
        self._RF.update(V7)
        self._RF.update(V8)
        self._RF.update(V9)
        self._RF.update(V10)
        self._RF.update(V11)
        self._RF.update(V12)
        self._RF.update(V13)
        self._RF.update(V14)
        self._RF.update(V15)
        self._RF.update(V16)
        self._RF.update(V17)
        self._RF.update(V18)
        self._RF.update(V19)
        self._RF.update(V20)
        self._RF.update(V21)
        self._RF.update(V22)
        self._RF.update(V23)
        self._RF.update(V24)
        self._RF.update(V25)
        self._RF.update(V26)
        self._RF.update(V27)
        self._RF.update(V28)
        self._RF.update(V29)
        self._RF.update(V30)
        self._RF.update(V31)
        self._RF.update(LUT8X8)
        self._RF.update(LUT4X4)
        self._RF.update(LUT6X4)
        self._RF.update(LUT8X4)
        self._RF.update(LUT8X32)
        self._RF.update(SP)
        self._RF.update(LR)
        self._RF.update(FP)
        self._RF.update(GP)
        self._RF.update(PC)
        self._RF.update(CSR)
		


        self._RF.update(MMR)

        

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
                                  "Params"  : 0}                                          ,
                "add": {"Cycles": 1,
                    "Exec": None,
                    "Pattern": re.compile("\s+add\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)"),
                    "Params": 0},
                "sd": {"Cycles": 5,
                   "Exec": None,
                   "Pattern": re.compile("\s+sd\s+(\w+)\,\s+(.+)\,\s+(\w+)"),
                   "Params": 0},
                "ld": {"Cycles": 5,
                   "Exec": None,
                   "Pattern": re.compile("\s+ld\s+(\w+)\,\s+(.+)\,\s+(\w+)"),
                   "Params": 0},
                "sw": {"Cycles": 5,
                   "Exec": None,
                   "Pattern": re.compile("\s+sw\s+(\w+)\,\s+(.+)"),
                   "Params": 0},
                "lw": {"Cycles": 5,
                   "Exec": None,
                   "Pattern": re.compile("\s+lw\s+(\w+)\,\s+(.+)"),
                   "Params": 0},
                "li": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+li\s+(\w+)\,\s+(-?\w+)"),
                   "Params": 0},
                "liv": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+liv\s+(\w+)\,\s+(-?\w+)"),
                   "Params": 0},
                "mv": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+mv\s+(\w+)\,\s+(\w+)"),
                   "Params": 0},
                "bjlab": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+bjlab\s+(\w+)\,\s+(\w+)"),
                   "Params": 0},
                "bjr": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+bjr\s+(\w+)\,\s+(\w+)"),
                   "Params": 0},
                "bne": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+bne\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                   "Params": 0},
                "beq": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+beq\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                   "Params": 0},
                "bgt": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+bgt\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                   "Params": 0},
                "bge": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+bge\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                   "Params": 0},
                "blt": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+blt\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                   "Params": 0},
                "ble": {"Cycles": 1,
                   "Exec": None,
                   "Pattern": re.compile("\s+ble\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                   "Params": 0},
                "qand"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qand\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qand64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qand64\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qand128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qand128\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qor"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qor\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qor64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qor64\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qor128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qor128\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qxor"     :    {"Cycles"  : 1,
                                  "Exec"    : None,
                                  "Pattern": re.compile("\s+qxor\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params": 0},
                "qxor64"   :    {"Cycles": 1,
                                  "Exec": None,
                                  "Pattern": re.compile("\s+qxor64\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params": 0},
                "qxor128"  :    { "Cycles": 1,
                                   "Exec": None,
                                   "Pattern": re.compile("\s+qxor128\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                   "Params": 0},
                "qnot"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qnot\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qnot64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qnot64\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qnot128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qnot128\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qtli"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qtli\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qtl"       :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qtl\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qsxor"       :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qsxor\s+(.+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qsxor64"       :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qsxor64\s+(.+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qsxor128"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qsxor128\s+(.+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qcmp"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qcmp\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qcmp64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qcmp64\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qcmp128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qcmp128\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qtest"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qtest\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qtest64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qtest64\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qtest128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qtest128\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qtesti"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qtesti\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qtesti64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qtesti64\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qtesti128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qtesti128\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qteqi"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qteqi\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qteqi64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qteqi64\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qteqi128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qteqi128\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qteq"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qteq\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qteq64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qteq64\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qteq128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qteq128\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qadd"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qadd\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qadd64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qadd64\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qadd128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qadd128\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qsub"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qsub\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qsub64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qsub64\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qsub128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qsub128\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmodadd8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodadd8\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmodadd16"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodadd16\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qmodadd32"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodadd32\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmodadd64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodadd64\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qmodadd128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodadd128\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmodsub8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodsub8\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmodsub16"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodsub16\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qmodsub32"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodsub32\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmodsub64"   :   { "Cycles"  : 1                 ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodsub64\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                  "Params"  : 0},
                "qmodsub128"   :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodsub128\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmul8l"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmul8l\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmul8h"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmul8h\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0}, 
                "qmul16l"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmul16l\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0}, 
                "qmul16h"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmul16h\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0}, 
                "qmul32l"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmul32l\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0}, 
                "qmul32h"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmul32h\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmodmul8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodmul8\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmodmul16"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodmul16\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmodmul32"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmodmul32\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qishl32"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qishl32\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)") ,
                                  "Params"  : 0}, 
                "qishl8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qishl8\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)") ,
                                  "Params"  : 0}, 
                "qshl32"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qshl32\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0}, 
                "qshl8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qshl8\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qishr32"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qishr32\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)") ,
                                  "Params"  : 0}, 
                "qishr8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qishr8\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)") ,
                                  "Params"  : 0}, 
                "qshr32"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qshr32\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0}, 
                "qshr8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qshr8\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0}, 
                "qirol32"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qirol32\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)") ,
                                  "Params"  : 0}, 
                "qirol8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qirol8\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)") ,
                                  "Params"  : 0}, 
                "qrol32"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qrol32\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0}, 
                "qrol8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qrol8\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qiror32"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qiror32\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)") ,
                                  "Params"  : 0}, 
                "qiror8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qiror8\s+(\w+)\,\s+(\w+)\,\s+(-?\w+)") ,
                                  "Params"  : 0}, 
                "qror32"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qror32\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0}, 
                "qror8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qror8\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qsbitperm32": {"Cycles": 1,
                                 "Exec": None,
                                 "Pattern": re.compile("\s+qsbitperm32\s+(\w+)\,\s+(\w+)"),
                                 "Params": 0},

                "qsbitperm64": {"Cycles": 1,
                                "Exec": None,
                                "Pattern": re.compile("\s+qsbitperm64\s+(\w+)\,\s+(\w+)"),
                                "Params": 0},
                "qsbitperm128": {"Cycles": 1,
                                "Exec": None,
                                "Pattern": re.compile("\s+qsbitperm128\s+(\w+)\,\s+(\w+)"),
                                "Params": 0},
                "qsbitperm8": {"Cycles": 1,
                                "Exec": None,
                                "Pattern": re.compile("\s+qsbitperm8\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                "Params": 0},
                "qdbitperm32": {"Cycles": 1,
                                "Exec": None,
                                "Pattern": re.compile("\s+qdbitperm32\s+(\w+)\,\s+(\w+)"),
                                "Params": 0},
                "qbyteperm32": {"Cycles": 1,
                                "Exec": None,
                                "Pattern": re.compile("\s+qbyteperm32\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                "Params": 0},
                "qbyteperm64": {"Cycles": 1,
                                "Exec": None,
                                "Pattern": re.compile("\s+qbyteperm64\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                "Params": 0},
                "qbyteperm128": {"Cycles": 1,
                                "Exec": None,
                                "Pattern": re.compile("\s+qbyteperm128\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                "Params": 0},
                "qbitsw": {"Cycles": 1,
                                "Exec": None,
                                "Pattern": re.compile("\s+qbitsw\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                                "Params": 0},
                "qbytesw": {"Cycles": 1,
                           "Exec": None,
                           "Pattern": re.compile("\s+qbytesw\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                           "Params": 0},
                "qlut8m8": {"Cycles": 1,
                            "Exec": None,
                            "Pattern": re.compile("\s+qlut8m8\s+(\w+)\,\s+(\w+)"),
                            "Params": 0},
                "q4lut8m8": {"Cycles": 1,
                            "Exec": None,
                            "Pattern": re.compile("\s+q4lut8m8\s+(\w+)\,\s+(\w+)"),
                            "Params": 0},
                "qlut4m4": {"Cycles": 1,
                            "Exec": None,
                            "Pattern": re.compile("\s+qlut4m4\s+(\w+)\,\s+(\w+)"),
                            "Params": 0},
                "qlut6m4": {"Cycles": 1,
                            "Exec": None,
                            "Pattern": re.compile("\s+qlut6m4\s+(\w+)\,\s+(\w+)"),
                            "Params": 0},
                "qlut8m4": {"Cycles": 1,
                            "Exec": None,
                            "Pattern": re.compile("\s+qlut8m4\s+(\w+)\,\s+(\w+)"),
                            "Params": 0},
                "qlut8m32": {"Cycles": 1,
                            "Exec": None,
                            "Pattern": re.compile("\s+qlut8m32\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                            "Params": 0},
                "q4lut8m32": {"Cycles": 1,
                             "Exec": None,
                             "Pattern": re.compile("\s+q4lut8m32\s+(\w+)\,\s+(\w+)"),
                             "Params": 0},
                "qlutsw": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qlutsw\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qgf8_2mulx" : {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qgf8_2mulx\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qgf8_3mulx": {"Cycles": 1,
                               "Exec": None,
                               "Pattern": re.compile("\s+qgf8_3mulx\s+(\w+)\,\s+(\w+)"),
                               "Params": 0},
                "qgfinv": {"Cycles": 1,
                               "Exec": None,
                               "Pattern": re.compile("\s+qgfinv\s+(\w+)\,\s+(\w+)"),
                               "Params": 0},
                "qgf8_4mulx": {"Cycles": 1,
                               "Exec": None,
                               "Pattern": re.compile("\s+qgf8_4mulx\s+(\w+)\,\s+(\w+)"),
                               "Params": 0},
                "qgf8_mulv": {"Cycles": 1,
                               "Exec": None,
                               "Pattern": re.compile("\s+qgf8_mulv\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                               "Params": 0},
                "qgf8_2mulv": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qgf8_2mulv\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qgf8_3mulv": {"Cycles": 1,
                               "Exec": None,
                               "Pattern": re.compile("\s+qgf8_3mulv\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                               "Params": 0},
                "qgf8_4mulv": {"Cycles": 1,
                               "Exec": None,
                               "Pattern": re.compile("\s+qgf8_4mulv\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                               "Params": 0},
                "qmds4"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmds4\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qmds8"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmds8\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},		
                "qmds16"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qmds16\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},										  
                "qgfmulx"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qgfmulx\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},		
                "qgfmul8x"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qgfmul8x\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},		
                "qgfmulb"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qgfmulb\s+(\w+)\,\s+(\w+)\,\s+(.+)") ,
                                  "Params"  : 0},	
                "qgfmulc"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qgfmulc\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qgf8_matc"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qgf8_matc\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qgf8_mat"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qgf8_mat\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qgf8_matcv"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qgf8_matcv\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qgf8_matv"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qgf8_matv\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qbfmul32l"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qbfmul32l\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qbfmul32h"      :   { "Cycles"  : 1                ,
                                  "Exec"    : None              ,
                                  "Pattern" : re.compile("\s+qbfmul32h\s+(\w+)\,\s+(\w+)\,\s+(\w+)") ,
                                  "Params"  : 0},
                "qslfsr128": {"Cycles": 1,
                               "Exec": None,
                               "Pattern": re.compile("\s+qslfsr128\s+(\w+)\,\s+(\w+)"),
                               "Params": 0},
                "qslfsr256": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qslfsr256\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qslfsr512": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qslfsr512\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qdlfsr128": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qdlfsr128\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qdlfsr256": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qdlfsr256\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qdlfsr512": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qdlfsr512\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qnlfsr128": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qnlfsr128\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qnlfsr256": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qnlfsr256\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qnlfsr512": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qnlfsr512\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qsfcsr128": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qsfcsr128\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qsfcsr256": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qsfcsr256\s+(\w+)\,\s+(\w+)"),
                              "Params": 0},
                "qsfcsr512": {"Cycles": 1,
                              "Exec": None,
                              "Pattern": re.compile("\s+qsfcsr512\s+(\w+)\,\s+(\w+)\,\s+(\w+)"),
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
            
        