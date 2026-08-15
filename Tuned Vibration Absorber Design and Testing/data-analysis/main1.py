import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# ===== SETTINGS =====
FILE = "mpu6050_log.csv"
SAMPLE_RATE = 200  # Hz
# ====================

os.makedirs("plots_time_no_abs", exist_ok=True)
os.makedirs("plots_fft_no_abs", exist_ok=True)

df = pd.read_csv(FILE)

# Detect AZ column
if 'az_g' in df.columns:
    az_col = 'az_g'
elif 'az' in df.columns:
    az_col = 'az'
else:
    raise ValueError("AZ column not found")

df = df[['voltage', az_col]].dropna()
df['voltage'] = df['voltage'].round(2)

unique_voltages = sorted(df['voltage'].unique())
print("Voltages:", unique_voltages)

results = []

for v in unique_voltages:

    segment = df[df['voltage'] == v].reset_index(drop=True)

    # 🔥 SPECIAL CASE: 7V → skip first 1000 samples
    if np.isclose(v, 7.0) and len(segment) > 1000:
        print("Fixing 7V duplicate...")
        segment = segment.iloc[1000:]

    if len(segment) < 100:
        continue

    az = segment[az_col].values
    az = az - np.mean(az)

    t = np.arange(len(az)) / SAMPLE_RATE

    # -------- TIME DOMAIN --------
    plt.figure(figsize=(10, 4))
    plt.plot(t[:1000], az[:1000])
    plt.title(f"Time Domain AZ at {v}V (NO absorber)")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (g)")
    plt.grid()

    plt.savefig(f"plots_time_no_abs/time_{v}V.png", dpi=150)
    plt.close()

    # -------- METRICS --------
    rms = np.sqrt(np.mean(az**2))
    p2p = np.max(az) - np.min(az)

    # -------- FFT --------
    n = len(az)
    freqs = np.fft.rfftfreq(n, d=1/SAMPLE_RATE)
    fft_mag = np.abs(np.fft.rfft(az))

    idx = np.argmax(fft_mag[1:]) + 1
    dom_freq = freqs[idx]

    plt.figure(figsize=(10, 4))
    plt.plot(freqs, fft_mag)
    plt.title(f"FFT AZ at {v}V (NO absorber)")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.xlim(0, 50)
    plt.grid()

    plt.savefig(f"plots_fft_no_abs/fft_{v}V.png", dpi=150)
    plt.close()

    results.append({
        'voltage': v,
        'rms': rms,
        'peak_to_peak': p2p,
        'dominant_freq': dom_freq
    })

# -------- SUMMARY --------
res_df = pd.DataFrame(results)
res_df.to_csv("summary_no_abs.csv", index=False)

# RMS plot
plt.figure()
plt.plot(res_df['voltage'], res_df['rms'], marker='o')
plt.title("RMS vs Voltage (NO absorber)")
plt.xlabel("Voltage")
plt.ylabel("RMS (g)")
plt.grid()
plt.savefig("rms_vs_voltage_no_abs.png", dpi=150)
plt.close()

# P2P plot
plt.figure()
plt.plot(res_df['voltage'], res_df['peak_to_peak'], marker='o')
plt.title("Peak-to-Peak vs Voltage (NO absorber)")
plt.xlabel("Voltage")
plt.ylabel("Peak-to-Peak (g)")
plt.grid()
plt.savefig("p2p_vs_voltage_no_abs.png", dpi=150)
plt.close()

print("\n===== SUMMARY (NO ABSORBER) =====")
print(res_df)