# Makefile
# See https://docs.cocotb.org/en/stable/quickstart.html for more info

# defaults
SIM ?= icarus
FST ?= -fst
TOPLEVEL_LANG ?= verilog

SRC_DIR = $(PWD)/../src
PROJECT_SOURCES = alu8.v tiny8_cpu.v tiny8_prgmem.v tiny8_spi_loader.v tt_um_tiny8_risclike.v

ifneq ($(GATES),yes)

# RTL simulation
SIM_BUILD = sim_build/rtl
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))

else

# Gate level simulation
SIM_BUILD = sim_build/gl
COMPILE_ARGS += -DGL_TEST
COMPILE_ARGS += -DFUNCTIONAL
COMPILE_ARGS += -DUSE_POWER_PINS
COMPILE_ARGS += -DSIM
COMPILE_ARGS += -DUNIT_DELAY=\#1

VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v

# this gets copied in by the GDS action workflow
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v

endif

# Allow source includes
COMPILE_ARGS += -I$(SRC_DIR)

# Testbench
VERILOG_SOURCES += $(PWD)/tb.v
TOPLEVEL = tb
MODULE = test

# Include cocotb rules
include $(shell cocotb-config --makefiles)/Makefile.sim
