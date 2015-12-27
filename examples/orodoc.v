//
// Run a method that extracts the PYDOC strings from Oroboro.
//

module pydoc;

  reg [31:0] res;

initial
  res = $apvm("Pydoc!", "orodoc", "orodoc");

endmodule

