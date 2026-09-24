"""
SmartWaste Model Evaluation
Usage: python ml/evaluate.py
"""
import json, logging, argparse
from pathlib import Path
import yaml, numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)

def evaluate(config):
    from tensorflow import keras
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    model_dir = Path(config["output"]["model_dir"])
    model_path = model_dir / config["output"]["model_filename"]
    meta_path = model_dir / config["output"]["metadata_filename"]
    prepared_dir = Path(config["dataset"]["prepared_dir"])
    eval_dir = Path(config["output"]["evaluation_dir"]); eval_dir.mkdir(parents=True, exist_ok=True)

    if not model_path.exists():
        log.error(f"Model not found at {model_path}. Run: python ml/train.py"); return
    model = keras.models.load_model(str(model_path))
    with open(meta_path) as f:
        metadata = json.load(f)
    class_names = metadata["class_names"]
    image_size = metadata["image_size"]
    log.info(f"Model: {metadata['model_version']} | Classes: {class_names}")

    test_gen = ImageDataGenerator(rescale=1./255).flow_from_directory(
        prepared_dir/"test", target_size=(image_size, image_size), batch_size=32,
        class_mode="categorical", classes=class_names, shuffle=False)
    if test_gen.samples == 0:
        log.error("No test images found."); return

    log.info(f"Inferring on {test_gen.samples} test images...")
    preds = model.predict(test_gen, verbose=1)
    y_pred = np.argmax(preds, axis=1)
    y_true = test_gen.classes

    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
    cm = confusion_matrix(y_true, y_pred)

    log.info(f"\nAccuracy: {acc*100:.2f}%  |  Macro F1: {report['macro avg']['f1-score']:.4f}")
    for cls in class_names:
        r = report[cls]
        log.info(f"  {cls:<20} P={r['precision']:.3f}  R={r['recall']:.3f}  F1={r['f1-score']:.3f}  n={int(r['support'])}")

    results = {
        "model_version": metadata["model_version"], "accuracy": round(acc, 4),
        "macro_f1": round(report["macro avg"]["f1-score"], 4),
        "per_class": {c: {"precision": round(report[c]["precision"],4), "recall": round(report[c]["recall"],4),
            "f1_score": round(report[c]["f1-score"],4), "support": int(report[c]["support"])} for c in class_names},
        "confusion_matrix": cm.tolist(), "class_names": class_names,
    }
    with open(eval_dir / "evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    try:
        import matplotlib.pyplot as plt, seaborn as sns
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
        plt.title(f"Confusion Matrix — {metadata['model_version']}\nAccuracy: {acc*100:.1f}%")
        plt.ylabel("True"); plt.xlabel("Predicted"); plt.tight_layout()
        plt.savefig(eval_dir / "confusion_matrix.png", dpi=150); plt.close()
    except Exception as e:
        log.warning(f"Could not save confusion matrix plot: {e}")
    log.info(f"Results saved to {eval_dir}/")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="ml/config.yaml")
    evaluate(load_config(parser.parse_args().config))
