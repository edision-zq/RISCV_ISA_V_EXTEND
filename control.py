import os
for i in range(2):
    os.system('C:\\Users\\zhangquan\\Anaconda3\\python.exe initialize.py')
    os.system('C:\\Users\\zhangquan\\Anaconda3\\python.exe convolution.py')
    os.system('C:\\Users\\zhangquan\\Anaconda3\\python.exe MyCodeTEST.py')
file_expect = open('./Result/expect_result.data')
file_actual = open('./Result/actually_result.data')
expect = file_expect.readlines()
actual = file_actual.readlines()
if expect==actual:
    print('the comparsion of expect and actual is successful!')
else:
    raise FError('Result compared failed!!!!!!!!!!')