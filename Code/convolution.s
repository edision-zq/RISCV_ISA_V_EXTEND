# Assuming the lane is N(N is defined by customed hardware and can be configured)

# define the function of pairwise-multiple and the merge of Lanes
Loop_mul:
    setvl    t0, a0
    vld      v0, a1
    vld      v1, a2
    vld      v2, a3
    vmul     v3, v0, v1
    vadd     v3, v3, v2
    vst      v3, a3
    add      a1, a1, t0
    add      a2, a2, t0
#    add      a3, a3, t0
    sub      a0, a0, t0
    bnez     a0, Loop_mul
    ret

# the sum of lane(configured with 2^n)	
Lane_sum:
    srli     a0, a0, 1
    setvl    t0, a0
    vld      v0, a1
    add      a1, a1, a0
    vld      v1, a1
    vadd     v0, v0, v1
    sub      a1, a1, a0
    vst      v0, a1
    srli     s2, a0, 1
    bnez     s2, Lane_sum
    ret

# Mem_clear:
#    setvl    t0, a0
#    vst      v4, a1
#    ret
    

main:
# initialized address of index feature-array
    li       s0, 6400
# address of destination
    li       a3, 8785
# counter
    li       s1, 9
# used for clear memory
    li       v4, 0
# initialized applied length
    li       a0, 256
kernel_cycle:
# the address of kernel-array
    li       a1, 6481
# the address of index feature-array
    ld       a2, 0(s0)
    addi     ra, PC, 2	
    call     Loop_mul
    mv       a0, mvl
#    sub      a3, a3, a0
    mv       a1, a3
    addi     ra, PC, 2
    call     Lane_sum
# configured data length
    li       a0, 256
    addi     a3, a3, 1
    addi     s0, s0, 1

Mem_clear:
    setvl    t0, a0
    vst      v4, a3

    addi     s1, s1, -1
    bnez     s1, kernel_cycle
end:
        