# Tiny8 CPU with SPI Program Load and Internal Execution

## 1. Overview

This project implements a compact 8-bit CPU in Verilog for Tiny Tapeout.

The processor does not depend on a fixed hardcoded program. Instead, a short instruction sequence is loaded through SPI into internal program memory, and then the CPU executes that program autonomously.

The design is intentionally compact so it can fit within a Tiny Tapeout 1x1 tile while still supporting programmable behavior.

---

## 2. Main idea

The system operates in two phases:

### Program loading phase
When `RUN = 0`, the external controller sends instruction frames through SPI.  
Those instructions are stored in internal memory.

### Execution phase
When `RUN = 1`, the CPU starts executing from address `0` and runs autonomously.

This gives the design programmability without needing a large internal ROM.

---

## 3. RTL architecture

The project is organized into the following RTL blocks:

### `alu8.v`
8-bit ALU used for arithmetic and logic operations.

### `tiny8_cpu.v`
CPU core responsible for:
- instruction fetch from internal program memory
- instruction decode
- arithmetic and logic sequencing
- branching
- output generation
- HALT state

### `tiny8_prgmem.v`
Internal instruction memory.

The final implementation uses **10 valid instruction slots**, with valid addresses:

- `0` to `9`

Addresses outside this range are treated as invalid.

### `tiny8_spi_loader.v`
SPI loader that receives 24-bit frames and writes instructions into internal program memory.

### `tt_um_tiny8_risclike.v`
Tiny Tapeout top-level wrapper that connects:
- SPI loader
- instruction memory
- CPU
- Tiny Tapeout IO pins

---

## 4. Program memory model

The internal program memory stores **10 instruction words**.

Each instruction word is **16 bits** wide.

### Valid addresses
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

### Invalid addresses
If the CPU reads outside the valid range, the memory returns:

- `16'hD000`

which corresponds to:

- `HALT`

This prevents undefined execution when an invalid address is reached.

---

## 5. CPU execution model

The CPU uses:

- one accumulator register: `ACC`
- one auxiliary register: `R1`
- one output port: `port_out`
- one zero flag: `Z`

The program counter starts from address `0`.

### Sequential execution
The program counter advances normally through valid memory.

### Wrap behavior
Sequential execution wraps from address `9` back to address `0`.

### Branch behavior
Branch instructions (`JMP`, `BZ`, `BNZ`) use the low address bits of the instruction.

If the branch target is outside the valid range, the CPU redirects execution to address `0`.

### Halt behavior
When `HALT` is executed:
- `halted` becomes `1`
- the CPU remains in halt state until reset or `RUN` is deasserted

---

## 6. Instruction set

The CPU uses a compact 4-bit opcode in `instr[15:12]`.

---

### 6.1 Data and register operations

#### `LDI_ACC`
- Opcode: `0x1`
- Operation: `ACC <- imm8`

Format:
- `1xxx`

Example:
- `0x102A` → load `0x2A` into `ACC`

---

#### `LDI_R1`
- Opcode: `0x2`
- Operation: `R1 <- imm8`

Format:
- `2xxx`

Example:
- `0x2033` → load `0x33` into `R1`

---

#### `MOV_ACC_R1`
- Opcode: `0xE`
- Operation: `ACC <- R1`

Format:
- `0xE000`

---

### 6.2 Arithmetic and logic operations

All arithmetic/logic operations use:
- operand A = `ACC`
- operand B = `R1`

#### `ADD`
- Opcode: `0x3`
- Operation: `ACC <- ACC + R1`

Format:
- `0x3000`

---

#### `SUB`
- Opcode: `0x4`
- Operation: `ACC <- ACC - R1`

Format:
- `0x4000`

---

#### `AND`
- Opcode: `0x5`
- Operation: `ACC <- ACC & R1`

Format:
- `0x5000`

---

#### `OR`
- Opcode: `0x6`
- Operation: `ACC <- ACC | R1`

Format:
- `0x6000`

---

#### `XOR`
- Opcode: `0x7`
- Operation: `ACC <- ACC ^ R1`

Format:
- `0x7000`

---

#### `CMP`
- Opcode: `0x8`
- Operation: compute comparison result through ALU subtraction path and update `Z`

Format:
- `0x8000`

This instruction updates comparison state through the zero-result condition.

---

### 6.3 Output and control operations

#### `OUT`
- Opcode: `0x9`
- Operation: `port_out <- ACC`

Format:
- `0x9000`

---

#### `OUT_R1`
- Opcode: `0xF`
- Operation: `port_out <- R1`

Format:
- `0xF000`

---

#### `JMP`
- Opcode: `0xA`
- Operation: unconditional jump

Format:
- `0xA00a`

where the low address bits define the jump target.

Example:
- `0xA003` → jump to address `3`

---

#### `BZ`
- Opcode: `0xB`
- Operation: branch if zero flag is set

Format:
- `0xB00a`

---

#### `BNZ`
- Opcode: `0xC`
- Operation: branch if zero flag is not set

Format:
- `0xC00a`

---

#### `HALT`
- Opcode: `0xD`
- Operation: stop execution

Format:
- `0xD000`

---

#### `NOP`
- Opcode: `0x0`
- Operation: no operation

Format:
- `0x0000`

---

## 7. SPI loading protocol

The program loader receives **24-bit SPI frames**.

### Frame format
- bits `[23:16]` = address byte
- bits `[15:0]`  = instruction word

### Effective address usage
Only the needed low address bits are used internally.  
For the final memory implementation, only addresses corresponding to valid program slots are meaningful.

### Important condition
Instruction loading is enabled only when:

- `RUN = 0`

If `RUN = 1`, execution mode is active and memory writes are blocked.

---

## 8. Operating sequence

## 8.1 Reset
Apply reset to initialize:
- CPU state
- program memory contents
- output port
- status flags

## 8.2 Program load
Set:

- `RUN = 0`

Then send the desired instruction frames over SPI.

## 8.3 Program start
Set:

- `RUN = 1`

The CPU starts execution from address `0`.

## 8.4 Program monitoring
Observe:
- `uo[7:0]` for output values
- `uio[3]` for `PROGRAM_LOADED`
- `uio[4]` for `HALTED`
- `uio[5]` for `RUN_ECHO`

---

## 9. Tiny Tapeout IO mapping

### Dedicated inputs
- `ui[0]` = `RUN`

### Dedicated outputs
- `uo[7:0]` = CPU output port

### Bidirectional bank
- `uio[0]` = `SPI_SCK` input
- `uio[1]` = `SPI_CS_N` input
- `uio[2]` = `SPI_MOSI` input
- `uio[3]` = `PROGRAM_LOADED` output
- `uio[4]` = `HALTED` output
- `uio[5]` = `RUN_ECHO` output
- `uio[6]` = unused
- `uio[7]` = unused

---

## 10. Example program

Example sequence:

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
- CPU halts

---

## 11. Test structure

The repository test structure is intended to validate:

- SPI instruction loading
- instruction execution
- output correctness
- HALT signaling
- gate-level compatibility

The cocotb testbench loads a short program through SPI and verifies the visible output behavior.

---

## 12. Project intent

This project is an architectural extension of a simple ALU challenge.

Instead of manually applying operands for every operation, the ALU is controlled by a compact programmable CPU that:
- loads instructions
- stores them internally
- executes them autonomously

This makes the project more representative of a small programmable digital system while remaining compact enough for Tiny Tapeout.
