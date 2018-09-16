import random
file_init = open('./TestVector/initialize.mif', 'w')
file_init.write('WIDTH = 32;' + '\n')
file_init.write('DEPTH = 50000;' + '\n')
file_init.write('\n')
file_init.write('ADDRESS_RADIX = HEX;' + '\n')
file_init.write('DATA_RADIX = HEX;' + '\n')
file_init.write('\n')
file_init.write('CONTENT BEGIN' + '\n')
for i in range(6400):
    file_init.write(hex(i)[2:] + ' ' + ':' + ' ' + hex(random.randint(0, 255))[2:] + ';' + '\n')
for i in range(6400, 6427, 9):
    file_init.write(hex(i+0)[2:] + ' ' + ':' + ' ' + hex(int((i-6400)/9 + 0)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+1)[2:] + ' ' + ':' + ' ' + hex(int((i-6400)/9 + 1)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+2)[2:] + ' ' + ':' + ' ' + hex(int((i-6400)/9 + 2)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+3)[2:] + ' ' + ':' + ' ' + hex(int((i-6400)/9 + 5)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+4)[2:] + ' ' + ':' + ' ' + hex(int((i-6400)/9 + 6)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+5)[2:] + ' ' + ':' + ' ' + hex(int((i-6400)/9 + 7)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+6)[2:] + ' ' + ':' + ' ' + hex(int((i-6400)/9 + 10)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+7)[2:] + ' ' + ':' + ' ' + hex(int((i-6400)/9 + 11)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+8)[2:] + ' ' + ':' + ' ' + hex(int((i-6400)/9 + 12)*256)[2:] + ';' + '\n')
for i in range(6427, 6454, 9):
    file_init.write(hex(i+0)[2:] + ' ' + ':' + ' ' + hex(int((i-6427)/9 + 5)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+1)[2:] + ' ' + ':' + ' ' + hex(int((i-6427)/9 + 6)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+2)[2:] + ' ' + ':' + ' ' + hex(int((i-6427)/9 + 7)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+3)[2:] + ' ' + ':' + ' ' + hex(int((i-6427)/9 + 10)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+4)[2:] + ' ' + ':' + ' ' + hex(int((i-6427)/9 + 11)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+5)[2:] + ' ' + ':' + ' ' + hex(int((i-6427)/9 + 12)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+6)[2:] + ' ' + ':' + ' ' + hex(int((i-6427)/9 + 15)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+7)[2:] + ' ' + ':' + ' ' + hex(int((i-6427)/9 + 16)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+8)[2:] + ' ' + ':' + ' ' + hex(int((i-6427)/9 + 17)*256)[2:] + ';' + '\n')
for i in range(6454, 6481, 9):
    file_init.write(hex(i+0)[2:] + ' ' + ':' + ' ' + hex(int((i-6454)/9 + 10)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+1)[2:] + ' ' + ':' + ' ' + hex(int((i-6454)/9 + 11)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+2)[2:] + ' ' + ':' + ' ' + hex(int((i-6454)/9 + 12)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+3)[2:] + ' ' + ':' + ' ' + hex(int((i-6454)/9 + 15)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+4)[2:] + ' ' + ':' + ' ' + hex(int((i-6454)/9 + 16)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+5)[2:] + ' ' + ':' + ' ' + hex(int((i-6454)/9 + 17)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+6)[2:] + ' ' + ':' + ' ' + hex(int((i-6454)/9 + 20)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+7)[2:] + ' ' + ':' + ' ' + hex(int((i-6454)/9 + 21)*256)[2:] + ';' + '\n')
    file_init.write(hex(i+8)[2:] + ' ' + ':' + ' ' + hex(int((i-6454)/9 + 22)*256)[2:] + ';' + '\n')
j = 6481
s = 2304
for i in range(j, j+s, 1):
    file_init.write(hex(i)[2:] + ' ' + ':' + ' ' + hex(random.randint(0, 255))[2:] + ';' + '\n')
for k in range(15):
    j = j + s
    for i in range(j, j+s, 1):
        file_init.write(hex(i)[2:] + ' ' + ':' + ' ' + hex(random.randint(0, 255))[2:] + ';' + '\n')

for i in range(43345, 50000, 1):
    file_init.write(hex(i)[2:] + ' ' + ':' + ' ' + '0' + ';' + '\n')
file_init.write('END;')
file_init.close()
