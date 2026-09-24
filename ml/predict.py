"""
SmartWaste CLI prediction helper.
Usage: python ml/predict.py --image path/to/image.jpg
"""
import json, argparse
from pathlib import Path
import yaml, numpy as np

def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)

def predict_image(image_path, config):
    from tensorflow import keras
    from PIL import Image
    model_dir = Path(config["output"]["model_dir"])
    model_path = model_dir / config["output"]["model_filename"]
    meta_path = model_dir / config["output"]["metadata_filename"]
    if not model_path.exists():
        return {"error": "Model not trained. Run: python ml/train.py", "model_available": False}
    model = keras.models.load_model(str(model_path))
    with open(meta_path) as f:
        metadata = json.load(f)
    class_names = metadata["class_names"]
    image_size = metadata["image_size"]
    inf = config["inference"]
    img = Image.open(image_path).convert("RGB").resize((image_size, image_size))
    arr = np.array(img, dtype=np.float32) / 255.0
    probs = model.predict(np.expand_dims(arr, 0), verbose=0)[0]
    top_idx = int(np.argmax(probs)); top_conf = float(probs[top_idx])
    if top_conf < inf["uncertain_threshold"]:
        return {"category": "unknown", "confidence": round(top_conf, 4), "is_uncertain": True,
                "message": "Not sufficiently confident. Please verify manually."}
    alternatives = [{"category": class_names[i], "confidence": round(float(probs[i]),4)}
                    for i in np.argsort(probs)[::-1][:inf["max_alternatives"]]]
    return {"category": class_names[top_idx], "confidence": round(top_conf, 4),
            "is_uncertain": top_conf < inf["confidence_threshold"],
            "alternatives": alternatives, "model_version": metadata["model_version"]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--config", default="ml/config.yaml")
    args = parser.parse_args()
    result = predict_image(args.image, load_config(args.config))
    print("\n" + "="*50)
    for k, v in result.items():
        print(f"  {k}: {v}")
    print("="*50)
