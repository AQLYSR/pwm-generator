   module pwm_gen (
       input  wire       clk,
       input  wire       rst_n,
       input  wire [7:0] duty_cycle,
       output reg        pwm_out
   );
       reg [7:0] counter;

       always @(posedge clk or negedge rst_n) begin
           if (!rst_n) begin
               counter <= 8'd0;
               pwm_out <= 1'b0;
           end else begin
               counter <= counter + 8'd1;
               pwm_out <= (counter < duty_cycle);
           end
       end
   endmodule
