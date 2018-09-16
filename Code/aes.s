main:
#input initial key:
    add      sp, sp, 232
    ld32     s3, 3(sp) 
    # 0x00010203  
    ld32     s2, 2(sp) 
	# 0x04050607   
    ld32     s1, 1(sp) 
	# 0x08090a0b   
    ld32     s0, 0(sp) 
	# 0x0c0d0e0f
    add      sp, sp, -232
	
    li       s6, 0 
#counter for cycle:
    li       s7, 9

    add      sp, sp, 256 
#initialize LUT_8m8:
    flkt8m8  0(sp)
    add      sp, sp, -256	
    
    add      sp, sp, 320
    add      s8, sp, -84
Key_production:
    qirol32  s5, s0, 8
    qlut8m8  s5, s5
    ld32     s4, 0(s8)
    qxor     s5, s5, s4
    qxor     s3, s5, s3
    qxor     s2, s3, s2
    qxor     s1, s2, s1
    qxor     s0, s1, s0 
	# once round key has been produced
    sd32     s3, 3(sp)       	
    sd32     s2, 2(sp)      	
    sd32     s1, 1(sp)      	
    sd32     s0, 0(sp)
    add      sp, sp, 4
    add      s6, s6, 1
    add      s8, s8, 1
    ble      s6, s7, Key_production
	# the result stored in sp+256 to sp+296(sp = 3600)     
    add      sp, sp, -360 
	
# input plaintext and initial key
    add      sp, sp, 248
    ld128    v1, 0(sp)
    ld128    v2, -16(sp)
    add      sp, sp, -248

    li s6, 0 
	# flash count register 

Round_0:
    qxor128  v1, v1, v2 
    add      s0, sp, 200
    add      sp, sp, 320
Round_1_to_10:
    ld128    v2, 0(sp)
# get x round key
    q4lut8m8 v1, v1
# S-box    
# rows-shift is realized by push and pop operation
    sd128    v1, 0(s0)
    ld256    v4, 0(s0)
    qgf8_matv v4, v4
# first row shifts 0
    sd128    v1, 8(s0)
    ld256    v5, 8(s0)
    qgf8_matv v5, v5
    sd128    v5, 40(sp)
    ld32     s1, 40(sp)	
    ld32     s2, 41(sp)	
    ld32     s3, 42(sp)	
    ld32     s4, 43(sp)
    sd32     s4,  40(sp)	
    sd32     s1,  41(sp)	
    sd32     s2,  42(sp)	
    sd32     s3,  43(sp)
    ld128    v5, 40(sp)
# second row shifts 1
    sd128    v1, 16(s0)
    ld256    v6, 16(s0)
    qgf8_matv v6, v6
    sd128    v6, 40(sp)
    ld32     s1, 40(sp)	
    ld32     s2, 41(sp)	
    ld32     s3, 42(sp)	
    ld32     s4, 43(sp)
    sd32     s3, 40(sp)
    sd32     s4, 41(sp)
    sd32     s1, 42(sp)
    sd32     s2, 43(sp)
    ld128    v6, 40(sp)
# third row shifts 2
    sd128    v1, 24(s0)
    ld256    v7, 24(s0)
    qgf8_matv v7, v7
    sd128    v7, 40(sp)
    ld32     s1, 40(sp)	
    ld32     s2, 41(sp)	
    ld32     s3, 42(sp)	
    ld32     s4, 43(sp)
    sd32     s2, 40(sp)
    sd32     s3, 41(sp)
    sd32     s4, 42(sp)
    sd32     s1, 43(sp)
    ld128    v7, 40(sp)
# third row shifts 3
    qor128   v5, v4, v5
    qor128   v7, v6, v7
    qor128   v1, v5, v7
# get rows-shift results
    beq      s6, s7, add_key
    qgf8_matcv   v1, v1
# mix columns:
add_key:
    qxor128  v1, v2, v1
# add round key 
    add      s6, s6, 1
    add      sp, sp, 4
    ble      s6, s7, Round_1_to_10
    add      sp, sp, -360
result_store:
    sd128    v1, 360(sp)
nop: