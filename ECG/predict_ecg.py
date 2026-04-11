# ============================================================
#  ECG Predictor — Ensemble (ResNet + Inception + Transformer)
#  Folder: ECG\predict_ecg.py
#
#  কীভাবে চালাবে:
#    python predict_ecg.py --input cleaned_output\cleaned_ecg_xxx.csv
#
#  অথবা raw CSV সরাসরি দিলে auto-clean করবে:
#    python predict_ecg.py --input raw_output\ecg_xxx.csv --raw
#
#  60s signal হলে → 6 complete 10s segment → 6 prediction → final summary
# ============================================================

import numpy as np
import pandas as pd
import os
import sys
import argparse
import json
import tensorflow as tf
from tensorflow.keras import layers
from scipy.signal import butter, filtfilt, iirnotch

# ============================================================
#  Register custom PositionalEncoding layer (must match training)
# ============================================================
@tf.keras.utils.register_keras_serializable()
class PositionalEncoding(layers.Layer):
    """Positional encoding layer using pure TensorFlow ops (compatible with symbolic tensors)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, x):
        seq_len = tf.shape(x)[1]
        d_model = tf.shape(x)[2]
        positions = tf.range(seq_len, dtype=tf.float32)[:, tf.newaxis]          # (seq_len, 1)
        dims = tf.range(d_model, dtype=tf.float32)[tf.newaxis, :]               # (1, d_model)
        angle_rates = 1 / tf.pow(10000.0, (2 * (dims // 2)) / tf.cast(d_model, tf.float32))
        angles = positions * angle_rates                                        # (seq_len, d_model)
        # Apply sin to even indices, cos to odd indices
        even_mask = tf.cast(tf.math.floormod(dims, 2) == 0, tf.float32)
        odd_mask = 1 - even_mask
        angles = tf.sin(angles) * even_mask + tf.cos(angles) * odd_mask
        return x + angles[tf.newaxis, :, :]                                     # broadcast over batch

    def get_config(self):
        return super().get_config()


# ── Config ─────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(BASE_DIR, "..", "ECG Saved Model Download from Kaggle")

WINDOW_SIZE   = 3600   # 10s × 360Hz
SAMPLING_RATE = 360

CLASS_NAMES = [
    "Normal",
    "Supraventricular",
    "Ventricular",
    "Conduction Disorder",
    "Myocardial Infarction",
    "Hypertrophy",
    "Ischemia/ST-T",
    "Atrial Fibrillation"
]

W_RESNET      = 0.45
W_INCEPTION   = 0.35
W_TRANSFORMER = 0.20


# ── Load models (lazy, once) ───────────────────────────────
_MODELS = None

def load_models():
    global _MODELS
    if _MODELS is not None:
        return _MODELS

    model_files = {
        "resnet":      "resnet_final.keras",
        "inception":   "inception_final.keras",
        "transformer": "transformer_final.keras",
    }

    custom_objects = {'PositionalEncoding': PositionalEncoding}

    loaded = {}
    for name, fname in model_files.items():
        path = os.path.join(MODEL_DIR, fname)
        if not os.path.exists(path):
            print(f"❌ Model not found: {path}")
            print(f"   Kaggle থেকে download করে 'ECG Saved Model Download from Kaggle' folder এ রাখো।")
            sys.exit(1)
        print(f"  Loading {name}...", end='', flush=True)
        loaded[name] = tf.keras.models.load_model(path, custom_objects=custom_objects)
        print(" ✅")

    _MODELS = loaded
    return _MODELS


# ── Preprocess a single 10s window ────────────────────────
def preprocess_window(signal, fs=SAMPLING_RATE):
    """Training এর সাথে identical preprocessing।"""
    nyq  = 0.5 * fs
    low  = 0.5 / nyq
    high = min(45.0 / nyq, 0.99)

    b, a = butter(3, [low, high], btype='bandpass')
    sig  = filtfilt(b, a, signal)

    w0 = 50.0 / nyq
    if w0 < 1.0:
        bn, an = iirnotch(w0, 30)
        sig = filtfilt(bn, an, sig)

    mean = np.mean(sig)
    std  = np.std(sig)
    sig  = ((sig - mean) / (std + 1e-8)).astype(np.float32)
    return sig


# ── Predict a single 10s window ───────────────────────────
def predict_segment(window, models):
    """একটা 10s segment এর জন্য ensemble prediction।"""
    x = window.reshape(1, WINDOW_SIZE, 1).astype(np.float32)

    p_r = models["resnet"].predict(x, verbose=0)[0]
    p_i = models["inception"].predict(x, verbose=0)[0]
    p_t = models["transformer"].predict(x, verbose=0)[0]

    ensemble = W_RESNET * p_r + W_INCEPTION * p_i + W_TRANSFORMER * p_t
    class_idx = int(np.argmax(ensemble))
    confidence = float(ensemble[class_idx])

    return {
        "class_idx":  class_idx,
        "prediction": CLASS_NAMES[class_idx],
        "confidence": confidence,
        "class_probs": {CLASS_NAMES[i]: float(ensemble[i]) for i in range(len(CLASS_NAMES))}
    }


# ── Load cleaned CSV ───────────────────────────────────────
def load_signal(filepath):
    """Cleaned CSV থেকে signal load করে।"""
    try:
        df = pd.read_csv(filepath, comment='#', header=None)
    except Exception as e:
        print(f"❌ Cannot read CSV: {e}")
        return None

    # single column বা multi-column
    if df.shape[1] == 1:
        raw = df.iloc[:, 0]
    else:
        # header row detect
        first_val = df.iloc[0, -1]
        try:
            float(str(first_val))
            raw = df.iloc[:, -1]
        except ValueError:
            raw = df.iloc[1:, -1]

    raw = pd.to_numeric(raw, errors='coerce').dropna()
    return raw.values.astype(np.float32)


# ── Main prediction pipeline ───────────────────────────────
def predict_full_signal(signal_path, raw_mode=False):
    """পুরো signal কে 10s segment এ ভাগ করে predict করে।"""

    # Raw mode হলে auto-clean
    if raw_mode:
        print("🔧 Auto-cleaning raw signal...")
        # Import inside to avoid circular dependency if needed
        from clean_ecg import clean_pipeline
        cleaned_path = clean_pipeline(signal_path)
        if cleaned_path is None:
            return None
        signal_path = cleaned_path

    signal = load_signal(signal_path)
    if signal is None:
        return None

    total_samples = len(signal)
    total_seconds = total_samples / SAMPLING_RATE
    n_segments    = int(total_samples // WINDOW_SIZE)

    print(f"\n📊 Signal info:")
    print(f"   Total samples : {total_samples}")
    print(f"   Duration      : {total_seconds:.1f}s")
    print(f"   Segments (10s): {n_segments}")

    if n_segments == 0:
        print(f"❌ Signal too short for even 1 segment. Need ≥ {WINDOW_SIZE} samples.")
        return None

    # Remainder (leftover < 10s) warning
    leftover = total_samples - (n_segments * WINDOW_SIZE)
    if leftover > 0:
        print(f"   ⚠️  Last {leftover/SAMPLING_RATE:.1f}s discarded (< 10s)")

    print("\n🤖 Loading ensemble models...")
    models = load_models()

    print(f"\n⚡ Predicting {n_segments} segment(s)...\n")
    print(f"{'Seg':<5} {'Start':>7} {'End':>7} {'Prediction':<22} {'Confidence':>11}  Status")
    print("─" * 65)

    results = []
    all_class_probs = np.zeros(len(CLASS_NAMES))

    for seg_idx in range(n_segments):
        start_sample = seg_idx * WINDOW_SIZE
        end_sample   = start_sample + WINDOW_SIZE
        start_sec    = start_sample / SAMPLING_RATE
        end_sec      = end_sample   / SAMPLING_RATE

        window = signal[start_sample:end_sample]
        window = preprocess_window(window)   # re-preprocess each segment

        result = predict_segment(window, models)
        result["seg"]     = seg_idx + 1
        result["start_t"] = round(start_sec, 1)
        result["end_t"]   = round(end_sec,   1)

        all_class_probs += np.array([result["class_probs"][c] for c in CLASS_NAMES])

        is_normal = result["prediction"] == "Normal"
        status    = "✅ Normal" if is_normal else "⚠️  ABNORMAL"

        print(f"#{seg_idx+1:<4} {start_sec:>6.1f}s  {end_sec:>6.1f}s  "
              f"{result['prediction']:<22} {result['confidence']*100:>9.1f}%  {status}")

        results.append(result)

    # ── Summary ──────────────────────────────────────────────
    avg_probs = all_class_probs / n_segments
    top_idx   = int(np.argmax(avg_probs))
    top_condition = CLASS_NAMES[top_idx]
    top_prob      = float(avg_probs[top_idx]) * 100

    normal_count   = sum(1 for r in results if r["prediction"] == "Normal")
    abnormal_count = n_segments - normal_count

    print("\n" + "═" * 65)
    print("  📋 FINAL SUMMARY")
    print("═" * 65)
    print(f"  Overall Condition : {top_condition}")
    print(f"  Avg Probability   : {top_prob:.1f}%")
    print(f"  Normal Segments   : {normal_count} / {n_segments}")
    print(f"  Abnormal Segments : {abnormal_count} / {n_segments}")
    print()
    print("  Class Probabilities (avg across all segments):")
    for i, cls in enumerate(CLASS_NAMES):
        bar = "█" * int(avg_probs[i] * 30)
        print(f"    {cls:<25} {avg_probs[i]*100:>5.1f}% {bar}")
    print("═" * 65)

    # ── Return structured result (for API use) ─────────
    return {
        "top_condition":  top_condition,
        "top_prob":       round(top_prob, 2),
        "normal_count":   normal_count,
        "abnormal_count": abnormal_count,
        "total_segments": n_segments,
        "class_probs":    {CLASS_NAMES[i]: round(float(avg_probs[i]) * 100, 2)
                           for i in range(len(CLASS_NAMES))},
        "segments": [
            {
                "seg":        r["seg"],
                "start_t":    r["start_t"],
                "end_t":      r["end_t"],
                "prediction": r["prediction"],
                "confidence": round(r["confidence"], 4),
            }
            for r in results
        ]
    }


# ── Entry point ────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ECG Ensemble Predictor")
    parser.add_argument("--input", type=str, required=True,
                        help="Cleaned (or raw with --raw) ECG CSV file")
    parser.add_argument("--raw",   action="store_true",
                        help="Input is raw — auto-clean before predicting")
    parser.add_argument("--json",  action="store_true",
                        help="Print result as JSON (for API use)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ File not found: {args.input}")
        sys.exit(1)

    result = predict_full_signal(args.input, raw_mode=args.raw)

    if result and args.json:
        print("\n--- JSON OUTPUT ---")
        print(json.dumps(result, indent=2))