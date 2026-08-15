"""Analyze two MPU6050 CSV datasets (main mass vs absorber mass).

What this script does:
1) Reads two CSV files.
2) Groups data by voltage.
3) Creates time-domain plots of AZ for each voltage.
4) Creates frequency-domain (FFT) plots of AZ for each voltage.
5) Generates summary plots across voltages:
   - RMS acceleration vs voltage
   - Peak-to-peak acceleration vs voltage
   - Dominant frequency vs voltage
   - Absorber reduction percentage vs voltage
6) Prints a small text summary to the console.

Expected CSV columns (flexible):
- voltage column: voltage, Voltage, V, label
- AZ column: az, az_g, AZ, accel_z, a_z
- optional timestamp column: timestamp, time, ts

If timestamps are present, sampling frequency is estimated from the median
inter-sample time. Otherwise, a nominal sampling rate is used.
"""

from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    from scipy.signal import get_window
except Exception:  # pragma: no cover
    get_window = None


# =========================
# USER SETTINGS
# =========================
MAIN_CSV = "mpu6050_log.csv"          # <-- change this
ABSORBER_CSV = "mpu6050_log_2.csv"  # <-- change this
OUTPUT_DIR = "analysis_outputs"

# If timestamps are missing or unusable, this fallback sample rate is used.
# Set this to match your Arduino delay-based sampling rate if needed.
NOMINAL_FS_HZ = 200.0

# Plot only the first N samples in the time-domain plot to keep figures readable.
TIME_PLOT_SAMPLES = 1000

# FFT settings
FFT_WINDOW = "hann"
MAX_FFT_FREQ_HZ = None  # e.g. 50.0 to zoom in, or None for full range

# Volts you expect in the experiment
EXPECTED_VOLTAGES = [5, 6, 7, 8, 9, 10, 11, 11.5]

# =========================


@dataclass
class RunMetrics:
    voltage: float
    n_samples: int
    fs_hz: float
    rms: float
    peak_to_peak: float
    dominant_freq_hz: float
    dominant_amp: float
    mean_abs: float


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def pick_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


def load_csv_flexible(csv_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    voltage_col = pick_column(df, ["voltage", "Voltage", "V", "label"])
    az_col = pick_column(df, ["az", "az_g", "AZ", "accel_z", "a_z"])
    ts_col = pick_column(df, ["timestamp", "time", "ts"])

    if voltage_col is None:
        raise ValueError(
            f"Could not find a voltage column in {csv_path}. Expected something like 'voltage'."
        )
    if az_col is None:
        raise ValueError(
            f"Could not find an AZ column in {csv_path}. Expected something like 'az' or 'az_g'."
        )

    out = pd.DataFrame()
    out["voltage"] = pd.to_numeric(df[voltage_col], errors="coerce")
    out["az"] = pd.to_numeric(df[az_col], errors="coerce")

    if ts_col is not None:
        # Try parsing timestamps; if it fails, we'll ignore it later.
        out["timestamp"] = pd.to_datetime(df[ts_col], errors="coerce")
    else:
        out["timestamp"] = pd.NaT

    out = out.dropna(subset=["voltage", "az"]).copy()
    out["voltage"] = out["voltage"].round(1)

    return out


def estimate_fs_from_timestamps(ts: pd.Series, fallback_fs: float) -> float:
    if ts is None or ts.isna().all():
        return fallback_fs

    diffs = ts.sort_values().diff().dt.total_seconds().dropna()
    diffs = diffs[(diffs > 0) & np.isfinite(diffs)]
    if len(diffs) < 3:
        return fallback_fs

    median_dt = float(diffs.median())
    if median_dt <= 0:
        return fallback_fs
    return 1.0 / median_dt


def segment_by_voltage(df: pd.DataFrame, expected: List[float]) -> Dict[float, pd.DataFrame]:
    groups: Dict[float, pd.DataFrame] = {}
    for v in expected:
        seg = df[np.isclose(df["voltage"].values, v, atol=1e-6)].copy()
        if len(seg) > 0:
            seg = seg.reset_index(drop=True)
            groups[float(v)] = seg
    return groups


def get_time_axis(seg: pd.DataFrame, fs_hz: float) -> np.ndarray:
    if "timestamp" in seg.columns and not seg["timestamp"].isna().all():
        ts = seg["timestamp"]
        # Use time relative to first valid timestamp
        t0 = ts.dropna().iloc[0]
        t = (ts - t0).dt.total_seconds().to_numpy(dtype=float)
        # Fill NaNs, if any, with sample index / fs
        if np.isnan(t).any():
            idx = np.arange(len(seg), dtype=float) / fs_hz
            t = np.where(np.isnan(t), idx, t)
        return t
    return np.arange(len(seg), dtype=float) / fs_hz


def compute_metrics(az: np.ndarray, fs_hz: float) -> Tuple[float, float, float, float]:
    x = np.asarray(az, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return np.nan, np.nan, np.nan, np.nan

    x0 = x - np.mean(x)
    rms = float(np.sqrt(np.mean(x0 ** 2)))
    p2p = float(np.max(x0) - np.min(x0))
    mean_abs = float(np.mean(np.abs(x0)))

    n = len(x0)
    if n < 4:
        return rms, p2p, np.nan, np.nan

    if get_window is not None:
        w = get_window(FFT_WINDOW, n)
    else:
        w = np.hanning(n)

    X = np.fft.rfft(x0 * w)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs_hz)
    mag = np.abs(X) * 2.0 / np.sum(w)

    # Ignore DC when finding the dominant vibration frequency.
    if len(freqs) > 1:
        idx = np.argmax(mag[1:]) + 1
    else:
        idx = 0

    dom_f = float(freqs[idx])
    dom_amp = float(mag[idx])
    return rms, p2p, dom_f, dom_amp, mean_abs


def fft_spectrum(az: np.ndarray, fs_hz: float) -> Tuple[np.ndarray, np.ndarray]:
    x = np.asarray(az, dtype=float)
    x = x[np.isfinite(x)]
    x = x - np.mean(x)
    n = len(x)
    if n < 4:
        return np.array([]), np.array([])

    if get_window is not None:
        w = get_window(FFT_WINDOW, n)
    else:
        w = np.hanning(n)

    X = np.fft.rfft(x * w)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs_hz)
    mag = np.abs(X) * 2.0 / np.sum(w)
    return freqs, mag


def plot_time_domain_compare(main_seg: pd.DataFrame, abs_seg: pd.DataFrame, voltage: float, fs_main: float, fs_abs: float, outdir: Path) -> None:
    t_main = get_time_axis(main_seg, fs_main)
    t_abs = get_time_axis(abs_seg, fs_abs)

    m = main_seg["az"].to_numpy(dtype=float)
    a = abs_seg["az"].to_numpy(dtype=float)

    n_main = min(len(m), TIME_PLOT_SAMPLES)
    n_abs = min(len(a), TIME_PLOT_SAMPLES)

    fig, ax = plt.subplots(2, 1, figsize=(12, 7), sharex=False)
    fig.suptitle(f"AZ time domain at {voltage:g} V")

    ax[0].plot(t_main[:n_main], m[:n_main])
    ax[0].set_title("Main mass")
    ax[0].set_xlabel("Time (s)")
    ax[0].set_ylabel("AZ")
    ax[0].grid(True, alpha=0.3)

    ax[1].plot(t_abs[:n_abs], a[:n_abs])
    ax[1].set_title("With absorber mass")
    ax[1].set_xlabel("Time (s)")
    ax[1].set_ylabel("AZ")
    ax[1].grid(True, alpha=0.3)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(outdir / f"time_domain_{voltage:g}V.png", dpi=200)
    plt.close(fig)


def plot_fft_compare(main_seg: pd.DataFrame, abs_seg: pd.DataFrame, voltage: float, fs_main: float, fs_abs: float, outdir: Path) -> None:
    f_m, mag_m = fft_spectrum(main_seg["az"].to_numpy(dtype=float), fs_main)
    f_a, mag_a = fft_spectrum(abs_seg["az"].to_numpy(dtype=float), fs_abs)

    fig, ax = plt.subplots(2, 1, figsize=(12, 7), sharex=False)
    fig.suptitle(f"AZ FFT at {voltage:g} V")

    if len(f_m) > 0:
        ax[0].plot(f_m, mag_m)
    ax[0].set_title("Main mass")
    ax[0].set_xlabel("Frequency (Hz)")
    ax[0].set_ylabel("Amplitude")
    ax[0].grid(True, alpha=0.3)
    if MAX_FFT_FREQ_HZ is not None:
        ax[0].set_xlim(0, MAX_FFT_FREQ_HZ)

    if len(f_a) > 0:
        ax[1].plot(f_a, mag_a)
    ax[1].set_title("With absorber mass")
    ax[1].set_xlabel("Frequency (Hz)")
    ax[1].set_ylabel("Amplitude")
    ax[1].grid(True, alpha=0.3)
    if MAX_FFT_FREQ_HZ is not None:
        ax[1].set_xlim(0, MAX_FFT_FREQ_HZ)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(outdir / f"fft_{voltage:g}V.png", dpi=200)
    plt.close(fig)


def build_summary_table(dataset_name: str, groups: Dict[float, pd.DataFrame], outdir: Path) -> pd.DataFrame:
    rows = []
    for v in sorted(groups.keys()):
        seg = groups[v]
        fs = estimate_fs_from_timestamps(seg["timestamp"], NOMINAL_FS_HZ)
        rms, p2p, dom_f, dom_amp, mean_abs = compute_metrics(seg["az"].to_numpy(dtype=float), fs)
        rows.append(
            {
                "dataset": dataset_name,
                "voltage": v,
                "n_samples": len(seg),
                "fs_hz": fs,
                "rms": rms,
                "peak_to_peak": p2p,
                "dominant_freq_hz": dom_f,
                "dominant_amp": dom_amp,
                "mean_abs": mean_abs,
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(outdir / f"summary_{dataset_name}.csv", index=False)
    return table


def plot_metric_vs_voltage(main_summary: pd.DataFrame, abs_summary: pd.DataFrame, outdir: Path) -> None:
    merged = pd.merge(
        main_summary,
        abs_summary,
        on="voltage",
        suffixes=("_main", "_abs"),
        how="inner",
    ).sort_values("voltage")

    if merged.empty:
        return

    # RMS vs voltage
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(merged["voltage"], merged["rms_main"], marker="o", label="Main mass")
    ax.plot(merged["voltage"], merged["rms_abs"], marker="o", label="With absorber")
    ax.set_title("RMS AZ vs Voltage")
    ax.set_xlabel("Voltage")
    ax.set_ylabel("RMS of AZ")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "rms_vs_voltage.png", dpi=200)
    plt.close(fig)

    # Peak-to-peak vs voltage
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(merged["voltage"], merged["peak_to_peak_main"], marker="o", label="Main mass")
    ax.plot(merged["voltage"], merged["peak_to_peak_abs"], marker="o", label="With absorber")
    ax.set_title("Peak-to-Peak AZ vs Voltage")
    ax.set_xlabel("Voltage")
    ax.set_ylabel("Peak-to-peak of AZ")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "p2p_vs_voltage.png", dpi=200)
    plt.close(fig)

    # Dominant frequency vs voltage
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(merged["voltage"], merged["dominant_freq_hz_main"], marker="o", label="Main mass")
    ax.plot(merged["voltage"], merged["dominant_freq_hz_abs"], marker="o", label="With absorber")
    ax.set_title("Dominant Frequency vs Voltage")
    ax.set_xlabel("Voltage")
    ax.set_ylabel("Dominant frequency (Hz)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "dominant_freq_vs_voltage.png", dpi=200)
    plt.close(fig)

    # Absorber reduction percentage in RMS and P2P
    merged["rms_reduction_pct"] = np.where(
        merged["rms_main"] > 0,
        100.0 * (merged["rms_main"] - merged["rms_abs"]) / merged["rms_main"],
        np.nan,
    )
    merged["p2p_reduction_pct"] = np.where(
        merged["peak_to_peak_main"] > 0,
        100.0 * (merged["peak_to_peak_main"] - merged["peak_to_peak_abs"]) / merged["peak_to_peak_main"],
        np.nan,
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(merged["voltage"], merged["rms_reduction_pct"], marker="o", label="RMS reduction %")
    ax.plot(merged["voltage"], merged["p2p_reduction_pct"], marker="o", label="P2P reduction %")
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.set_title("Absorber Effect (Reduction vs Main Mass)")
    ax.set_xlabel("Voltage")
    ax.set_ylabel("Reduction (%)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "absorber_reduction_pct.png", dpi=200)
    plt.close(fig)

    merged.to_csv(outdir / "comparison_summary.csv", index=False)


def print_text_summary(main_summary: pd.DataFrame, abs_summary: pd.DataFrame) -> None:
    merged = pd.merge(
        main_summary,
        abs_summary,
        on="voltage",
        suffixes=("_main", "_abs"),
        how="inner",
    ).sort_values("voltage")

    if merged.empty:
        print("No overlapping voltages found between the two datasets.")
        return

    merged["rms_reduction_pct"] = np.where(
        merged["rms_main"] > 0,
        100.0 * (merged["rms_main"] - merged["rms_abs"]) / merged["rms_main"],
        np.nan,
    )
    merged["p2p_reduction_pct"] = np.where(
        merged["peak_to_peak_main"] > 0,
        100.0 * (merged["peak_to_peak_main"] - merged["peak_to_peak_abs"]) / merged["peak_to_peak_main"],
        np.nan,
    )

    print("\n===== SUMMARY =====")
    print(merged[[
        "voltage",
        "rms_main", "rms_abs", "rms_reduction_pct",
        "peak_to_peak_main", "peak_to_peak_abs", "p2p_reduction_pct",
        "dominant_freq_hz_main", "dominant_freq_hz_abs",
    ]].to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    best_rms = merged.loc[merged["rms_reduction_pct"].idxmax()]
    best_p2p = merged.loc[merged["p2p_reduction_pct"].idxmax()]

    print("\nLikely interpretation:")
    print(
        f"- The absorber is most effective in RMS at {best_rms['voltage']:g} V, "
        f"with about {best_rms['rms_reduction_pct']:.1f}% RMS reduction relative to the main mass."
    )
    print(
        f"- The absorber is most effective in peak-to-peak amplitude at {best_p2p['voltage']:g} V, "
        f"with about {best_p2p['p2p_reduction_pct']:.1f}% reduction."
    )
    print(
        "- If the main-mass plots show a strong peak near one voltage and the absorber dataset lowers "
        "the time-domain amplitude and FFT peak at the same voltage, that is consistent with resonance "
        "mitigation by the absorber."
    )
    print(
        "- If the dominant frequency stays nearly constant across voltages, the voltage is mainly changing "
        "response amplitude, not the system's natural frequency."
    )


def process_dataset(csv_path: str | Path, dataset_name: str, outdir: Path) -> Tuple[pd.DataFrame, Dict[float, pd.DataFrame]]:
    df = load_csv_flexible(csv_path)
    groups = segment_by_voltage(df, EXPECTED_VOLTAGES)

    if not groups:
        raise ValueError(f"No expected voltages found in {csv_path}. Check the voltage labels.")

    # Save cleaned data for reference
    df.to_csv(outdir / f"cleaned_{dataset_name}.csv", index=False)

    summary = build_summary_table(dataset_name, groups, outdir)
    return summary, groups


def main() -> None:
    outdir = ensure_dir(OUTPUT_DIR)
    time_dir = ensure_dir(outdir / "time_domain")
    fft_dir = ensure_dir(outdir / "fft")

    main_summary, main_groups = process_dataset(MAIN_CSV, "main", outdir)
    abs_summary, abs_groups = process_dataset(ABSORBER_CSV, "absorber", outdir)

    # Generate per-voltage plots only for voltages present in both datasets.
    common_voltages = sorted(set(main_groups.keys()).intersection(abs_groups.keys()))
    if not common_voltages:
        raise ValueError("No common voltages found between the two CSVs.")

    for v in common_voltages:
        main_seg = main_groups[v]
        abs_seg = abs_groups[v]
        fs_main = estimate_fs_from_timestamps(main_seg["timestamp"], NOMINAL_FS_HZ)
        fs_abs = estimate_fs_from_timestamps(abs_seg["timestamp"], NOMINAL_FS_HZ)

        plot_time_domain_compare(main_seg, abs_seg, v, fs_main, fs_abs, time_dir)
        plot_fft_compare(main_seg, abs_seg, v, fs_main, fs_abs, fft_dir)

    plot_metric_vs_voltage(main_summary, abs_summary, outdir)
    print_text_summary(main_summary, abs_summary)

    print(f"\nPlots and CSV summaries saved to: {Path(outdir).resolve()}")
    print(f"- Time-domain figures: {Path(time_dir).resolve()}")
    print(f"- FFT figures: {Path(fft_dir).resolve()}")


if __name__ == "__main__":
    main()
