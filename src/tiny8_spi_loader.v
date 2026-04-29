module tiny8_spi_loader (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        spi_sck,
    input  wire        spi_cs_n,
    input  wire        spi_mosi,
    output reg         wr_en,
    output reg  [4:0]  wr_addr,
    output reg  [15:0] wr_data,
    output reg         loaded_pulse
);

    reg [1:0] sck_ff;
    reg [1:0] cs_ff;
    reg [1:0] mosi_ff;
    reg       sck_prev;

    /* verilator lint_off UNUSEDSIGNAL */
    reg [23:0] shift_reg;
    /* verilator lint_on UNUSEDSIGNAL */

    reg [4:0]  bit_count;

    wire sck_sync  = sck_ff[1];
    wire cs_sync   = cs_ff[1];
    wire mosi_sync = mosi_ff[1];

    wire sck_rise = sck_sync & ~sck_prev;
    wire [23:0] next_shift = {shift_reg[22:0], mosi_sync};

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sck_ff       <= 2'b00;
            cs_ff        <= 2'b11;
            mosi_ff      <= 2'b00;
            sck_prev     <= 1'b0;
            shift_reg    <= 24'h000000;
            bit_count    <= 5'd0;
            wr_en        <= 1'b0;
            wr_addr      <= 5'd0;
            wr_data      <= 16'h0000;
            loaded_pulse <= 1'b0;
        end else begin
            sck_ff   <= {sck_ff[0], spi_sck};
            cs_ff    <= {cs_ff[0], spi_cs_n};
            mosi_ff  <= {mosi_ff[0], spi_mosi};
            sck_prev <= sck_sync;

            wr_en        <= 1'b0;
            loaded_pulse <= 1'b0;

            if (cs_sync) begin
                bit_count <= 5'd0;
                shift_reg <= 24'h000000;
            end else if (sck_rise) begin
                shift_reg <= next_shift;

                if (bit_count == 5'd23) begin
                    wr_addr      <= next_shift[20:16];
                    wr_data      <= next_shift[15:0];
                    wr_en        <= 1'b1;
                    loaded_pulse <= 1'b1;
                    bit_count    <= 5'd0;
                    shift_reg    <= 24'h000000;
                end else begin
                    bit_count <= bit_count + 5'd1;
                end
            end
        end
    end

endmodule
