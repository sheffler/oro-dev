module plusargs;

  reg [31:0] res;
  integer i;

initial
  begin

    for (i = 0; i < 50; i = i+1)
      begin
        res = $apvm("tkserver", "tkserverdemo", "client", i);
        res = $apvm("sleep", "tkserverdemo", "sleep");
      end
  end

endmodule
