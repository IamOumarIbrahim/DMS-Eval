"""
Generate Visual Figures:
1. Split Cue Proportions Grouped Bar Chart (assets/split_cue_proportions_comparison.png)
2. DMS-Eval End-to-End Pipeline Architecture Diagram (assets/dms_eval_pipeline.png)
=============================================================================
Saves 300 DPI publication-grade figures in assets/ and manuscript/figures/.
"""

import os
import shutil
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs("assets", exist_ok=True)
os.makedirs("manuscript/figures", exist_ok=True)

# Set high-quality styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

# -------------------------------------------------------------------------
# 1. SPLIT CUE PROPORTIONS GROUPED BAR CHART
# -------------------------------------------------------------------------
def generate_split_comparison_chart():
    cues = ['phone_use', 'drinking', 'yawning', 'hand_over_mouth']
    
    # Proportions in %
    global_props = [81.2063, 8.7971, 5.2982, 4.6984]
    train_props  = [81.0641, 8.8101, 5.3776, 4.7483]
    val_props    = [81.8466, 8.4507, 5.0078, 4.6948]
    test_props   = [80.9446, 9.1205, 5.3746, 4.5603]

    x = np.arange(len(cues))
    width = 0.20

    fig, ax = plt.subplots(figsize=(9.2, 5.4))

    rects1 = ax.bar(x - 1.5*width, global_props, width, label='Global Dataset (15,723 frames)', color='#2B6CB0', edgecolor='black', linewidth=0.8)
    rects2 = ax.bar(x - 0.5*width, train_props,  width, label='Train Split (8 Subj, 9,087 frames)', color='#38A169', edgecolor='black', linewidth=0.8)
    rects3 = ax.bar(x + 0.5*width, val_props,    width, label='Val Split (3 Subj, 3,423 frames)',   color='#DD6B20', edgecolor='black', linewidth=0.8)
    rects4 = ax.bar(x + 1.5*width, test_props,   width, label='Test Split (3 Subj, 3,213 frames)',  color='#805AD5', edgecolor='black', linewidth=0.8)

    ax.set_ylabel('Class Proportion within Positive Frames (%)', fontsize=11, fontweight='bold')
    ax.set_title('Target Warning Cue Proportions Across 8/3/3 Subject-Disjoint Splits\n(Max Absolute Relative Divergence $\\leq 5.48\\%$)', fontsize=12, fontweight='bold', pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(['phone_use\n(2,437 boxes)', 'drinking\n(264 boxes)', 'yawning\n(159 boxes)', 'hand_over_mouth\n(141 boxes)'], fontsize=10, fontweight='bold')
    ax.legend(frameon=True, facecolor='#F7FAFC', edgecolor='#CBD5E0', fontsize=9.5)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    ax.set_ylim(0, 95)

    # Add text labels on top of bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=7.5, rotation=45)

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    autolabel(rects4)

    plt.tight_layout()
    out_asset = "assets/split_cue_proportions_comparison.png"
    plt.savefig(out_asset, dpi=300)
    plt.close()
    shutil.copy(out_asset, "manuscript/figures/split_cue_proportions_comparison.png")
    print(f"[OK] Generated {out_asset}")

# -------------------------------------------------------------------------
# 2. DMS-EVAL PIPELINE ARCHITECTURE DIAGRAM
# -------------------------------------------------------------------------
def generate_pipeline_diagram():
    fig, ax = plt.subplots(figsize=(13, 6.8))
    ax.axis('off')
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)

    boxes = [
        # Box 1: Ingestion
        {"xy": (0.02, 0.52), "w": 0.21, "h": 0.40, "title": "1. Data Ingestion & Prep", 
         "lines": ["• DMD Video Corpus (81 vids)", "• 14 Human Subjects", "• 1 FPS Uniform Sampling", "• 640×640 Window Crop", "• 15,723 Total Frames"],
         "color": "#EBF8FF", "edge": "#3182CE"},
        
        # Box 2: Annotation
        {"xy": (0.27, 0.52), "w": 0.21, "h": 0.40, "title": "2. Authoritative Ground Truth",
         "lines": ["• 100% Direct Manual Labeling", "• 4 Cues: phone, drink, yawn, hand", "• Single-Annotation Policy", "• 12,722 Negatives (80.91%)", "• Master COCO JSON format"],
         "color": "#E6FFFA", "edge": "#319795"},

        # Box 3: Split Optimization
        {"xy": (0.52, 0.52), "w": 0.22, "h": 0.40, "title": "3. 8/3/3 Subject Split",
         "lines": ["• 60,060 Combinations Evaluated", "• Disjoint (Zero Identity Leakage)", "• Max Relative Dev $\\leq 5.48\\%$", "• Train: 8 Subj (9,087 frames)", "• Val: 3 Subj | Test: 3 Subj"],
         "color": "#FEFCBF", "edge": "#D69E2E"},

        # Box 4: Models & Training
        {"xy": (0.78, 0.52), "w": 0.20, "h": 0.40, "title": "4. Controlled Training",
         "lines": ["• YOLO11n (2.6M CNN)", "• YOLO26n (2.4M NMS-free)", "• D-FINE-N (3.8M RT-DETR)", "• 220 Epochs, Batch 1, Seed 13", "• RTX 4060 GPU, FP16 AMP"],
         "color": "#FEEBC8", "edge": "#DD6B20"},

        # Box 5: Validation Calibration
        {"xy": (0.27, 0.05), "w": 0.33, "h": 0.38, "title": "5. Validation Calibration (Zero Test Leakage)",
         "lines": ["• F1-Score Maximization Grid Sweep: $\\tau \\in [0.01, 0.99]$", "• Select optimal model checkpoint $e^*$ on Val split", "• Lock optimal confidence threshold $\\tau^*$ per architecture", "• Strict isolation of unseen test split"],
         "color": "#EDF2F7", "edge": "#4A5568"},

        # Box 6: Test Evaluation & Profiling
        {"xy": (0.64, 0.05), "w": 0.34, "h": 0.38, "title": "6. Test Evaluation & Latency Profiling",
         "lines": ["• Single-pass evaluation on Test Split (3,213 frames)", "• COCO Metrics: mAP@0.5:0.95, mAP@0.5, P, R, F1", "• 10 untimed warm-ups + CUDA Events timing", "• Median latency ($p50$), $p95$, $p99$, FPS, GFLOPs"],
         "color": "#FAF5FF", "edge": "#805AD5"}
    ]

    for b in boxes:
        fancy = patches.FancyBboxPatch(
            b["xy"], b["w"], b["h"],
            boxstyle="round,pad=0.01,rounding_size=0.02",
            facecolor=b["color"], edgecolor=b["edge"], linewidth=1.5
        )
        ax.add_patch(fancy)
        # Title
        ax.text(b["xy"][0] + b["w"]/2, b["xy"][1] + b["h"] - 0.045, b["title"], fontsize=10, fontweight='bold', ha='center', va='top', color='#1A202C')
        # Body lines
        y_pos = b["xy"][1] + b["h"] - 0.10
        for line in b["lines"]:
            ax.text(b["xy"][0] + 0.015, y_pos, line, fontsize=8.2, va='top', color='#2D3748')
            y_pos -= 0.052

    # Draw Arrows
    # 1 -> 2
    ax.annotate('', xy=(0.27, 0.72), xytext=(0.23, 0.72), arrowprops=dict(arrowstyle="->", color="#4A5568", lw=2))
    # 2 -> 3
    ax.annotate('', xy=(0.52, 0.72), xytext=(0.48, 0.72), arrowprops=dict(arrowstyle="->", color="#4A5568", lw=2))
    # 3 -> 4
    ax.annotate('', xy=(0.78, 0.72), xytext=(0.74, 0.72), arrowprops=dict(arrowstyle="->", color="#4A5568", lw=2))
    # 4 -> 5
    ax.annotate('', xy=(0.435, 0.43), xytext=(0.88, 0.52), arrowprops=dict(arrowstyle="->", color="#4A5568", lw=2, connectionstyle="arc3,rad=0.22"))
    # 5 -> 6
    ax.annotate('', xy=(0.64, 0.24), xytext=(0.60, 0.24), arrowprops=dict(arrowstyle="->", color="#4A5568", lw=2))

    plt.suptitle("DMS-Eval: End-to-End Benchmark Framework & Evaluation Protocol", fontsize=12.5, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    out_asset = "assets/dms_eval_pipeline.png"
    plt.savefig(out_asset, dpi=300)
    plt.close()
    shutil.copy(out_asset, "manuscript/figures/dms_eval_pipeline.png")
    print(f"[OK] Generated {out_asset}")

if __name__ == "__main__":
    generate_split_comparison_chart()
    generate_pipeline_diagram()
