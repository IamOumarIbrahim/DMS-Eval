# Placeholder manifest

The visible sentinel is `TO_BE_UPDATED`. In LaTeX it is centralized as `\DMSPending`, which renders the exact sentinel while keeping all unresolved values machine-auditable.

## Placeholder registry

| Group | Current source | Unit/format | Replacement source | Finalization |
|---|---|---|---|---|
| Per-seed quality: mAP@0.5:0.95, mAP@0.5, precision, recall, micro-F1, FAR | `generated/results_macros.tex` | proportions to 3 decimals; FAR per 100 negative frames to 2 decimals | nine canonical protected-result rows | automatic |
| Three-seed quality summaries | same | mean plus sample SD, `n=3` | recomputed from individual runs, never trusted from row text alone | automatic |
| Per-class AP for `phone_use`, `drinking`, `yawning`, `hand_over_mouth` | same | proportion to 3 decimals | canonical per-run `per_class_ap_50_95` | automatic |
| Forward-only p50/p95/p99 and sustained FPS | same | ms to 2 decimals; FPS to 1 decimal | canonical protected-result latency fields | automatic |
| Tensor-to-final-detections p50/p95/p99 and sustained FPS | same | ms to 2 decimals; FPS to 1 decimal | canonical protected-result latency fields | automatic |
| Peak allocated VRAM, parameters, inference artifact size | same | MiB to 1 decimal; M parameters to 2 decimals; MiB to 1 decimal | canonical protected-result resource fields | automatic |
| THOP and torch-profiler FLOPs | same | GFLOPs to 2 decimals, estimator named | canonical `flop_estimates` from each run | automatic |
| Fastest and highest-accuracy system | same | configured system name | rank model means by tensor-to-final p50 and mAP@0.5:0.95 | automatic |
| Abstract, Results, and Conclusion factual result sentences | same | concise IEEE prose | generated from validated means/sample SDs | automatic |
| Accuracy-efficiency, per-class, latency, and resource plots | absent until final aggregate | PDF/SVG/PNG | canonical aggregate after full validation | automatic |
| Training duration for each configured system | `manual_results.json` -> generated macros | hours to 2 decimals, state aggregation rule | official training logs for all three seeds; omit if not comparable | manual input, validated generation |
| Best accuracy-efficiency trade-off | `manual_results.json` -> generated macros | configured system name | declared multidimensional evidence, with rationale | manual judgment, validated generation |
| Discussion trade-off sentence | `manual_results.json` -> generated macros | one evidence-grounded sentence | same evidence as the trade-off selection | manual judgment, validated generation |
| Qualitative montage | `figures/Placeholder_image_1.png` | 3.3:1 PNG, at least 2148 by 650 pixels | predeclared seed-13 evaluator outputs only | manual; optional after license review |

The placeholder macro registry contains 355 unresolved leaf macros at initialization: 345 quantitative/per-seed/summary slots, three training-duration slots, three ranking/choice slots, and four prose slots. Automatic postprocessing resolves all aggregate-derived slots; the three durations, trade-off choice, and trade-off sentence remain intentionally manual.

## Current baseline audit (2026-08-22)

- Raw source literals: 12. Locations are `manual_results.json` (five manual values), `scripts/manuscript/generate_manuscript_assets.py` (the sentinel constant and placeholder-image label), `FINAL_UPDATE_PROMPT.md` (one instruction), `FINALIZE_AFTER_BENCHMARK.md` (one cross-reference), and this file (the definition and two audit commands).
- Escaped LaTeX rendering definitions: three. Two are generator templates and one is the initialized `generated/results_macros.tex` definition.
- Unresolved leaf macros in the initialized registry: 355, all in `generated/results_macros.tex`.
- Visible occurrences in the current five-page placeholder PDF: 58. `pdftotext` finds 57 (page 1: one; page 3: eight; page 4: 48); the remaining occurrence is visibly embedded in the page-5 qualitative placeholder raster.

These are intentional pre-results counts, not submission-ready counts. After complete aggregation and the five manual registry inputs, the unresolved leaf count and all visible PDF counts must be zero. Instructional mentions may remain in documentation and generator source.

## Required audits

Source-tree literal occurrences:

```powershell
rg -uu -n -F 'TO_BE_UPDATED' manuscript/main.tex manuscript/generated manuscript/manual_results.json -g '!dry_run/**'
```

Unresolved macro leaves:

```powershell
(rg -n -F '}{\DMSPending}' manuscript/generated/results_macros.tex | Measure-Object).Count
```

Rendered PDF occurrences after the final build:

```powershell
& "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\pdftotext.exe" manuscript/main.pdf - | rg -n -F 'TO_BE_UPDATED'
```

Before submission, all three audits must return zero unresolved manuscript placeholders. Because text extraction cannot see words embedded in a raster, the visual page audit must also confirm that `Placeholder_image_1.png` was replaced or its figure removed. Documentation and the generator may still mention the sentinel as an instruction.
