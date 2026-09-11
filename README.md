
```markdown
# Smart Meters Setup Guide

This repository provides a hands-on, end-to-end guide for configuring both
simulated and physical smart meter hardware systems.

---

## Directory Structure

smart_meter_setup/
│
├── Hardware_Setup/               # Physical hardware integration layer
│   ├── meter_reader.py           # Modbus RTU polling script for Schneider iEM3150
│   ├── SchneiderMeter_Manual.pdf # Manufacturer manual & register mappings
│   ├── PI_5_GPIO.png             # Raspberry Pi 5 GPIO header reference diagram
│   └── README.md                 # Physical hardware wiring & setup guide
│
├── Software_setup/               # Simulation, API, and web dashboard layer
│   ├── meter_simulator.py        # Synthetic MQTT publisher script
│   ├── web_ui.py                 # Flask web dashboard & MQTT subscriber
│   ├── templates/index.html      # Frontend web dashboard template
│   └── README.md                 # Software simulation & testing guide
│
├── venv/                         # Python virtual environment (Auto-generated after you run the commands)
└── README.md                     # Master project documentation

```

---

## Getting Started

Follow these initial steps to set up your environment:

### 1. Create and Navigate to Project Directory

```bash
mkdir -p ~/Desktop/smart_meter_setup
cd ~/Desktop/smart_meter_setup

```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv

```

### 3. Activate the Virtual Environment

```bash
source venv/bin/activate

```

### 4. Install Core Software Dependencies

```bash
pip install paho-mqtt flask

```

> **Note:** The dependencies above set up the software simulation stack (MQTT client + Flask web dashboard).

---

## Subsystem Navigation

### Software Setup (Simulation & Dashboard)

Once environment setup is complete:

1. Navigate to the software directory:
```bash
cd ~/Desktop/smart_meter_setup/Software_setup

```


2. Follow the step-by-step instructions inside [`Software_setup/README.md`] to run the simulator and view the live telemetry dashboard.

---

### Hardware Setup (Physical Modbus Meter & Relays)

To prepare your system for communication with physical smart meter hardware:

1. Return to the project root directory and activate the environment:
```bash
cd ~/Desktop/smart_meter_setup
source venv/bin/activate

```


2. Install Modbus RTU hardware drivers:
```bash
pip install pymodbus pyserial

```


> **Note:** These libraries enable RS-485/Modbus RTU serial communication with physical smart meters like the Schneider iEM3150.


3. Navigate to the hardware directory:
```bash
cd ~/Desktop/smart_meter_setup/Hardware_Setup

```


4. Follow the step-by-step instructions inside [`Hardware_Setup/README.md`] to connect your RS-485-to-USB adapter, wire the meter, test GPIO relay logic, and execute the reader script.

```

```
