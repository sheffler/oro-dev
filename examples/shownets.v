`timescale 1ns/1ns

module top;
  reg  [2:0] test;
  tri  [1:0] results;

  reg [31:0] retval;

  addbit i1 (test[0], test[1], test[2], results[0], results[1]);

  initial
    begin
      test = 3'b000;
      #1 test = 3'b011;

      /* TOM: the first call to shownets fails in a weird way! */
      #1 retval = $apvm("", "shownets", "shownets", top);
      #1 retval = $apvm("", "shownets", "shownets", top);
      #1 retval = $apvm("", "shownets", "shownets", i1);

      /* #1 $stop; */
      /* #1 $finish; */

    end

endmodule


module addbit(a, b, ci, sum, co);
  input a, b, ci;
  output sum, co;

  wire a, b, ci, sum, co,
       n1, n2, n3;

  xor     (n1, a, b);
  xor  #2 (sum, n1, ci);
  and     (n2, a, b);
  and     (n3, n1, ci);
  or   #2 (co, n2, n3);

endmodule
