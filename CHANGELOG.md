## [2026-08-19 23:53:00] - Remove social preview image embed from README header
- Remove `assets/branding/socialpreview.png` header embed from `README.md` while preserving the file in `assets/branding/`
- Streamline repository landing page presentation

## [2026-08-19 23:51:00] - Align Acknowledgment section with open-source tool attribution and placeholders
- Align `\section*{Acknowledgment}` in `manuscript/main.tex` with repository attribution standards: acknowledging the open-source architectures and tools (Ultralytics YOLO11/YOLO26, D-FINE, Label Studio) and placing institutional/grant funding as a standardized `[TO_BE_FILLED]` placeholder
- Recompile verified 6-page IEEE conference PDF (`manuscript/main.pdf`) with 0 errors and 0 undefined citations/references

## [2026-08-19 23:45:00] - Streamline manuscript narrative and eliminate unnecessary redundancies
- Streamline Introduction by removing repetitive low-level implementation lists (crop offsets, bounding box lists, split parameters) that are formalized in Sections III, IV, and V
- Polish Section II (Related Work) to remove self-referential meta-pointers and strengthen the discussion on subject biometric leakage
- Rename Section V-B from tautological *Controlled Training Controls* to *Standardized Training Protocol*
- Recompile camera-ready 6-page IEEE conference PDF (`manuscript/main.pdf`) with 0 errors and 0 undefined citations/references

## [2026-08-19 23:38:00] - Enable clickable hyperlinks in LaTeX manuscript and refine DMD corpus phrasing
- Configure `hyperref` package in `manuscript/main.tex` with IEEE-standard blue link styling (`colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue`) for citations, figures, tables, and URLs
- Refine DMD dataset description across Abstract and Section III-A with clear hierarchical phrasing (*"81 driver-facing RGB video recordings comprising 68 behavioral sessions across 14 subjects"*)
- Recompile camera-ready 6-page IEEE conference PDF (`manuscript/main.pdf`) with 0 errors and 0 undefined citations/references

## [2026-08-19 23:31:00] - Integrate split cue proportions figure into manuscript Section IV
- Add Figure 4 (`split_cue_proportions_comparison.png`) to Section IV-C visually proving warning cue distribution fidelity across 8/3/3 subject-disjoint partitions ($\le 5.4812\%$ relative divergence)
- Unify split frame composition and target cue breakdown tables into a single comprehensive **Table I** (*Dataset Split Composition and Warning Cue Distributions Across Partitions*), saving vertical float space
- Recompile and verify clean 6-page IEEE conference PDF (`manuscript/main.pdf`) with 0 errors and 0 undefined references

## [2026-08-19 23:25:00] - Enhance manuscript with PI-aligned research gap, edge justification, and temporal shuffling strategy
- Restructure Introduction with a dedicated 4-axis **Research Gap** subsection (Section I-A) explicitly contrasting sub-5M parameter single-stage detectors against classification-only baselines (AUC, ICK-PANet) and high-latency multi-stage pipelines (Zhang et al. YOLO11+AlphaPose+LSTM, Drive&Act, UTA-RLDD)
- Integrate automotive edge deployment engineering rationale highlighting on-chip SRAM constraints ($4\text{--}8\,\text{MB}$), divergence between theoretical GFLOPs and wall-clock latency, and MLPerf-aligned batch-1 CUDA-event profiling
- Formalize **Subsection IV-D** (*Temporal Shuffling and Sequence Preservation*) detailing deterministic seed-13 permutation on $S_{\text{train}}$ for gradient decorrelation alongside chronological preservation on $S_{\text{val}}$ and $S_{\text{test}}$ for contiguous event error analysis
- Refine research question and contributions in the future tense per research-in-progress requirements
- Recompile LaTeX source to maintain strict 6-page maximum IEEE conference limit

## [2026-08-19 22:50:00] - Generate split-grouped per-subject dataset with seed-13 shuffled training sets
- Create [`dataset/annotations_per_subject_shuffled/`](dataset/annotations_per_subject_shuffled/) organizing per-subject annotations into `Training/` (8 subjects), `Validation/` (3 subjects), and `Test/` (3 subjects) folders
- Implement deterministic pseudo-random shuffling (seed 13) strictly for the 8 training subjects across `coco_annotations.json` and `raw_annotations.json` to break 1 FPS sequence correlations during model training
- Maintain `Validation/` and `Test/` splits in exact sequential/index order for temporal analysis and deterministic evaluation
- Create [`scripts/create_shuffled_annotations.py`](scripts/create_shuffled_annotations.py) to reproducibly generate and verify the partition hierarchy with 100% data integrity (15,723 frames, 3,001 bboxes)
- Create [`dataset/annotations_per_subject_shuffled/README.md`](dataset/annotations_per_subject_shuffled/README.md) and update documentation in [`docs/quick-start.md`](docs/quick-start.md), [`docs/annotation-protocol.md`](docs/annotation-protocol.md), and [`scripts/README.md`](scripts/README.md)

## [2026-08-19 22:45:00] - Reorganize assets directory into categorized subdirectories
- Categorize all visual assets into 4 semantic subfolders under `assets/`:
  - `assets/branding/`: `socialpreview.png` (820 px repository social card and header banner)
  - `assets/diagrams/`: `dms_eval_pipeline.png` (6-module end-to-end benchmark framework architecture diagram)
  - `assets/charts/`: `benchmark_distributions_combined.png`, `cue_class_distribution_pie.png`, `dataset_frame_composition_pie.png`, `split_cue_proportions_comparison.png`
  - `assets/examples/`: `640X640.png`, `drinking_annotation_example.png`, `hand_over_mouth_annotation_example.png`, `phone_use_annotation_example.png`, `yawning_annotation_example.png`
- Create comprehensive [`assets/README.md`](assets/README.md) documenting directory layout, asset specifications table, and reproduction commands
- Update asset paths across all documentation (`README.md`, `docs/annotation-protocol.md`, `docs/quick-start.md`, `scripts/README.md`)
- Update chart generation scripts in `scripts/charts/` to output directly to `assets/charts/` and `assets/diagrams/`
- Verify zero broken links across entire repository

## [2026-08-19 22:34:00] - Restructure scripts directory into clean modular hierarchy
- Encapsulate presentation generation scripts into gitignored `scripts/presentation/` (`build_presentation_pptx.py`)
- Standardize top-level `scripts/` layout around core reproducible pipeline stages (`extract_and_crop_dmd.py`, `assemble_master_coco.py`, `split_annotations_per_subject.py`, `balance_splits.py`)
- Rewrite [`scripts/README.md`](scripts/README.md) with comprehensive documentation, CLI usage examples, and architecture references for all pipeline stages and subdirectories
- Update `.gitignore` to track `scripts/presentation/`

## [2026-08-19 22:30:00] - Restructure docs directory into clean modular hierarchy
- Create dedicated [`docs/README.md`](docs/README.md) serving as the navigation hub for all 4 benchmark protocols and the desktop PDF field guide
- Encapsulate presentation materials into `docs/presentation/` (`presentation-15min.md`, `DMS-Eval-Presentation-15min.pptx`, `presentation.pptx`)
- Encapsulate internal development artifacts into gitignored `docs/internal/` (`execution-checklist.md`, `resolve_later.md`, `dev-ref/`, `literature/`)
- Update `scripts/build_presentation_pptx.py` output paths to `docs/presentation/`
- Verify zero broken links across all repository documentation

## [2026-08-19 22:25:00] - Consolidate Resolve Later ledgers and future result tables into gitignored docs/resolve_later.md
- Create `docs/resolve_later.md` consolidating all open decision checklists, priority matrices, and future empirical result tables (pinned environment manifest, validation model selection, isolated test benchmark, computational complexity/GFLOPs, and PyTorch hardware latency/throughput profiling)
- Add `docs/resolve_later.md` to `.gitignore`
- Remove all distracting Resolve Later checklist tables and unresolved subsections from public reviewer-facing documents (`README.md`, `docs/annotation-protocol.md`, `docs/evaluation-protocol.md`, `docs/quick-start.md`, `docs/training-protocol.md`, `scripts/README.md`, `tools/label-studio/README.md`)

## [2026-08-19 19:42:00] - Audit reviewer-facing documentation and gitignore internal development artifacts
- Add internal roadmap, presentation decks, and local logs to `.gitignore` (`docs/execution-checklist.md`, `docs/presentation*`, `docs/*.pptx`, `scripts/build_presentation_pptx.py`, `tools/label-studio/annotation_progress_ledger.json`, `tools/label-studio/annotation_decision_log.json`)
- Untrack internal development files from git index while preserving local disk copies
- Clean all links to `execution-checklist.md` across public documentation (`README.md`, `docs/annotation-protocol.md`, `docs/evaluation-protocol.md`, `docs/quick-start.md`, `docs/training-protocol.md`, `scripts/README.md`, `tools/label-studio/README.md`)

## [2026-08-19 19:37:00] - Streamline Table 2 and remove salience rank column
- Remove Salience Rank column from Table 2 in `docs/annotation-protocol.md`
- Rename section to **Behavioral Domains & Target Cue Definitions** with clean centered table layout

## [2026-08-19 19:35:00] - Standardize single-pass manual human expert annotation protocol
- Remove multi-annotator, second-pass review, and voting references from `docs/annotation-protocol.md` and `docs/execution-checklist.md`
- Clarify protocol: all 15,723 frames are annotated directly once by a single manual human expert annotator under frozen deterministic rules

## [2026-08-19 19:33:00] - Enforce 100% frame retention policy and delete excluded_frames.csv
- Enforce strict zero-frame-removal rule: all 15,723 uniformly sampled frames (at 1 FPS across all 81 DMD videos) are permanently preserved in the dataset
- Remove `dataset/excluded_frames.csv`
- Update `docs/annotation-protocol.md` and `docs/execution-checklist.md` (Module 1.4) to reflect 100% frame retention

## [2026-08-19 19:26:00] - Standardize drinking bounding box extent to hand + bottle
- Audit repository and correct `drinking` bounding box extent from `face + bottle` to `hand + bottle` (enclosing interacting hand and beverage container together in active consumption posture)
- Update definitions across `docs/annotation-protocol.md`, `README.md`, `manuscript/main.tex`, `docs/presentation-15min.md`, `scripts/build_presentation_pptx.py`, `docs/execution-checklist.md`, and `tools/label-studio/generate_pdf_guide.py`
- Recompile `docs/manual-annotation-guide.pdf` and rebuild presentation PowerPoint decks

## [2026-08-19 19:18:00] - Refactor chart scripts and update gitignore rules
- Move chart generation scripts into dedicated `scripts/charts/` subfolder:
  - `scripts/charts/generate_distribution_charts.py`
  - `scripts/charts/generate_pipeline_and_split_charts.py`
  - `scripts/charts/generate_pipeline_diagram_redesign.py`
- Add `scripts/charts/`, `charts/`, and `tools/macros/` to `.gitignore`
- Untrack `tools/macros/` files from git while preserving local utilities on disk

## [2026-08-19 19:15:00] - Rename annotations directory to annotations_per_subject
- Rename `dataset/Annotations_split/` to `dataset/annotations_per_subject/` to follow standardized lowercase snake_case and avoid confusion with train/val/test split files
- Update `scripts/split_annotations_per_subject.py` output paths and verify 14-subject integrity (15,723 frames, 3,001 bounding boxes)

## [2026-08-19 19:12:00] - Standardize README manuscript link and table status emojis
- Streamline manuscript download link in `README.md` to a clean, professional link
- Add status emojis to Table 3 in `README.md` (`🧊 Frozen`, `⚠️ Frozen + resolve later`, `📋 Practical field guide`, `🎯 Actionable checklist`)

## [2026-08-19 19:10:00] - Redesign pipeline diagram typography and enhance PPTX deck
- Update `scripts/charts/generate_pipeline_diagram_redesign.py` to center module banner titles, enlarge body typography to 12.2pt, and eliminate dead whitespace
- Re-render high-DPI assets at `assets/dms_eval_pipeline.png` and `manuscript/figures/dms_eval_pipeline.png`
- Scale up body typography across presentation slides (12.0–12.5pt) and dedicate Slide 9 to the full-prominence evaluation framework diagram

## [2026-08-19 19:00:00] - Create comprehensive 15-minute presentation deck (Markdown & PPTX)
- Create Marp-compatible 15-minute technical presentation slide deck in `docs/presentation-15min.md` with slide timings, talk tracks, and placeholder tags for unfinalized test metrics
- Implement `scripts/build_presentation_pptx.py` to generate 16:9 widescreen PowerPoint presentation (`docs/DMS-Eval-Presentation-15min.pptx` and `docs/presentation.pptx`) with embedded figures and native speaker notes
- Conduct automated bounding-box audit verifying zero visual overlaps and zero canvas overflows across all 16 slides

## [2026-08-19 18:53:00] - Format annotation examples figure as 2x2 grid in manuscript
- Update `manuscript/main.tex` Fig. 2 to structure 4 target cue annotation examples into a compact 2x2 subfigure grid with standardized captions
- Recompile `manuscript/main.pdf`

## [2026-08-19 18:49:00] - Configure direct raw PDF download link
- Configure raw GitHub media download link for `manuscript/main.pdf` in `README.md`
- Add Adobe Reader badge and direct download anchor

## [2026-08-19 18:42:00] - Convert file:/// links to relative paths across documentation
- Standardize all repository internal documentation links across `docs/` and `README.md` to relative Markdown paths for seamless web and GitHub browsing

## [2026-08-19 18:38:00] - Add Resolve Later checklist table to documentation
- Add standardized Resolve Later tracking ledger table to footer of `README.md`, `docs/quick-start.md`, `docs/annotation-protocol.md`, `docs/training-protocol.md`, and `docs/evaluation-protocol.md`

## [2026-08-19 18:31:00] - Fix KaTeX math syntax for GitHub rendering
- Correct LaTeX delimiters across Markdown documents for full KaTeX rendering compatibility on GitHub and web viewers

## [2026-08-19 18:24:00] - Redesign pipeline diagram with 2x3 serpentine grid
- Implement `generate_pipeline_diagram_redesign.py` generating high-contrast 2x3 grid lifecycle diagram without crossing arrows
- Save to `assets/dms_eval_pipeline.png` and integrate into documentation and manuscript

## [2026-08-19 18:21:00] - Center tables and fix Mermaid diagram rendering
- Center all Markdown protocol tables in `README.md` using `<div align="center">` containers
- Fix Mermaid diagram syntax and flowcharts in `docs/evaluation-protocol.md` and `docs/execution-checklist.md`

## [2026-08-19 18:10:00] - Authoritative 8/3/3 subject split selection and permanent freeze
- Implement `scripts/balance_splits.py` with deterministic exhaustive proportion-matching algorithm (evaluating all 60,060 candidate assignments)
- Permanently freeze `dataset/splits.json` (Train: 8 subjects [01, 04, 06, 07, 08, 09, 13, 14], Validation: 3 subjects [02, 03, 11], Test: 3 subjects [05, 10, 12])
- Save detailed audit report to `dataset/split_selection_report.json` ($\le 5.48\%$ maximum relative divergence across positive rate and all 4 cue proportions)
- Update documentation across `README.md`, `docs/quick-start.md`, `docs/evaluation-protocol.md`, `docs/execution-checklist.md` (M2.1, M2.2, M2.3 frozen), and `manuscript/main.tex`

## [2026-08-19 18:06:00] - Update manuscript title
- Update paper title in `manuscript/main.tex` to:
  *Real-Time Driver Behavior Detection Using Lightweight Object Detection Models with Subject-Disjoint Evaluation*
- Recompile `manuscript/main.pdf`

## [2026-08-19 17:56:00] - Generate per-subject split annotation directories
- Implement `scripts/split_annotations_per_subject.py` partitioning annotations into 14 distinct folders under `dataset/Annotations_split/subject_01/` ... `subject_14/`
- Each subject folder contains both standard `coco_annotations.json` and `raw_annotations.json` (Label Studio task format)
- Verified exact 14-subject total consistency (15,723 frames, 3,001 bounding boxes)

## [2026-08-19 17:45:00] - Commit 14-subject annotation source and generate master COCO ground truth
- Commit full 14-subject annotation source export in `dataset/All_Subjects_annotated/` (15,723 tasks, 3,001 bounding boxes, 12,722 negative frames)
- Implement `scripts/assemble_master_coco.py` to assemble and validate canonical `dataset/annotations.json`
- Enforce relative image paths (`images/subject_XX/video_YY/...`), standardized 1-indexed category IDs (1: `yawning`, 2: `hand_over_mouth`, 3: `drinking`, 4: `phone_use`), and validated $640 \times 640$ bounding boxes

## [2026-08-19 17:35:00] - Generate and integrate benchmark distribution pie charts
- Implement `scripts/generate_distribution_charts.py` creating high-resolution publication-quality pie charts:
  - `assets/dataset_frame_composition_pie.png` (80.9% negative vs 19.1% positive frames)
  - `assets/cue_class_distribution_pie.png` (81.2% phone_use, 8.8% drinking, 5.3% yawning, 4.7% hand_over_mouth)
  - `assets/benchmark_distributions_combined.png` (2-panel combined publication figure)
- Integrate distribution figures across `docs/annotation-protocol.md` (Figure 5), `README.md` (Figure 3), `docs/quick-start.md` (Figure 2), and `manuscript/main.tex` (Figure 3)
- Recompile LaTeX manuscript PDF

## [2026-08-19 16:20:00] - Add citations and references for Label Studio and label-studio-converter
- Add BibTeX entries for `label_studio` and `label_studio_converter` in `manuscript/bib/references.bib`
- Add formal citations `\cite{label_studio}` and `\cite{label_studio_converter}` and `\bibitem` entries in `manuscript/main.tex`
- Reference `label-studio-converter` repository across `docs/annotation-protocol.md`, `docs/quick-start.md`, `docs/execution-checklist.md`, and `README.md`
- Recompile LaTeX manuscript PDF

## [2026-08-18 23:26:00] - Add drinking manual annotation visual example to documentation and manuscript
- Save `drinking_annotation_example.png` visual asset illustrating Label Studio face + beverage container bounding box
- Document `drinking` annotation example as Figure 3 in `docs/annotation-protocol.md` and update figure numbering
- Update `README.md` Figure 2 gallery to display all 4 target warning cues
- Update `manuscript/main.tex` Fig. 2 to include all 4 visual examples with comprehensive caption

## [2026-08-18 22:22:00] - Document DMD three-folder source composition and negative frame richness
- Document inclusion of all three DMD session categories (`distraction`, `drowsiness`, `gaze`) across 81 videos
- Document negative frame abundance rationale to prevent lightweight model overtraining on positive targets
- Update `docs/quick-start.md`, `docs/annotation-protocol.md`, `README.md`, and `manuscript/main.tex`

## [2026-08-18 22:19:00] - Enforce single-annotation policy and yawning/hand_over_mouth mutual exclusivity
- Enforce strict single-annotation constraint (at most one bounding box per image across dataset)
- Establish mutual exclusivity between `yawning` and `hand_over_mouth` (prioritizing `hand_over_mouth` when hand covers mouth)
- Update `docs/annotation-protocol.md`, `README.md`, `docs/execution-checklist.md`, and `manuscript/main.tex`
- Update Decision Matrix in `tools/label-studio/generate_pdf_guide.py` and recompile `docs/manual-annotation-guide.pdf`

## [2026-08-18 22:16:00] - Document head orientation removal rationale and recompile PDF guide
- Document mirror-check ambiguity rationale across `docs/annotation-protocol.md`, `README.md`, and `manuscript/main.tex`
- Update Decision Matrix and edge case rules in `tools/label-studio/generate_pdf_guide.py`
- Recompile 1-page manual annotation field guide PDF (`docs/manual-annotation-guide.pdf`)

## [2026-08-18 19:15:00] - Refine warning cue ontology to 4 frozen target cues
- Establish a focused 4-cue benchmark ontology (`yawning`, `hand_over_mouth`, `drinking`, `phone_use`)
- Update `docs/annotation-protocol.md`, `README.md`, `docs/quick-start.md`, `docs/execution-checklist.md`, and `docs/evaluation-protocol.md` to reflect the 4-cue ontology
- Update Label Studio XML configuration and PDF field guide generator
- Clean legacy annotation logs and backups
- Complete full-repository audit verifying zero residual occurrences across documentation and code

## [2026-08-18 18:49:00] - Add yawning manual annotation example to documentation
- Add `yawning_annotation_example.png` visual asset illustrating Label Studio mouth-region bounding box
- Document `yawning` annotation example as Figure 1 in annotation protocol
- Update figure numbering across annotation protocol rules
- Add `yawning` annotation example to README Figure 2 gallery with updated captions

## [2026-08-16 00:22:24] - Improve README navigation and license visibility
- Add MIT license badge beside project status
- Add table of contents for key sections
- Align license heading with README structure

## [2026-08-16 00:27:13] - Refine README structure and project description
- Clarify the driver monitoring benchmark scope
- Expand navigation with detailed overview sections
- Fix heading consistency and acknowledgment formatting

## [2026-08-16 00:40:59] - Reorganize manuscript and ignore LaTeX build artifacts
- Move references file to manuscript main source
- Ignore common LaTeX build artifacts
- Add empty Python requirements file

## [2026-08-16 01:36:48] - Expand benchmark documentation and ignore design candidates
- Clarify DMS Eval scope and dataset scenarios
- Document evaluated models metrics and controlled protocol
- Exclude unused candidate images from version control

## [2026-08-16 01:44:39] - Improve evaluated models documentation and table formatting
- Highlight compute constraints in a tip callout
- Clarify the controlled evaluation methodology
- Center model comparison table headers and values

## [2026-08-16 02:03:11] - Add model computational comparison charts
- Add parameter comparison chart
- Add FLOPs comparison chart
- Embed both charts in the README

## [2026-08-16 02:08:15] - Refine model comparison documentation
- Replace parameter and FLOPs columns with post processing details
- Present computational charts in a balanced table layout
- Add descriptive figure caption and improved image accessibility

## [2026-08-16 02:10:14] - Center and refine computational comparison figure
- Center the computational characteristics table
- Expand both comparison images to full cell width
- Restyle the figure caption with smaller emphasized text

## [2026-08-16 02:12:52] - Simplify model comparison figure layout
- Replace table markup with inline comparison images
- Preserve balanced widths and descriptive alt text
- Simplify Figure 1 caption formatting

## [2026-08-16 02:15:05] - Add official model sources to README
- Added official source column to model comparison
- Linked each model to its documentation or repository
- Closed the model table container before figures

## [2026-08-16 02:30:14] - Add benchmark results to README
- Adds benchmark comparison table for four models
- Documents model parameters FLOPs and performance placeholders
- Updates navigation and removes corrupted link text

## [2026-08-16 02:31:34] - Reorganize benchmark results for clearer comparison
- Split accuracy and efficiency metrics into separate tables
- Remove redundant input resolution column
- Preserve model parameters and FLOPs comparisons

## [2026-08-16 02:39:04] - Update evaluation documentation and project structure
- Rename Benchmark Results to Evaluation Results
- Document assets core docs and manuscript directories
- Add requirements file to the project structure

## [2026-08-16 02:52:20] - Adopt Apache license and expand project credits
- Replace MIT License with Apache License 2.0
- Update README license badge and navigation
- Add architecture acknowledgments and reorganize author credits

## [2026-08-16 03:22:40] - Document controlled evaluation setup
- Add evaluation setup table with standardized benchmark settings
- Add 640×640 input resolution visual asset
- Improve model comparison figure layout and README navigation

## [2026-08-16 03:33:59] - Clarify benchmark metrics and evaluation setup
- Add captions for standardized inputs and evaluation configuration
- Introduce a categorized summary table for benchmark metrics
- Standardize metric terminology across descriptions and results tables

## [2026-08-16 03:36:22] - Improve benchmark evaluation layout
- Balance image and configuration table widths
- Align benchmark panels consistently at the top
- Simplify nested HTML table structure

## [2026-08-16 03:44:55] - Refine evaluation setup layout
- Remove duplicate Evaluation Setup heading
- Stack benchmark image above configuration table
- Shorten figure and table captions

## [2026-08-16 03:49:18] - Improve README figure and table captions
- Add descriptive captions to architecture performance and runtime tables
- Standardize figure numbering and caption formatting
- Refine HTML spacing and caption placement throughout README

## [2026-08-16 03:52:10] - Document asset figure mappings
- Add 640X640 image to asset tree
- Relabel parameters image as Figure 2a
- Relabel GFLOPs image as Figure 2b

## [2026-08-16 11:42:21] - Expand benchmark documentation and dataset scope
- Document evaluation datasets visual cues and limitations
- Clarify benchmark metrics terminology and optimization directions
- Add social preview image and ignore terminology notes

## [2026-08-16 12:09:23] - Refine README evaluation scope and dataset roadmap
- Clarify frame level drowsiness and distraction benchmark scope
- Document candidate datasets and pending curation protocol
- Add research question badges and future work roadmap

## [2026-08-16 12:25:47] - Expand model architecture and efficiency documentation
- Fix malformed research question text
- Add model families inputs parameters and GFLOPs
- Rename YOLOv12n Turbo and correct specifications

## [2026-08-16 13:08:37] - Document official model benchmarks and references
- Add official COCO performance and latency benchmarks
- Clarify model architecture and evaluation metric documentation
- Add YOLO11 and YOLOv12 bibliography references

## [2026-08-16 13:59:55] - Clarify benchmark scope and runtime metrics
- Refine study scope and evaluation tradeoffs
- Distinguish end-to-end FPS from model-only latency
- Clarify memory measurement and temporal exclusions

## [2026-08-16 15:33:56] - add ieee manuscript scaffold and reference materials
- Add IEEE LaTeX class bst and abbreviation files to support manuscript formatting
- Create benchmark protocol and 6 page manuscript outline for the paper
- Update README author metadata and ignore local manuscript archive files

## [2026-08-16 15:38:13] - update readme badges and author links
- Removed the top level ORCID badge from the project status line
- Replaced plain author ORCID text with badge links for both contributors
- Standardized the contact lines in the acknowledgments section

## [2026-08-16 17:12:48] - clarify benchmark as planned and add dataset guide
- Reframes README and manuscript language from completed benchmark to planned in development
- Adds a detailed DMD drowsiness dataset guide covering structure annotations and licensing
- Updates docs and project structure to reflect manuscript scope budget and planned evaluation artifacts

## [2026-08-16 17:15:03] - clean dataset docs and latex ignores
- Remove the obsolete DMD dataset README from the repo
- Expand `.gitignore` to cover more LaTeX build and sync artifacts
- Stop tracking the generated `main.synctex(busy)` file in `manuscript`

## [2026-08-16 18:30:33] - Refine evaluation protocol and dataset documentation
- Specify subject splits hardware precision and protocol settings
- Add balanced accuracy and false positive safety metrics
- Define DMD real car subset as benchmark dataset

## [2026-08-16 19:24:12] - Refine benchmark scope and consolidate project schedule
- Refocus evaluation on three lightweight detectors under controlled conditions
- Expand results tracking with robustness and latency percentile metrics
- Consolidate planning documents into a comprehensive project schedule

## [2026-08-16 20:04:32] - Expand benchmark documentation and execution protocol
- Add detailed benchmark scope setup models and limitations
- Define controlled evaluation metrics dataset splits and fairness
- Introduce phased execution timeline and structured results tables

## [2026-08-16 20:15:15] - Reorganize and expand benchmark documentation
- Add centralized documentation index and navigation
- Organize documentation into focused topic directories
- Expand model specifications and bibliography references

## [2026-08-16 21:36:48] - Expand benchmark references and documentation
- Add citations for detection models DMD and COCO
- Document the August 20 benchmark design freeze
- Expand literature ignore rules and update project structure

## [2026-08-16 21:49:57] - Remove obsolete benchmark and methodology documentation
- Removed the central documentation index
- Deleted benchmark protocols model specifications scope and setup
- Removed experiment timelines results contributions and limitations

## [2026-08-16 22:44:33] - Refine benchmark documentation and add task taxonomy
- Clarify sub 5M detector scope metrics and thresholds
- Separate overall robustness and deployment result tables
- Add computer vision taxonomy figure and citation

## [2026-08-16 23:37:43] - Streamline README around driver cue ontology
- Replaced benchmark documentation with a concise ontology
- Defined bounding boxes for six driver behavior cues
- Corrected bibliography reference metadata

## [2026-08-17 00:44:53] - Document frozen benchmark scope and annotation rules
- Define frozen dataset models resolution and frame sampling policy
- Refine six target cues with precise bounding box guidance
- Add annotation rules cue categories ordering and future work

## [2026-08-17 01:05:16] - Document frozen benchmark dataset and annotation protocols
- Define fixed frame extraction cropping and naming rules
- Establish subject disjoint splits and persistent manifests
- Expand COCO structure and cue specific annotation guidance

## [2026-08-17 01:29:26] - Expand benchmark documentation and annotation quality guidance
- Reorganize sections into a consistent heading hierarchy
- Standardize benchmark and cue definition tables
- Add review rules for ambiguous annotations and data quality

## [2026-08-17 02:03:17] - Document evaluation protocol and fixed dataset splits
- Add frozen metrics evaluation harness and selection procedures
- Fix dataset split at 8 3 3 subjects
- Add credits license and annotation reference

## [2026-08-17 02:07:10] - Refine benchmark documentation and annotation guidelines
- Clarify benchmark mission sampling and preprocessing constraints
- Strengthen subject disjoint splits and annotation sources
- Streamline cue definitions and bounding box rules

## [2026-08-17 02:11:36] - Streamline benchmark documentation and evaluation specifications
- Consolidate benchmark scope and preprocessing details into structured tables
- Clarify cue salience categories exclusions and bounding box rules
- Expand evaluation metrics with reporting granularity and protocol roles

## [2026-08-17 02:28:51] - Add dataset metadata placeholders
- Add empty annotations metadata file
- Add excluded frames CSV placeholder
- Add preprocessing and split configuration placeholders

## [2026-08-17 12:32:15] - Document standardized model training protocol
- Define pretrained full-model fine-tuning and model-specific recipes
- Freeze shared training controls across all three architectures
- Record unresolved training and evaluation configuration values

## [2026-08-17 13:05:56] - Refine benchmark evaluation and preprocessing protocols
- Clarify fixed cropping and cue balanced subject splits
- Define matching threshold and checkpoint tie breaking rules
- Specify runtime profiling and deployment metric sources

## [2026-08-17 13:53:15] - Restructure benchmark documentation into dedicated protocol guides
- Streamline README with benchmark overview and protocol links
- Add detailed annotation training and evaluation protocols
- Add quick start guide covering data preprocessing and splits

## [2026-08-17 14:49:58] - Freeze preprocessing training and runtime benchmark protocols
- Fix dataset-wide crop geometry at 640x640
- Define FP16 CUDA runtime timing and throughput procedures
- Reduce unresolved items to splits thresholds environment and deployment sources

## [2026-08-17 15:07:45] - Freeze deployment profiling measurement protocols
- Standardize local THOP GFLOPs calculation across all models
- Measure final validation selected checkpoint sizes consistently
- Track THOP versions and unsupported operator handling as unresolved

## [2026-08-17 15:26:27] - Adjust training protocol whitespace
- Adds whitespace to a blank separator line
- Leaves documented training controls unchanged
- Preserves all protocol content and structure

## [2026-08-17 15:49:50] - Add DMD frame extraction cropping and verification pipeline
- Add parallel video frame extraction and standardized face cropping
- Verify cropped frames for corruption black pixels and sharpness
- Document preprocessing usage outputs and ignored generated images

## [2026-08-17 16:16:37] - Ignore developer reference documentation
- Adds docs dev-ref to ignored paths
- Keeps third party documentation untracked
- Removes an unnecessary blank line

## [2026-08-17 16:38:26] - Add dataset manifest and refine preprocessing workflow
- Add subject and video mappings with frame counts
- Improve extraction cropping and dataset organization tooling
- Clarify CVAT review requirements and sampling documentation

## [2026-08-17 16:46:10] - Correct frozen final-image naming rule
- Make the existing cropped-image filenames authoritative
- Define frame numbers as sequential sampled-frame indices within each video
- Remove the claim that final-image frame numbers are absolute MP4 source-frame indices

## [2026-08-17 16:47:33] - Correct sampled frame naming documentation
- Define frames as sequential sampled indices per video
- Document four digit numbering beginning at 0001
- Remove claims of absolute MP4 source frame indices

## [2026-08-17 18:22:33] - Add execution roadmap and annotation review workflow
- Add seven-module benchmark execution checklist and submission roadmap
- Define CVAT review states and external annotation progress tracking
- Simplify README tables and link protocol documentation consistently

## [2026-08-17 19:21:18] - Add Label Studio annotation and preannotation workflow
- Replace CVAT documentation with Label Studio review procedures
- Add project setup import export and launcher utilities
- Add agent predictions with progress and decision tracking
