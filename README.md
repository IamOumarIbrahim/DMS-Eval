# DMS-Eval


**DMS-Eval** is a planned benchmark framework currently in development for evaluating nano-scale (lightweight) object detection architectures for detecting visual cues associated with driver drowsiness and distraction in real-time across diverse cabin operating conditions.

![Status: In Development](https://img.shields.io/badge/Status-In_Development-orange?style=flat) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) ![Input: 640×640](https://img.shields.io/badge/Input-640%C3%97640-555?style=flat) ![Detectors: YOLO | DETR](https://img.shields.io/badge/Detectors-YOLO%20%7C%20DETR-4c1?style=flat)


# Ontology

| Frozen cue         | Meaning                                                                            | Bounding box          |
| ------------------ | ---------------------------------------------------------------------------------- | --------------------- |
| `yawning`          | Driver is visibly yawning                                                          | Full-face             |
| `eyes_closed`      | Driver's eyes are visibly closed                                                   | Separate box per eye  |
| `head_turned_away` | Head is substantially turned left/right or away from the forward driving direction | Full head/face        |
| `head_down`        | Head is visibly lowered/forward, consistent with a drooping posture                | Full head/face        |
| `hand_over_mouth`  | Hand visibly covers/occludes the mouth                                             | Hand + mouth together |
`phone_use` | driver is visibly texting / interacting with a phone in hand | hand + phone together

## Relation
> Drowsiness-related:
```
yawning
eyes_closed 
head_down
```
> Attention/distraction-related
```
head_turned_away
```
> Occlusion/context
```
hand_over_mouth
```




