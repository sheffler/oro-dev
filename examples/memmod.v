/*
 * A very simple memory-like device model with 8 storage locations.
 *  - cmds sampled on negative clock edges
 *  - data sampled and driven on pos and neg clock edges
 *
 * Cmd format: {1,0, addr{2:0}} - write
 * Cmd format: {1,1, addr{2:0}} - read
 *
 */

module memmod(clk, cmd, data);

input   clk;
input	cmd;	/* The command bus */
inout   data;   /* The data bus */

wire [0:0] clk;
wire [4:0] cmd;
wire [7:0] data;

reg  [2:0] addr;    /* address for the memory op */

reg  [7:0] data_d;  /* our driver for the data */

integer i;
integer address;
integer clkcounter;
integer wcounter;
integer rcounter;

/* The local storage */
reg [7:0] memcore [16:0];

/* Temp storage */
reg [7:0] data0;
reg [7:0] data1;

initial begin
  data_d = 8'bzzzzzzzz;
  clkcounter = 0;
  wcounter = 0;
  rcounter = 0;

  for (i = 0; i < 16; i= i+1) begin
    memcore[i] = 0;
  end
end

/* assign the driver to the bus */
assign data = data_d;


always @(negedge clk)
begin

  clkcounter = clkcounter + 1;
//  $display("NEGEDGE %t", $time);

  if (wcounter != 0) wcounter = wcounter-1;
  if (rcounter != 0) rcounter = rcounter-1;

  if (cmd[4:3] == 2'b10) begin
    $display("MEM WRITE, ADDR 0x%x %t", cmd[2:0], $time);
    wcounter = 4;
    addr = cmd[2:0];  /* store address */
  end

  if (cmd[4:3] == 2'b11) begin
    $display("MEM READ, ADDR 0x%x %t", cmd[2:0], $time);
    rcounter = 6;
    addr = cmd[2:0];

    /* retrieve data */
    data0 = memcore[{addr,1'b0}];
    data1 = memcore[{addr,1'b1}];
    $display("<READ DATA 0x%x 0x%x", data0, data1);
  end

  if (wcounter == 1) begin
    $display("MEM SAMPLE DATA0 0x%x %t", data, $time);
    data0 = data; /* sample data */
    memcore[{addr,1'b0}] = data0;
  end

  if (rcounter == 2) begin
    $display("MEM DRIVE DATA0 0x%x %t", data0, $time);
    data_d = data0;
  end

  if (rcounter == 1) begin
    data_d = 8'bzzzzzzzz;
  end

end

always @(posedge clk)
begin

  if (rcounter == 2) begin
    $display("MEM DRIVE DATA1 0x%x %t", data1, $time);
    data_d = data1;
  end

  if (wcounter == 1) begin
    $display("MEM SAMPLE DATA1 0x%x %t", data, $time);
    address = {addr,1'b1};
    data1 = data; /* sample data */
    memcore[address] = data1;
    $display("  ADDRESS 0x%x, 0x%x %t", address, data1, $time);
  end

end

endmodule
