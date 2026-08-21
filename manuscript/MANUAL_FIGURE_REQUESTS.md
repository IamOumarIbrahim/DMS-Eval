# Manual figure requests

## Placeholder_image_1.png - qualitative detections and failure cases

- Manuscript location: Discussion, "Qualitative Failure Analysis"; included as a double-column figure.
- Purpose: show representative correct detection, negative-frame false positive, false negative, class confusion, and localization error cases. It is explanatory evidence, not a source of quantitative conclusions.
- Essentiality: optional for numerical validity but strongly useful for review. If DMD licensing or privacy review prevents redistribution, remove the figure and retain the protocol text.
- Required canvas: approximately 3.3:1 landscape, at least 2148 by 650 pixels at 300 dpi; use the full IEEE double-column width. The generated placeholder is 1676 by 508 pixels and conveys the intended geometry, not the desired final resolution.
- Recommended layout: five labeled columns (one category each), with up to three vertically stacked seed-13 examples per column; use identical font, bounding-box style, confidence precision, and class colors throughout. Include model name, category, and an anonymized source identifier in a compact label.
- Caption already in `main.tex`: it states that the examples were selected deterministically during the single protected-test pass and that the montage uses the predeclared reference seed 13.
- Exact source of images: the evaluator-emitted `qualitative_analysis.path` in each seed-13 protected-result JSON. Under the frozen layout these are expected beneath `results/qualitative/yolo11n_seed13`, `results/qualitative/yolo26n_seed13`, and `results/qualitative/dfine_n_seed13`. Use only the already emitted candidates/contact sheets and their metadata.
- Prohibited sourcing: do not traverse the protected test set again, rerun inference, change thresholds, search by image, substitute later seeds, or select examples after seeing which model looks best.
- Selection rule: use the evaluator's predeclared ordering and first three available items in each category. If an entire category is absent, show an explicit "no candidate emitted" tile instead of finding a replacement.
- Privacy/license: DMD material is subject to its source license (CC BY-NC-ND on the project site at the time of the reference audit). Confirm that publication of annotated crops is permitted by the dataset terms and venue policy; retain source attribution; do not expose personal identifiers or local paths.

The automated quantitative plots need no manual artwork. They are generated from the canonical aggregate in PDF, SVG, and PNG form by `scripts/manuscript/generate_manuscript_assets.py`.
