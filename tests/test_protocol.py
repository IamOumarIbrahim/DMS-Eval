"""Frozen configuration and category mapping tests."""

from core.dataset import COCO_TO_YOLO, YOLO_TO_COCO
from core.protocol import load_protocol, load_yaml, validate_protocol


def test_protocol_is_self_consistent_and_fingerprinted():
    protocol = validate_protocol()
    assert protocol["training"]["physical_batch_size"] == 8
    assert protocol["training"]["gradient_accumulation_steps"] == 4
    assert protocol["training"]["effective_batch_size"] == 32
    assert protocol["training"]["optimization"]["ultralytics"] == {
        "optimizer": "SGD",
        "lr0": 0.01,
        "momentum": 0.937,
        "weight_decay": 0.0005,
        "cos_lr": False,
    }
    assert protocol["profiling"]["warmup_passes"] == 10


def test_category_mapping_round_trip():
    assert COCO_TO_YOLO == {1: 0, 2: 1, 3: 2, 4: 3}
    assert YOLO_TO_COCO == {0: 1, 1: 2, 2: 3, 3: 4}


def test_dfine_frozen_training_overrides():
    config = load_yaml("configs/dfine/dfine_n_dms.yml")
    assert config["epochs"] == 220
    assert config["gradient_accumulation_steps"] == 4
    assert config["train_dataloader"]["total_batch_size"] == 8
    assert config["optimizer"]["lr"] == 0.00025
    assert config["optimizer"]["weight_decay"] == 0.0001
    assert config["train_dataloader"]["dataset"]["transforms"]["policy"]["epoch"] == 148
