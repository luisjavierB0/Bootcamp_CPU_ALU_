import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer


async def spi_send_bit(dut, bit_value):
    dut.uio_in.value = (dut.uio_in.value.integer & 0xF8) | ((bit_value & 1) << 2) | (0 << 1) | 0
    await Timer(20, units="us")
    dut.uio_in.value = (dut.uio_in.value.integer & 0xF8) | ((bit_value & 1) << 2) | (0 << 1) | 1
    await Timer(20, units="us")
    dut.uio_in.value = (dut.uio_in.value.integer & 0xF8) | ((bit_value & 1) << 2) | (0 << 1) | 0
    await Timer(20, units="us")


async def spi_send_word24(dut, addr, instr):
    # uio_in[0] = sck
    # uio_in[1] = cs_n
    # uio_in[2] = mosi
    frame = ((addr & 0x1F) << 16) | (instr & 0xFFFF)

    # CS low
    dut.uio_in.value = (dut.uio_in.value.integer & 0xF8) | (0 << 2) | (0 << 1) | 0
    await Timer(20, units="us")

    for i in range(23, -1, -1):
        await spi_send_bit(dut, (frame >> i) & 1)

    # CS high
    dut.uio_in.value = (dut.uio_in.value.integer & 0xF8) | (0 << 2) | (1 << 1) | 0
    await Timer(40, units="us")


@cocotb.test()
async def test_load_and_run_program(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0b00000010  # cs_n idle high, sck=0, mosi=0
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Programa:
    # 0: LDI_ACC 0x2A
    # 1: OUT
    # 2: HALT
    await spi_send_word24(dut, 0, 0x102A)
    await spi_send_word24(dut, 1, 0x9000)
    await spi_send_word24(dut, 2, 0xD000)

    await ClockCycles(dut.clk, 10)

    # Verificar que el loader marcó programa cargado
    assert (dut.uio_out.value.integer >> 3) & 1 == 1, "prog_loaded no se activó"
    assert dut.uio_oe.value.integer == 0x38, f"uio_oe inesperado: 0x{dut.uio_oe.value.integer:02X}"

    # Ejecutar programa
    dut.ui_in.value = 0x01  # run=1, debug off
    await ClockCycles(dut.clk, 20)

    assert dut.uo_out.value.integer == 0x2A, f"Se esperaba 0x2A y salió 0x{dut.uo_out.value.integer:02X}"
    assert (dut.uio_out.value.integer >> 4) & 1 == 1, "halted no se activó"
