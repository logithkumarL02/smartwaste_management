"""
SmartWaste Dataset Preparation
Dataset: TrashNet (garythung/trashnet) from HuggingFace
Classes: glass, paper, cardboard, plastic, metal, trash (6 classes, ~2527 images)

NOTE: organic, e_waste, textile are NOT in TrashNet and are NOT fabricated.

Usage:
  python ml/prepare_dataset.py
  python ml/prepare_dataset.py --config ml/config.yaml --seed 42
"""
import os, sys, json, shutil, random, logging, argparse
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict

import yaml
from PIL import Image, UnidentifiedImageError
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

CLASS_MAPPING = {
    "glass": "glass", "paper": "paper_cardboard", "cardboard": "paper_cardboard",
    "plastic": "plastic", "metal": "metal", "trash": "other",
}
UNSUPPORTED_CLASSES = ["organic", "e_waste", "textile"]
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def validate_image(path: Path, min_size: int = 32) -> bool:
    try:
        with Image.open(path) as img:
            w, h = img.size
            if w < min_size or h < min_size:
                return False
            img.verify()
        return True
    except Exception:
        return False

def download_trashnet(raw_dir: Path) -> Path:
    try:
        from datasets import load_dataset
    except ImportError:
        log.error("Install 'datasets': pip install datasets")
        sys.exit(1)
    if (raw_dir / ".downloaded").exists():
        log.info("Dataset already downloaded. Skipping.")
        return raw_dir
    log.info("Downloading TrashNet from HuggingFace (~40 MB)...")
    ds = load_dataset("garythung/trashnet")
    raw_dir.mkdir(parents=True, exist_ok=True)
    label_names = ds["train"].features["label"].names
    log.info(f"Labels: {label_names}")
    saved = defaultdict(int)
    for split_name, split_data in ds.items():
        for item in tqdm(split_data, desc=f"Saving {split_name}"):
            label_name = label_names[item["label"]]
            class_dir = raw_dir / label_name
            class_dir.mkdir(parents=True, exist_ok=True)
            img_path = class_dir / f"{label_name}_{saved[label_name]:05d}.jpg"
            item["image"].save(img_path, format="JPEG", quality=95)
            saved[label_name] += 1
    (raw_dir / ".downloaded").touch()
    log.info(f"Downloaded {sum(saved.values())} images.")
    return raw_dir

def prepare_dataset(config: dict) -> dict:
    ds_cfg = config["dataset"]
    raw_dir = Path(ds_cfg["raw_dir"])
    prepared_dir = Path(ds_cfg["prepared_dir"])
    manifest_path = Path(ds_cfg["manifest_path"])
    train_r, val_r, test_r = ds_cfg["train_split"], ds_cfg["val_split"], ds_cfg["test_split"]
    assert abs(train_r + val_r + test_r - 1.0) < 1e-6, "Splits must sum to 1.0"

    download_trashnet(raw_dir)

    log.info("Scanning and mapping categories...")
    category_images: Dict[str, list] = defaultdict(list)
    skipped = 0
    for source_class in sorted(os.listdir(raw_dir)):
        class_dir = raw_dir / source_class
        if not class_dir.is_dir() or source_class.startswith("."):
            continue
        if source_class not in CLASS_MAPPING:
            log.warning(f"  Unknown class '{source_class}' — skipping")
            continue
        app_cat = CLASS_MAPPING[source_class]
        log.info(f"  {source_class} → {app_cat}")
        for img_file in sorted(class_dir.iterdir()):
            if img_file.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            if validate_image(img_file):
                category_images[app_cat].append(img_file)
            else:
                skipped += 1

    log.info(f"Skipped {skipped} corrupt images.")
    min_samples = ds_cfg.get("min_samples_per_class", 50)
    trained_categories = [c for c, imgs in category_images.items() if len(imgs) >= min_samples]
    log.info(f"Trained categories: {trained_categories}")

    prepared_dir.mkdir(parents=True, exist_ok=True)
    for split in ["train", "val", "test"]:
        (prepared_dir / split).mkdir(exist_ok=True)

    split_counts: dict = {"train": Counter(), "val": Counter(), "test": Counter()}
    for cat_id in trained_categories:
        images = category_images[cat_id][:]
        random.shuffle(images)
        n = len(images)
        n_train = int(n * train_r)
        n_val = int(n * val_r)
        splits_data = {
            "train": images[:n_train],
            "val": images[n_train:n_train + n_val],
            "test": images[n_train + n_val:],
        }
        for sname, simages in splits_data.items():
            sdir = prepared_dir / sname / cat_id
            sdir.mkdir(parents=True, exist_ok=True)
            for src in simages:
                shutil.copy2(src, sdir / src.name)
            split_counts[sname][cat_id] = len(simages)

    total = sum(sum(c.values()) for c in split_counts.values())
    manifest = {
        "dataset_source": "garythung/trashnet",
        "class_mapping": CLASS_MAPPING,
        "trained_categories": trained_categories,
        "missing_categories": UNSUPPORTED_CLASSES,
        "splits": {s: dict(c) for s, c in split_counts.items()},
        "total_images": total,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    log.info("=" * 60)
    log.info(f"DONE. {total} images prepared in {prepared_dir}")
    log.info(f"Manifest: {manifest_path}")
    log.info("NOTE: organic/e_waste/textile excluded — not in TrashNet.")
    log.info("=" * 60)
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="ml/config.yaml")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    random.seed(args.seed)
    prepare_dataset(load_config(args.config))
