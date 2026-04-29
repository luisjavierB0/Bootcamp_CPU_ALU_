# Tiny8 CPU with SPI Program Load and Internal Execution

This project implements a compact 8-bit CPU in Verilog.

The processor loads a short instruction sequence through SPI into internal program memory and then executes that program autonomously.

The architecture is intended for Tiny Tapeout and is designed to provide programmable behavior while keeping the implementation compact.

---

## Main idea

The system works in two phases:

### Program load phase
When `RUN = 0`, an external controller sends SPI frames containing:
- instruction address
- 16-bit instruction word

Those instructions are stored into internal program memory.

### Execution phase
When `RUN = 1`, the CPU starts from address `0` and executes autonomously from the stored program.

This means the chip itself does not read files directly. A controller outside the ASIC stores the program, converts it into SPI frames, and sends those frames into the design.

---

## Main features

- compact 8-bit CPU
- SPI-based program loading
- internal instruction memory
- autonomous execution
- 10 valid instruction slots
- compact enriched ISA
- visible output port and execution status signals

---

## RTL architecture

The design is organized into:

- `alu8.v`  
  8-bit ALU for arithmetic and logic operations

- `tiny8_cpu.v`  
  CPU core, decode, branching, execution control, and output generation

- `tiny8_prgmem.v`  
  internal instruction memory

- `tiny8_spi_loader.v`  
  SPI loader used to write instructions into internal memory

- `tt_um_tiny8_risclike.v`  
  top-level wrapper for external integration

---

## Program memory

The implemented design uses **10 valid instruction slots**.

Valid addresses are:

- `0` to `9`

If an invalid address is accessed, the memory returns:

- `HALT`

This prevents undefined execution when an invalid target is reached.

---

## Supported instructions

### Data and register operations
- `NOP`
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

---

## SPI loading model

The program loader receives **24-bit SPI frames**:

- upper byte = address byte
- lower 16 bits = instruction word

Writes are enabled only when:

- `RUN = 0`

When:

- `RUN = 1`

the CPU executes from internal memory.

---

## I/O summary

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

---

## Example program

| Address | Instruction | Meaning |
|--------:|-------------|---------|
| 0 | `0x2033` | `LDI_R1 0x33` |
| 1 | `0xE000` | `MOV_ACC_R1` |
| 2 | `0x9000` | `OUT` |
| 3 | `0xF000` | `OUT_R1` |
| 4 | `0xD000` | `HALT` |

Expected visible result:
- `uo[7:0] = 0x33`
- `HALTED = 1` at the end of execution

---

## Physical use

In a real setup, a controller outside the ASIC stores the program and sends it through SPI into the chip.

A practical demonstration flow is:

1. keep `RUN = 0`
2. send SPI instruction frames
3. wait for `PROGRAM_LOADED`
4. set `RUN = 1`
5. observe `uo[7:0]`, `HALTED`, and `RUN_ECHO`

For human-visible demonstrations, the external controller should provide either:
- a slow clock
- a step clock
- or a final-result-only demonstration

---

## Validation

The repository test flow is intended to validate:

- SPI instruction loading
- correct memory writes
- autonomous execution
- visible output behavior
- halt signaling
- gate-level compatibility

---

## Documentation

For the complete architectural and usage description, see:

- `docs/info.md`
