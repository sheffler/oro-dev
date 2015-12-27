
module top;

reg    [0:0] clk_d;    /* driven here */
wire   [0:0] clk;

reg    [0:0] sclk_d;   /* setup clock driven here */
wire   [0:0] sclk;

reg    [4:0] cmd_d;    /* for use by Oro */
wire   [4:0] cmd;

reg    [7:0] data_d;   /* for use by Oro */
wire   [7:0] data;

integer i;
integer res;

assign clk = clk_d;
assign sclk = sclk_d;
assign cmd = cmd_d;
assign data = data_d;

initial clk_d = 1;
initial sclk_d = 1;
initial cmd_d = 0;
initial data_d = 8'bzzzzzzzz;

/* Instantiate the memory */
memmod mem0 (clk, cmd, data);

initial begin
  $dumpvars;
  res = $apvm("oro", "oroboro", "oroboro");
  $display("VERILOG %t APVM returns!\n", $time);
end


/* generate a clock */
initial
  for (i = 0; i < 1000; i=i+1) begin
    #5 sclk_d = 0;  /* precedes sample clock by 90 degress */
    #5 clk_d = 0;
    #5 sclk_d = 1;
    #5 clk_d = 1;
  end

always @(sclk)
begin
//  $display("SAMPLE DATA: 0x%x", data);
end

endmodule







