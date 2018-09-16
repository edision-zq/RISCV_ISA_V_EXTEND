# Assuming the lane is N(N is defined by customed hardware and can be configured)

# define the function of pairwise-multiple and the merge of Lanes
Loop_mul:
    setvl    t0, s0
    vld      v0, s1
    vld      v1, s2
    vld      v2, s3
    vmul     v3, v0, v1
    vadd     v3, v3, v2
    vst      v3, s3
    add      s1, s1, t0
    add      s2, s2, t0
#    add      a3, a3, t0
    sub      s0, s0, t0
    bnez     s0, Loop_mul
    ret

# the sum of lane(configured with 2^n)	
Lane_sum:
    srli     s4, s4, 1
    setvl    t0, s4
    vld      v0, s5
    add      s5, s5, s4
    vld      v1, s5
    vadd     v0, v0, v1
    sub      s5, s5, s4
    vst      v0, s5
    srli     s6, s4, 1
    bnez     s6, Lane_sum
    ret

# just for one point
one_kernel_row_cycle:
#    li       s0, 256
#    li       s1, # kernel-array
#    li       s2, # feature-array
#    li       s3, # destination
    ld       s2, 0(s10)
    addi     ra, PC, 2
    call     Loop_mul
    mv       s4, mvl
    mv       s5, s3
    addi     ra, PC, 2
    call     Lane_sum
    li       s0, 256
    addi     s3, s3, 1
    addi     s10, s10, 1
Mem_clear1:
    setvl    t0, s0
    vst      v4, s3
    addi     t1, t1, -1
    sub      s1, s1, s8
    bnez     t1, one_kernel_row_cycle
#    sub      s5, s3, s12
#    mv       s4, mvl
#    addi     ra, PC, 2
#    call     Lane_sum
    mv       ra, s15
    ret

main:
# initialized parameter
    li       s8, 256
    li       s9, 6225
    li       s10, 6400
    li       s11, 8776
# inter and outer counter
    li       s12, 9
    li       s13, 9
    li       s14, 2304
    li       v4, 0
    mv       s1, s9
    addi     s3, s11, 9
Cycle:
    mv       s0, s8
    add      s1, s1, s8
#    ld       s2, 0(s10)
#    addi     s3, s11, 9
Mem_clear2:
    setvl    t0, s0
    vst      v4, s3
    mv       t1, s12
    addi     s15, PC, 2
    call     one_kernel_row_cycle
#    add      s10, s12, s10
    addi     s11, s11, 1
    addi     s13, s13, -1
    bnez     s13, Cycle
#Mem_clear3:
#    addi     s11, s11, 1
#    setvl    t0, s8
#    vst      v4, s11	
end:
        