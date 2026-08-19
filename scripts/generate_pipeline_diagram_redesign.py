"""
Generate Redesigned, Highly Readable DMS-Eval Pipeline Diagram
=============================================================
Features:
- Symmetrical 2x3 Grid with Serpentine Clean Flow (No crossing arrows!)
- Card Header Banners with Distinct High-Contrast Themes
- Large, Crisp Typography (300 DPI)
- Clean tabular alignment inside cards
"""

import os
import shutil
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("assets", exist_ok=True)
os.makedirs("manuscript/figures", exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

def generate_pipeline_diagram():
    fig, ax = plt.subplots(figsize=(15.5, 9.0))
    ax.axis('off')
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)

    # Background canvas
    fig.patch.set_facecolor('#FFFFFF')

    # Card dimensions
    card_w = 0.298
    card_h = 0.385
    
    cards = [
        # Box 1 (Top-Left)
        {
            "num": "MODULE 1", "title": "Data Ingestion & Crop",
            "xy": (0.022, 0.505), "w": card_w, "h": card_h,
            "header_bg": "#1E3A8A", "body_bg": "#F8FAFC", "border": "#3B82F6",
            "bullets": [
                "• Source Corpus: 81 DMD cabin videos",
                "• Human Subjects: 14 participants",
                "• Sampling Rate: 1 FPS uniform extraction",
                "• Spatial Crop: 640×640 window (x=272, y=71)",
                "• Dataset Size: 15,723 RGB frames"
            ]
        },
        # Box 2 (Top-Middle)
        {
            "num": "MODULE 2", "title": "Master Ground Truth",
            "xy": (0.351, 0.505), "w": card_w, "h": card_h,
            "header_bg": "#065F46", "body_bg": "#F0FDF4", "border": "#10B981",
            "bullets": [
                "• 100% Direct Manual Human Labeling",
                "• 4 Warning Cues: phone, drink, yawn, hand",
                "• Single-Annotation Policy (0 or 1 box)",
                "• Mutual Exclusivity: hand covers mouth",
                "• 12,722 Negative Frames (80.91% alert)"
            ]
        },
        # Box 3 (Top-Right)
        {
            "num": "MODULE 3", "title": "8/3/3 Subject Split",
            "xy": (0.680, 0.505), "w": card_w, "h": card_h,
            "header_bg": "#854D0E", "body_bg": "#FEFCE8", "border": "#EAB308",
            "bullets": [
                "• Zero Identity Leakage across splits",
                "• Exhaustive Search across 60,060 sets",
                "• Max Relative Divergence ≤ 5.48%",
                "• Train Split: 8 Subj (9,087 frames, 1,748 box)",
                "• Val / Test Splits: 3 Subj each (3.4k / 3.2k)"
            ]
        },
        # Box 4 (Bottom-Right)
        {
            "num": "MODULE 4", "title": "Controlled Training",
            "xy": (0.680, 0.055), "w": card_w, "h": card_h,
            "header_bg": "#9A3412", "body_bg": "#FFF7ED", "border": "#F97316",
            "bullets": [
                "• Models: YOLO11n, YOLO26n, D-FINE-N",
                "• Budget: 220 Epochs (No early stopping)",
                "• Batch: Size = 1, Accumulation = 0",
                "• Precision: FP16 AMP, Seed = 13",
                "• Dedicated NVIDIA RTX 4060 (8 GB)"
            ]
        },
        # Box 5 (Bottom-Middle)
        {
            "num": "MODULE 5", "title": "Validation Calibration",
            "xy": (0.351, 0.055), "w": card_w, "h": card_h,
            "header_bg": "#3730A3", "body_bg": "#EEF2FF", "border": "#6366F1",
            "bullets": [
                "• Strict Test Isolation: Zero test access",
                "• Threshold Sweep: τ in [0.01, 0.99] on Val",
                "• Checkpoint Choice: Max Validation F1",
                "• Lock Optimal Threshold τ* per Model",
                "• Deterministic Tie-Breaking Logic"
            ]
        },
        # Box 6 (Bottom-Left)
        {
            "num": "MODULE 6", "title": "Test Evaluation & Latency",
            "xy": (0.022, 0.055), "w": card_w, "h": card_h,
            "header_bg": "#6B21A8", "body_bg": "#FAF5FF", "border": "#A855F7",
            "bullets": [
                "• Single-Pass Test Pass: 3,213 unseen frames",
                "• Metrics: mAP@0.5:0.95, mAP@0.5, P, R, F1",
                "• Hardware Timing: PyTorch CUDA Events",
                "• Latency Reporting: Median (p50), p95, FPS",
                "• Deployment: Local THOP GFLOPs, MB size"
            ]
        }
    ]

    header_h = 0.072

    for c in cards:
        x, y = c["xy"]
        w, h = c["w"], c["h"]

        # Main Card Body Box
        body_patch = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.006,rounding_size=0.022",
            facecolor=c["body_bg"], edgecolor=c["border"], linewidth=2.2
        )
        ax.add_patch(body_patch)

        # Header Pill / Banner Box
        header_patch = patches.FancyBboxPatch(
            (x, y + h - header_h), w, header_h,
            boxstyle="round,pad=0.006,rounding_size=0.022",
            facecolor=c["header_bg"], edgecolor=c["header_bg"], linewidth=1.0
        )
        ax.add_patch(header_patch)

        # Header Text
        ax.text(x + 0.015, y + h - 0.024, c["num"], fontsize=9.0, fontweight='bold', color='#E2E8F0', va='center')
        ax.text(x + 0.015, y + h - 0.049, c["title"], fontsize=12.0, fontweight='bold', color='#FFFFFF', va='center')

        # Bullets inside Card Body
        y_cursor = y + h - header_h - 0.038
        for bullet in c["bullets"]:
            # Format bullet with strong readable styling
            ax.text(x + 0.015, y_cursor, bullet, fontsize=9.8, color='#1E293B', va='center', fontweight='normal')
            y_cursor -= 0.054

    # Connecting Arrows
    arrow_kw = dict(arrowstyle="-|>", color="#0F172A", lw=3.0, mutation_scale=20)

    # 1 -> 2 (Top Left to Top Middle)
    ax.annotate('', xy=(0.349, 0.70), xytext=(0.322, 0.70), arrowprops=arrow_kw)

    # 2 -> 3 (Top Middle to Top Right)
    ax.annotate('', xy=(0.678, 0.70), xytext=(0.651, 0.70), arrowprops=arrow_kw)

    # 3 -> 4 (Top Right down to Bottom Right - Clean vertical turn)
    ax.annotate('', xy=(0.829, 0.442), xytext=(0.829, 0.503), arrowprops=arrow_kw)

    # 4 -> 5 (Bottom Right to Bottom Middle)
    ax.annotate('', xy=(0.651, 0.25), xytext=(0.678, 0.25), arrowprops=arrow_kw)

    # 5 -> 6 (Bottom Middle to Bottom Left)
    ax.annotate('', xy=(0.322, 0.25), xytext=(0.349, 0.25), arrowprops=arrow_kw)

    # Title Banner at Top
    plt.suptitle("DMS-Eval: End-to-End Benchmark Framework & Evaluation Protocol", fontsize=15.5, fontweight='bold', color='#0F172A', y=0.965)
    ax.text(0.5, 0.926, "Standardized Ingestion  ➜  Master Ground Truth  ➜  Subject-Disjoint Split  ➜  Controlled Training  ➜  Validation Calibration  ➜  Isolated Test Profiling",
            fontsize=10.0, color='#475569', ha='center', va='center', fontweight='bold')

    plt.tight_layout()
    out_asset = "assets/dms_eval_pipeline.png"
    plt.savefig(out_asset, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    shutil.copy(out_asset, "manuscript/figures/dms_eval_pipeline.png")
    print(f"[OK] Generated redesigned {out_asset}")

if __name__ == "__main__":
    generate_pipeline_diagram()
