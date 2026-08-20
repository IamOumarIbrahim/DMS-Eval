"""Generate the manuscript's source-to-crop geometry schematic."""

from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    figure, axis = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    figure.patch.set_facecolor("white")
    axis.set_xlim(0, 1280)
    axis.set_ylim(720, 0)
    axis.set_aspect("equal")
    axis.axis("off")

    axis.add_patch(Rectangle((0, 0), 1280, 720, facecolor="#0f172a", edgecolor="#334155", linewidth=4))
    axis.text(28, 45, "SOURCE RGB FRAME  •  1280 × 720", color="white", fontsize=15, weight="bold", va="top")
    axis.text(28, 92, "Uniform geometry for every recording and subject", color="#cbd5e1", fontsize=11, va="top")

    crop_x, crop_y, crop_w, crop_h = 272, 71, 640, 640
    axis.add_patch(
        Rectangle(
            (crop_x, crop_y),
            crop_w,
            crop_h,
            facecolor="#2563eb",
            alpha=0.28,
            edgecolor="#60a5fa",
            linewidth=6,
        )
    )
    axis.text(
        crop_x + crop_w / 2,
        crop_y + crop_h / 2 - 22,
        "FIXED DRIVER-WORKSPACE CROP",
        color="white",
        fontsize=16,
        weight="bold",
        ha="center",
        va="center",
    )
    axis.text(
        crop_x + crop_w / 2,
        crop_y + crop_h / 2 + 28,
        "640 × 640  •  no resize, padding, or distortion",
        color="#dbeafe",
        fontsize=12,
        ha="center",
        va="center",
    )
    axis.annotate(
        "",
        xy=(crop_x + crop_w, crop_y + crop_h + 4),
        xytext=(crop_x, crop_y + crop_h + 4),
        arrowprops={"arrowstyle": "<->", "color": "#fbbf24", "lw": 2.5},
    )
    axis.text(crop_x + crop_w / 2, crop_y + crop_h - 18, "width = 640 px", color="#fde68a", fontsize=11, ha="center")
    axis.text(
        940,
        112,
        "Top-left  (272, 71)\nBottom-right  (912, 711)\nOutput  640 × 640 RGB",
        color="white",
        fontsize=9.5,
        linespacing=1.5,
        bbox={"boxstyle": "round,pad=0.6", "facecolor": "#1e293b", "edgecolor": "#64748b"},
    )

    manuscript = REPO_ROOT / "manuscript" / "figures" / "640X640.png"
    asset = REPO_ROOT / "assets" / "diagrams" / "dms_crop_geometry.png"
    example = REPO_ROOT / "assets" / "examples" / "640X640.png"
    manuscript.parent.mkdir(parents=True, exist_ok=True)
    asset.parent.mkdir(parents=True, exist_ok=True)
    example.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(manuscript, dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.05)
    plt.close(figure)
    shutil.copyfile(manuscript, asset)
    shutil.copyfile(manuscript, example)
    print(f"Generated {manuscript}, {asset}, and {example}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
