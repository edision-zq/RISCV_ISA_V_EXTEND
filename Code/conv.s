# define the function of pairwise-multiple
Loop_mul:
    setvl   t0, a0
    vld     v0, a1
    vld     v2, a2
    vmul    v1, v0, v2
    vst     v1, a3
    add     a1, a1, t0
    add     a2, a2, t0
    add     a3, a3, t0
    sub     a0, a0, t0
    bnez    a0, Loop_mul
    ret
# rearrange the input data
Loop_input_index:
    setvl   t0, a0
    vld     v0, a1
    vld     v2, a2
    vadd    v1, v0, v2
    vldx    v1, v1
    vst     v1, a3
    add     a1, a1, t0
    add     a2, a2, t0
    add     a3, a3, t0
    sub     a0, a0, t0
    bnez    a0, Loop_input_index
    ret
# the sum of one lane
Lane_sum:
    setvl   t0, a0
# t0 = MAXLANES

# 4 + 4	
    srli    a0, a0, 1
    setvl   t0, a0
    vld     v0, a1
    add     a1, a1, a0
    vld     v1, a1
    vadd    v1, v0, v1
    sub     a1, a1, a0
    vst     v1, a1
# 2 + 2
    srli    a0, a0, 1
    setvl   t0, a0
    vld     v0, a1
    add     a1, a1, a0
    vld     v1, a1
    vadd    v1, v0, v1
    sub     a1, a1, a0
    vst     v1, a1
# 1 + 1
    srli    a0, a0, 1
    setvl   t0, a0
    vld     v0, a1
    add     a1, a1, a0
    vld     v1, a1
    vadd    v1, v0, v1
    sub     a1, a1, a0
    vst     v1, a1
    ret
	
main:
# vcfg 3*V32bINT
# fetch the width and length of feature-array
    ld      s0, -14(sp)
    li      s1, -13(sp)
# fetch the width and length of kernel-array
    ld      s2, -12(sp)
    ld      s3, -11(sp)
    mul     s8, s2, s3
    mv      a0, s8
# fetch stride and pad
    ld      s4, -10(sp)
    ld      s5, -9(sp)
# compute the width and length of output-array
# maybe can compute previously
#    sub     s6, s0, s2
#    slli    s7, s5, 1
#    add     s6, s6, s7
#    div     s6, s4
#    addi    s6, s6, 1
#    mv      s9, s6
#    sub     s6, s1, s3
#    slli    s7, s5, 1
#    add     s6, s6, s7
#    div     s6, s4
#    addi    s6, s6, 1
#    mul     s6, s6, s9
    ld      s9, -8(sp)
    ld      s6, -7(sp)
    mul     s6, s6, s9

convolution:
# address of initial feature-array(index) 
    li      a1, -32
# address of stride
    li      a2, -23
# address of dest
    li      a3, 34
    mv      s0, s8
Cycle:
    mv      s10, mvl
    mv      s8, s0
# address of being arranged
    mv      a4, a1
    addi    ra, PC, 2    
    call    Loop_input_index
# previously stored in memory(kernel-array)
    li      a1, 24        	
    mv      a2, a3
    addi    ra, PC, 2
    call    Loop_mul
# prepare for sum	
    mv      a5, a0
    div     s8, s10
    addi    a1, a3, 0
    addi    a2, a3, 8
    vld     v1, a1
    li      a0, 8
    setvl   t0, a0	
Lanes_merge:
    vld     v2, a2	
    vadd    v1, v1, v2
    addi    a2, a2, 8
    addi    s8, s8, -1
    bnez    s8, Lanes_merge
    setvl   t0, s10
    vld     v2, a2
    setvl   t0, a0
    vadd    v1, v1, v2
    mv      a2, a1
    addi    ra, PC, 2
    call    Lane_sum
	
    subi    s6, s6, 1
    addi    a1, a4, 1
    addi    a3, a3, 1
    mv      a0, a5
    bnez    s6, Cycle
end:






	
    