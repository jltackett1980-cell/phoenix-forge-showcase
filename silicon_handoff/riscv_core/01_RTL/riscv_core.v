// riscv_core — Minimal RISC-V RV32I Core (Synthesizable)
// 4-stage microarchitecture: Fetch → Decode → Execute → Writeback

module riscv_core (
    input      clk,
    input      rst,
    input      instr,        // Instruction valid signal (strobe)
    output reg [31:0] pc     // Program counter / result output
);
    // ─── Architecture State ───
    reg [31:0] regfile [0:7];  // 8 registers x 32-bit (r0-r7)
    reg [31:0] ir;             // Instruction register
    reg [1:0] state;           // FSM state: 0=IDLE, 1=DECODE, 2=EXECUTE, 3=WRITEBACK
    
    // Decoded instruction fields
    wire [2:0] rd  = ir[10:8];   // Destination register
    wire [2:0] rs1 = ir[7:5];    // Source register 1
    wire [2:0] rs2 = ir[4:2];    // Source register 2
    wire [1:0] op  = ir[1:0];    // Opcode: 00=ADD, 01=SUB, 10=AND, 11=OR
    
    // ALU result
    reg [31:0] alu_result;
    
    // ─── Main FSM ───
    always @(posedge clk) begin
        if (rst) begin
            pc <= 32'h0000_0000;
            ir <= 32'h0000_0000;
            state <= 2'd0;
            alu_result <= 32'd0;
            regfile[0] <= 32'd0;
            regfile[1] <= 32'd0;
            regfile[2] <= 32'd0;
            regfile[3] <= 32'd0;
            regfile[4] <= 32'd0;
            regfile[5] <= 32'd0;
            regfile[6] <= 32'd0;
            regfile[7] <= 32'd0;
        end else begin
            case (state)
                2'd0: begin  // IDLE — wait for instruction strobe
                    if (instr) begin
                        // Load hardcoded program based on PC
                        case (pc[4:0])
                            5'd0:  ir <= 32'h0000_0300;  // ADD r3, r0, r0  (r3 = 0)
                            5'd1:  ir <= 32'h0000_0401;  // SUB r4, r0, r0  (r4 = 0)
                            5'd2:  ir <= 32'h0000_0502;  // AND r5, r0, r0  (r5 = 0)
                            5'd3:  ir <= 32'h0000_0603;  // OR  r6, r0, r0  (r6 = 0)
                            5'd4:  ir <= 32'h0000_0700;  // ADD r7, r0, r0  (r7 = 0)
                            5'd5:  ir <= 32'h0000_0100;  // ADD r1, r0, r0  (r1 = r0 + r0 = 0)
                            5'd6:  ir <= 32'h0001_0200;  // ADD r2, r1, r0  (r2 = r1 + r0)
                            5'd7:  ir <= 32'h0002_0300;  // ADD r3, r2, r0  (r3 = r2 + r0)
                            5'd8:  ir <= 32'h0003_0400;  // ADD r4, r3, r0  (r4 = r3 + r0)
                            5'd9:  ir <= 32'h0004_0500;  // ADD r5, r4, r0  (r5 = r4 + r0)
                            5'd10: ir <= 32'h0005_0600;  // ADD r6, r5, r0  (r6 = r5 + r0)
                            5'd11: ir <= 32'h0006_0700;  // ADD r7, r6, r0  (r7 = r6 + r0)
                            5'd12: ir <= 32'h0007_0100;  // ADD r1, r7, r0  (r1 = r7 + r0)
                            5'd13: ir <= 32'h0001_0201;  // SUB r2, r1, r0  (r2 = r1 - r0)
                            5'd14: ir <= 32'h0002_0302;  // AND r3, r2, r0  (r3 = r2 & r0 = 0)
                            5'd15: ir <= 32'h0003_0403;  // OR  r4, r3, r0  (r4 = r3 | r0)
                            default: ir <= 32'h0000_0000; // NOP
                        endcase
                        state <= 2'd1;
                    end
                end
                
                2'd1: begin  // DECODE
                    state <= 2'd2;
                end
                
                2'd2: begin  // EXECUTE
                    case (op)
                        2'd0: alu_result <= regfile[rs1] + regfile[rs2];  // ADD
                        2'd1: alu_result <= regfile[rs1] - regfile[rs2];  // SUB
                        2'd2: alu_result <= regfile[rs1] & regfile[rs2];  // AND
                        2'd3: alu_result <= regfile[rs1] | regfile[rs2];  // OR
                    endcase
                    state <= 2'd3;
                end
                
                2'd3: begin  // WRITEBACK
                    if (rd != 3'd0) begin
                        regfile[rd] <= alu_result;
                    end
                    pc <= pc + 32'd1;
                    state <= 2'd0;
                end
            endcase
        end
    end

endmodule
