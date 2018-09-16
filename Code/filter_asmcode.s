
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
    sub      s0, s0, t0
    bnez     s0, Loop_mul
    ret

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

one_kernel_row_cycle:
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
    mv       ra, s15
    ret

weights_sum:
    setvl    t0, s18
    vld      v0, s19
    vld      v1, s20
    vadd     v2, v1, v0
    vst      v2, s20
    add      s19, s19, t0
    add      s20, s20, t0
    sub      s18, s18, t0
    bnez     s18, weights_sum
    ret

main:
    li       s8, 256
    li       s9, 6225
    li       s10, 6400
    li       s11, 43345
    li       s16, 6481
    li       s17, 44641
    mv       s19, s11
    addi     s20, s17, 9
    li       s22, 16
    li       s12, 9
    li       s13, 144
    li       s14, 2304
    li       v4, 0
    mv       s1, s9
    mv       s3, s11
    mv       s21, s12
Cycle:
    mv       s0, s8
    add      s1, s1, s8
Mem_clear2:
    setvl    t0, s0
    vst      v4, s3
    mv       t1, s12
    bneq     s10, s16, call_one_kernel_row_cycle
    subi     s10, s10, 81 
call_one_kernel_row_cycle:
    addi     s15, PC, 2
    call     one_kernel_row_cycle
    addi     s11, s11, 1
    addi     s13, s13, -1
    bnez     s13, Cycle
weights_sum_0_2_15:
    mv       s18, s12
    sub      s20, s20, s12 
    addi     ra, PC, 2
    call     weights_sum
    addi     s21, s21, -1
    bnez     s21, weights_sum_0_2_15
    addi     s20, s20, 9
    mv       s21, s12
    addi     s22, s22, -1
    bnez     s22, weights_sum_0_2_15
end:
