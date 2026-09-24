# SmartWaste — AI-Powered Waste Segregation System

> **AI-powered waste segregation for a cleaner tomorrow.**

SmartWaste is a production-quality full-stack web application that uses a CNN (EfficientNetB0) trained on real waste imagery to classify waste into recyclable categories and simulate hardware sorting commands. Built as a college final-year software engineering project.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Prerequisites](#4-prerequisites)
5. [Supabase Setup](#5-supabase-setup)
6. [Dataset](#6-dataset)
7. [ML Pipeline](#7-ml-pipeline)
8. [Backend Setup](#8-backend-setup)
9. [Frontend Setup](#9-frontend-setup)
10. [Environment Variables](#10-environment-variables)
11. [Running the Project](#11-running-the-project)
12. [API Documentation](#12-api-documentation)
13. [Hardware Simulation](#13-hardware-simulation)
14. [Future Hardware Integration](#14-future-hardware-integration)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. Project Overview

SmartWaste allows users to:

- Upload a waste image **or** use a live webcam feed
- Get an AI-predicted waste category (plastic, metal, glass, paper/cardboard, other)
- See confidence score with clear uncertainty indication
- Receive disposal/recycling recommendations
- See the corresponding hardware sorting command
- View their full classification history with filters
- See dashboard statistics and charts

The system includes a hardware abstraction layer so that a simulated sorter can be replaced with a Raspberry Pi, ESP32, or robotic arm without changing any ML or API logic.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────┐
│                 Next.js Frontend                 │
│  (login · register · dashboard · classify ·      │
│   history · profile)                             │
└────────────────────┬────────────────────────────┘
                     │ REST (JSON)
┌────────────────────▼────────────────────────────┐
│              FastAPI Backend                     │
│  /health · /api/predict · /api/model/info        │
│  /api/predict/webcam · /api/hardware/sort        │
│  /api/categories                                 │
│                                                  │
│  ┌──────────────┐  ┌───────────────────────┐    │
│  │  Inference   │  │  Hardware Abstraction │    │
│  │  Classifier  │  │  (Simulation / Pi /   │    │
│  │  (OpenCV +   │  │   ESP32 / Arm)        │    │
│  │   Keras CNN) │  └───────────────────────┘    │
│  └──────────────┘                                │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────▼─────────────┐
        │  Supabase (PostgreSQL)   │
        │  profiles · predictions  │
        │  Auth · RLS · Storage    │
        └──────────────────────────┘
```

---

## 3. Tech Stack

| Layer       | Technology                                              |
|-------------|--------------------------------------------------------|
| Frontend    | Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts |
| Backend     | Python, FastAPI, Uvicorn, Pydantic v2                  |
| ML          | TensorFlow/Keras, EfficientNetB0, OpenCV, Pillow        |
| Auth / DB   | Supabase Auth, Supabase PostgreSQL, Row Level Security  |
| Dataset     | TrashNet (garythung/trashnet on HuggingFace)            |

---

## 4. Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **pip** (or conda)
- A **Supabase** account (free tier is sufficient — see §5)
- A modern browser with camera support (for webcam mode)

---

## 5. Supabase Setup

### Supabase Free Tier Limits (as of 2025)
The free tier is **more than sufficient** for a college project:
- 500 MB PostgreSQL database
- 1 GB file storage
- 5 GB egress per month
- 50,000 monthly active users

No subscription is required unless you need more than these limits.

### Steps

1. Go to [supabase.com](https://supabase.com) and create a free project.
2. Once created, open the **SQL Editor** in your project dashboard.
3. Paste and run the contents of `supabase_schema.sql` (in the project root).
4. Go to **Project Settings → API** and copy:
   - `Project URL` → `SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_URL`
   - `anon public` key → `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY` (**backend only, never expose to browser**)

---

## 6. Dataset

SmartWaste uses **TrashNet** — a real, publicly available dataset from a Stanford CS229 project (Yang & Thung, 2016), hosted on HuggingFace as `garythung/trashnet`.

**TrashNet contains 2527 images across 6 classes:**

| TrashNet class | SmartWaste category  | Count (approx.) |
|----------------|----------------------|-----------------|
| glass          | glass                | 501             |
| paper          | paper_cardboard      | 594             |
| cardboard      | paper_cardboard      | 403             |
| plastic        | plastic              | 482             |
| metal          | metal                | 410             |
| trash          | other                | 137             |

**Why only 5 categories are trained (not 8):**  
The full SmartWaste spec defines 8 categories (plastic, metal, glass, paper_cardboard, organic, e_waste, textile, other). TrashNet does not include organic waste, e-waste, or textile images. Rather than fabricate synthetic training data, these categories are **intentionally excluded** from the model. The system is honest about this: uncertain/out-of-distribution items return a low-confidence flag. If a dataset with these classes is found (e.g., Kaggle's Waste Classification Data v2), re-run `prepare_dataset.py` with an updated `config.yaml` mapping to add them.

---

## 7. ML Pipeline

### Step 1 — Prepare dataset

```bash
cd smartwaste         # project root
python ml/prepare_dataset.py
```

This downloads TrashNet from HuggingFace (~40 MB), maps classes, validates images, and splits into train/val/test. A manifest is saved to `data/manifest.json`.

### Step 2 — Train

```bash
python ml/train.py
```

Trains EfficientNetB0 with ImageNet weights. Two-phase training:
- Phase 1: frozen backbone, train head only
- Phase 2: unfreeze top 20 backbone layers, fine-tune at lower LR

Saves model to `model/waste_classifier.keras` and metadata to `model/metadata.json`.

To use a different architecture:
```bash
python ml/train.py --architecture MobileNetV2
```

### Step 3 — Evaluate

```bash
python ml/evaluate.py
```

Reports accuracy, precision, recall, F1, confusion matrix. Saves results to `evaluation/`.

### Step 4 — Test single image

```bash
python ml/predict.py --image path/to/image.jpg
```

### Configuration

All training parameters live in `ml/config.yaml`. Edit there — no code changes needed.

---

## 8. Backend Setup

```bash
cd backend
cp .env.example .env    # fill in your Supabase keys and model path
pip install -r requirements.txt
```

Verify the `.env` has the correct `MODEL_PATH` pointing to your trained model.

---

## 9. Frontend Setup

```bash
cd frontend
cp .env.example .env.local    # fill in Supabase public keys
npm install
```

---

## 10. Environment Variables

### Backend (`backend/.env`)

| Variable                  | Description                                      |
|---------------------------|--------------------------------------------------|
| `SUPABASE_URL`            | Your Supabase project URL                        |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (never expose to browser)     |
| `MODEL_PATH`              | Path to trained `.keras` model file              |
| `MODEL_METADATA_PATH`     | Path to `metadata.json`                          |
| `CONFIDENCE_THRESHOLD`    | Min confidence for a "confident" result (0–1)    |
| `UNCERTAIN_THRESHOLD`     | Below this → "unknown" result (0–1)              |
| `HARDWARE_MODE`           | `simulation` (default), or future modes          |
| `CORS_ORIGINS`            | JSON array of allowed frontend origins           |

### Frontend (`frontend/.env.local`)

| Variable                              | Description                    |
|---------------------------------------|--------------------------------|
| `NEXT_PUBLIC_SUPABASE_URL`            | Supabase project URL           |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`| Supabase anon key              |
| `NEXT_PUBLIC_API_URL`                 | FastAPI backend URL            |
| `NEXT_PUBLIC_WEBCAM_INTERVAL_MS`      | Webcam capture interval (ms)   |

---

## 11. Running the Project

### Terminal 1 — Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Run backend tests

```bash
cd backend
pytest tests/ -v
```

### Run ML tests

```bash
cd smartwaste
python -m pytest ml/tests/ -v
```

---

## 12. API Documentation

When the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint              | Description                          |
|--------|-----------------------|--------------------------------------|
| GET    | `/health`             | Health check, model & hardware status |
| GET    | `/api/model/info`     | Model version, classes, thresholds   |
| POST   | `/api/predict`        | Classify an uploaded image file      |
| POST   | `/api/predict/webcam` | Classify a base64 webcam frame       |
| POST   | `/api/hardware/sort`  | Send a sorting command to hardware   |
| GET    | `/api/categories`     | All waste category definitions       |

### Prediction Response

```json
{
  "category": "plastic",
  "display_name": "Plastic",
  "confidence": 0.942,
  "is_uncertain": false,
  "recommendation": "Clean and rinse plastic items before recycling...",
  "hardware_command": "SORT_PLASTIC",
  "model_version": "efficientnetb0-v1"
}
```

### Uncertain Prediction Response

```json
{
  "category": "unknown",
  "display_name": "Unknown",
  "confidence": 0.38,
  "is_uncertain": true,
  "message": "The system is not sufficiently confident. Please verify manually.",
  "hardware_command": "MANUAL_REVIEW",
  "model_version": "efficientnetb0-v1"
}
```

---

## 13. Hardware Simulation

The current implementation uses `SimulationSortingDevice`, which logs sorting commands visually without any physical connection. This is controlled by:

```env
HARDWARE_MODE=simulation
```

When a prediction triggers a sort:

```
🔵 [BIN 1 - PLASTIC]   → Opening gate A
⚫ [BIN 2 - METAL]     → Activating magnet conveyor
🟢 [BIN 3 - GLASS]     → Lowering soft-drop chute
🟡 [BIN 4 - PAPER]     → Activating paper belt
⚠️  [MANUAL REVIEW]     → Flagging for human inspection
```

---

## 14. Future Hardware Integration

To add a new hardware device:

1. Create `backend/app/hardware/raspberry_pi.py`
2. Implement `SortingDevice`:
   ```python
   from .base import SortingDevice
   class RaspberryPiSortingDevice(SortingDevice):
       def sort(self, command: str): ...
       def get_mode(self): return "raspberry_pi"
       def is_available(self): ...
   ```
3. Register it in `controller.py`:
   ```python
   SUPPORTED_MODES = {
       "simulation": SimulationSortingDevice,
       "raspberry_pi": RaspberryPiSortingDevice,
   }
   ```
4. Set `HARDWARE_MODE=raspberry_pi` in `.env`.

**No changes to ML, classification, or API logic are required.**

### Edge Deployment (Raspberry Pi)

```
Keras model (.keras)
        ↓
TFLite Converter
        ↓
waste_classifier.tflite
        ↓
Raspberry Pi (tflite-runtime)
        ↓
InferenceService → RaspberryPiSortingDevice
```

---

## 15. Troubleshooting

| Issue | Solution |
|-------|----------|
| `503 Model not available` | Run `python ml/train.py` first |
| `Camera permission denied` | Allow camera in browser settings |
| Supabase auth errors | Check `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` is the **anon** key, not service role |
| CORS error from frontend | Add your frontend URL to `CORS_ORIGINS` in backend `.env` |
| `datasets` package missing | `pip install datasets` |
| Training OOM on CPU | Reduce `batch_size` in `ml/config.yaml` to 16 or 8 |
| Predictions not saving | Confirm `SUPABASE_SERVICE_ROLE_KEY` is set correctly in backend `.env` |
