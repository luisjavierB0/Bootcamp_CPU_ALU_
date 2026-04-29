import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer


def set_spi_lines(dut, sck: int, cs_n: int, mosi: int) -> None:
    current = dut.uio_in.value.integer & 0xF8
    dut.uio_in.value = current | ((mosi & 1) << 2) | ((cs_n & 1) << 1) | (sck & 1)


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
    #
    # En el loader solo se usan 3 bits de direccion: next_shift[18:16]
    # Por eso basta con mandar addr en el byte alto.
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

    # Idle SPI: cs_n=1, sck=0, mosi=0
    set_spi_lines(dut, 0, 1, 0)

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

    # Verifica que el loader sí marcó programa cargado
    prog_loaded = (dut.uio_out.value.integer >> 3) & 1
    assert prog_loaded == 1, "prog_loaded no se activó"

    # uio_oe esperado:
    # [0]=0 [1]=0 [2]=0 [3]=1 [4]=1 [5]=1 [6]=0 [7]=0
    assert dut.uio_oe.value.integer == 0x38, (
        f"uio_oe inesperado: 0x{dut.uio_oe.value.integer:02X}"
    )

    # Ejecutar programa: ui_in[0] = run = 1
    dut.ui_in.value = 0x01
    await ClockCycles(dut.clk, 20)

    assert dut.uo_out.value.integer == 0x2A, (
        f"Se esperaba 0x2A y salió 0x{dut.uo_out.value.integer:02X}"
    )

    halted = (dut.uio_out.value.integer >> 4) & 1
    assert halted == 1, "halted no se activó"
