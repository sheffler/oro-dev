
module pytest;

reg [31:0] res;

reg [31:0] r1, r2, r3;

initial
  begin

    #1 r1 = 1;
   
    $display("DISPLAY %d\n", r1);

    res = $apvm("me", "apvm", "_example", r1, r2, r3);
    #3 r2 = 5;

    #6 r3= 10;

  end

endmodule
