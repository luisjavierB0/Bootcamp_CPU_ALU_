# Tiny8 CPU with SPI Program Load and Internal Execution

This project implements a compact 8-bit CPU in Verilog for Tiny Tapeout.

## Main idea

The processor does not rely on a fixed hardcoded program.  
A short instruction sequence is loaded through SPI into internal program memory, and then executed autonomously by the CPU.

This approach keeps the design programmable while remaining compact enough for a Tiny Tapeout 1x1 implementation.

## Main features

- 8-bit CPU
- SPI-based instruction loading
- internal program memory
- autonomous execution
- 10 valid instruction slots
- compact enriched ISA
- output port and execution status signaling

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

## RTL architecture

The design is organized into:

- `alu8.v`
- `tiny8_cpu.v`
- `tiny8_prgmem.v`
- `tiny8_spi_loader.v`
- `tt_um_tiny8_risclike.v`

## IO summary

### Inputs
- `ui[0]` = `RUN`

### Main outputs
- `uo[7:0]` = CPU output port

### UIO usage
- `uio[0]` = `SPI_SCK` input
- `uio[1]` = `SPI_CS_N` input
- `uio[2]` = `SPI_MOSI` input
- `uio[3]` = `PROGRAM_LOADED` output
- `uio[4]` = `HALTED` output
- `uio[5]` = `RUN_ECHO` output

## How to use

1. Keep `RUN = 0`
2. Send 24-bit SPI frames:
   - upper byte = address
   - lower 16 bits = instruction
3. Load instructions into valid addresses
4. Set `RUN = 1`
5. Observe execution on `uo[7:0]`
6. Monitor `PROGRAM_LOADED` and `HALTED`

## Example program

| Address | Instruction | Meaning |
|--------:|-------------|---------|
| 0 | `0x2033` | `LDI_R1 0x33` |
| 1 | `0xE000` | `MOV_ACC_R1` |
| 2 | `0x9000` | `OUT` |
| 3 | `0xF000` | `OUT_R1` |
| 4 | `0xD000` | `HALT` |

## Validation

- RTL simulation: OK
- cocotb testbench: OK
- gate-level test: OK
- Tiny Tapeout-oriented hardening flow prepared

## More details

See:

- `docs/info.md`

for the complete usage and architecture description.
