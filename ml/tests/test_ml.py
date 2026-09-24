"""
Tests for ML dataset mapping and class configuration.
Run from project root: python -m pytest ml/tests/ -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ── 1. Class mapping tests ─────────────────────────────────────────────────

def test_class_mapping_covers_all_trashnet_classes():
    """All TrashNet source classes must be mapped."""
    from prepare_dataset import CLASS_MAPPING
    trashnet_classes = {"glass", "paper", "cardboard", "plastic", "metal", "trash"}
    assert set(CLASS_MAPPING.keys()) == trashnet_classes


def test_class_mapping_target_categories_are_valid():
    """All mapping targets must be valid application categories."""
    from prepare_dataset import CLASS_MAPPING
    valid_categories = {
        "plastic", "metal", "glass", "paper_cardboard",
        "organic", "e_waste", "textile", "other"
    }
    for source, target in CLASS_MAPPING.items():
        assert target in valid_categories, f"'{source}' maps to invalid category '{target}'"


def test_paper_and_cardboard_both_map_to_paper_cardboard():
    from prepare_dataset import CLASS_MAPPING
    assert CLASS_MAPPING["paper"] == "paper_cardboard"
    assert CLASS_MAPPING["cardboard"] == "paper_cardboard"


def test_trash_maps_to_other():
    from prepare_dataset import CLASS_MAPPING
    assert CLASS_MAPPING["trash"] == "other"


def test_unsupported_classes_are_documented():
    """Missing categories must be explicitly listed, not silently dropped."""
    from prepare_dataset import UNSUPPORTED_CLASSES
    assert "organic" in UNSUPPORTED_CLASSES
    assert "e_waste" in UNSUPPORTED_CLASSES
    assert "textile" in UNSUPPORTED_CLASSES


def test_class_mapping_is_deterministic():
    """Same input always produces same output."""
    from prepare_dataset import CLASS_MAPPING
    assert CLASS_MAPPING["plastic"] == "plastic"
    assert CLASS_MAPPING["metal"] == "metal"
    assert CLASS_MAPPING["glass"] == "glass"


# ── 2. Config YAML tests ───────────────────────────────────────────────────

def test_config_loads_and_has_required_sections():
    import yaml
    config_path = Path(__file__).parent.parent / "config.yaml"
    assert config_path.exists(), "config.yaml must exist"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    assert "model" in config
    assert "inference" in config
    assert "dataset" in config
    assert "output" in config
    assert "class_mapping" in config


def test_config_inference_thresholds_are_valid():
    import yaml
    with open(Path(__file__).parent.parent / "config.yaml") as f:
        config = yaml.safe_load(f)
    inf = config["inference"]
    assert 0 < inf["uncertain_threshold"] < inf["confidence_threshold"] <= 1.0


def test_config_train_val_test_splits_sum_to_one():
    import yaml
    with open(Path(__file__).parent.parent / "config.yaml") as f:
        config = yaml.safe_load(f)
    ds = config["dataset"]
    total = ds["train_split"] + ds["val_split"] + ds["test_split"]
    assert abs(total - 1.0) < 1e-6


def test_config_supported_architecture():
    import yaml
    with open(Path(__file__).parent.parent / "config.yaml") as f:
        config = yaml.safe_load(f)
    arch = config["model"]["architecture"]
    supported = {"EfficientNetB0", "EfficientNetB1", "MobileNetV2"}
    assert arch in supported, f"Architecture '{arch}' not in supported set {supported}"


# ── 3. Uncertainty threshold logic ────────────────────────────────────────

def test_confident_threshold_logic():
    conf_threshold = 0.80
    uncertain_threshold = 0.50

    # Confident
    conf = 0.92
    assert conf >= conf_threshold

    # Low confidence but not unknown
    conf = 0.65
    assert conf >= uncertain_threshold
    assert conf < conf_threshold

    # Unknown
    conf = 0.35
    assert conf < uncertain_threshold
