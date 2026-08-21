# Finalize the manuscript after the benchmark

This workflow is intentionally aggregate-only. It must not import the evaluator, load protected-test images, rerun inference, select runs, or search for favorable examples.

## Preconditions

1. The official benchmark has finished all nine predeclared runs: three configured systems (`yolo11n`, `yolo26n`, and `dfine_n`) at seeds 13, 37, and 73.
2. The protected evaluator and the repository aggregator have each run exactly as specified by the frozen protocol.
3. There is one canonical schema-v3 `dms_eval_aggregate` JSON artifact. Do not use backup, partial, ad hoc, or hand-edited summaries.
4. Resolve any benchmark integrity failure before manuscript finalization. In particular, a checkpoint that did not reach epoch 220 is not a completed run.

## One-command postprocessing

After this branch is merged back into the benchmark checkout, run from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\manuscript\generate_manuscript_assets.py --aggregate auto --build
```

If the manuscript worktree remains separate, pass the canonical aggregate by absolute path:

```powershell
& 'C:\Dev\repos\Public repos\DMS-Eval\.venv\Scripts\python.exe' 'C:\Dev\repos\Public repos\DMS-Eval-manuscript\scripts\manuscript\generate_manuscript_assets.py' --aggregate 'C:\Dev\repos\Public repos\DMS-Eval\results\PATH_TO_CANONICAL_AGGREGATE.json' --build
```

The command refuses to proceed unless it sees exactly the 3-by-3 model-seed matrix, one suite ID, unique extant source artifacts, both FLOP estimators, the four declared classes, finite in-range metrics, and means/sample SDs that exactly agree with recomputation from the nine runs. Auto-discovery also refuses zero or multiple canonical aggregates.

## Generated outputs

The postprocessor atomically replaces the following files under `manuscript/generated/`:

- `results_macros.tex`: per-run values, mean/sample-SD values, factual rankings, and factual manuscript sentences.
- `tables/primary_results.tex`: publication table split into quality, latency, and resource panels.
- `tables/per_class_results.tex` and `tables/per_seed_results.tex`: auditable companion tables.
- `figures/`: accuracy-efficiency, per-class AP, latency, and resource plots in PDF, SVG, and PNG.
- `result_summary.json`, `source_hashes.json`, `FINAL_RESULT_REPORT.md`, and `factual_results.tex`: machine- and human-readable provenance.

The script never writes mock data into the final generated directory. Fixture inputs are accepted only with `--dry-run`, which writes to `manuscript/generated/dry_run/` and watermarks every output.

## Manual completion after generation

1. Read `generated/FINAL_RESULT_REPORT.md` and compare it with the canonical aggregate.
2. Fill `manual_results.json`: enter each comparable three-seed training duration in hours from official logs, choose one of the three model IDs for `best_tradeoff_model`, and write one evidence-grounded trade-off sentence. If durations are not comparable, remove the duration sentence from `main.tex` instead of inventing values.
3. Rerun the one-command postprocessor. It validates the manual registry, records its hash, and resolves its five manuscript macros deterministically.
4. Build `figures/Placeholder_image_1.png` only from the evaluator's predeclared seed-13 qualitative outputs, following `MANUAL_FIGURE_REQUESTS.md`. If license/privacy review does not permit publication, remove the montage and keep the textual failure-analysis protocol.
5. Run the sentinel audit in `TO_BE_UPDATED_MANIFEST.md`. A submission PDF must contain no unresolved sentinel.
6. Visually inspect every PDF page at normal size and 200% zoom. Confirm six pages or fewer, readable tables, legible plots, intact references, and no mock watermark.

## Connection status

No hook was added to the currently running benchmark or its queue. This is deliberate: changing the active checkout could invalidate frozen-code provenance. The exact postprocessing command above is the safe fallback once the benchmark has stopped and its final aggregate is available.
