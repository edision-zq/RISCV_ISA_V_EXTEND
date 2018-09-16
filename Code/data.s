# Assuming the Lanes is 8(MVL = 8)
# data need to be store priviously
# the index of first array for feature-array
_InitBegin:
    li      sp, 400
    li      s0, -1
    sw      s0, 0(sp)
    liv     v0, 0x0000_0001_0004_0005_0006_0009_000a_000b
    vst     v0, 1(sp)
# stride (default = 1)
    liv     v0, 0x0001_0001_0001_0001_0001_0001_0001_0001
    vst     v0, 9(sp)
    li      s0, 0x0001
    sw      s0, 17(sp)
# the width and length of feature-array
    li      s0, 5
    sw      s0, 18(sp)
    li      s0, 5
    sw      s0, 19(sp)
# the width and length of kernel-array
    li      s0, 3
    sw      s0, 20(sp)
    li      s0, 3
    sw      s0, 21(sp)
# stride and pad
    li      s0, 1
    sw      s0, 22(sp)
    li      s0, 0
    sw      s0, 23(sp)	
# store feature-array
    add     sp, sp, 32
    liv     v0, 0x0000_0002_0004_0006_0008_0001_0003_0005
    vst     v0, 0(sp)
    liv     v0, 0x0007_0009_0002_0004_0006_0008_000a_0003
    vst     v0, 8(sp)
    liv     v0, 0x0005_0007_0009_000b_0004_0006_0008_000a
    vst     v0, 16(sp)
    li      s0, 0x000c
    sw      s0, 24(sp)
# store kernel-array
    liv     v0, 0x0000_0000_0000_0000_0001_0002_0000_0002
    vst     v0, 25(sp)
    li      s0, 0x0004
    sw      s0, 33(sp)
_InitEnd: