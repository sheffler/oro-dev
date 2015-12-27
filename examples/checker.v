module pytest;

   reg [31:0] val;
   integer    i;
   reg [31:0] retval;

initial
  begin

     val = 4;

     for (i = 0; i < 25; i=i+1)
	begin
	   val = i % 5;
	   retval = $apvm("noname", "checker", "checker", val);
	end
  end

endmodule // pytest
