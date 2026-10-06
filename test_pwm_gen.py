
   import cocotb
   from cocotb.clock import Clock
   from cocotb.triggers import RisingEdge, ClockCycles

   @cocotb.test()
   async def test_pwm_duty_cycle(dut):
       # Start a clock signal
       clock = Clock(dut.clk, 10, units="ns")
       cocotb.start_soon(clock.start())

       # Apply reset
       dut.rst_n.value = 0
       dut.duty_cycle.value = 64
       await ClockCycles(dut.clk, 5)
       dut.rst_n.value = 1

       # Count how many cycles the output stays high
       high_count = 0
       total_cycles = 256
       for _ in range(total_cycles):
           await RisingEdge(dut.clk)
           if dut.pwm_out.value == 1:
               high_count += 1

       measured_duty = high_count / total_cycles
       expected_duty = 64 / 256

       assert abs(measured_duty - expected_duty) < 0.01, (
           f"Duty cycle error. Measured {measured_duty}, expected {expected_duty}"
       )
