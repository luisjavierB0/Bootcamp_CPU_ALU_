`timescale 1ns/1ps

module alu8 (
    input  wire [7:0] a,
    input  wire [7:0] b,
    input  wire [2:0] op,
    output reg  [7:0] y,
    output reg        c
);

    reg [8:0] tmp;

    always @(*) begin
        y   = 8'h00;
        c   = 1'b0;
        tmp = 9'h000;

        case (op)
            3'b000: begin // ADD
                tmp = {1'b0, a} + {1'b0, b};
                y   = tmp[7:0];
                c   = tmp[8];
            end

            3'b001: begin // AND
                y = a & b;
                c = 1'b0;
            end

            3'b010: begin // OR
                y = a | b;
                c = 1'b0;
            end

            3'b011: begin // XOR
                y = a ^ b;
                c = 1'b0;
            end

            3'b100: begin // SUB
                tmp = {1'b0, a} - {1'b0, b};
                y   = tmp[7:0];
                c   = ~tmp[8]; // 1 = no borrow
            end

            3'b101: begin // SHL
                y = a << 1;
                c = a[7];
            end

            3'b110: begin // SHR
                y = a >> 1;
                c = a[0];
            end

            3'b111: begin // PASS B
                y = b;
                c = 1'b0;
            end

            default: begin
                y = 8'h00;
                c = 1'b0;
            end
        endcase
    end

endmodule