//
// Run a method that extracts the PYDOC strings from APVM.
//

module pydoc;

  reg [31:0] res;

initial
  res = $apvm("Pydoc!", "pydoc", "pydoc");

endmodule

