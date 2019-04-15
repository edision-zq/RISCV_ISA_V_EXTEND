main:
move $v0, $0
addi $a0, $0, 32766
addi $a1, $0, 32767
beq $a0, $0, endofmult
beq $a1, $0, endofmult

move $s0, $a0		
move $s1, $a1		
move $s2, $0		

move $s3, $0
move $s4, $0

loop:
andi $t0, $s0, 1
beq $t0, $0, adjust
add $s3, $s3, $s1
sltu $t1, $s3, $s1
addu $s4, $s4, $t1
addu $s4, $s4, $s2

adjust:
srl $t2, $s1, 31
sll $s1, $s1, 1
sll $s2, $s2, 1
addu $s2, $s2, $t2
srl $s0, $s0, 1
bne $s0, $0, loop

endofmult:
move $v0, $s4
end:
