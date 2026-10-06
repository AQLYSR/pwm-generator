# RTL-to-GDS Flow for a PWM Generator

## 1. What Is a PWM Generator?

PWM means Pulse Width Modulation. A PWM generator is a circuit. It makes a square wave signal. The signal switches between two states: a high state and a low state.

The signal repeats at a fixed rate. This rate is called the frequency. Within each repeat, called a period, the signal stays high for part of the time. The signal stays low for the rest of the time.

The fraction of time the signal stays high is called the duty cycle. The duty cycle is a percentage. A duty cycle of 25% means the signal is high for one quarter of each period. A duty cycle of 75% means the signal is high for three quarters of each period.

A PWM generator lets you control the duty cycle. You send it a target value. The circuit produces a wave with that duty cycle.

### 1.1 How a Digital PWM Generator Works

A digital PWM generator uses a counter. The counter is a circuit block. It counts up by one on every clock cycle. When the counter reaches its maximum value, it resets to zero and starts again.

The circuit compares the counter value to the target duty cycle value. The output signal follows this rule:

- The output is high, when the counter value is less than the duty cycle value.
- The output is low, when the counter value is equal to or greater than the duty cycle value.

This simple comparison creates the PWM wave.

## 2. What Is a PWM Generator For?

Engineers use PWM generators in many real products. This section lists common uses.

### 2.1 Motor Speed Control

A motor needs power to spin. A PWM signal can control a motor at different speeds. A higher duty cycle sends more average power to the motor. A lower duty cycle sends less average power. The motor spins faster or slower as a result.

### 2.2 LED Brightness Control

An LED can show different brightness levels. A PWM signal can dim an LED. A higher duty cycle makes the LED look brighter. A lower duty cycle makes the LED look dimmer. The human eye cannot see the fast switching. The eye only sees the average brightness.

### 2.3 Power Supply Regulation

Many power supply circuits use PWM. These circuits are called switching regulators. A switching regulator adjusts its duty cycle to keep the output voltage steady. This method is more efficient than older, linear methods.

### 2.4 Audio Signal Generation

A PWM signal can represent an audio signal. The circuit changes the duty cycle quickly to match an audio waveform. A simple filter then turns the PWM signal into a smooth analog sound signal.

## 3. What You Will Build

In this project, you will build a digital PWM generator. You will use an industry-style design flow. This flow is called RTL-to-GDS.

RTL means Register Transfer Level. This is a way to describe digital circuit behavior in code.

GDS means Graphic Data System. A GDS file describes the exact physical layout of a chip. This file is what a chip factory uses to manufacture the chip.

The RTL-to-GDS flow has these main stages:

1. Write the circuit behavior in Verilog code.
2. Check the code for correctness with a testbench.
3. Convert the code into a physical chip layout.
4. Check the layout for manufacturing errors.

You will complete all four stages in this guide.

## 4. What You Need Before You Start

You need the following items:

- A Mac computer.
- Homebrew. Homebrew is a package manager for macOS. It installs software from the terminal.
- Python, version 3.8 or later.
- Basic knowledge of digital logic. You should know what a clock signal is, and what a reset signal is.

You will install these tools during the project:

- **Icarus Verilog**: This tool simulates Verilog code.
- **cocotb**: This tool lets you write testbenches in Python.
- **OpenLane**: This tool converts Verilog code into a physical chip layout.
- **Sky130 PDK**: This is a Process Design Kit. It contains the manufacturing rules and cell library for the Sky130 process. Sky130 is an open-source process from SkyWater Technology.

## 5. Step-by-Step Instructions

Follow these steps in order. Do not skip a step.

### Step 1: Define the Design Specification

Before you write any code, write down the exact behavior of your circuit. This step prevents confusion later.

Your PWM generator has these signals:

| Signal | Direction | Width | Purpose |
|---|---|---|---|
| `clk` | Input | 1 bit | The clock signal |
| `rst_n` | Input | 1 bit | The reset signal. Active when low. |
| `duty_cycle` | Input | 8 bits | The target duty cycle value, from 0 to 255 |
| `pwm_out` | Output | 1 bit | The PWM output signal |

The circuit behavior is this:

- An internal 8-bit counter increases by one on every clock cycle.
- The output `pwm_out` is high, when the counter value is less than `duty_cycle`.
- The output `pwm_out` is low, when the counter value is equal to or greater than `duty_cycle`.
- A low signal on `rst_n` resets the counter to zero and sets `pwm_out` to low.

### Step 2: Install the Verification Tools

1. Open the Terminal application on your Mac.
2. Install Icarus Verilog with this command:

   ```
   brew install icarus-verilog
   ```

3. Install cocotb with this command:

   ```
   pip install cocotb
   ```

4. Check the installation. Type this command:

   ```
   cocotb-config --version
   ```

   The terminal must show a version number. If it shows an error, the installation did not finish correctly.

### Step 3: Write the Verilog Code

1. Create a new folder for your project. Name it `pwm_generator`.
2. Inside this folder, create a new file. Name it `pwm_gen.v`.
3. Open `pwm_gen.v` in your text editor.
4. Write the Verilog module. The module must match the specification from Step 1. Use this code:

   ```verilog
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
   ```

5. Save the file.

### Step 4: Check the Code Style

1. Read through your code line by line.
2. Confirm that the module name matches the file name.
3. Confirm that every signal name matches the specification table from Step 1.
4. Confirm that you used `<=` for all assignments inside the `always` block. This symbol is correct for sequential logic.

### Step 5: Write the cocotb Testbench

The testbench checks that your circuit behaves correctly. It does not change the circuit. It only observes the circuit and reports pass or fail results.

1. In the `pwm_generator` folder, create a new file. Name it `test_pwm_gen.py`.
2. Write the test code. Use this code:

   ```python
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
   ```

3. Save the file.

This test sets the target duty cycle to 64, which equals 25%. The test then counts how many cycles the output stays high, out of 256 total cycles. The test compares this measured value to the expected value.

### Step 6: Create the Makefile

1. In the `pwm_generator` folder, create a new file. Name it `Makefile`.
2. Write this content:

   ```makefile
   SIM ?= icarus
   TOPLEVEL_LANG ?= verilog

   VERILOG_SOURCES += $(PWD)/pwm_gen.v
   TOPLEVEL = pwm_gen
   MODULE = test_pwm_gen

   include $(shell cocotb-config --makefiles)/Makefile.sim
   ```

3. Save the file.

### Step 7: Run the Test

1. In the terminal, go to the `pwm_generator` folder. Use the `cd` command.
2. Run this command:

   ```
   make
   ```

3. Wait for the simulation to finish.
4. Read the output. Look for the word `PASS` next to your test name. This word confirms the test succeeded.
5. If the output shows `FAIL`, read the error message. The message tells you the measured value and the expected value. Use this information to find the error in your Verilog code.

### Step 8: Add a Second Test

One test is not enough. Add a test for a boundary condition. A boundary condition is an extreme input value.

1. Open `test_pwm_gen.py` again.
2. Add a new test function below the first one. Use this code:

   ```python
   @cocotb.test()
   async def test_pwm_zero_duty(dut):
       clock = Clock(dut.clk, 10, units="ns")
       cocotb.start_soon(clock.start())

       dut.rst_n.value = 0
       dut.duty_cycle.value = 0
       await ClockCycles(dut.clk, 5)
       dut.rst_n.value = 1

       for _ in range(256):
           await RisingEdge(dut.clk)
           assert dut.pwm_out.value == 0, "Output must stay low when duty_cycle is 0"
   ```

3. Save the file.
4. Run `make` again.
5. Confirm both tests show `PASS`.

This second test checks that a duty cycle of zero produces a constant low output. This is a correct edge case for your design.

### Step 9: Install OpenLane

OpenLane converts your Verilog code into a physical chip layout. This step uses more disk space and more time than the earlier steps.

1. In the terminal, run this command:

   ```
   pip install openlane
   ```

2. Wait for the installation to finish. This command also sets up a supporting environment for the physical design tools.
3. Check the installation. Run this command:

   ```
   openlane --version
   ```

   The terminal must show a version number.

### Step 10: Create the OpenLane Configuration File

1. In the `pwm_generator` folder, create a new file. Name it `config.json`.
2. Write this content:

   ```json
   {
       "DESIGN_NAME": "pwm_gen",
       "VERILOG_FILES": "dir::pwm_gen.v",
       "CLOCK_PORT": "clk",
       "CLOCK_PERIOD": 10,
       "PDK": "sky130A"
   }
   ```

3. Save the file.

This file tells OpenLane the name of your design, the location of your Verilog file, the name of your clock signal, the target clock period in nanoseconds, and the manufacturing process to target.

### Step 11: Run the OpenLane Flow

1. In the terminal, confirm you are in the `pwm_generator` folder.
2. Run this command:

   ```
   openlane config.json
   ```

3. Wait for the flow to finish. This process includes several stages: synthesis, floorplanning, placement, clock tree synthesis, and routing. The process can take several minutes.
4. Watch the terminal output for error messages. A successful run ends without error messages, and it creates a results folder with your final files.

### Step 12: Check the Results

1. Open the results folder created by OpenLane.
2. Find the final GDS file. This file has the extension `.gds`.
3. Find the final timing report. This report shows the maximum clock frequency your design can reach.
4. Find the final area report. This report shows the physical size of your design, in square micrometers.
5. Write down these three values:
   - The maximum clock frequency.
   - The design area.
   - Confirmation that the flow completed without DRC or LVS errors. DRC means Design Rule Check. LVS means Layout Versus Schematic. Both checks confirm your layout is correct and manufacturable.

### Step 13: Document Your Project

1. Create a file named `README.md` in your project folder.
2. In this file, include the following items:
   - A short description of the PWM generator and its purpose.
   - The signal table from Step 1.
   - A screenshot or description of your passing test results from Step 7 and Step 8.
   - The final metrics from Step 12: clock frequency, area, and DRC/LVS status.
3. Upload your project folder to a code hosting website, for example, GitHub.
4. Confirm that your `README.md` file displays correctly on the website.

## 6. Summary of What You Learned

After you complete this guide, you will have practiced these skills:

- Writing synthesizable Verilog code for a digital circuit.
- Writing a Python-based testbench with cocotb.
- Running circuit simulations with Icarus Verilog.
- Running a complete RTL-to-GDS physical design flow with OpenLane.
- Using the open-source Sky130 process design kit.
- Reading timing, area, and manufacturability reports.

These skills form the core workflow of a real digital IC design engineer.
