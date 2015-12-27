
/*
 * Verilog Module wrapper for apvm_delay module.
 *
 * Args:
 *  delay - register with integer # of system time units
 *  in    - input wire
 *  en    - enable input wire
 *  out   - output from register
 *
 */

module apvm_delay ( delay, in, en, out );

  input  [31:0] delay;
  input  [ 0:0]    in;
  input  [ 0:0]    en;
  output [ 0:0]   out;

  reg    [ 0:0]    id;  // id for $apvm module

  reg    [ 0:0] o_drv;  // driver reg for output
  reg    [31:0]   res;  // return code from $apvm

  assign out = o_drv;

  initial
    res = $apvm(id, "apvm_delay", "delayelt", delay, in, en, o_drv);

endmodule



  
