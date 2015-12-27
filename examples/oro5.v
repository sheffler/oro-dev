`timescale 1ns/1ns

module top;

reg	[0:0] clk_d;
wire	[0:0] clk;

assign clk = clk_d;

integer i;
integer res;

initial
  for (i=0; i<5; i=i+1)
    begin
      #10 clk_d = 1;
      #10 clk_d = 0;
    end

initial
  begin
    clk_d = 0;

    res = $apvm("oro", "oroboro", "oroboro");
    $display("VERILOG %t APVM returns!\n", $time);

    $display("VERILOG DISPLAY AT TIME 0\n");
    $dumpvars;

  end

endmodule
