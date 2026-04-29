`timescale 1ns/1ps

module tt_um_tiny8_risclike (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    wire run = ui_in[0];

    wire        wr_en_raw;
    wire [4:0]  wr_addr;
    wire [15:0] wr_data;
    wire        loaded_pulse;

    wire [4:0]  instr_addr;
    wire [15:0] instr_word;

    wire [7:0]  port_out;
    wire        halted;

    reg prog_loaded;

    wire prg_wr_en = (~run) & wr_en_raw;

    tiny8_spi_loader loader_i (
        .clk         (clk),
        .rst_n       (rst_n),
        .spi_sck     (uio_in[0]),
        .spi_cs_n    (uio_in[1]),
        .spi_mosi    (uio_in[2]),
        .wr_en       (wr_en_raw),
        .wr_addr     (wr_addr),
        .wr_data     (wr_data),
        .loaded_pulse(loaded_pulse)
    );

    tiny8_prgmem prgmem_i (
        .clk    (clk),
        .rst_n  (rst_n),
        .wr_en  (prg_wr_en),
        .wr_addr(wr_addr),
        .wr_data(wr_data),
        .rd_addr(instr_addr),
        .rd_data(instr_word)
    );

    tiny8_cpu cpu_i (
        .clk       (clk),
        .rst_n     (rst_n),
        .run       (run),
        .instr_addr(instr_addr),
        .instr_in  (instr_word),
        .port_out  (port_out),
        .halted    (halted)
    );

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            prog_loaded <= 1'b0;
        else if (loaded_pulse)
            prog_loaded <= 1'b1;
    end

    wire [7:0] dbg_uio    = uio_in;
    wire [7:0] dbg_status = {ui_in[7:3], prog_loaded, halted, ena};

    assign uo_out = ui_in[1] ? dbg_uio    :
                    ui_in[2] ? dbg_status :
                               port_out;

    // uio[0:2] = entradas SPI
    // uio[3]   = program loaded
    // uio[4]   = cpu halted
    // uio[5]   = run echo
    assign uio_out[0] = 1'b0;
    assign uio_out[1] = 1'b0;
    assign uio_out[2] = 1'b0;
    assign uio_out[3] = prog_loaded;
    assign uio_out[4] = halted;
    assign uio_out[5] = run;
    assign uio_out[6] = 1'b0;
    assign uio_out[7] = 1'b0;

    assign uio_oe[0] = 1'b0;
    assign uio_oe[1] = 1'b0;
    assign uio_oe[2] = 1'b0;
    assign uio_oe[3] = 1'b1;
    assign uio_oe[4] = 1'b1;
    assign uio_oe[5] = 1'b1;
    assign uio_oe[6] = 1'b0;
    assign uio_oe[7] = 1'b0;

endmodule