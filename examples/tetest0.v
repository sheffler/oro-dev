
module top;

reg	clk;	initial clk = 0;
reg	a;	initial a = 0;
reg	b;	initial b = 0;
reg	c;	initial c = 0;

reg	[31:0] res;

integer i;

initial

  begin

  $dumpvars;

  $display("Temporal Expression Example\n");
  res = $apvm("oro", "oroboro", "oroboro");

  for (i = 0; i < 20; i=i+1) 
    begin
      #5 clk = 1;
      #5 clk = 0;
    end

  end

endmodule
