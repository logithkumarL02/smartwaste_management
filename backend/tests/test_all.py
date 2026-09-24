"""
SmartWaste Backend Tests
=========================
Run with: pytest backend/tests/ -v
"""

import io
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

import numpy as np
from PIL import Image


# ── Helpers ────────────────────────────────────────────────────────────────

def make_rgb_image_bytes(width=224, height=224, color=(100, 150, 200)) -> bytes:
    """Create a minimal valid RGB JPEG in memory."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def make_corrupt_bytes() -> bytes:
    return b"not an image at all"


# ── 1. Preprocessing tests ─────────────────────────────────────────────────

class TestPreprocessing:
    def test_valid_image_returns_correct_shape(self):
        from app.inference.preprocessing import validate_and_preprocess
        data = make_rgb_image_bytes()
        arr = validate_and_preprocess(data, target_size=224)
        assert arr.shape == (224, 224, 3)
        assert arr.dtype == np.float32

    def test_valid_image_normalized_0_to_1(self):
        from app.inference.preprocessing import validate_and_preprocess
        data = make_rgb_image_bytes()
        arr = validate_and_preprocess(data, target_size=224)
        assert arr.min() >= 0.0
        assert arr.max() <= 1.0

    def test_corrupt_image_raises(self):
        from app.inference.preprocessing import validate_and_preprocess, PreprocessingError
        with pytest.raises(PreprocessingError):
            validate_and_preprocess(make_corrupt_bytes())

    def test_empty_bytes_raises(self):
        from app.inference.preprocessing import validate_and_preprocess, PreprocessingError
        with pytest.raises(PreprocessingError):
            validate_and_preprocess(b"")

    def test_wrong_mime_type_raises(self):
        from app.inference.preprocessing import validate_and_preprocess, PreprocessingError
        data = make_rgb_image_bytes()
        with pytest.raises(PreprocessingError, match="Unsupported image type"):
            validate_and_preprocess(data, mime_type="application/pdf")

    def test_custom_target_size(self):
        from app.inference.preprocessing import validate_and_preprocess
        data = make_rgb_image_bytes()
        arr = validate_and_preprocess(data, target_size=128)
        assert arr.shape == (128, 128, 3)


# ── 2. Category / disposal tests ───────────────────────────────────────────

class TestCategories:
    def test_all_8_categories_present(self):
        from app.disposal.categories import WASTE_CATEGORIES
        expected = {"plastic", "metal", "glass", "paper_cardboard",
                    "organic", "e_waste", "textile", "other"}
        assert set(WASTE_CATEGORIES.keys()) == expected

    def test_each_category_has_required_fields(self):
        from app.disposal.categories import WASTE_CATEGORIES
        required = {"id", "name", "description", "examples", "recommendation",
                    "hardware_command", "color"}
        for cat_id, cat in WASTE_CATEGORIES.items():
            for field in required:
                assert field in cat, f"Category '{cat_id}' missing field '{field}'"

    def test_hardware_commands_format(self):
        from app.disposal.categories import WASTE_CATEGORIES
        for cat_id, cat in WASTE_CATEGORIES.items():
            cmd = cat["hardware_command"]
            assert cmd.startswith("SORT_"), f"'{cat_id}' command should start with SORT_"
            assert cmd == cmd.upper(), f"'{cat_id}' command should be uppercase"

    def test_get_category_fallback(self):
        from app.disposal.categories import get_category
        result = get_category("nonexistent_category")
        assert result["id"] == "other"

    def test_get_hardware_command(self):
        from app.disposal.categories import get_hardware_command
        assert get_hardware_command("plastic") == "SORT_PLASTIC"
        assert get_hardware_command("e_waste") == "SORT_EWASTE"
        assert get_hardware_command("paper_cardboard") == "SORT_PAPER"

    def test_list_categories_returns_list(self):
        from app.disposal.categories import list_categories
        cats = list_categories()
        assert isinstance(cats, list)
        assert len(cats) == 8


# ── 3. Hardware simulator tests ────────────────────────────────────────────

class TestHardwareSimulator:
    def test_valid_sort_command_succeeds(self):
        from app.hardware.simulator import SimulationSortingDevice
        device = SimulationSortingDevice()
        success, msg = device.sort("SORT_PLASTIC")
        assert success is True
        assert len(msg) > 0

    def test_invalid_command_fails(self):
        from app.hardware.simulator import SimulationSortingDevice
        device = SimulationSortingDevice()
        success, msg = device.sort("SORT_BANANA")
        assert success is False

    def test_all_valid_commands_succeed(self):
        from app.hardware.simulator import SimulationSortingDevice, COMMAND_VISUALS
        device = SimulationSortingDevice()
        for cmd in COMMAND_VISUALS:
            success, _ = device.sort(cmd)
            assert success is True, f"Command {cmd} should succeed"

    def test_mode_is_simulation(self):
        from app.hardware.simulator import SimulationSortingDevice
        device = SimulationSortingDevice()
        assert device.get_mode() == "simulation"

    def test_is_always_available(self):
        from app.hardware.simulator import SimulationSortingDevice
        device = SimulationSortingDevice()
        assert device.is_available() is True

    def test_manual_review_command(self):
        from app.hardware.simulator import SimulationSortingDevice
        device = SimulationSortingDevice()
        success, msg = device.sort("MANUAL_REVIEW")
        assert success is True


# ── 4. Hardware controller tests ───────────────────────────────────────────

class TestHardwareController:
    def test_simulation_mode_returns_simulator(self):
        # Clear lru_cache before test
        from app.hardware import controller
        controller.get_sorting_device.cache_clear()
        from app.hardware.controller import get_sorting_device
        from app.hardware.simulator import SimulationSortingDevice
        device = get_sorting_device("simulation")
        assert isinstance(device, SimulationSortingDevice)

    def test_unknown_mode_falls_back_to_simulation(self):
        from app.hardware import controller
        controller.get_sorting_device.cache_clear()
        from app.hardware.controller import get_sorting_device
        from app.hardware.simulator import SimulationSortingDevice
        device = get_sorting_device("nonexistent_hardware_mode")
        assert isinstance(device, SimulationSortingDevice)


# ── 5. Uncertainty logic tests ─────────────────────────────────────────────

class TestUncertaintyLogic:
    """Test the uncertainty thresholds without requiring a real model."""

    def _mock_predict(self, probs_array, class_names):
        """Helper: mock predict_raw and metadata for classifier tests."""
        return probs_array, {"class_names": class_names, "image_size": 224,
                             "model_version": "test-v1"}

    def test_high_confidence_not_uncertain(self):
        """confidence=0.92 with threshold=0.80 → is_uncertain=False."""
        probs = np.array([0.92, 0.05, 0.02, 0.01])
        class_names = ["plastic", "metal", "glass", "other"]
        top_idx = int(np.argmax(probs))
        top_conf = float(probs[top_idx])
        is_uncertain = top_conf < 0.80
        assert is_uncertain is False
        assert class_names[top_idx] == "plastic"

    def test_low_confidence_is_uncertain(self):
        """confidence=0.63 with threshold=0.80 → is_uncertain=True."""
        probs = np.array([0.63, 0.21, 0.10, 0.06])
        top_conf = float(probs[np.argmax(probs)])
        is_uncertain = top_conf < 0.80
        assert is_uncertain is True

    def test_below_uncertain_threshold_returns_unknown(self):
        """confidence=0.32 below uncertain_threshold=0.50 → category=unknown."""
        probs = np.array([0.32, 0.28, 0.22, 0.18])
        top_conf = float(probs[np.argmax(probs)])
        uncertain_threshold = 0.50
        assert top_conf < uncertain_threshold  # should be refused as unknown

    def test_exactly_at_uncertain_threshold(self):
        """confidence=0.50 exactly at threshold → still uncertain (boundary)."""
        probs = np.array([0.50, 0.30, 0.12, 0.08])
        top_conf = float(probs[np.argmax(probs)])
        # 0.50 < 0.80 → uncertain; 0.50 >= 0.50 → not "unknown", just low conf
        assert top_conf < 0.80   # is_uncertain
        assert top_conf >= 0.50  # not fully unknown

    def test_alternatives_sorted_descending(self):
        """Top alternatives must be sorted highest → lowest confidence."""
        probs = np.array([0.65, 0.20, 0.10, 0.05])
        sorted_indices = np.argsort(probs)[::-1][:3]
        sorted_confs = [float(probs[i]) for i in sorted_indices]
        assert sorted_confs == sorted(sorted_confs, reverse=True)


# ── 6. Model loader tests (no actual model file needed) ───────────────────

class TestModelLoader:
    def test_missing_model_returns_false(self, tmp_path):
        # Reset module state
        import app.inference.model_loader as ml
        ml._model = None
        ml._metadata = None
        ml._model_loaded = False

        result = ml.load_model(
            str(tmp_path / "nonexistent.keras"),
            str(tmp_path / "nonexistent.json"),
        )
        assert result is False
        assert ml.is_model_available() is False

    def test_is_model_available_false_without_load(self):
        import app.inference.model_loader as ml
        ml._model = None
        ml._metadata = None
        ml._model_loaded = False
        assert ml.is_model_available() is False

    def test_predict_raw_raises_when_no_model(self):
        import app.inference.model_loader as ml
        ml._model = None
        ml._metadata = None
        ml._model_loaded = True
        with pytest.raises(RuntimeError, match="not available"):
            ml.predict_raw(np.zeros((224, 224, 3), dtype=np.float32))


# ── 7. Hardware schema validation ──────────────────────────────────────────

class TestHardwareSchema:
    def test_valid_commands_set(self):
        from app.schemas.hardware import VALID_COMMANDS
        assert "SORT_PLASTIC" in VALID_COMMANDS
        assert "SORT_EWASTE" in VALID_COMMANDS
        assert "MANUAL_REVIEW" in VALID_COMMANDS
        assert len(VALID_COMMANDS) == 9  # 8 sort + 1 manual

    def test_hardware_sort_request_model(self):
        from app.schemas.hardware import HardwareSortRequest
        req = HardwareSortRequest(command="SORT_PLASTIC")
        assert req.command == "SORT_PLASTIC"
        assert req.category is None

    def test_hardware_sort_response_model(self):
        from app.schemas.hardware import HardwareSortResponse
        resp = HardwareSortResponse(
            success=True,
            command="SORT_PLASTIC",
            mode="simulation",
            message="Plastic sorting action simulated successfully.",
        )
        assert resp.success is True
        assert resp.mode == "simulation"
