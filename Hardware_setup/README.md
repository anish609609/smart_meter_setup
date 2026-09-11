# Hardware Setup: Physical Smart Meter & Relay Control

This directory contains the documentation and instructions for connecting a physical smart meter(Schneider-Electric-IEM3150) and a relay module to your Raspberry Pi.

---

## What is Inside This Folder?

* **`meter_reader.py`**: Python script using Modbus RTU communication to read real-time voltage, current, power, and energy measurements directly from the physical meter.
* **`SchneiderMeter_Manual.pdf`**: Official manual for the laboratory smart meter containing detailed hardware specs and Modbus register mapping.
* **`PI_5_GPIO.png`**: Visual pinout reference diagram for the Raspberry Pi GPIO headers.
* **`README.md`**: The hardware integration guide you are reading right now!

---

## Step 1: Connecting the Smart Meter to Raspberry Pi

1. **Hardware Connection**: Connect the Schneider iEM3150 smart meter to the Raspberry Pi using an **RS-485 to USB converter** (or RS-232 to USB converter depending on your adapter model).
2. **Meter Configuration**:
   * Refer to the manual (`SchneiderMeter_Manual.pdf`), specifically **pages 40–45**.
   * On **page 45**, review the default communication parameters for the lab meter model (**iEM3150**).
3. **Configure Settings**:
   * Ensure the hardware settings on the physical meter match the settings defined inside `meter_reader.py`:
     * **Port**: USB port path (e.g., `/dev/ttyUSB0` or `/dev/ttyUSB1`)
     * **Slave Address**: Modbus ID assigned to the meter (must be unique if cascading multiple meters)
     * **Baud Rate**: Communication speed (e.g., `19200` or `9600`)
     * **Parity**: Parity bit setting (e.g., Even, Odd, or None)

---

## Step 2: Testing Meter Communication

Navigate to the project root, activate your virtual environment, and run the reader script:

```bash
cd ~/Desktop/smart_meters
source venv/bin/activate
cd Hardware_Setup
python3 meter_reader.py

```

### Expected Terminal Output

Upon a successful Modbus read, your terminal will display real-time parameter outputs similar to this:

```text
--------------------------------------
2026-09-11 15:48:13
--------------------------------------
Current L1                 :        0.259 A
Current L2                 :        0.000 A
Current L3                 :        0.000 A
Current Average            :        0.086 A
Voltage L1-L2              :      115.833 V
Voltage L2-L3              :        0.000 V
Voltage L3-L1              :      115.860 V
Voltage L-L Average        :       77.231 V
Voltage L1-N               :      231.946 V
Voltage L2-N               :      116.114 V
Voltage L3-N               :      116.091 V
Voltage L-N Average        :      154.717 V
Active Power L1            :        0.058 kW
Active Power L2            :        0.000 kW
Active Power L3            :        0.000 kW
Active Power Total         :        0.058 kW
Power Factor Total         :        1.000 
Frequency                  :       49.926 Hz
Total Active Energy        :        0.270 kWh
Partial Active Energy      :        0.270 kWh
Active Energy L1           :        0.270 kWh
Active Energy L2           :        0.000 kWh
Active Energy L3           :        0.000 kWh

```

### Understanding the Meter Parameters

* **Current (L1, L2, L3, Average) [Amperes - A]**: The flow of electric charge through each individual phase line. The average gives the arithmetic mean across all 3 phases.
* **Voltage Line-to-Line (L1-L2, L2-L3, L3-L1, Average) [Volts - V]**: The potential difference measured directly between any two phase conductors.
* **Voltage Line-to-Neutral (L1-N, L2-N, L3-N, Average) [Volts - V]**: The potential difference measured between a specific phase conductor and the neutral wire (standard single-phase operating voltage).
* **Active Power (L1, L2, L3, Total) [Kilowatts - kW]**: Real, useful electrical power currently being consumed by connected loads to perform actual work.
* **Power Factor Total**: The ratio of real power flowing to the load over apparent power in the circuit (a value closer to `1.000` indicates maximum electrical efficiency).
* **Frequency [Hertz - Hz]**: The oscillation frequency of the AC power supply (typically stable around 50 Hz or 60 Hz).
* **Total Active Energy [Kilowatt-hours - kWh]**: Cumulative real electrical energy consumed over time since the meter was commissioned (this value is used for utility billing).
* **Partial Active Energy [Kilowatt-hours - kWh]**: Cumulative energy measured since the last user-triggered counter reset.
* **Active Energy (L1, L2, L3) [Kilowatt-hours - kWh]**: Breakdown of accumulated energy consumption per individual phase line.

---

## Step 3: Relay Setup & GPIO Control

To control external electrical loads or simulate remote load disconnection, connect a multi-channel relay module to the Raspberry Pi GPIO headers.

### Wiring Reference

Check the included file `PI_5_GPIO.png` for physical pin locations on the Raspberry Pi header:

* **Relay VCC** → **Raspberry Pi 5V Power** (Pin 2)
* **Relay GND** → **Raspberry Pi Ground** (Pin 6)
* **Relay IN1** → **Raspberry Pi GPIO17** (Pin 11) *(You can use any other standard output-capable GPIO pin)*

---


### Manual GPIO Testing Commands

Test relay activation directly from the terminal using the standard Raspberry Pi GPIO control utility (`pinctrl`). 

> **Note on Relay Logic:** Many relay modules use **active-low** logic (where `dl` turns the relay **ON** and `dh` turns it **OFF**), while others use **active-high** logic (where `dh` turns it **ON** and `dl` turns it **OFF**). Test both commands to determine your board's specific behavior.

1. **Drive Output High (`dh`):**
   ```bash
   pinctrl set 17 op dh
   ```

2. **Drive Output Low (`dl`):**
   ```bash
   pinctrl set 17 op dl
   ```

   *Verification:* In one of these state changes, you should hear a distinct mechanical "click" sound and observe the indicator LED for `IN1` on the relay board turn on. In the opposite state, the LED will turn off and the relay will open.

3. **Testing Additional Channels:**
   Move the signal wire from `IN1` to `IN2`, `IN3`, or `IN4` and repeat the commands, or connect 4 separate GPIO wires to test each channel independently using their respective GPIO numbers.
