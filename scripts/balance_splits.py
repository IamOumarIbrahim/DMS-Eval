"""
DMS-Eval Authoritative Subject Split Selection Algorithm (8/3/3 Disjoint Split)
=============================================================================
Deterministically selects the optimal 8 Train / 3 Validation / 3 Test subject
split by exhaustively evaluating all C(14, 8) * C(6, 3) = 60,060 candidate assignments.

Optimization Objective:
Selects the assignment whose positive frame rate and 4 warning cue class proportions
most closely match the complete dataset distribution.

Lexicographic Tiebreak Hierarchy:
1. Minimum worst absolute relative deviation across all splits and quantities (15 values)
2. Minimum overall RMSE of all 15 relative deviations
3. Minimum test-split worst relative deviation (5 values)
4. Minimum test-split RMSE (5 values)
5. Lexicographically smallest subject-ID assignment
"""

import os
import json
import math
from itertools import combinations
from collections import defaultdict, Counter

CLASS_NAMES = {
    1: 'yawning',
    2: 'hand_over_mouth',
    3: 'drinking',
    4: 'phone_use'
}

CLASS_IDS = [4, 3, 1, 2]  # phone_use, drinking, yawning, hand_over_mouth

def extract_subject_from_path(file_name: str) -> str:
    """Extract canonical subject ID (e.g., 'subject_01') from image path."""
    normalized = file_name.replace('\\', '/')
    parts = normalized.split('/')
    for p in parts:
        if p.startswith('subject_') and len(p) == 10 and p[8:].isdigit():
            return p
    # Fallback to filename parsing
    fname = parts[-1]
    tokens = fname.split('_')
    if len(tokens) >= 2 and tokens[0] == 'subject':
        return f"subject_{tokens[1]}"
    raise ValueError(f"Could not extract subject ID from path: {file_name}")

def compute_per_subject_matrix(coco_data: dict):
    """
    Computes per-subject frame counts, positive/negative frame counts,
    and class-specific positive frame counts from COCO data.
    """
    subject_images = defaultdict(set)
    subject_pos_frames = defaultdict(set)
    subject_class_frames = defaultdict(lambda: defaultdict(set))

    # Index images
    for img in coco_data['images']:
        img_id = img['id']
        subj = extract_subject_from_path(img['file_name'])
        subject_images[subj].add(img_id)

    # Index annotations
    for ann in coco_data['annotations']:
        img_id = ann['image_id']
        cat_id = ann['category_id']
        # Find subject for this image
        subj = None
        for s, img_set in subject_images.items():
            if img_id in img_set:
                subj = s
                break
        if subj is None:
            continue
        subject_pos_frames[subj].add(img_id)
        subject_class_frames[subj][cat_id].add(img_id)

    subjects = sorted(subject_images.keys())
    per_subject_stats = {}

    for s in subjects:
        tot = len(subject_images[s])
        pos = len(subject_pos_frames[s])
        neg = tot - pos
        class_counts = {cid: len(subject_class_frames[s][cid]) for cid in CLASS_IDS}
        per_subject_stats[s] = {
            'total_images': tot,
            'negative_frames': neg,
            'positive_frames': pos,
            'class_counts': class_counts
        }

    return per_subject_stats

def calculate_split_metrics(subjects_in_split, per_subject_stats):
    """Aggregates metrics for a set of subjects."""
    tot = sum(per_subject_stats[s]['total_images'] for s in subjects_in_split)
    neg = sum(per_subject_stats[s]['negative_frames'] for s in subjects_in_split)
    pos = sum(per_subject_stats[s]['positive_frames'] for s in subjects_in_split)
    class_counts = {
        cid: sum(per_subject_stats[s]['class_counts'][cid] for s in subjects_in_split)
        for cid in CLASS_IDS
    }
    pos_rate = pos / tot if tot > 0 else 0.0
    class_props = {
        cid: (class_counts[cid] / pos if pos > 0 else 0.0)
        for cid in CLASS_IDS
    }
    return {
        'total_images': tot,
        'negative_frames': neg,
        'positive_frames': pos,
        'positive_rate': pos_rate,
        'class_counts': class_counts,
        'class_proportions': class_props
    }

def run_exhaustive_search(coco_path="dataset/annotations.json"):
    print(f"Loading master annotations from {coco_path}...")
    with open(coco_path, 'r', encoding='utf-8') as f:
        coco_data = json.load(f)

    per_subject_stats = compute_per_subject_matrix(coco_data)
    subjects = sorted(per_subject_stats.keys())
    num_subjects = len(subjects)
    print(f"Discovered {num_subjects} subjects: {subjects}")
    assert num_subjects == 14, f"Expected exactly 14 subjects, got {num_subjects}"

    # Global Dataset Metrics
    global_metrics = calculate_split_metrics(subjects, per_subject_stats)
    print("\n=== GLOBAL DATASET METRICS ===")
    print(f"Total Images:    {global_metrics['total_images']}")
    print(f"Negative Frames: {global_metrics['negative_frames']}")
    print(f"Positive Frames: {global_metrics['positive_frames']} ({global_metrics['positive_rate']*100:.4f}%)")
    for cid in CLASS_IDS:
        name = CLASS_NAMES[cid]
        cnt = global_metrics['class_counts'][cid]
        prop = global_metrics['class_proportions'][cid] * 100
        print(f"  - {name:<16}: {cnt:>5} ({prop:.4f}%)")

    # Combinatorial search
    total_evaluated = 0
    total_rejected = 0
    best_candidate = None
    best_score = None

    # C(14, 8) = 3003 train combinations
    for train_comb in combinations(subjects, 8):
        train_set = set(train_comb)
        remaining = [s for s in subjects if s not in train_set]
        
        # C(6, 3) = 20 val combinations
        for val_comb in combinations(remaining, 3):
            total_evaluated += 1
            val_set = set(val_comb)
            test_comb = tuple(s for s in remaining if s not in val_set)
            test_set = set(test_comb)

            # Verification of disjointness
            assert len(train_set) == 8
            assert len(val_set) == 3
            assert len(test_set) == 3
            assert len(train_set | val_set | test_set) == 14

            # Calculate split stats
            train_m = calculate_split_metrics(train_comb, per_subject_stats)
            val_m = calculate_split_metrics(val_comb, per_subject_stats)
            test_m = calculate_split_metrics(test_comb, per_subject_stats)

            # Rejection: Every class must appear in every split
            has_all_classes = (
                all(train_m['class_counts'][cid] > 0 for cid in CLASS_IDS) and
                all(val_m['class_counts'][cid] > 0 for cid in CLASS_IDS) and
                all(test_m['class_counts'][cid] > 0 for cid in CLASS_IDS)
            )
            if not has_all_classes:
                total_rejected += 1
                continue

            # Calculate absolute relative deviations for 5 quantities per split (15 total)
            devs_all = []
            devs_split = {}

            for split_name, m in [('train', train_m), ('validation', val_m), ('test', test_m)]:
                devs = []
                # 1. Positive rate relative deviation
                dev_pos = abs(m['positive_rate'] - global_metrics['positive_rate']) / global_metrics['positive_rate']
                devs.append(dev_pos)

                # 2-5. Class proportions relative deviations
                for cid in CLASS_IDS:
                    dev_c = abs(m['class_proportions'][cid] - global_metrics['class_proportions'][cid]) / global_metrics['class_proportions'][cid]
                    devs.append(dev_c)

                devs_split[split_name] = devs
                devs_all.extend(devs)

            # Metrics
            worst_dev_all = max(devs_all)
            rmse_all = math.sqrt(sum(d ** 2 for d in devs_all) / len(devs_all))
            
            worst_dev_test = max(devs_split['test'])
            rmse_test = math.sqrt(sum(d ** 2 for d in devs_split['test']) / len(devs_split['test']))

            subject_order = (tuple(sorted(train_comb)), tuple(sorted(val_comb)), tuple(sorted(test_comb)))
            score = (worst_dev_all, rmse_all, worst_dev_test, rmse_test, subject_order)

            if best_score is None or score < best_score:
                best_score = score
                best_candidate = {
                    'train': sorted(train_comb),
                    'validation': sorted(val_comb),
                    'test': sorted(test_comb),
                    'train_metrics': train_m,
                    'validation_metrics': val_m,
                    'test_metrics': test_m,
                    'deviations': {
                        'train': devs_split['train'],
                        'validation': devs_split['validation'],
                        'test': devs_split['test'],
                        'all': devs_all
                    },
                    'scores': {
                        'worst_relative_deviation_all': worst_dev_all,
                        'rmse_all': rmse_all,
                        'worst_relative_deviation_test': worst_dev_test,
                        'rmse_test': rmse_test
                    }
                }

    print("\n=== SEARCH RESULTS ===")
    print(f"Total Assignments Evaluated: {total_evaluated} (Expected: 60,060)")
    print(f"Total Assignments Rejected:  {total_rejected}")
    print(f"Valid Assignments Evaluated: {total_evaluated - total_rejected}")
    assert total_evaluated == 60060, f"Expected 60,060 evaluations, got {total_evaluated}"

    print("\n=== OPTIMAL FROZEN 8/3/3 SPLIT ===")
    print("Train:      ", best_candidate['train'])
    print("Validation: ", best_candidate['validation'])
    print("Test:       ", best_candidate['test'])

    print(f"\nOptimization Score Values:")
    print(f"  1. Worst Relative Deviation (All 15 quantities): {best_candidate['scores']['worst_relative_deviation_all']*100:.4f}%")
    print(f"  2. Overall RMSE (All 15 quantities):             {best_candidate['scores']['rmse_all']*100:.4f}%")
    print(f"  3. Test Worst Relative Deviation (5 quantities): {best_candidate['scores']['worst_relative_deviation_test']*100:.4f}%")
    print(f"  4. Test RMSE (5 quantities):                     {best_candidate['scores']['rmse_test']*100:.4f}%")

    return best_candidate, global_metrics, per_subject_stats, total_evaluated, total_rejected

def format_percentage(val):
    return f"{val * 100:.4f}%"

def generate_reports_and_freeze(best_candidate, global_metrics, per_subject_stats, total_evaluated, total_rejected):
    splits_json_path = "dataset/splits.json"
    report_json_path = "dataset/split_selection_report.json"

    # 1. Write dataset/splits.json
    frozen_splits = {
        "train": best_candidate['train'],
        "validation": best_candidate['validation'],
        "test": best_candidate['test']
    }
    with open(splits_json_path, 'w', encoding='utf-8') as f:
        json.dump(frozen_splits, f, indent=2)
    print(f"\n[OK] Wrote frozen split to {splits_json_path}")

    # 2. Write dataset/split_selection_report.json
    report_data = {
        "algorithm": {
            "name": "DMS-Eval Exhaustive Proportion-Matching 8/3/3 Subject-Disjoint Split Selection",
            "version": "1.0",
            "total_candidates_evaluated": total_evaluated,
            "total_candidates_rejected": total_rejected,
            "valid_candidates_scored": total_evaluated - total_rejected,
            "quantities_scored_per_split": [
                "positive_rate",
                "phone_use_proportion",
                "drinking_proportion",
                "yawning_proportion",
                "hand_over_mouth_proportion"
            ],
            "tiebreak_hierarchy": [
                "1. Minimum worst absolute relative deviation across all splits and quantities (15 values)",
                "2. Minimum overall RMSE of all 15 relative deviations",
                "3. Minimum test-split worst relative deviation (5 values)",
                "4. Minimum test-split RMSE (5 values)",
                "5. Lexicographically smallest subject-ID assignment"
            ]
        },
        "score_results": {
            "worst_relative_deviation_overall": best_candidate['scores']['worst_relative_deviation_all'],
            "rmse_overall": best_candidate['scores']['rmse_all'],
            "worst_relative_deviation_test": best_candidate['scores']['worst_relative_deviation_test'],
            "rmse_test": best_candidate['scores']['rmse_test']
        },
        "frozen_split": frozen_splits,
        "global_statistics": {
            "total_images": global_metrics['total_images'],
            "negative_frames": global_metrics['negative_frames'],
            "positive_frames": global_metrics['positive_frames'],
            "positive_rate": global_metrics['positive_rate'],
            "positive_rate_percent": format_percentage(global_metrics['positive_rate']),
            "class_counts": {
                CLASS_NAMES[cid]: global_metrics['class_counts'][cid] for cid in CLASS_IDS
            },
            "class_proportions": {
                CLASS_NAMES[cid]: global_metrics['class_proportions'][cid] for cid in CLASS_IDS
            },
            "class_proportions_percent": {
                CLASS_NAMES[cid]: format_percentage(global_metrics['class_proportions'][cid]) for cid in CLASS_IDS
            }
        },
        "per_subject_statistics": {
            s: {
                "total_images": per_subject_stats[s]['total_images'],
                "negative_frames": per_subject_stats[s]['negative_frames'],
                "positive_frames": per_subject_stats[s]['positive_frames'],
                "class_counts": {
                    CLASS_NAMES[cid]: per_subject_stats[s]['class_counts'][cid] for cid in CLASS_IDS
                }
            }
            for s in sorted(per_subject_stats.keys())
        },
        "split_statistics": {
            "train": {
                "subjects": best_candidate['train'],
                "total_images": best_candidate['train_metrics']['total_images'],
                "negative_frames": best_candidate['train_metrics']['negative_frames'],
                "positive_frames": best_candidate['train_metrics']['positive_frames'],
                "positive_rate": best_candidate['train_metrics']['positive_rate'],
                "positive_rate_percent": format_percentage(best_candidate['train_metrics']['positive_rate']),
                "class_counts": {
                    CLASS_NAMES[cid]: best_candidate['train_metrics']['class_counts'][cid] for cid in CLASS_IDS
                },
                "class_proportions": {
                    CLASS_NAMES[cid]: best_candidate['train_metrics']['class_proportions'][cid] for cid in CLASS_IDS
                },
                "class_proportions_percent": {
                    CLASS_NAMES[cid]: format_percentage(best_candidate['train_metrics']['class_proportions'][cid]) for cid in CLASS_IDS
                }
            },
            "validation": {
                "subjects": best_candidate['validation'],
                "total_images": best_candidate['validation_metrics']['total_images'],
                "negative_frames": best_candidate['validation_metrics']['negative_frames'],
                "positive_frames": best_candidate['validation_metrics']['positive_frames'],
                "positive_rate": best_candidate['validation_metrics']['positive_rate'],
                "positive_rate_percent": format_percentage(best_candidate['validation_metrics']['positive_rate']),
                "class_counts": {
                    CLASS_NAMES[cid]: best_candidate['validation_metrics']['class_counts'][cid] for cid in CLASS_IDS
                },
                "class_proportions": {
                    CLASS_NAMES[cid]: best_candidate['validation_metrics']['class_proportions'][cid] for cid in CLASS_IDS
                },
                "class_proportions_percent": {
                    CLASS_NAMES[cid]: format_percentage(best_candidate['validation_metrics']['class_proportions'][cid]) for cid in CLASS_IDS
                }
            },
            "test": {
                "subjects": best_candidate['test'],
                "total_images": best_candidate['test_metrics']['total_images'],
                "negative_frames": best_candidate['test_metrics']['negative_frames'],
                "positive_frames": best_candidate['test_metrics']['positive_frames'],
                "positive_rate": best_candidate['test_metrics']['positive_rate'],
                "positive_rate_percent": format_percentage(best_candidate['test_metrics']['positive_rate']),
                "class_counts": {
                    CLASS_NAMES[cid]: best_candidate['test_metrics']['class_counts'][cid] for cid in CLASS_IDS
                },
                "class_proportions": {
                    CLASS_NAMES[cid]: best_candidate['test_metrics']['class_proportions'][cid] for cid in CLASS_IDS
                },
                "class_proportions_percent": {
                    CLASS_NAMES[cid]: format_percentage(best_candidate['test_metrics']['class_proportions'][cid]) for cid in CLASS_IDS
                }
            }
        }
    }

    with open(report_json_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)
    print(f"[OK] Wrote selection report to {report_json_path}")

if __name__ == "__main__":
    best_candidate, global_metrics, per_subject_stats, total_eval, total_rej = run_exhaustive_search()
    generate_reports_and_freeze(best_candidate, global_metrics, per_subject_stats, total_eval, total_rej)
