# Tiny8 CPU with SPI program load and internal execution

## Overview

This project implements a compact 8-bit CPU for Tiny Tapeout.  
The processor loads a short program through SPI into an internal instruction memory, and then executes that program autonomously.

The final stable version uses:

- an 8-bit accumulator (`ACC`)
- one auxiliary 8-bit register (`R1`)
- a 10-word internal program memory
- a compact instruction set with arithmetic, logic, branch, output, and simple register transfer operations

The design was optimized to remain compatible with a 1x1 Tiny Tapeout tile while still supporting programmable behavior.

---

## Architecture

The design is split into the following RTL blocks:

- `alu8.v`  
  8-bit ALU used for arithmetic and logic operations.

- `tiny8_cpu.v`  
  CPU core implementing program sequencing, decoding, branching, and output behavior.

- `tiny8_prgmem.v`  
  Internal instruction memory with 10 instruction slots.

- `tiny8_spi_loader.v`  
  SPI-based loader that receives instruction frames and writes them into program memory.

- `tt_um_tiny8_risclike.v`  
  Tiny Tapeout top wrapper integrating loader, memory, CPU, and IO mapping.

---

## Operating principle

### Program load phase
When `RUN=0`, the SPI loader is allowed to write instructions into internal memory.

Each SPI frame is 24 bits:

- upper byte: address byte
- lower 16 bits: instruction word

Only addresses `0..9` are valid in the final stable implementation.

### Execution phase
When `RUN=1`, the CPU starts executing from address `0`.

The program counter wraps around inside the valid program space, and branch targets outside the valid range are redirected safely.

---

## Instruction set

The final stable ISA includes:

- `NOP`
- `LDI_ACC`
- `LDI_R1`
- `ADD`
- `SUB`
- `AND`
- `OR`
- `XOR`
- `CMP`
- `OUT`
- `JMP`
- `BZ`
- `BNZ`
- `HALT`
- `MOV_ACC_R1`
- `OUT_R1`

### Added enriched ISA instructions
The final enriched version adds:

- `MOV_ACC_R1`  
  Copies `R1` into `ACC`

- `OUT_R1`  
  Sends `R1` directly to the external output port

These instructions increase expressiveness without significantly increasing hardware complexity.

---

## IO behavior

### Dedicated inputs
- `ui[0]` = `RUN`

### Dedicated outputs
- `uo[7:0]` = CPU output port

### Bidirectional bank usage
- `uio[0]` = `SPI_SCK` input
- `uio[1]` = `SPI_CS_N` input
- `uio[2]` = `SPI_MOSI` input
- `uio[3]` = `PROGRAM_LOADED` output
- `uio[4]` = `HALTED` output
- `uio[5]` = `RUN_ECHO` output

---

## Example program

A simple test program can be loaded as:

- `0: LDI_R1 0x33`
- `1: MOV_ACC_R1`
- `2: OUT`
- `3: OUT_R1`
- `4: HALT`

This demonstrates:

- SPI loading
- register transfer
- output behavior
- HALT state signaling

---

## Final stable configuration

The version documented here corresponds to the stable implementation that successfully balanced:

- programmability
- compact area usage
- enriched ISA
- internal instruction storage
- Tiny Tapeout 1x1 compatibility
