module top();

    reg     clk;    initial clk = 0;
    integer value;  initial value = 0;
    integer i;
    integer res;

    initial
      res = $apvm("oro", "oroboro", "oroboro");

    initial
      for (i = 0; i < 10; i=i+1) begin
        #10 clk = 1;
        #10 clk = 0;
      end

    always @(value) begin
      $display("VL: Change detected at time %t.  New value is %d", $time, value);
    end

endmodule
