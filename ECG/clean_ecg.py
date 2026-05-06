# ============================================================
#  ECG Signal Cleaner — Ultra Advanced Noise Cancellation
#  Folder: ECG\clean_ecg.py
#
#  Simplified usage:
#    python clean_ecg.py
#  (automatically finds the latest raw CSV in raw_output folder)
#
#  Input format supported:
#    - Single column of float values (no header), e.g.:
#        -0.02357178
#        -0.09708435
#    - Two columns with header: sample_index,ecg_value (legacy)
#
#  Advanced features:
#    - Wavelet denoising (multi-level DWT thresholding)
#    - Hampel filter for outlier removal (robust)
#    - Adaptive notch filter for 50 Hz and harmonics
#    - Baseline wander removal via cubic spline fitting
#    - Median filter for impulse spikes
#    - MAD-based outlier detection
#    - Flat-line interpolation
#    - Bandpass filtering (0.5-40 Hz)
#    - Automatic resampling to 360 Hz
# ============================================================

import numpy as np
import pandas as pd
import os
import argparse
import glob
from scipy.signal import butter, filtfilt, iirnotch, resample_poly, medfilt
from scipy.interpolate import CubicSpline
from scipy.stats import median_abs_deviation
from math import gcd
from datetime import datetime

# Optional wavelet import
try:
    import pywt
    WAVELET_AVAILABLE = True
except ImportError:
    WAVELET_AVAILABLE = False
    print("⚠️ PyWavelets not installed. Wavelet denoising disabled. Install with: pip install PyWavelets")

# ── Config ─────────────────────────────────────────────────
TARGET_FS     = 360
WINDOW_SIZE   = 3600
MIN_SAMPLES   = WINDOW_SIZE

FLAT_WINDOW   = 72
HAMPEL_WINDOW = 11          # Window size for Hampel filter
HAMPEL_THRESH = 3.5         # Number of MADs for outlier detection
MAD_THRESH    = 5.0

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleaned_output")
RAW_DIR    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw_output")

# ── Helper: find latest raw file ──────────────────────────
def find_latest_raw_file():
    if not os.path.exists(RAW_DIR):
        return None
    csv_files = glob.glob(os.path.join(RAW_DIR, "*.csv"))
    if not csv_files:
        return None
    latest = max(csv_files, key=os.path.getctime)
    return latest

# ── Load CSV ──────────────────────────────────────────────
def load_csv(filepath):
    print(f"\n📂 Loading: {os.path.basename(filepath)}")
    try:
        # Try reading with no header first to inspect
        df_raw = pd.read_csv(filepath, comment='#', header=None)
    except Exception as e:
        print(f"  ❌ CSV read failed: {e}")
        return None

    if df_raw.shape[1] == 0:
        print("  ❌ Empty file.")
        return None

    # ── Detect format ──────────────────────────────────────
    # Check if first row looks like a header (non-numeric string)
    first_val = str(df_raw.iloc[0, 0]).strip().lower()
    has_header = not _is_numeric(first_val)

    if has_header:
        # Re-read with header
        try:
            df = pd.read_csv(filepath, comment='#')
        except Exception as e:
            print(f"  ❌ CSV re-read with header failed: {e}")
            return None

        # Pick the ecg_value column if present, otherwise last numeric column
        if 'ecg_value' in df.columns:
            raw = df['ecg_value']
        else:
            raw = df.iloc[:, -1]
        print(f"  ℹ️  Detected format: with header ({list(df.columns)})")
    else:
        # Headerless — single or multi column
        if df_raw.shape[1] == 1:
            # Pure single-column float file (new format)
            raw = df_raw.iloc[:, 0]
            print("  ℹ️  Detected format: headerless single-column floats")
        elif df_raw.shape[1] >= 2:
            # Possibly index + value without header
            raw = df_raw.iloc[:, -1]
            print(f"  ℹ️  Detected format: headerless {df_raw.shape[1]}-column, using last column")
        else:
            print("  ❌ Unrecognized CSV format.")
            return None

    raw = pd.to_numeric(raw, errors='coerce').dropna()
    if len(raw) == 0:
        print("  ❌ No numeric data found.")
        return None

    signal = raw.values.astype(np.float64)
    print(f"  ✅ Loaded {len(signal)} samples ({len(signal)/TARGET_FS:.1f}s at {TARGET_FS}Hz)")
    return signal

def _is_numeric(s):
    """Return True if string s can be parsed as a float."""
    try:
        float(s)
        return True
    except ValueError:
        return False

# ── Ultra‑advanced: Wavelet Denoising ─────────────────────
def wavelet_denoise(signal, wavelet='db4', level=4, method='soft'):
    """Multi-level wavelet denoising using universal threshold."""
    if not WAVELET_AVAILABLE:
        return signal
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745
    if sigma < 1e-8:
        return signal
    threshold = sigma * np.sqrt(2 * np.log(len(signal)))
    new_coeffs = [coeffs[0]]
    for i in range(1, len(coeffs)):
        if method == 'soft':
            new_coeffs.append(pywt.threshold(coeffs[i], threshold, mode='soft'))
        else:
            new_coeffs.append(pywt.threshold(coeffs[i], threshold, mode='hard'))
    denoised = pywt.waverec(new_coeffs, wavelet)
    if len(denoised) > len(signal):
        denoised = denoised[:len(signal)]
    print(f"  ✅ Wavelet denoising (wavelet={wavelet}, level={level}, method={method})")
    return denoised

# ── Hampel filter for outlier removal ─────────────────────
def hampel_filter(signal, window_size=HAMPEL_WINDOW, n_sigmas=HAMPEL_THRESH):
    """Hampel identifier: replace outliers with median of window."""
    signal = signal.copy()
    n = len(signal)
    half_window = window_size // 2
    for i in range(n):
        start = max(0, i - half_window)
        end = min(n, i + half_window + 1)
        window = signal[start:end]
        median = np.median(window)
        mad = median_abs_deviation(window)
        if mad == 0:
            continue
        if abs(signal[i] - median) > n_sigmas * mad:
            signal[i] = median
    print(f"  ✅ Hampel filter applied (window={window_size}, sigma={n_sigmas})")
    return signal

# ── Remove lead-off & saturation (float-aware) ────────────
def remove_lead_off_artifacts(signal):
    """
    For float signals, detect statistical outliers instead of
    fixed ADC thresholds. Samples beyond MAD_THRESH * MAD from
    the median are treated as artifacts and interpolated.
    """
    signal = signal.copy()
    n = len(signal)
    median = np.median(signal)
    mad = median_abs_deviation(signal)
    if mad < 1e-8:
        return signal
    bad_mask = np.abs(signal - median) > MAD_THRESH * mad
    bad_count = np.sum(bad_mask)
    if bad_count == 0:
        return signal
    indices = np.arange(n)
    good_idx = indices[~bad_mask]
    good_val = signal[~bad_mask]
    if len(good_val) >= 2:
        signal[bad_mask] = np.interp(indices[bad_mask], good_idx, good_val)
        print(f"  ✅ Fixed {bad_count} lead-off/saturation artifacts ({bad_count/n*100:.1f}%)")
    return signal

# ── Baseline wander removal (cubic spline) ────────────────
def remove_baseline_wander(signal, fs=TARGET_FS, cutoff=0.5):
    """Estimate baseline by cubic spline on minima every 0.5s."""
    signal = signal.copy()
    n = len(signal)
    step = int(fs * 0.5)
    indices = np.arange(0, n, step)
    if len(indices) < 4:
        return signal
    min_vals = [np.min(signal[max(0, i-step//2):min(n, i+step//2)]) for i in indices]
    spline = CubicSpline(indices, min_vals, bc_type='natural')
    baseline = spline(np.arange(n))
    corrected = signal - baseline
    print(f"  ✅ Baseline wander removed (cubic spline, step={step} samples)")
    return corrected

# ── Adaptive notch filter for 50 Hz and harmonics ─────────
def adaptive_notch_filter(signal, fs=TARGET_FS, freqs=[50, 100, 150, 200], quality=30):
    """Remove multiple powerline harmonics."""
    filtered = signal.copy()
    nyq = 0.5 * fs
    for freq in freqs:
        w0 = freq / nyq
        if w0 < 1.0:
            b, a = iirnotch(w0, quality)
            filtered = filtfilt(b, a, filtered)
    print(f"  ✅ Adaptive notch filter applied (freqs: {freqs} Hz)")
    return filtered

# ── Median filter for spikes ──────────────────────────────
def median_filter_denoise(signal, kernel_size=5):
    filtered = medfilt(signal, kernel_size)
    print(f"  ✅ Median filter (kernel={kernel_size})")
    return filtered

# ── Flat-line detection ───────────────────────────────────
def fix_flatline_segments(signal):
    signal = signal.copy()
    n = len(signal)
    bad_mask = np.zeros(n, dtype=bool)
    i = 0
    flat_count = 0
    while i < n - FLAT_WINDOW:
        window = signal[i:i+FLAT_WINDOW]
        if np.std(window) < 1e-4:          # float-safe threshold (was 0.5 for ADC)
            bad_mask[i:i+FLAT_WINDOW] = True
            flat_count += 1
            i += FLAT_WINDOW
        else:
            i += 1
    count = np.sum(bad_mask)
    if count == 0:
        return signal
    indices = np.arange(n)
    good_idx = indices[~bad_mask]
    good_val = signal[~bad_mask]
    if len(good_val) >= 2:
        signal[bad_mask] = np.interp(indices[bad_mask], good_idx, good_val)
        print(f"  ✅ Fixed {count} flat-line samples in {flat_count} segments")
    return signal

# ── Bandpass filter (0.5 - 40 Hz) ─────────────────────────
def bandpass_filter(signal, fs=TARGET_FS, lowcut=0.5, highcut=40.0, order=4):
    nyq = 0.5 * fs
    low = max(lowcut / nyq, 0.001)
    high = min(highcut / nyq, 0.99)
    b, a = butter(order, [low, high], btype='bandpass')
    filtered = filtfilt(b, a, signal)
    print(f"  ✅ Bandpass filter ({lowcut}-{highcut} Hz, order {order})")
    return filtered

# ── Resample ──────────────────────────────────────────────
def resample_signal(signal, from_fs, to_fs):
    if from_fs == to_fs:
        return signal
    g = gcd(int(from_fs), int(to_fs))
    up = int(to_fs) // g
    down = int(from_fs) // g
    resampled = resample_poly(signal, up, down)
    print(f"  ✅ Resampled {from_fs}Hz → {to_fs}Hz ({len(signal)} → {len(resampled)} samples)")
    return resampled

# ── Normalize ─────────────────────────────────────────────
def normalize_signal(signal):
    mean = np.mean(signal)
    std = np.std(signal)
    if std < 1e-8:
        return signal
    normalized = ((signal - mean) / (std + 1e-8)).astype(np.float32)
    print(f"  ✅ Normalized (mean={mean:.6f}, std={std:.6f})")
    return normalized

# ── Save cleaned CSV ──────────────────────────────────────
def save_cleaned(signal, original_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(original_path))[0]
    out_path = os.path.join(output_dir, f"cleaned_{basename}.csv")
    pd.DataFrame(signal, columns=["ecg_value"]).to_csv(out_path, index=False)
    print(f"\n💾 Saved: {out_path}")
    print(f"   Total samples: {len(signal)}")
    print(f"   Duration     : {len(signal)/TARGET_FS:.1f}s")
    segments = len(signal) // WINDOW_SIZE
    print(f"   10s segments : {segments}")
    return out_path

# ── Main pipeline (ultra advanced) ────────────────────────
def clean_pipeline(input_path, input_fs=TARGET_FS):
    print("=" * 60)
    print("  ECG Signal Cleaning — Ultra Advanced Pipeline")
    print("=" * 60)

    signal = load_csv(input_path)
    if signal is None:
        return None

    print("\n🔧 Cleaning steps (ultra advanced):")

    # 1. Remove lead-off/saturation (MAD-based for float signals)
    signal = remove_lead_off_artifacts(signal)

    # 2. Median filter for spikes
    signal = median_filter_denoise(signal, kernel_size=5)

    # 3. Hampel filter for outliers
    signal = hampel_filter(signal, window_size=11, n_sigmas=3.5)

    # 4. Flat-line correction
    signal = fix_flatline_segments(signal)

    # 5. Wavelet denoising (if available)
    if WAVELET_AVAILABLE:
        signal = wavelet_denoise(signal, wavelet='db4', level=4, method='soft')
    else:
        print("  ⚠️ Wavelet denoising skipped (install PyWavelets)")

    # 6. Baseline wander removal
    signal = remove_baseline_wander(signal, fs=TARGET_FS)

    # 7. Resample if needed
    if input_fs != TARGET_FS:
        signal = resample_signal(signal, input_fs, TARGET_FS)

    # 8. Bandpass filter (0.5-40 Hz)
    signal = bandpass_filter(signal, fs=TARGET_FS, lowcut=0.5, highcut=40.0, order=4)

    # 9. Adaptive notch filter (50, 100, 150, 200 Hz)
    signal = adaptive_notch_filter(signal, fs=TARGET_FS, freqs=[50, 100, 150, 200], quality=30)

    # 10. Normalize
    signal = normalize_signal(signal)

    if len(signal) < MIN_SAMPLES:
        print(f"\n❌ After cleaning, signal too short ({len(signal)} samples).")
        return None

    out_path = save_cleaned(signal, input_path, OUTPUT_DIR)
    print(f"\n✅ Ultra advanced cleaning complete!\n📌 Next step: python predict_ecg.py --input \"{out_path}\"")
    return out_path

# ── Entry point ────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ECG Signal Cleaner (Ultra Advanced)")
    parser.add_argument("--input", type=str, default=None,
                        help="Input CSV file or folder path. If not given, uses latest file in raw_output/")
    parser.add_argument("--fs", type=int, default=TARGET_FS,
                        help=f"Input sampling rate in Hz (default: {TARGET_FS})")
    args = parser.parse_args()

    if args.input:
        input_path = args.input
    else:
        input_path = find_latest_raw_file()
        if input_path is None:
            print("❌ No raw CSV file found in 'raw_output' folder. Please record data first or specify --input.")
            exit(1)
        print(f"🔍 Auto-selected latest raw file: {os.path.basename(input_path)}")

    if os.path.isdir(input_path):
        csv_files = [f for f in os.listdir(input_path) if f.endswith('.csv')]
        if not csv_files:
            print(f"❌ No CSV files found in {input_path}")
            exit(1)
        print(f"Found {len(csv_files)} CSV file(s).")
        for csv_file in csv_files:
            full_path = os.path.join(input_path, csv_file)
            clean_pipeline(full_path, input_fs=args.fs)
    elif os.path.isfile(input_path):
        clean_pipeline(input_path, input_fs=args.fs)
    else:
        print(f"❌ Path not found: {input_path}")
        exit(1)