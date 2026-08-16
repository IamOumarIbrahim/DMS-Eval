# Research Question

> “Under a controlled compute-constrained evaluation, how do lightweight object detectors compare in accuracy, inference efficiency, and robustness when detecting visual cues associated with driver distraction and drowsiness across normal and low-light driving conditions?”

## Fairness & Control Matrix

All models are evaluated under the following controlled protocol.

### Data & Splits
- Use the exact same fixed train, validation, and test manifests for every model.
- Enforce subject-disjoint splits so no driver identity appears across train/validation/test partitions.
- Prevent video-sequence leakage by keeping frames from the same source video/session within a single split.
- Use the same class ontology, class IDs, annotation files, and bounding-box coordinate conventions for every model.
- Keep the final test set untouched during model selection, threshold tuning, and hyperparameter adjustment.

### Input & Preprocessing
- Use the same input resolution for all models.
- Use the same image decoding, color-space conversion, resizing/letterboxing, aspect-ratio handling, padding policy, and padding value wherever the architecture permits.
- Record any architecture-required preprocessing difference explicitly instead of silently treating it as equivalent.

### Training Protocol
- Train every model on the same training data for a declared and comparable training budget.
- Use the same effective batch-size target where practical, including gradient accumulation when required.
- Use the same pretrained-data baseline policy (for example, official COCO-pretrained weights) for all models.
- Fix and record random seeds and deterministic settings for data loading and CPU/CUDA execution where supported.
- Keep augmentation policies aligned where equivalent operations exist; document architecture/framework-specific augmentations that cannot be matched exactly.
- Do not force architecture-specific optimizer, loss, or learning-rate hyperparameters to be numerically identical when doing so would disadvantage a model; instead, document the official or selected settings transparently.

### Evaluation & Metrics
- Evaluate all models against the exact same held-out ground-truth annotations.
- Compute mAP, precision, recall, and F1-score using one shared evaluation implementation and identical IoU/confidence conventions.
- Report robustness as condition-wise metric breakdowns for normal, distracted, drowsy, and low-light/night subsets rather than as an undefined standalone score.
- Select any operating thresholds using validation data only; never tune thresholds on the test set.

### Runtime & Efficiency
- Measure every model on the same hardware, operating environment, numerical precision, input resolution, and batch size.
- Use the same inference timing procedure, including warm-up iterations, synchronization barriers, timed iterations, and reported statistic.
- State clearly whether latency measures model-only inference or the full pipeline; use the same definition for every model.
- Compare models through the same inference backend/export path within each reported runtime table (for example, PyTorch FP32 with PyTorch FP32).
- Measure parameter count, FLOPs, and model file size using the same profiling methodology where supported.

### Reproducibility & Auditability
- Freeze the dataset manifests, configuration files, model checkpoints, software versions, and evaluation scripts used for the final results.
- Record the exact repository version/commit and dependency environment for each model implementation.
- Run automated checks before final evaluation to verify split integrity, class mapping, image resolution, metric configuration, runtime settings, and test-set isolation.
- Treat unavoidable architecture-specific differences as documented limitations or implementation differences, not automatically as fairness failures.
