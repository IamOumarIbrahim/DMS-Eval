"""
Generate publication-quality pie charts for DMS-Eval benchmark distributions:
1. Dataset Frame Composition (Negative vs. Positive Frames)
2. Warning Cue Bounding Box Distribution across 4 Target Classes
"""

import os
import matplotlib.pyplot as plt
import numpy as np

# Set high-quality styling
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.size'] = 11

def generate_charts():
    os.makedirs("assets", exist_ok=True)
    os.makedirs("manuscript/figures", exist_ok=True)

    # -------------------------------------------------------------
    # 1. Dataset Frame Composition (Negative vs. Positive)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    
    frame_counts = [12722, 3001]
    frame_labels = [
        f'Negative Background\n12,722 frames (80.9%)',
        f'Positive Warning Cues\n3,001 frames (19.1%)'
    ]
    frame_colors = ['#4A5568', '#3182CE']  # Slate gray, Professional blue
    explode = (0, 0.08)

    wedges, texts, autotexts = ax.pie(
        frame_counts,
        explode=explode,
        labels=frame_labels,
        autopct='%1.1f%%',
        pctdistance=0.6,
        startangle=140,
        colors=frame_colors,
        textprops=dict(color='black', fontsize=11),
        wedgeprops=dict(width=0.65, edgecolor='white', linewidth=2)  # Donut style
    )

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')
        autotext.set_fontsize(12)

    ax.set_title("Dataset Frame Composition\n(Total: 15,723 Frames)", fontsize=13, weight='bold', pad=15)
    plt.tight_layout()

    fig.savefig("assets/dataset_frame_composition_pie.png", dpi=300)
    fig.savefig("manuscript/figures/dataset_frame_composition_pie.png", dpi=300)
    plt.close(fig)
    print("Saved dataset_frame_composition_pie.png")

    # -------------------------------------------------------------
    # 2. Cue Class Distribution (4 Target Warning Cues)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.5, 5), dpi=300)

    cue_counts = [2437, 264, 159, 141]
    cue_labels = [
        'phone_use\n(2,437 | 81.2%)',
        'drinking\n(264 | 8.8%)',
        'yawning\n(159 | 5.3%)',
        'hand_over_mouth\n(141 | 4.7%)'
    ]
    # Colors matching our ontology theme
    cue_colors = ['#D53F8C', '#3182CE', '#DD6B20', '#805AD5'] # Pink, Blue, Orange, Purple
    explode = (0.02, 0.08, 0.12, 0.14)

    wedges, texts, autotexts = ax.pie(
        cue_counts,
        explode=explode,
        labels=cue_labels,
        autopct='%1.1f%%',
        pctdistance=0.65,
        startangle=160,
        colors=cue_colors,
        textprops=dict(color='black', fontsize=10.5),
        wedgeprops=dict(width=0.65, edgecolor='white', linewidth=2)
    )

    for idx, autotext in enumerate(autotexts):
        autotext.set_color('white')
        autotext.set_weight('bold')
        autotext.set_fontsize(10.5)

    ax.set_title("Target Warning Cue Distribution\n(Total: 3,001 Bounding Boxes)", fontsize=13, weight='bold', pad=15)
    plt.tight_layout()

    fig.savefig("assets/cue_class_distribution_pie.png", dpi=300)
    fig.savefig("manuscript/figures/cue_class_distribution_pie.png", dpi=300)
    plt.close(fig)
    print("Saved cue_class_distribution_pie.png")

    # -------------------------------------------------------------
    # 3. Combined Side-by-Side 2-Panel Figure
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=300)

    # Subplot 1: Frame composition
    wedges1, texts1, autotexts1 = ax1.pie(
        frame_counts,
        explode=(0, 0.08),
        labels=frame_labels,
        autopct='%1.1f%%',
        pctdistance=0.55,
        startangle=140,
        colors=frame_colors,
        textprops=dict(color='black', fontsize=10.5),
        wedgeprops=dict(width=0.65, edgecolor='white', linewidth=2)
    )
    for autotext in autotexts1:
        autotext.set_color('white')
        autotext.set_weight('bold')
        autotext.set_fontsize(11)
    ax1.set_title("(a) Frame-Level Composition (15,723 Frames)", fontsize=12, weight='bold', pad=12)

    # Subplot 2: Class distribution
    wedges2, texts2, autotexts2 = ax2.pie(
        cue_counts,
        explode=explode,
        labels=cue_labels,
        autopct='%1.1f%%',
        pctdistance=0.62,
        startangle=160,
        colors=cue_colors,
        textprops=dict(color='black', fontsize=10),
        wedgeprops=dict(width=0.65, edgecolor='white', linewidth=2)
    )
    for autotext in autotexts2:
        autotext.set_color('white')
        autotext.set_weight('bold')
        autotext.set_fontsize(10)
    ax2.set_title("(b) Warning Cue Distribution (3,001 Boxes)", fontsize=12, weight='bold', pad=12)

    plt.tight_layout()
    fig.savefig("assets/benchmark_distributions_combined.png", dpi=300)
    fig.savefig("manuscript/figures/benchmark_distributions_combined.png", dpi=300)
    plt.close(fig)
    print("Saved benchmark_distributions_combined.png")

if __name__ == "__main__":
    generate_charts()
