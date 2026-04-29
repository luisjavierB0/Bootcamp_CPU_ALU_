# Tiny8 CPU with SPI Program Load and Internal Execution

## Overview

This project implements a compact 8-bit CPU in Verilog.

The processor does not execute from a fixed hardcoded ROM. Instead, a short instruction sequence is loaded from an external controller through SPI into internal program memory, and then the CPU executes that program autonomously.

The architecture was designed to keep the system programmable while remaining compact enough for a Tiny Tapeout 1x1 implementation.

---

## Main idea

The system operates in two phases:

### 1. Program loading phase
When `RUN = 0`, an external controller sends SPI frames that contain:

- instruction address
- 16-bit instruction word

Those instructions are written into internal program memory.

### 2. Execution phase
When `RUN = 1`, the CPU starts from address `0` and executes autonomously from the internal instruction memory.

This means the chip itself does **not** read files directly.  
A host system or controller stores the program externally, converts it into SPI frames, and sends those frames into the ASIC.

---

## RTL architecture

The project is organized into the following RTL blocks:

### `alu8.v`
8-bit ALU used for arithmetic and logic operations.

### `tiny8_cpu.v`
CPU core that handles:

- instruction sequencing
- decode
- ALU control
- branching
- output generation
- halt control

### `tiny8_prgmem.v`
Internal instruction memory.

The implemented design uses **10 valid instruction slots**.

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

### `tiny8_spi_loader.v`
SPI loader that receives 24-bit frames and writes instructions into internal memory.

### `tt_um_tiny8_risclike.v`
Top-level wrapper for integration with the external pin interface.

---

## Internal program memory model

The internal program memory stores:

- **10 instruction words**
- each instruction is **16 bits**

### Valid addresses
Valid program addresses are:

- `0` to `9`

### Invalid addresses
If the CPU reads outside the valid range, the memory returns:

- `16'hD000`

which corresponds to:

- `HALT`

This prevents undefined execution if an invalid program address is reached.

---

## CPU execution model

The CPU contains:

- one accumulator register: `ACC`
- one auxiliary register: `R1`
- one visible output register: `port_out`
- one zero flag: `Z`

### Reset behavior
After reset:

- `ACC = 0`
- `R1 = 0`
- `port_out = 0`
- `PC = 0`
- `halted = 0`

### Sequential execution
The CPU fetches one instruction at a time from the current program counter and executes it.

### Program counter wrap
Sequential execution wraps from address `9` back to address `0`.

### Branch behavior
Branch instructions use the low address bits of the instruction.

If a branch target is outside the valid range, execution is redirected to address `0`.

### Halt behavior
When `HALT` is executed:

- `halted = 1`
- execution stops
- the CPU remains halted until reset or until `RUN` is deasserted and asserted again according to the external operating flow

---

## Instruction set

The opcode is stored in:

- `instr[15:12]`

The implemented ISA includes the following instructions.

---

## Instruction encoding reference

### `NOP`
- Opcode: `0x0`
- Encoding: `0x0000`
- Effect: no operation

### `LDI_ACC`
- Opcode: `0x1`
- Encoding: `0x1xxx`
- Effect: `ACC <- imm8`

Example:
- `0x102A` → load `0x2A` into `ACC`

### `LDI_R1`
- Opcode: `0x2`
- Encoding: `0x2xxx`
- Effect: `R1 <- imm8`

Example:
- `0x2033` → load `0x33` into `R1`

### `ADD`
- Opcode: `0x3`
- Encoding: `0x3000`
- Effect: `ACC <- ACC + R1`

### `SUB`
- Opcode: `0x4`
- Encoding: `0x4000`
- Effect: `ACC <- ACC - R1`

### `AND`
- Opcode: `0x5`
- Encoding: `0x5000`
- Effect: `ACC <- ACC & R1`

### `OR`
- Opcode: `0x6`
- Encoding: `0x6000`
- Effect: `ACC <- ACC | R1`

### `XOR`
- Opcode: `0x7`
- Encoding: `0x7000`
- Effect: `ACC <- ACC ^ R1`

### `CMP`
- Opcode: `0x8`
- Encoding: `0x8000`
- Effect: update the comparison state through the subtraction path and zero flag

### `OUT`
- Opcode: `0x9`
- Encoding: `0x9000`
- Effect: `port_out <- ACC`

### `JMP`
- Opcode: `0xA`
- Encoding: `0xA00a`
- Effect: unconditional jump to address `a`

Example:
- `0xA003` → jump to address `3`

### `BZ`
- Opcode: `0xB`
- Encoding: `0xB00a`
- Effect: branch to address `a` if `Z = 1`

### `BNZ`
- Opcode: `0xC`
- Encoding: `0xC00a`
- Effect: branch to address `a` if `Z = 0`

### `HALT`
- Opcode: `0xD`
- Encoding: `0xD000`
- Effect: stop execution and assert `halted`

### `MOV_ACC_R1`
- Opcode: `0xE`
- Encoding: `0xE000`
- Effect: `ACC <- R1`

### `OUT_R1`
- Opcode: `0xF`
- Encoding: `0xF000`
- Effect: `port_out <- R1`

---

## SPI loading protocol

Instructions are written through **24-bit SPI frames**.

### Frame format
- bits `[23:16]` = address byte
- bits `[15:0]`  = instruction word

### Effective use
Only the valid internal program addresses are meaningful in the final implementation.

### Write condition
Program memory writes are enabled only when:

- `RUN = 0`

If `RUN = 1`, the CPU is in execution mode and memory writes are blocked.

---

## Operating sequence

### Step 1: Reset the system
Apply reset to initialize:

- CPU state
- memory contents
- output register
- status signals

### Step 2: Keep execution disabled
Set:

- `RUN = 0`

### Step 3: Load the program
Send the SPI frames, one frame per instruction.

### Step 4: Confirm loading
Observe:

- `PROGRAM_LOADED`

### Step 5: Start execution
Set:

- `RUN = 1`

The CPU begins execution from address `0`.

### Step 6: Observe the result
Monitor:

- `uo[7:0]`
- `HALTED`
- `RUN_ECHO`

---

## Pin mapping

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

Example program:

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

For the example above, the SPI frames are:

| Address | Instruction | 24-bit frame |
|--------:|-------------|--------------|
| 0 | `0x2033` | `0x002033` |
| 1 | `0xE000` | `0x01E000` |
| 2 | `0x9000` | `0x029000` |
| 3 | `0xF000` | `0x03F000` |
| 4 | `0xD000` | `0x04D000` |

---

## Physical use in a real setup

## What is loaded physically
The chip does **not** read a file directly.

In a real setup, an external controller stores the program file, converts each line into a 24-bit SPI frame, and sends those frames to the ASIC.

That means the practical flow is:

1. create a file containing address/instruction pairs
2. convert them to 24-bit frames
3. send them through SPI while `RUN = 0`
4. set `RUN = 1` to start execution

## Typical physical controller
A practical controller may be:

- a microcontroller
- an FPGA
- a USB-to-GPIO host
- a demo board controller

The controller acts as:

- SPI master
- clock/control source
- external program source

The ASIC acts as:

- SPI program target
- internal program memory
- autonomous execution engine

---

## Human-visible operation

## Important practical detail
If the CPU is clocked too fast, a human will not be able to observe the intermediate behavior directly.

That means the design is easiest to demonstrate in one of these ways:

### 1. Slow clock mode
Use a slow external clock so that the output can be seen by eye.

For example, the controller may provide:

- one instruction every visible fraction of a second
- a very slow continuous clock
- or a manual step-style clock

### 2. Step-by-step demonstration
Advance the clock manually or under software control so the observer can see:

- when `PROGRAM_LOADED` goes high
- when `RUN` is active
- when `HALTED` goes high
- what value appears on `uo[7:0]`

### 3. Final-result-only demonstration
Run the CPU at normal speed, then simply display the final output and halt status.

---

## Practical interpretation of outputs

### `uo[7:0]`
This is the visible CPU output port.

In a real setup, it can be connected to:

- LEDs
- a logic analyzer
- a microcontroller input bank
- a display interface outside the ASIC

### `uio[3] = PROGRAM_LOADED`
Useful to verify that at least one instruction write has been accepted.

### `uio[4] = HALTED`
Useful to know when the program finished.

### `uio[5] = RUN_ECHO`
Useful to confirm the current execution mode.

---

## Real-world loading example

A realistic usage scenario is:

1. Keep `RUN = 0`
2. Send the frames:
   - `0x002033`
   - `0x01E000`
   - `0x029000`
   - `0x03F000`
   - `0x04D000`
3. Wait for `PROGRAM_LOADED = 1`
4. Apply a slow visible clock or a step clock
5. Set `RUN = 1`
6. Observe:
   - `uo[7:0] = 0x33`
   - `HALTED = 1` at the end

---

## What this architecture is optimized for

The architecture is optimized for:

- compact programmable behavior
- external program loading
- internal autonomous execution
- simple physical interfacing
- easy demonstration of final outputs and execution status

It is **not** optimized for:

- long programs
- large internal memories
- direct file parsing on-chip
- human-visible execution at high clock frequency without external assistance

For human-friendly demos, the external controller should provide either:

- a slow clock
- a step clock
- or a final-result display strategy

---

## Validation intent

The project test flow is meant to validate:

- SPI instruction loading
- correct memory writes
- autonomous execution
- output behavior
- halt signaling
- gate-level compatibility

The validation strategy matches the real usage model:

- load through SPI
- execute internally
- verify visible output and status signals

---

## Project intent

This design extends a simple ALU-style exercise into a compact programmable processing system.

Instead of triggering operations manually every time, the ALU is controlled by a small CPU that:

- receives a short program
- stores it internally
- executes it autonomously

This makes the project closer to a real programmable digital block while still remaining compact enough for Tiny Tapeout.
