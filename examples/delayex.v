
`timescale 1ps/1ps

module delayex;

  reg [0:0]  en;
  reg [0:0]  in;
//  reg [0:0]  out;
  wire [0:0]  out;

  reg [31:0]  delay;

  reg [31:0]  result;

  apvm_delay a1 (delay, in, en, out);
  

initial
  begin

    // result = $apvm("delayelt!", "apvm_delay", "delayelt", delay, in, en, out);


    $dumpvars();

    en = 1'b0;
    in = 1'b0;
//    out = 1'bx;
    delay = 10;



    #10 en = 1'b1;

    #2  in = 1'b1;
    #1  in = 1'b0;
    #1  in = 1'b1;
    #1  in = 1'b0;

    #10 en = 1'b0;

    #10;

    #1  in = 1'b0;
    #1  in = 1'b1;

    #10;
    
    #10 en = 1'b1;
    #2  in = 1'b1;
    #1  in = 1'b0;
    #1  in = 1'b1;
    #1  in = 1'b0;

    #10 en = 1'b0;

  end

endmodule
