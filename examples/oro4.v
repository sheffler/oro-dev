
module top;

reg  [31:0] clk_d;
wire [31:0] clk;
reg  [31:0] oro_d;
wire [31:0] oro;
wire [0:0] andres;
reg  [31:0] res;

integer i;

assign clk = clk_d;
assign oro = oro_d;

and (andres, clk[0], oro[0]);

initial
  for (i = 0; i < 10; i = i + 1)
    begin
      #5 clk_d = 1;
      #5 clk_d = 0;
      #5 clk_d = 1;
      #5 clk_d = 0;
    end

always @(andres)
  begin
    $display("VERILOG %t SAW ANDRES CHANGE: %d\n", $time, andres);
  end

always @(clk)
  begin
    $display("VERILOG %t SAW CLK CHANGE: %d\n", $time, clk);
  end

always @(oro)
  begin
    $display("VERILOG %t SAW ORO CHANGE: %d\n", $time, oro);
  end    


initial

  begin
    clk_d = 0;
    oro_d = 0;

    $display("VERILOG DISPLAY AT TIME 0\n");
    $dumpvars;

    res = $apvm("oro", "oroboro", "oroboro");
    $display("VERILOG %t APVM returns!\n", $time);

  end

endmodule
