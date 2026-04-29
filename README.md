# Bootcamp_CPU_ALU_

Tiny Tapeout project implementing a compact 8-bit CPU with SPI program loading and internal execution.

## Final stable version

This repository is aligned to the stable implementation with:

- 8-bit CPU core
- internal program memory with 10 instruction slots
- SPI loader for writing instructions into memory
- enriched ISA including:
  - `MOV_ACC_R1`
  - `OUT_R1`

## Main RTL files

Located in `src/`:

- `alu8.v`
- `tiny8_cpu.v`
- `tiny8_prgmem.v`
- `tiny8_spi_loader.v`
- `tt_um_tiny8_risclike.v`

## Testing

Located in `test/`:

- `Makefile`
- `tb.v`
- `test.py`

The testbench loads a short program through SPI and then executes it, validating:

- program loading
- execution
- output behavior
- HALT signaling

## IO summary

### Inputs
- `ui[0]` = `RUN`

### Outputs
- `uo[7:0]` = CPU output port

### UIO usage
- `uio[0]` = `SPI_SCK input`
- `uio[1]` = `SPI_CS_N input`
- `uio[2]` = `SPI_MOSI input`
- `uio[3]` = `PROGRAM_LOADED output`
- `uio[4]` = `HALTED output`
- `uio[5]` = `RUN_ECHO output`

## Notes

This repository intentionally keeps the final stable configuration rather than the more aggressive memory variants that exceeded practical placement limits in the 1x1 tile.
