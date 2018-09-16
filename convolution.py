import numpy
import re
file_input = open('./TestVector/initialize.mif')
list = file_input.readlines()
print(list[7])
file_output = open('./Result/expect_result.data', 'a')

F0 = numpy.zeros(256)
F1 = numpy.zeros(256)
F2 = numpy.zeros(256)
F3 = numpy.zeros(256)
F4 = numpy.zeros(256)
F5 = numpy.zeros(256)
F6 = numpy.zeros(256)
F7 = numpy.zeros(256)
F8 = numpy.zeros(256)
F9 = numpy.zeros(256)
F10 = numpy.zeros(256)
F11 = numpy.zeros(256)
F12 = numpy.zeros(256)
F13 = numpy.zeros(256)
F14 = numpy.zeros(256)
F15 = numpy.zeros(256)
F16 = numpy.zeros(256)
F17 = numpy.zeros(256)
F18 = numpy.zeros(256)
F19 = numpy.zeros(256)
F20 = numpy.zeros(256)
F21 = numpy.zeros(256)
F22 = numpy.zeros(256)
F23 = numpy.zeros(256)
F24 = numpy.zeros(256)
K0 = numpy.zeros(256)
K1 = numpy.zeros(256)
K2 = numpy.zeros(256)
K3 = numpy.zeros(256)
K4 = numpy.zeros(256)
K5 = numpy.zeros(256)
K6 = numpy.zeros(256)
K7 = numpy.zeros(256)
K8 = numpy.zeros(256)
j = 7
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F0[i-j] = int(m1.group(4), 16)

j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F1[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F2[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F3[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F4[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F5[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F6[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F7[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F8[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F9[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F10[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F11[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F12[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F13[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F14[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F15[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F16[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F17[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F18[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F19[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F20[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F21[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F22[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F23[i-j] = int(m1.group(4), 16)
	
j = j + 256	
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    F24[i-j] = int(m1.group(4), 16)
	
j = 6488 + 2304
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    K0[i-j] = int(m1.group(4), 16)

j = j + 256
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    K1[i-j] = int(m1.group(4), 16)
	
j = j + 256
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    K2[i-j] = int(m1.group(4), 16)
	
j = j + 256
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    K3[i-j] = int(m1.group(4), 16)
	
j = j + 256
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    K4[i-j] = int(m1.group(4), 16)
	
j = j + 256
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    K5[i-j] = int(m1.group(4), 16)
	
j = j + 256
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    K6[i-j] = int(m1.group(4), 16)
	
j = j + 256
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    K7[i-j] = int(m1.group(4), 16)
	
j = j + 256
for i in range(j, j+256, 1):
    m1 = re.match(r'(\w+)(\s+)\:(\s+)(\w+)', list[i])
    K8[i-j] = int(m1.group(4), 16)

# kernel for once    
F0_K0 = F0 * K0
F1_K0 = F1 * K0
F2_K0 = F2 * K0
F5_K0 = F5 * K0
F6_K0 = F6 * K0
F7_K0 = F7 * K0
F10_K0 = F10 * K0
F11_K0 = F11 * K0
F12_K0 = F12 * K0
# kernel for second	
F1_K1 = F1 * K1
F2_K1 = F2 * K1
F3_K1 = F3 * K1
F6_K1 = F6 * K1
F7_K1 = F7 * K1
F8_K1 = F8 * K1
F11_K1 = F11 * K1
F12_K1 = F12 * K1
F13_K1 = F13 * K1
# kernel for third
F2_K2 = F2 * K2
F3_K2 = F3 * K2
F4_K2 = F4 * K2
F7_K2 = F7 * K2
F8_K2 = F8 * K2
F9_K2 = F9 * K2
F12_K2 = F12 * K2
F13_K2 = F13 * K2
F14_K2 = F14 * K2
# kernel for fourth
F5_K3 = F5 * K3
F6_K3 = F6 * K3
F7_K3 = F7 * K3
F10_K3 = F10 * K3
F11_K3 = F11 * K3
F12_K3 = F12 * K3
F15_K3 = F15 * K3
F16_K3 = F16 * K3
F17_K3 = F17 * K3
# kernel for fifth
F6_K4 = F6 * K4
F7_K4 = F7 * K4
F8_K4 = F8 * K4
F11_K4 = F11 * K4
F12_K4 = F12 * K4
F13_K4 = F13 * K4
F16_K4 = F16 * K4
F17_K4 = F17 * K4
F18_K4 = F18 * K4
# kernel for sixth 
F7_K5 = F7 * K5
F8_K5 = F8 * K5
F9_K5 = F9 * K5
F12_K5 = F12 * K5
F13_K5 = F13 * K5
F14_K5 = F14 * K5
F17_K5 = F17 * K5
F18_K5 = F18 * K5
F19_K5 = F19 * K5
# kernel for seventh
F10_K6 = F10 * K6
F11_K6 = F11 * K6
F12_K6 = F12 * K6
F15_K6 = F15 * K6
F16_K6 = F16 * K6
F17_K6 = F17 * K6
F20_K6 = F20 * K6
F21_K6 = F21 * K6
F22_K6 = F22 * K6
# kernel for eighth
F11_K7 = F11 * K7
F12_K7 = F12 * K7
F13_K7 = F13 * K7
F16_K7 = F16 * K7
F17_K7 = F17 * K7
F18_K7 = F18 * K7
F21_K7 = F21 * K7
F22_K7 = F22 * K7
F23_K7 = F23 * K7
# kernel for nineth
F12_K8 = F12 * K8
F13_K8 = F13 * K8
F14_K8 = F14 * K8
F17_K8 = F17 * K8
F18_K8 = F18 * K8
F19_K8 = F19 * K8
F22_K8 = F22 * K8
F23_K8 = F23 * K8
F24_K8 = F24 * K8

sum0 = F0_K0 + F1_K1 + F2_K2 +F5_K3 + F6_K4 + F7_K5 + F10_K6 + F11_K7 + F12_K8
dot0 = 0
for i in range(256):
    dot0 = dot0 + sum0[i]
print(hex(int(dot0)))

sum1 = F1_K0 + F2_K1 + F3_K2 +F6_K3 + F7_K4 + F8_K5 + F11_K6 + F12_K7 + F13_K8
dot1 = 0
for i in range(256):
    dot1 = dot1 + sum1[i]
print(hex(int(dot1)))

sum2 = F2_K0 + F3_K1 + F4_K2 +F7_K3 + F8_K4 + F9_K5 + F12_K6 + F13_K7 + F14_K8
dot2 = 0
for i in range(256):
    dot2 = dot2 + sum2[i]
print(hex(int(dot2)))

sum3 = F5_K0 + F6_K1 + F7_K2 +F10_K3 + F11_K4 + F12_K5 + F15_K6 + F16_K7 + F17_K8
dot3 = 0
for i in range(256):
    dot3 = dot3 + sum3[i]
print(hex(int(dot3)))

sum4 = F6_K0 + F7_K1 + F8_K2 +F11_K3 + F12_K4 + F13_K5 + F16_K6 + F17_K7 + F18_K8
dot4 = 0
for i in range(256):
    dot4 = dot4 + sum4[i]
print(hex(int(dot4)))

sum5 = F7_K0 + F8_K1 + F9_K2 +F12_K3 + F13_K4 + F14_K5 + F17_K6 + F18_K7 + F19_K8
dot5 = 0
for i in range(256):
    dot5 = dot5 + sum5[i]
print(hex(int(dot5)))

sum6 = F10_K0 + F11_K1 + F12_K2 +F15_K3 + F16_K4 + F17_K5 + F20_K6 + F21_K7 + F22_K8
dot6 = 0
for i in range(256):
    dot6 = dot6 + sum6[i]
print(hex(int(dot6)))

sum7 = F11_K0 + F12_K1 + F13_K2 +F16_K3 + F17_K4 + F18_K5 + F21_K6 + F22_K7 + F23_K8
dot7 = 0
for i in range(256):
    dot7 = dot7 + sum7[i]
print(hex(int(dot7)))

sum8 = F12_K0 + F13_K1 + F14_K2 +F17_K3 + F18_K4 + F19_K5 + F22_K6 + F23_K7 + F24_K8
dot8 = 0
for i in range(256):
    dot8 = dot8 + sum8[i]
print(hex(int(dot8)))

#file_output.write('******************expect_result 0 - 9*******************\n')
#file_output.write(dot0 + '\n')
#file_output.write(dot1 + '\n')
#file_output.write(dot2 + '\n')
#file_output.write(dot3 + '\n')
#file_output.write(dot4 + '\n')
#file_output.write(dot5 + '\n')
#file_output.write(dot6 + '\n')
#file_output.write(dot7 + '\n')
#file_output.write(dot8 + '\n')
#file_output.write('******************results have been written**************\n')
file_input.close()
file_output.close()

