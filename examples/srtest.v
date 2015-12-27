
module pytest;

reg [31:0] res;

reg [3:0] x, y, z;  /* for SR tests */

initial
  begin

    x= 0;
    y = 0;
   
    res = $apvm("sr1", "apvm_sr", "sr");

    #500 $display("X: %b, Y: %b\n", x, y);

  end

endmodule
