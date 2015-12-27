module top;

reg [15:0] addr;

reg [31:0] data;

reg [31:0] retval;

reg [31:0] mem1;

reg [64:0] outfile;

integer i;

initial
  begin

    /* Cause RUSAGE to be printed at end of simulation */
    retval = $apvm("getrusage0", "apvm_rusage", "printrusage");

    outfile = "mem.dump";
    addr = 10;
    data = 10;
    retval = $apvm("m0", "apvm_mem", "mem", top.mem1,
                       addr, data, "put");
    $display("Retval: %d", retval);


    for (i=20; i < 100; i=i+1)
      begin
       addr = i;
       data = { 1'bx, i[30:0]};
       retval = $apvm("m1", "apvm_mem", "mem", top.mem1,
                         addr, data, "put");
	 #10;
       $display("Retval: %d", retval);
      end
 
    retval = $apvm("m2", "apvm_mem", "mem", top.mem1,
                       addr, data, "dump", "mem.dump");
    $display("Retval: %d", retval);
  end


endmodule
