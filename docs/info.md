# Tiny8 CPU with SPI Program Load and Internal Execution

## Overview

This project implements a compact 8-bit CPU in Verilog for Tiny Tapeout.

The processor does not depend on a fixed hardcoded program. Instead, a short instruction sequence is loaded through SPI into internal program memory, and then executed autonomously by the CPU.

The final implementation targets a compact architecture that fits a Tiny Tapeout 1x1 tile while still supporting programmable behavior.

---

## Main idea

The system works in two phases:

### 1. Program loading phase
When `RUN = 0`, an external controller sends instruction frames through SPI.  
Those frames are decoded by the on-chip SPI loader and stored into internal program memory.

### 2. Execution phase
When `RUN = 1`, the CPU starts executing from address `0` and runs autonomously from the stored instruction memory.

This approach preserves programmability without requiring a permanently fixed program in silicon.

---

## Architecture

The design is divided into the following RTL blocks:

### `alu8.v`
8-bit ALU used by the CPU for arithmetic and logic operations.

### `tiny8_cpu.v`
CPU core that handles:
- instruction sequencing
- decode
- branching
- ALU control
- output register updates
- HALT state management

### `tiny8_prgmem.v`
Internal instruction memory.

The final implementation uses **10 valid instruction slots**.

Valid instruction addresses are:

- `0`
- `1`
- `2`
- `3`
- `4`
- `5`
- `6`
- `7`
- `8`
- `9`

Addresses outside this valid range are treated as invalid.

### `tiny8_spi_loader.v`
SPI loader that receives 24-bit frames and writes instructions into internal program memory.

### `tt_um_tiny8_risclike.v`
Tiny Tapeout top-level wrapper.  
This module connects:
- SPI input signals
- program memory
- CPU
- output/status signals
- Tiny Tapeout external pins

---

## Program memory model

The internal memory stores **10 instruction words**.

Each instruction word is **16 bits** wide.

### Valid addresses
Instruction slots are valid only for addresses:

- `0` to `9`

### Invalid addresses
If the CPU attempts to read outside the valid range, the program memory returns:

- `16'hD000`

which corresponds to:

- `HALT`

This prevents undefined execution if a bad address is reached.

---

## CPU execution model

The CPU includes:

- one accumulator register: `ACC`
- one auxiliary register: `R1`
- one visible output port: `port_out`
- one zero flag: `Z`

### Reset behavior
After reset:
- `ACC = 0`
- `R1 = 0`
- `port_out = 0`
- `PC = 0`
- `halted = 0`

### Sequential execution
The CPU fetches from the current program counter and executes instructions one by one.

### Program counter wrap
Sequential execution wraps from address `9` back to address `0`.

### Branch behavior
Branch targets are taken from the low address bits of the instruction.

If a branch target is outside the valid address range, execution is redirected safely to address `0`.

### Halt behavior
When `HALT` is executed:
- `halted = 1`
- the CPU remains in halt state
- execution only restarts after reset or after deasserting `RUN`

---

## Instruction set

The instruction opcode is stored in:

- `instr[15:12]`

The current ISA includes:

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

## Instruction encoding reference

### `NOP`
- Opcode: `0x0`
- Format: `0x0000`
- Effect: no operation

### `LDI_ACC`
- Opcode: `0x1`
- Format: `0x1xxx`
- Effect: `ACC <- imm8`

Example:
- `0x102A` → load `0x2A` into `ACC`

### `LDI_R1`
- Opcode: `0x2`
- Format: `0x2xxx`
- Effect: `R1 <- imm8`

Example:
- `0x2033` → load `0x33` into `R1`

### `ADD`
- Opcode: `0x3`
- Format: `0x3000`
- Effect: `ACC <- ACC + R1`

### `SUB`
- Opcode: `0x4`
- Format: `0x4000`
- Effect: `ACC <- ACC - R1`

### `AND`
- Opcode: `0x5`
- Format: `0x5000`
- Effect: `ACC <- ACC & R1`

### `OR`
- Opcode: `0x6`
- Format: `0x6000`
- Effect: `ACC <- ACC | R1`

### `XOR`
- Opcode: `0x7`
- Format: `0x7000`
- Effect: `ACC <- ACC ^ R1`

### `CMP`
- Opcode: `0x8`
- Format: `0x8000`
- Effect: update comparison state through ALU subtraction path and zero flag result

### `OUT`
- Opcode: `0x9`
- Format: `0x9000`
- Effect: `port_out <- ACC`

### `JMP`
- Opcode: `0xA`
- Format: `0xA00a`
- Effect: unconditional jump to address `a`

Example:
- `0xA003` → jump to address `3`

### `BZ`
- Opcode: `0xB`
- Format: `0xB00a`
- Effect: branch to address `a` if `Z = 1`

### `BNZ`
- Opcode: `0xC`
- Format: `0xC00a`
- Effect: branch to address `a` if `Z = 0`

### `HALT`
- Opcode: `0xD`
- Format: `0xD000`
- Effect: stop execution and assert `halted`

### `MOV_ACC_R1`
- Opcode: `0xE`
- Format: `0xE000`
- Effect: `ACC <- R1`

### `OUT_R1`
- Opcode: `0xF`
- Format: `0xF000`
- Effect: `port_out <- R1`

---

## SPI loading protocol

Instructions are loaded through **24-bit SPI frames**.

### Frame format
- bits `[23:16]` = address byte
- bits `[15:0]`  = instruction word

### Effective address use
Only valid internal instruction addresses are meaningful in the final design.

### Write condition
Program writes are allowed only when:

- `RUN = 0`

If `RUN = 1`, the CPU is in execution mode and memory writes are blocked.

---

## Operating sequence

## 1. Reset
Apply reset to initialize:
- CPU state
- memory contents
- output port
- flags and status

## 2. Load program
Set:
- `RUN = 0`

Then send the desired SPI frames, one instruction per frame.

## 3. Confirm load status
Observe:
- `PROGRAM_LOADED`

to confirm that at least one program word has been written.

## 4. Start execution
Set:
- `RUN = 1`

The CPU begins execution from address `0`.

## 5. Observe execution
Monitor:
- `uo[7:0]` for output values
- `HALTED` to detect end of program
- `RUN_ECHO` to confirm run state

---

## Tiny Tapeout pin mapping

### Dedicated inputs
- `ui[0]` = `RUN`

### Main outputs
- `uo[7:0]` = CPU output port

### Bidirectional bank usage
- `uio[0]` = `SPI_SCK` input
- `uio[1]` = `SPI_CS_N` input
- `uio[2]` = `SPI_MOSI` input
- `uio[3]` = `PROGRAM_LOADED` output
- `uio[4]` = `HALTED` output
- `uio[5]` = `RUN_ECHO` output
- `uio[6]` = unused
- `uio[7]` = unused

---

## Example program

A simple example program is:

| Address | Instruction | Meaning |
|--------:|-------------|---------|
| 0 | `0x2033` | `LDI_R1 0x33` |
| 1 | `0xE000` | `MOV_ACC_R1` |
| 2 | `0x9000` | `OUT` |
| 3 | `0xF000` | `OUT_R1` |
| 4 | `0xD000` | `HALT` |

### Expected behavior
- `R1` receives `0x33`
- `ACC` receives `R1`
- output port shows `0x33`
- output port is written again with `R1`
- CPU enters halt state

---

## Example SPI frames

For the example program above, the frames would be:

| Address | Instruction | 24-bit frame |
|--------:|-------------|--------------|
| 0 | `0x2033` | `0x002033` |
| 1 | `0xE000` | `0x01E000` |
| 2 | `0x9000` | `0x029000` |
| 3 | `0xF000` | `0x03F000` |
| 4 | `0xD000` | `0x04D000` |

---

## Physical use on the Tiny Tapeout demo board

## General concept
In physical use, the design is intended to be driven by the Tiny Tapeout demo board controller.

The CPU does **not** fetch instructions continuously from external memory during execution.  
Instead:

1. the external controller sends instruction frames through SPI,
2. the ASIC stores them into internal memory,
3. the ASIC executes autonomously from internal memory.

## Practical board-level use
A typical physical demonstration would follow this sequence:

### Step 1: Power and select the design
Power the Tiny Tapeout demo board and select the target project.

### Step 2: Provide clock
Use the board clock source for the ASIC.

### Step 3: Hold execution disabled
Keep:

- `RUN = 0`

so that the CPU remains in program load mode.

### Step 4: Send SPI program frames
Drive these pins:

- `uio[0]` → `SPI_SCK`
- `uio[1]` → `SPI_CS_N`
- `uio[2]` → `SPI_MOSI`

One 24-bit frame is sent for each instruction.

### Step 5: Wait for load confirmation
Observe:

- `uio[3]` → `PROGRAM_LOADED`

### Step 6: Start program execution
Set:

- `RUN = 1`

The CPU starts from address `0`.

### Step 7: Observe result and end of execution
Monitor:

- `uo[7:0]` → program result/output
- `uio[4]` → `HALTED`
- `uio[5]` → `RUN_ECHO`

## Practical interpretation of demo board memory
If the demo board controller stores the intended instruction frames on its side, that board-side storage is used only as a **source for loading**.  
The actual execution takes place from the ASIC internal instruction memory.

So, physically, the board acts as:
- instruction source
- SPI master
- clock/control provider

while the ASIC acts as:
- instruction memory target
- autonomous execution engine

---

## Test and validation concept

The project test flow validates:

- SPI instruction loading
- correct memory writes
- autonomous execution
- output behavior
- halt detection
- gate-level compatibility

The testbench structure reflects the real usage model of the design:
- load through SPI
- execute internally
- verify output and status

---

## Project intent

This project extends a simple ALU-style exercise into a compact programmable processing system.

Instead of applying operations manually every time, the ALU is controlled by a small CPU that:
- receives a short program
- stores it internally
- executes it autonomously

This makes the project more representative of a real programmable digital block while still remaining compact enough for Tiny Tapeout.
