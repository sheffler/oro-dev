module plusargs;

  reg [31:0] res;

initial
  begin

    $display("Beginning simulation.\n");

    res = $apvm("plusargs!", "plusargs", "plusargs");

  end

endmodule
