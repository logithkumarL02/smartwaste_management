"""
SmartWaste CNN Training — EfficientNetB0 (configurable)
Usage:
  python ml/train.py
  python ml/train.py --architecture MobileNetV2
"""
import os, sys, json, logging, argparse
from pathlib import Path
from datetime import datetime
import yaml, numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)

def get_backbone(arch, image_size):
    import tensorflow as tf
    shape = (image_size, image_size, 3)
    a = arch.lower()
    if a == "efficientnetb0":
        from tensorflow.keras.applications import EfficientNetB0
        return EfficientNetB0(include_top=False, weights="imagenet", input_shape=shape)
    elif a == "efficientnetb1":
        from tensorflow.keras.applications import EfficientNetB1
        return EfficientNetB1(include_top=False, weights="imagenet", input_shape=shape)
    elif a == "mobilenetv2":
        from tensorflow.keras.applications import MobileNetV2
        return MobileNetV2(include_top=False, weights="imagenet", input_shape=shape)
    else:
        log.error(f"Unsupported architecture: {arch}"); sys.exit(1)

def build_model(config, num_classes, architecture=None):
    from tensorflow import keras
    mc = config["model"]
    arch = architecture or mc["architecture"]
    image_size = mc["image_size"]
    backbone = get_backbone(arch, image_size)
    backbone.trainable = not mc["freeze_backbone"]
    inputs = keras.Input(shape=(image_size, image_size, 3), name="image_input")
    if arch.lower().startswith("mobilenet"):
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        x = keras.layers.Lambda(preprocess_input, name="preprocess")(inputs)
        x = backbone(x, training=False)
    else:
        x = backbone(inputs, training=False)
    x = keras.layers.GlobalAveragePooling2D()(x)
    x = keras.layers.Dropout(mc["dropout"])(x)
    outputs = keras.layers.Dense(num_classes, activation="softmax", name="predictions")(x)
    return keras.Model(inputs=inputs, outputs=outputs), backbone

def train(config, architecture=None):
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    log.info(f"TensorFlow: {tf.__version__} | GPUs: {tf.config.list_physical_devices('GPU')}")
    manifest_path = Path(config["dataset"]["manifest_path"])
    if not manifest_path.exists():
        log.error(f"Manifest not found at {manifest_path}. Run: python ml/prepare_dataset.py"); sys.exit(1)
    with open(manifest_path) as f:
        manifest = json.load(f)
    class_names = sorted(manifest["trained_categories"])
    num_classes = len(class_names)
    log.info(f"Training on {num_classes} categories: {class_names}")

    mc = config["model"]; aug = config["augmentation"]
    prepared_dir = Path(config["dataset"]["prepared_dir"])
    model_dir = Path(config["output"]["model_dir"]); model_dir.mkdir(parents=True, exist_ok=True)
    arch = architecture or mc["architecture"]

    model, backbone = build_model(config, num_classes, arch)
    model.summary(print_fn=log.info)

    aug_gen = ImageDataGenerator(rescale=1./255, rotation_range=aug["rotation_range"],
        width_shift_range=aug["width_shift_range"], height_shift_range=aug["height_shift_range"],
        horizontal_flip=aug["horizontal_flip"], zoom_range=aug["zoom_range"],
        brightness_range=aug.get("brightness_range"), fill_mode=aug["fill_mode"]) if aug["enabled"] \
        else ImageDataGenerator(rescale=1./255)
    val_gen = ImageDataGenerator(rescale=1./255)

    img_size = mc["image_size"]; bs = mc["batch_size"]
    train_g = aug_gen.flow_from_directory(prepared_dir/"train", target_size=(img_size, img_size),
        batch_size=bs, class_mode="categorical", classes=class_names, shuffle=True, seed=42)
    val_g = val_gen.flow_from_directory(prepared_dir/"val", target_size=(img_size, img_size),
        batch_size=bs, class_mode="categorical", classes=class_names, shuffle=False)

    model_path = model_dir / config["output"]["model_filename"]
    callbacks = [
        keras.callbacks.ModelCheckpoint(str(model_path), save_best_only=True, monitor="val_accuracy", verbose=1),
        keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=8, restore_best_weights=True, verbose=1),
        keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=4, min_lr=1e-7, verbose=1),
        keras.callbacks.CSVLogger(str(model_dir / "training_log.csv")),
    ]

    model.compile(optimizer=keras.optimizers.Adam(mc["learning_rate"]),
                  loss="categorical_crossentropy", metrics=["accuracy"])

    phase1_epochs = min(mc.get("unfreeze_after_epoch", mc["epochs"]), mc["epochs"])
    log.info(f"Phase 1: Training head (epochs 1–{phase1_epochs})")
    model.fit(train_g, epochs=phase1_epochs, validation_data=val_g, callbacks=callbacks, verbose=1)

    if mc.get("unfreeze_after_epoch", mc["epochs"]) < mc["epochs"]:
        log.info(f"Phase 2: Fine-tuning top {mc['unfreeze_layers']} layers")
        backbone.trainable = True
        for layer in backbone.layers[:-mc.get("unfreeze_layers", 20)]:
            layer.trainable = False
        model.compile(optimizer=keras.optimizers.Adam(mc["learning_rate"] * 0.1),
                      loss="categorical_crossentropy", metrics=["accuracy"])
        model.fit(train_g, epochs=mc["epochs"], initial_epoch=phase1_epochs,
                  validation_data=val_g, callbacks=callbacks, verbose=1)

    class_mapping = {i: n for i, n in enumerate(class_names)}
    with open(model_dir / "class_mapping.json", "w") as f:
        json.dump(class_mapping, f, indent=2)

    metadata = {
        "model_version": f"{arch.lower()}-v1", "architecture": arch,
        "classes": num_classes, "class_names": class_names,
        "image_size": mc["image_size"], "trained_at": datetime.utcnow().isoformat() + "Z",
        "dataset": manifest["dataset_source"], "missing_categories": manifest.get("missing_categories", []),
        "confidence_threshold": config["inference"]["confidence_threshold"],
        "uncertain_threshold": config["inference"]["uncertain_threshold"],
    }
    with open(model_dir / config["output"]["metadata_filename"], "w") as f:
        json.dump(metadata, f, indent=2)

    log.info(f"Model saved: {model_path}")
    log.info("Run: python ml/evaluate.py")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="ml/config.yaml")
    parser.add_argument("--architecture", default=None)
    args = parser.parse_args()
    train(load_config(args.config), args.architecture)
