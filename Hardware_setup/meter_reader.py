import struct
import time
from pymodbus.client import ModbusSerialClient

# ============================================================
# iEM3150 MODBUS SERIAL CONFIGURATION
# ============================================================

PORT = "/dev/ttyUSB0"  # USB-to-RS485 adapter path on Raspberry Pi/Linux
SLAVE_ID = 1          # Modbus slave address assigned to the physical meter
BAUDRATE = 9600        # Communication speed (must match meter display config)
PARITY = "E"           # Parity bit: 'E' (Even), 'O' (Odd), or 'N' (None)
STOPBITS = 1           # Number of stop bits
BYTESIZE = 8           # Data bits count per frame

# ============================================================
# MODBUS REGISTER MAP (Schneider iEM3150)
#
# Schneider documentation uses 1-based register indexing.
# PyModbus requires zero-based addresses (Address = Register - 1).
# Each IEEE-754 Float32 value spans 2 consecutive 16-bit registers.
# ============================================================

REGISTERS = {
    # --- Current Measurements ---
    "Current L1": {"register": 3000, "unit": "A"},
    "Current L2": {"register": 3002, "unit": "A"},
    "Current L3": {"register": 3004, "unit": "A"},
    "Current Average": {"register": 3010, "unit": "A"},
    
    # --- Voltage Measurements ---
    "Voltage L1-L2": {"register": 3020, "unit": "V"},
    "Voltage L2-L3": {"register": 3022, "unit": "V"},
    "Voltage L3-L1": {"register": 3024, "unit": "V"},
    "Voltage L-L Average": {"register": 3026, "unit": "V"},
    "Voltage L1-N": {"register": 3028, "unit": "V"},
    "Voltage L2-N": {"register": 3030, "unit": "V"},
    "Voltage L3-N": {"register": 3032, "unit": "V"},
    "Voltage L-N Average": {"register": 3036, "unit": "V"},
    
    # --- Active Power Measurements ---
    "Active Power L1": {"register": 3054, "unit": "kW"},
    "Active Power L2": {"register": 3056, "unit": "kW"},
    "Active Power L3": {"register": 3058, "unit": "kW"},
    "Active Power Total": {"register": 3060, "unit": "kW"},
    
    # --- Power Factor & Frequency ---
    "Power Factor Total": {"register": 3084, "unit": ""},
    "Frequency": {"register": 3110, "unit": "Hz"},
    
    # --- Energy Accumulators ---
    "Total Active Energy": {"register": 45100, "unit": "kWh"},
    "Partial Active Energy": {"register": 45108, "unit": "kWh"},
    "Active Energy L1": {"register": 45112, "unit": "kWh"},
    "Active Energy L2": {"register": 45114, "unit": "kWh"},
    "Active Energy L3": {"register": 45116, "unit": "kWh"},
}


# ============================================================
# DATA DECODING HELPER
# ============================================================

def registers_to_float(registers):
    """
    Packs two 16-bit integer Modbus registers (big-endian) into bytes 
    and unpacks them into a single 32-bit IEEE-754 floating-point number.
    """
    if len(registers) != 2:
        raise ValueError("Float32 decoding requires exactly 2 Modbus registers.")

    # '>HH' = Big-endian pack for two unsigned short integers (16-bit each)
    raw_bytes = struct.pack(">HH", registers[0], registers[1])
    
    # '>f' = Big-endian unpack into a single 32-bit float
    return struct.unpack(">f", raw_bytes)[0]


# ============================================================
# MODBUS READ FUNCTION
# ============================================================

def read_float32(client, register):
    """
    Converts 1-based Schneider register to 0-based Modbus address,
    reads 2 consecutive holding registers, and returns the decoded float.
    """
    address = register - 1  # Offset conversion for zero-based Modbus addressing

    # PyModbus 3.x uses 'device_id' instead of 'slave'
    result = client.read_holding_registers(
        address=address,
        count=2,
        device_id=SLAVE_ID
    )

    if result.isError():
        raise Exception(f"Modbus Read Error: {result}")

    return registers_to_float(result.registers)

# ============================================================
# MAIN APPLICATION LOOP
# ============================================================

# Initialize Modbus Serial Client (RS-485 via USB)
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity=PARITY,
    stopbits=STOPBITS,
    bytesize=BYTESIZE,
    timeout=2  # Response timeout in seconds
)

print("\n======================================")
print(" Schneider iEM3150 Modbus Reader")
print("======================================")
print(f"Port     : {PORT}")
print(f"Slave ID : {SLAVE_ID}")
print(f"Baudrate : {BAUDRATE}")
print(f"Parity   : {PARITY}\n")

# Attempt hardware connection
if not client.connect():
    print("ERROR: Could not open Modbus serial connection.")
    print("Check RS-485 wiring, USB port (/dev/ttyUSB0), and user permissions.")
    exit(1)

print("Modbus connection established successfully.\n")

try:
    while True:
        # Print timestamp header for each polling cycle
        print("--------------------------------------")
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        print("--------------------------------------")

        # Iterate through defined parameters and fetch real-time readings
        for name, info in REGISTERS.items():
            try:
                value = read_float32(client, info["register"])
                print(f"{name:25s}: {value:12.3f} {info['unit']}")
            except Exception as e:
                print(f"{name:25s}: ERROR -> {e}")

        print()
        time.sleep(2)  # Delay between polling cycles

except KeyboardInterrupt:
    print("\nScript stopped by user.")

finally:
    client.close()  # Safely release serial port on exit
    print("Serial connection closed.")
