# Tiny8 CPU with SPI Program Load and Internal Execution

This project implements a compact 8-bit CPU in Verilog for Tiny Tapeout.

## Main idea
The processor does not rely on a fixed hardcoded program.  
Instead, a short instruction sequence is loaded into internal program memory through SPI, and then executed autonomously by the CPU.

This approach preserves programmability while keeping the architecture small enough for a Tiny Tapeout 1x1 implementation.

## Main features
- 8-bit accumulator-based CPU
- SPI program loading into internal instruction memory
- autonomous execution after loading
- 10 instruction slots in internal program memory
- compact enriched ISA

## Supported instructions
### Data and register operations
- `LDI_ACC`
- `LDI_R1`
- `MOV_ACC_R1`

### Arithmetic and logic operations
- `ADD`
- `SUB`
- `AND`
- `OR`
- `XOR`
- `CMP`

### Output and control operations
- `OUT`
- `OUT_R1`
- `JMP`
- `BZ`
- `BNZ`
- `HALT`
- `NOP`

## Architecture
The design is organized into the following RTL blocks:

- `alu8.v`  
  8-bit ALU for arithmetic and logic operations

- `tiny8_cpu.v`  
  CPU core, instruction decode, control flow, and output generation

- `tiny8_prgmem.v`  
  internal instruction memory

- `tiny8_spi_loader.v`  
  SPI loader used to write instructions into program memory

- `tt_um_tiny8_risclike.v`  
  Tiny Tapeout top-level wrapper

## Program loading model
The SPI loader receives 24-bit frames:

- upper byte: address byte
- lower 16 bits: instruction word

Only the valid internal instruction addresses are used by the final design.

When `RUN=0`, instructions can be loaded into memory.  
When `RUN=1`, the CPU starts executing from address `0`.

## Current I/O usage
### Dedicated inputs
- `ui[0]`: `RUN`

### Main outputs
- `uo[7:0]`: CPU output port

### Bidirectional bank
- `uio[0]`: `SPI_SCK` input
- `uio[1]`: `SPI_CS_N` input
- `uio[2]`: `SPI_MOSI` input
- `uio[3]`: `PROGRAM_LOADED` output
- `uio[4]`: `HALTED` output
- `uio[5]`: `RUN_ECHO` output

## Validation status
- RTL simulation: OK
- SPI program load testbench: OK
- cocotb-based execution test: OK
- gate-level test: OK
- LibreLane/OpenROAD hardening: validated for the selected architecture and memory depth

## Example behavior
A program can be loaded through SPI, stored in internal memory, and then executed to produce visible output on `uo[7:0]`.

A simple example sequence is:

- load immediate into `R1`
- move `R1` into `ACC`
- write `ACC` to output
- write `R1` to output
- halt execution

## Note
This project extends the original ALU challenge into a small programmable processor.  
The ALU operations are not triggered through a direct manual interface; instead, they are executed under CPU control from an instruction sequence loaded through SPI.
