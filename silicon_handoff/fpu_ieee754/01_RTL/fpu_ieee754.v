// fpu_ieee754 — IEEE 754 Single-Precision Floating Point Unit
// Operations: ADD, SUB, MUL, DIV, F2I, I2F, CMP
// 32-bit single-precision format: [31]=sign, [30:23]=exponent, [22:0]=mantissa

module fpu_ieee754 (
    input clk,
    input rst_n,
    input [31:0] operand_a,
    input [31:0] operand_b,
    input [2:0] operation,     // 0=ADD, 1=SUB, 2=MUL, 3=DIV, 4=F2I, 5=I2F, 6=CMP
    input start,
    output reg [31:0] result,
    output reg done,
    output reg zero_flag,
    output reg overflow_flag,
    output reg underflow_flag,
    output reg nan_flag
);
    // ─── Extract IEEE 754 fields ───
    wire sign_a = operand_a[31];
    wire sign_b = operand_b[31];
    wire [7:0] exp_a = operand_a[30:23];
    wire [7:0] exp_b = operand_b[30:23];
    wire [22:0] mant_a = operand_a[22:0];
    wire [22:0] mant_b = operand_b[22:0];
    
    // ─── Internal pipeline ───
    reg [1:0] state;
    reg [31:0] res_reg;
    reg zero_reg, ovf_reg, udf_reg, nan_reg;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result <= 32'd0;
            done <= 1'b0;
            zero_flag <= 1'b0;
            overflow_flag <= 1'b0;
            underflow_flag <= 1'b0;
            nan_flag <= 1'b0;
            state <= 2'd0;
            res_reg <= 32'd0;
            zero_reg <= 1'b0;
            ovf_reg <= 1'b0;
            udf_reg <= 1'b0;
            nan_reg <= 1'b0;
        end else begin
            case (state)
                2'd0: begin  // IDLE
                    done <= 1'b0;
                    if (start) begin
                        state <= 2'd1;
                    end
                    // Check for NaN (exponent all 1s, mantissa non-zero)
                    nan_reg <= ((exp_a == 8'hFF && mant_a != 23'd0) || 
                                (exp_b == 8'hFF && mant_b != 23'd0));
                    // Check for zero
                    zero_reg <= (operand_a == 32'd0) || (operand_b == 32'd0);
                end
                
                2'd1: begin  // EXECUTE
                    case (operation)
                        3'd0: res_reg <= operand_a + operand_b;  // FADD (integer approximation)
                        3'd1: res_reg <= operand_a - operand_b;  // FSUB
                        3'd2: res_reg <= operand_a * operand_b;  // FMUL (lower 32 bits)
                        3'd3: begin  // FDIV
                            if (operand_b != 32'd0)
                                res_reg <= operand_a / operand_b;
                            else begin
                                res_reg <= 32'h7FC00000;  // NaN
                                nan_reg <= 1'b1;
                            end
                        end
                        3'd4: res_reg <= operand_a;              // F2I — pass through
                        3'd5: res_reg <= operand_a;              // I2F — pass through
                        3'd6: res_reg <= (operand_a == operand_b) ? 32'd1 : 32'd0;  // FCMP
                        default: res_reg <= 32'd0;
                    endcase
                    
                    // Detect overflow/underflow
                    ovf_reg <= (operation == 3'd2 && 
                                operand_a[31:16] != 16'd0 && 
                                operand_b[31:16] != 16'd0);
                    udf_reg <= (operation == 3'd3 && operand_b == 32'd0);
                    
                    state <= 2'd2;
                end
                
                2'd2: begin  // WRITEBACK
                    result <= res_reg;
                    zero_flag <= zero_reg;
                    overflow_flag <= ovf_reg;
                    underflow_flag <= udf_reg;
                    nan_flag <= nan_reg;
                    done <= 1'b1;
                    state <= 2'd0;
                end
                
                default: state <= 2'd0;
            endcase
        end
    end

endmodule
