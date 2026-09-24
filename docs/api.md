# SmartWaste API Reference

Base URL: `http://localhost:8000` (development)

---

## GET /health

Returns the current status of the API, model, and hardware device.

**Response:**
```json
{
  "status": "ok",
  "model_available": true,
  "model_version": "efficientnetb0-v1",
  "hardware_mode": "simulation",
  "hardware_available": true
}
```

---

## GET /api/model/info

Returns metadata about the currently loaded model.

**Response:**
```json
{
  "model_version": "efficientnetb0-v1",
  "architecture": "EfficientNetB0",
  "classes": 5,
  "class_names": ["glass", "metal", "other", "paper_cardboard", "plastic"],
  "image_size": 224,
  "trained_at": "2024-01-15T10:30:00Z",
  "confidence_threshold": 0.80,
  "uncertain_threshold": 0.50,
  "missing_categories": ["organic", "e_waste", "textile"],
  "model_available": true
}
```

---

## POST /api/predict

Classify a waste image uploaded as multipart/form-data.

**Request:** `Content-Type: multipart/form-data`  
**Field:** `file` — JPEG, PNG, WebP, or BMP image (max 10 MB)  
**Header:** `Authorization: Bearer <supabase_jwt>` (optional — saves to history if provided)

**Response (confident):**
```json
{
  "category": "plastic",
  "display_name": "Plastic",
  "confidence": 0.942,
  "is_uncertain": false,
  "recommendation": "Clean and rinse plastic items before recycling...",
  "hardware_command": "SORT_PLASTIC",
  "model_version": "efficientnetb0-v1",
  "message": null,
  "alternatives": null
}
```

**Response (low confidence):**
```json
{
  "category": "plastic",
  "display_name": "Plastic",
  "confidence": 0.63,
  "is_uncertain": true,
  "recommendation": "...",
  "hardware_command": "SORT_PLASTIC",
  "model_version": "efficientnetb0-v1",
  "message": "Prediction has low confidence. Please verify before disposal.",
  "alternatives": [
    {"category": "plastic", "confidence": 0.63},
    {"category": "other",   "confidence": 0.21},
    {"category": "metal",   "confidence": 0.10}
  ]
}
```

**Response (unknown):**
```json
{
  "category": "unknown",
  "display_name": "Unknown",
  "confidence": 0.38,
  "is_uncertain": true,
  "recommendation": "Unable to classify. Please sort manually.",
  "hardware_command": "MANUAL_REVIEW",
  "model_version": "efficientnetb0-v1",
  "message": "The system is not sufficiently confident about this item. Please verify manually before disposal."
}
```

**Error codes:**
- `413` — File too large
- `415` — Unsupported file type
- `422` — Invalid/corrupt image
- `503` — Model not trained yet

---

## POST /api/predict/webcam

Classify a webcam frame sent as a base64 data URI.

**Request body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgAB..."
}
```

**Response:** Same schema as `/api/predict`.

---

## POST /api/hardware/sort

Execute (or simulate) a sorting command.

**Request:**
```json
{
  "command": "SORT_PLASTIC",
  "category": "plastic",
  "confidence": 0.942
}
```

**Valid commands:**
`SORT_PLASTIC`, `SORT_METAL`, `SORT_GLASS`, `SORT_PAPER`, `SORT_ORGANIC`, `SORT_EWASTE`, `SORT_TEXTILE`, `SORT_OTHER`, `MANUAL_REVIEW`

**Response:**
```json
{
  "success": true,
  "command": "SORT_PLASTIC",
  "mode": "simulation",
  "message": "Plastic sorting action simulated successfully."
}
```

---

## GET /api/categories

Returns all 8 waste category configurations.

**Response:**
```json
{
  "categories": [
    {
      "id": "plastic",
      "name": "Plastic",
      "description": "...",
      "examples": ["water bottles", "..."],
      "recommendation": "...",
      "disposal_method": "Plastic recycling stream",
      "hardware_command": "SORT_PLASTIC",
      "color": "#3B82F6",
      "icon": "bottle"
    }
  ]
}
```
