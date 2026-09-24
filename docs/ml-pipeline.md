# SmartWaste — ML Pipeline

## Dataset: TrashNet

- **Source:** `garythung/trashnet` on HuggingFace
- **Paper:** Yang & Thung, *Classification of Trash for Recyclability Status*, Stanford CS229, 2016
- **Images:** 2,527 real photographs, 6 classes

## Class Mapping

| TrashNet class | App category    |
|----------------|-----------------|
| glass          | glass           |
| paper          | paper_cardboard |
| cardboard      | paper_cardboard |
| plastic        | plastic         |
| metal          | metal           |
| trash          | other           |

**Not in dataset:** organic, e_waste, textile — these are NOT fabricated.

## Model Architecture

```
Input (224×224×3)
     ↓
EfficientNetB0 backbone (ImageNet pretrained, 7.2M params)
     ↓
GlobalAveragePooling2D
     ↓
Dropout(0.3)
     ↓
Dense(num_classes, softmax)
```

## Training Strategy

Phase 1 — Head only (backbone frozen):
- Epochs 1–15, LR=1e-4
- Only classification head learns

Phase 2 — Fine-tuning (top 20 backbone layers):
- Epochs 16–30, LR=1e-5
- Backbone top layers unfreeze

## Augmentation

Random rotation ±30°, horizontal flip, zoom ±20%, brightness ±20%, shift ±15%.

## Uncertainty Thresholds

| Confidence       | Result                                    |
|------------------|-------------------------------------------|
| ≥ 0.80           | Confident prediction                      |
| 0.50 – 0.79      | Low-confidence (shows alternatives)       |
| < 0.50           | Unknown (refuse to classify, manual review) |

All thresholds are configurable in `ml/config.yaml` and can be overridden at runtime via environment variables.

## Evaluation Outputs

After `python ml/evaluate.py`:
- `evaluation/evaluation_results.json` — full metrics JSON
- `evaluation/confusion_matrix.png` — heatmap plot

## Adding New Classes

1. Find a dataset with the missing class images (organic, e_waste, textile).
2. Add entries to `class_mapping` in `ml/config.yaml`.
3. Re-run `python ml/prepare_dataset.py --config ml/config.yaml`.
4. Re-run `python ml/train.py`.
5. The backend picks up the new model automatically on restart.
