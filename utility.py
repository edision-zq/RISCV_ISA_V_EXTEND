import re
import sys
import fileinput
import numpy as np

def vec(a):
    tempt = np.array([0, 0, 0, 0, 0, 0, 0, 0])
    for i in range(8):
        tempt[i] = (a>>(32*i)) & (0xffffffff>>1)
# should be careful, tempt[i]<sys.maxsize
    result = tempt
    return result

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

def mask_op(data, mask):
    coff = bit32(mask)
    result = 0
    for i in range(32):
        if coff[i] :
            result = result + (data & 0xff<<(i*8))
    return result

def read_mif(File, twos_complement=False):
    try:
        hfile = open(File)
    except Exception as e:
        print(e)
        sys.exit()

    line = ""
    # Data Width
    while re.match(r'^\s*$', line):
        line = hfile.readline().strip()
    data_width = re.match(r'\s*WIDTH\s*=\s*(\d+)\s*;\s*',  line).groups(1)

    # Data Depth
    line = hfile.readline().strip()
    while re.match(r'^\s*$', line):
        line = hfile.readline().strip()
    data_depth = re.match(r'\s*DEPTH\s*=\s*(\d+)\s*;\s*', line).group(1)

    # Address Radix
    line = hfile.readline().strip()
    while re.match(r'^\s*$', line):
        line = hfile.readline().strip()
    address_radix = re.match(r'\s*ADDRESS_RADIX\s*=\s*(\w+)\s*;\s*', line).group(1)

    # Data Radix
    line = hfile.readline().strip()
    while re.match(r'^\s*$', line):
        line = hfile.readline().strip()
    data_radix = re.match(r'\s*DATA_RADIX\s*=\s*(\w+)\s*;\s*', line).group(1)

    line = hfile.readline().strip()
    while re.match(r'^\s*$', line):
        line = hfile.readline().strip()
    assert re.match(r'\s*CONTENT\s*BEGIN\s*', line), "mif file format error: mif file format error\n"

    assert data_radix == address_radix, "mif file format error: data radix and address radix should be consistent with eachother\n"

    if twos_complement:
        pattern_hex = re.compile(r'\s*([A-Fa-f0-9]+)\s*:\s*([A-Fa-f0-9]+)\s*;\s*') 
        pattern_bin = re.compile(r'\s*([0-1]+)\s*:\s*([0-1]+)\s*;\s*')
    else:
        pattern_hex = re.compile(r'\s*([A-Fa-f0-9]+)\s*:\s*([+-]?[A-Fa-f0-9]+)\s*;\s*') 
        pattern_bin = re.compile(r'\s*([0-1]+)\s*:\s*([+-]?[0-1]+)\s*;\s*')

    mem = {}
    line_cnt = 0
    line = hfile.readline().strip()
    while not re.match(r'\s*END\s*;\s*', line):
        while re.match(r'^\s*$', line):
            line = hfile.readline().strip()
        if(address_radix == "HEX" and data_radix == "HEX"):
            match_line = pattern_hex.match(line)
            assert int(match_line.group(1), 16) == line_cnt, "mif file format error: memory address error at address: " + str(line_cnt)
            mem[int(match_line.group(1), 16)] = int(match_line.group(2), 16)
        else:
            match_line = pattern_bin.match(line)
            assert int(match_line.group(1), 2) == line_cnt, "mif file format error: memory address error at address: " + str(line_cnt)
            mem[int(match_line.group(1), 2)] = int(match_line.group(2), 2)
        line_cnt = line_cnt + 1
        line = hfile.readline().strip()
    assert line_cnt == int(data_depth), "mif file format error: memory size does not consist with the memory depth "

    hfile.close()
    return mem




def write_mif(mem_file, mem={}, data_width=256, radix="HEX", twos_complement=False):
    try:
        hfile = open(mem_file, 'w')
    except Exception as e:
        print(e)
        sys.exit()

    mif_string = ""
    mif_string = mif_string + "WIDTH = " + str(data_width) + ";\n"
    mif_string = mif_string + "DEPTH = " + str(max(mem.keys())+1) + ";\n\n"
    mif_string = mif_string + "ADDRESS_RADIX = " + radix + ";\n"
    mif_string = mif_string + "DATA_RADIX = " + radix + ";\n\n"
    mif_string = mif_string + "CONTENT BEGIN" + "\n"
    for add in range(max(mem.keys())+1):
        if add in mem.keys():
            if twos_complement:
                data = ((1<<data_width)+mem[add])%(1<<data_width)
                mif_string = mif_string + hex(add)[2:].strip("L") + " : " + hex(data)[2:].strip("L") + ";\n"
            else:
                if (not (add in list(mem.keys()))) :
                    mif_string = mif_string + hex(add)[2:].strip("L") + " : " + hex(0x0)[2:] + ";\n"
                elif mem[add] < 0:
                    mif_string = mif_string + hex(add)[2:].strip("L") + " : " + "-" + hex(abs(mem[add]))[2:].strip("L") + ";\n"
                else:
                   mif_string = mif_string + hex(add)[2:].strip("L") + " : " + hex(mem[add])[2:].strip("L") + ";\n"     
        else:
            mif_string = mif_string + hex(add)[2:].strip("L") + " : " + hex(0)[2:].strip("L") + ";\n"
    mif_string = mif_string + "END;"

    hfile.write(mif_string)
    hfile.close()

# def check_result(src_file, dst_file,  addr_begin=0, addr_end=0):
def check_result(src_file, dst_file,  addr_chk, width=256):
    src_mem = read_mif(src_file)
    dst_mem = read_mif(dst_file)

    if (len(addr_chk)==0):
        raise Exception("no address for checking!")

    for (addr_begin, addr_end) in addr_chk:
        check = True
        for addr in range(addr_begin, addr_end):
            if (src_mem[addr]&((1<<width)-1)) != (dst_mem[addr]&((1<<width)-1)):
               check = False
    
    return check    

def filter_asmCode(src_file,dir_file):
    filter_asmcode=[]
    for line in fileinput.input(src_file):
      filter_asmcode.append(line.strip("\n,\r"))
    write_file=open(dir_file,'w')
    for i in filter_asmcode:
        if re.match('\s*#', i):
            pass
        elif re.match('\s+\.',i) or i.find('%hi')!=-1 or i.find('%lo')!=-1:
            pass
        elif re.match('[^#].+:',i) and i.find('#')!=-1:
            temp=i[:i.find(':')+1]
            write_file.write(temp+'\n')
        else:
            write_file.write(i+'\n')
    write_file.close()

if __name__ == '__main__':
    __doc__ = "Utility for simulator: \n" + \
              "read_mif : used to read memory initialiation file (mif), return dictionry contains the memory contents\n" \
              "write_mif: used to write dictionary variables which conatins memory data to a mif file\n" \
              "filter_asmCode: used to filter the original asmCode\n"
    
    print(__doc__)