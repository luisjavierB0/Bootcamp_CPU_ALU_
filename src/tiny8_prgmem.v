module tiny8_prgmem (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        wr_en,
    input  wire [3:0]  wr_addr,
    input  wire [15:0] wr_data,
    input  wire [3:0]  rd_addr,
    output wire [15:0] rd_data
);

    reg [15:0] mem [0:11];
    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 12; i = i + 1)
                mem[i] <= 16'h0000; // NOP
        end else if (wr_en && (wr_addr < 4'd12)) begin
            mem[wr_addr] <= wr_data;
        end
    end

    assign rd_data = (rd_addr < 4'd12) ? mem[rd_addr] : 16'hD000; // HALT fuera de rango

endmodule
