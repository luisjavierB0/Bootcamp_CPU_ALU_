import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer


def make_uio_byte(sck: int, cs_n: int, mosi: int) -> int:
    # uio_in[0] = spi_sck
    # uio_in[1] = spi_cs_n
    # uio_in[2] = spi_mosi
    # uio_in[7:3] = 0
    return ((mosi & 1) << 2) | ((cs_n & 1) << 1) | (sck & 1)


def set_spi_lines(dut, sck: int, cs_n: int, mosi: int) -> None:
    dut.uio_in.value = make_uio_byte(sck, cs_n, mosi)


async def spi_send_bit(dut, bit_value: int) -> None:
    set_spi_lines(dut, 0, 0, bit_value)
    await Timer(20, units="us")

    set_spi_lines(dut, 1, 0, bit_value)
    await Timer(20, units="us")

    set_spi_lines(dut, 0, 0, bit_value)
    await Timer(20, units="us")


async def spi_send_word24(dut, addr: int, instr: int) -> None:
    # Frame de 24 bits:
    # [23:16] = byte de direccion
    # [15:0]  = instruccion
    frame = ((addr & 0xFF) << 16) | (instr & 0xFFFF)

    # CS activo en bajo
    set_spi_lines(dut, 0, 0, 0)
    await Timer(20, units="us")

    for i in range(23, -1, -1):
        await spi_send_bit(dut, (frame >> i) & 1)

    # CS inactivo en alto
    set_spi_lines(dut, 0, 1, 0)
    await Timer(40, units="us")


@cocotb.test()
async def test_load_and_run_program(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.rst_n.value = 0
    dut.uio_in.value = make_uio_byte(0, 1, 0)  # idle SPI

    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Programa:
    # 0: LDI_R1 0x33
    # 1: MOV_ACC_R1
    # 2: OUT
    # 3: OUT_R1
    # 4: HALT
    await spi_send_word24(dut, 0, 0x2033)
    await spi_send_word24(dut, 1, 0xE000)
    await spi_send_word24(dut, 2, 0x9000)
    await spi_send_word24(dut, 3, 0xF000)
    await spi_send_word24(dut, 4, 0xD000)

    await ClockCycles(dut.clk, 10)

    prog_loaded = (int(dut.uio_out.value) >> 3) & 1
    assert prog_loaded == 1, "prog_loaded no se activó"

    assert int(dut.uio_oe.value) == 0x38, (
        f"uio_oe inesperado: 0x{int(dut.uio_oe.value):02X}"
    )

    # Ejecutar
    dut.ui_in.value = 0x01
    await ClockCycles(dut.clk, 30)

    # Tanto OUT como OUT_R1 deben terminar dejando 0x33 en salida
    assert int(dut.uo_out.value) == 0x33, (
        f"Se esperaba 0x33 y salió 0x{int(dut.uo_out.value):02X}"
    )

    halted = (int(dut.uio_out.value) >> 4) & 1
    assert halted == 1, "halted no se activó"
