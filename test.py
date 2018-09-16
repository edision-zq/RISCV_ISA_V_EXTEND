import fileinput
import re
from Crypto.Util import *
from MMQP
import MyCodeTEST
from bitarray import bitarray
def bit8(data):
    tempt = ((bin(data)[2:])[::-1])+'00000000'
    result = bitarray(tempt)
    return result

def bit16(data):
    tempt = ((bin(data)[2:])[::-1])+'0000000000000000'
    result = bitarray(tempt)
    return result
	
def bit32(data):
    tempt = ((bin(data)[2:])[::-1])+'00000000000000000000000000000000'
    result = bitarray(tempt)
    return result

def qand(rs1, rs2):
    rd_qand = rs1 & rs2
    return rd_qand
	
def qand64(rs1, rs2, rs3, rs4):
    rd1_qand64 = rs1 & rs3
    rd2_qand64 = rs2 & rs4
    return rd1_qand64, rd2_qand64
	
def qand128(rs1, rs2, rs3, rs4, rs5, rs6, rs7, rs8):
    rd1_qand128 = rs1 & rs5
    rd2_qand128 = rs2 & rs6
    rd3_qand128 = rs3 & rs7
    rd4_qand128 = rs4 & rs8
    return rd1_qand128, rd2_qand128, rd3_qand128, rd4_qand128
	
def qor(rs1, rs2):
    rd_qor = rs1 | rs2
    return rd_qor
	
def qor64(rs1, rs2, rs3, rs4):
    rd1_qor64 = rs1 | rs3
    rd2_qor64 = rs2 | rs4
    return rd1_qor64, rd2_qor64
	
def qor128(rs1, rs2, rs3, rs4, rs5, rs6, rs7, rs8):
    rd1_qor128 = rs1 | rs5
    rd2_qor128 = rs2 | rs6
    rd3_qor128 = rs3 | rs7
    rd4_qor128 = rs4 | rs8
    return rd1_qor128, rd2_qor128, rd3_qor128, rd4_qor128
	
def qxor(rs1, rs2):
    rd_qxor = rs1 ^ rs2
    return rd_qxor
	
def qxor64(rs1, rs2, rs3, rs4):
    rd1_qxor64 = rs1 ^ rs3
    rd2_qxor64 = rs2 ^ rs4
    return rd1_qxor64, rd2_qxor64
	
def qxor128(rs1, rs2, rs3, rs4, rs5, rs6, rs7, rs8):
    rd1_qxor128 = rs1 | rs5
    rd2_qxor128 = rs2 | rs6
    rd3_qxor128 = rs3 | rs7
    rd4_qxor128 = rs4 | rs8
    return rd1_qxor128, rd2_qxor128, rd3_qxor128, rd4_qxor128
	
def qnot(rs):
    rd_qnot = int('0xffffffff', 16) - rs
    return rd_qnot
	
def qnot64(rs1, rs2):
    rd1_qnot64 = int('0xffffffff', 16) - rs1
    rd2_qnot64 = int('0xffffffff', 16) - rs2
    return rd1_qnot64, rd2_qnot64
	
def qnot128(rs1, rs2, rs3, rs4):
    rd1_qnot128 = int('0xffffffff', 16) - rs1
    rd2_qnot128 = int('0xffffffff', 16) - rs2
    rd3_qnot128 = int('0xffffffff', 16) - rs3
    rd4_qnot128 = int('0xffffffff', 16) - rs4
    return rd1_qnot128, rd2_qnot128, rd3_qnot128, rd4_qnot128
	
def qcmp(rs1, rs2):
    if rs1 >= rs2:
        rd_qcmp = 0
    else:
        rd_qcmp = 1
    return rd_qcmp
	
def qcmp64(rs1, rs2, rs3, rs4):
    s1_64 = rs1 * pow(2, 32) + rs2
    s2_64 = rs3 * pow(2, 32) + rs4
    if s1_64 >= s2_64:
        rd_qcmp64 = 0
    else:
        rd_qcmp64 = 1
    return rd_qcmp64
	
def qcmp128(rs1, rs2, rs3, rs4, rs5, rs6, rs7, rs8):
    s1_128 = rs1 * pow(2, 96) + rs2 * pow(2, 64) + rs3 * pow(2, 32) + rs4
    s2_128 = rs5 * pow(2, 96) + rs6 * pow(2, 64) + rs7 * pow(2, 32) + rs8
    if s1_128 >= s2_128:
	    rd_qcmp128 = 0
    else:
	    rd_qcmp128 = 1
    return rd_qcmp128
	
def qtli(rs1, rs2, rs3, imm):
    if imm>255:
	    return False
    else:
        log = bit8(imm)
        A = rs1
        B = rs2
        C = rs3
        result = ((log[7] & A & B & C) | (log[6] & A & B & qnot(C)) | 
		(log[5] & A & qnot(B) & C) | (log[4] & A & qnot(B) & qnot(C)) | 
		(log[3] & qnot(A) & B & C) | (log[2] & qnot(A) & B & qnot(C)) |
		(log[1] & qnot(A) & qnot(B) & C) | (log[0] & qnot(A) & qnot(B) & qnot(C)) )
        return result
		
def qtl(rs1, rs2, rs3, rs4):
    if rs4>255:
	    return False
    else:
        log = bit8(rs4)
        A = rs1
        B = rs2
        C = rs3
        result = ((log[7] & A & B & C) | (log[6] & A & B & qnot(C)) | 
		(log[5] & A & qnot(B) & C) | (log[4] & A & qnot(B) & qnot(C)) | 
		(log[3] & qnot(A) & B & C) | (log[2] & qnot(A) & B & qnot(C)) |
		(log[1] & qnot(A) & qnot(B) & C) | (log[0] & qnot(A) & qnot(B) & qnot(C)) )
        return result   

def qsxor(rd.j, rs1, rs2):
    s = str(rd.j)
    index = s.find('.')
    j = int(s[index+1:], 10)
    rd = s[0:index+1]
    tempt = 0
    log2 = bit32(rs2)
    log1 = bit32(rs1)
    for i in range(32) :
        if log2[i]:
		    tempt = tempt ^ log1[i]
    result = tempt * pow(2, j)
    return result
	
def qsxor64(rd.j, rs1, rs2, rs3, rs4):
    s = str(rd.j)
    index = s.find('.')
    j = int(s[index+1:], 10)
    rd = s[0:index+1]
    tempt = 0
    log2 = bit32((rs3<<32) + (rs4))
    log1 = bit32((rs1<<32) + (rs2))
    for i in range(64) :
        if log2[i]:
		    tempt = tempt ^ log1[i]
    result = tempt * pow(2, j)
    return result
	
def qsxor128(rd.j, rs1, rs2, rs3, rs4, rs5, rs6, rs7, rs8):
    s = str(rd.j)
    index = s.find('.')
    j = int(s[index+1:], 10)
    rd = s[0:index+1]
    tempt = 0
    log2 = bit32((rs5<<96) + (rs6<<64) + (rs7<<32) + rs8)
    log1 = bit32((rs1<<96) + (rs2<<64) + (rs3<<32) + rs4)
    for i in range(128) :
        if log2[i]:
		    tempt = tempt ^ log1[i]
    result = tempt * pow(2, j)
    return result
	
