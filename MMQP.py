from math import *
import random
from Crypto.Util import *
def Ext_Euclid(a, b):
    if (b == 0):
        return 1, 0, a
    else:
        x, y, q = Ext_Euclid(b, a%b)
        x, y = y, x-(a//b)*y
        return x, y, q

def MMQP(A, B, P1, P2, P, n, r):
    """
    Montgomery Modular Multiplication With Quotient Pipelining Algorithm
    r is the radix
    """

    assert A  < 2**(r+2)*P, "Input Out of Range \n"
    assert B  < 2**(r+2)*P, "Input Out of Range \n"
    assert ceil(log(P, 2))+r < n*r-2, "Input Out of Range \n"

    Z = 0
    Q1 = 0 
    Q2 = 0 
    for i in range(n+1):
      #  print("i=%s Z=%x" %(i,Z))
        Q2 = Z%(2**r)
        Z = (Z>>r) 
     #   print("i=%s Z-shift=%x" %(i,Z))
        Z = Z + A*((B>>(i*r))%(2**r)) 
     #   print("i=%s Z-add=%x" %(i,Z))
        Z = Z + Q1*P2
        Q1 = Q2
    Z = Z + Q1*P1
    return Z


if __name__ == '__main__':
    #P = 2**192-2**64-1
    #P=0x24000000004c809168003cf6e7be9c53079b1db804b96af6e7f8a59fb181f9967
    #curve is y^2=x^3+  and y^2=x^3+(0,5) ,beita=-2 
    u=0x600000000058F98A
    P=82434016654578246444830763105245969129603161266935169637912592173415460324733
    n = 12
    r = 24
    R = 2**(n*r)
    (R_inv, P_dot, gcd_R_P) = Ext_Euclid(R, P)
    P1 = (((-P_dot)%(2**r))*P+1)>>r
    P2 = (((-P_dot)%(2**(2*r)))*P+1)>>(2*r)
    
    #A = random.randint(0, P*(2**(r+2)))
    #B = random.randint(0, P*(2**(r+2)))  
    A=0x7402ee1901ae164e5d7beb439b979b94afc212e447ef4f37ab5ea39479729a4ddfb704
    B=0x98d5df25579d1e07ad44d084cb11dfe7dda45172ca3503740f14d12695a915c5
    x=(P-1)*R%P
    y=2*R%P
    z=R%P
    
    x_mont=0x28bcf72fc5b8e4092e32397ac02280172574c78ea210a0010c5f4aaf4907b40593c065a
    y_mont=0x2bd1e7c9e5308654a9a790d69a7ab1c1d792691fa7560e39f5ce693fb42bf6563d31a47
    z_mont=0x5979cd35014bb64388fdc11ffa87d464487e6926fd5d9b6ce427074c4efd34d4ba3128
    x_ref=x_mont*number.inverse(R,P)%P
    x_montR=MMQP(x_mont, 1, P1, P2, P, n, r)%P
    y_montR=MMQP(y_mont, 1, P1, P2, P, n, r)%P
    z_montR=MMQP(z_mont, 1, P1, P2, P, n, r)%P

    Z = MMQP(A, B, P1, P2, P, n, r)

    if ((A*B)%P)==((Z*R)%P) and Z < P*(2**(r+2)):
        print("Pass")
    Z = MMQP(x, y, P1, P2, P, n, r)
    Z = MMQP(Z, 1, P1, P2, P, n, r)%P
    print("%x"%Z)
    print("%x"%(-2%P))
    print("x=%x"%x)
    print("y=%x"%y)
    print("z=%x"%z)
    
    
    print('p1=',P1)
    print(P2)