# DMS-Eval

**DMS-Eval** is a planned benchmark framework currently in development for evaluating nano-scale (lightweight) object detection architectures for detecting visual cues associated with driver drowsiness and distraction in real time across diverse cabin operating conditions.

![Status: In Development](https://img.shields.io/badge/Status-In_Development-orange?style=flat) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) ![Input: 640×640](https://img.shields.io/badge/Input-640%C3%97640-555?style=flat) ![Detectors: YOLO | DETR](https://img.shields.io/badge/Detectors-YOLO%20%7C%20DETR-4c1?style=flat)

## Frozen Benchmark Scope

| Setting                     | Frozen value                             |
| :-------------------------- | :--------------------------------------- |
| Dataset                     | DMD-derived dataset                      |
| Models                      | YOLO11n, D-FINE-N, YOLO26n               |
| Input resolution            | 640×640                                  |
| Model input unit            | Individual image frames                  |
| Source video frame rate     | 29.76 FPS                                |
| Source video duration range | 55.28–519.39 s                           |
| Frame sampling              | 1 frame every 1 second                   |
| Sampling policy             | Same fixed sampling rule for every video |

Longer videos are allowed to contribute more sampled frames than shorter videos.

Frames are sampled systematically across the full videos rather than selecting only frames containing target cues. Frames containing none of the target warning cues remain valid background frames.

> Training settings, dataset splits, evaluation metrics, thresholds, hardware, inference precision, augmentation, optimization, and the remaining evaluation protocol are not yet frozen.

# Target Warning Cues

There are currently **6 frozen target warning cues**.

| Frozen cue         | Meaning                                                                                                      | Bounding box          |
| :----------------- | :----------------------------------------------------------------------------------------------------------- | :-------------------- |
| `eyes_closed`      | Driver's eyes are visibly closed, including fully closed and visibly partially closed / heavy-lidded eyes    | Separate box per eye  |
| `yawning`          | Driver is visibly yawning; an ordinary open mouth is not sufficient                                          | Mouth region only     |
| `head_down`        | Head is clearly and substantially lowered/forward relative to normal forward-facing driving posture          | Full head/face        |
| `hand_over_mouth`  | Hand visibly covers or occludes the mouth                                                                    | Full head/face        |
| `phone_use`        | Driver is texting or actively interacting with a handheld phone; resting phones and phone calls are excluded | Hand + phone together |
| `head_turned_away` | Head is substantially turned left/right or away from the forward driving direction                           | Full head/face        |

## Annotation Rules

All target cues are judged from the **individual sampled frame only**. Surrounding video frames are not used to determine the ground-truth label.

For `eyes_closed`, no temporal blink-filtering rule is used because the benchmark operates on single-frame inputs.

For `yawning`, annotate only frames that visibly show a yawn. `mouth_open` is not a separate class.

For `head_down`, small downward glances are not annotated. The head must be clearly and substantially lowered/forward.

A frame may contain **multiple target warning cues simultaneously**. When two or more cues are clearly visible, all applicable cues are annotated. Bounding boxes are allowed to overlap.

## Cue Categories

### Drowsiness-related

```text
eyes_closed
yawning
head_down
hand_over_mouth
```

### Attention/distraction-related

```text
phone_use
head_turned_away
```

## Cue Strength Ordering

This ordering represents the strongest/directest visual warning cue to the weakest/more ambiguous cue from a **single frame**. It does not represent expected model accuracy.

### Drowsiness-related

1. `eyes_closed`
2. `yawning`
3. `head_down`
4. `hand_over_mouth`

### Attention/distraction-related

1. `phone_use`
2. `head_turned_away`

## Future Work

> Future work may extend the ontology with cues that are deliberately outside the current benchmark scope.

* `reach_behind`
* `hair_makeup`
* `reach_side`
* `head_nodding` — temporal cue requiring multiple frames
