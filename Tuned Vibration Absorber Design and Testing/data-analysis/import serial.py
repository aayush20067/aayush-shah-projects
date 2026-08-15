import serial
import csv
import time
from datetime import datetime

# ===== SETTINGS =====
PORT = '/dev/cu.usbserial-A5069RR4'   # Change to '/dev/cu.usbserial-XXXX' on Mac
BAUDRATE = 115200
OUTPUT_FILE = 'mpu6050_log.csv'
EXPECTED_SAMPLES = 1000
# ====================

def open_serial():
    ser = serial.Serial(PORT, BAUDRATE, timeout=2)
    time.sleep(2)  # allow board reset
    ser.reset_input_buffer()
    return ser

def get_voltage():
    while True:
        try:
            val = float(input("Enter voltage (max 11.5): "))
            return val
        except:
            print("Invalid input")

def main():
    ser = open_serial()

    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'voltage', 'ax_g', 'ay_g', 'az_g'])

        print("System ready.\n")

        while True:
            voltage = get_voltage()

            # 🔥 Send voltage command to Arduino
            ser.write(f"{voltage}\n".encode())

            print(f"\nCollecting {EXPECTED_SAMPLES} samples at {voltage}V...\n")

            count = 0

            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()

                # Stop condition from Arduino
                if line == "DONE":
                    break

                try:
                    ax, ay, az = map(float, line.split(','))

                    writer.writerow([
                        datetime.now().isoformat(),
                        voltage,
                        ax, ay, az
                    ])

                    count += 1
                    print(f"{count}/{EXPECTED_SAMPLES} -> {ax:.4f}, {ay:.4f}, {az:.4f}")

                except:
                    continue  # skip malformed lines

            print(f"\nFinished {count} samples at {voltage}V\n")

            if voltage == 11.5:
                print("Stopping experiment.")
                break

    ser.close()
    print("Data saved to", OUTPUT_FILE)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped manually.")