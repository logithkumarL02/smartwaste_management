# SmartWaste --- Setup Guide

## Requirements

-   Windows 10/11
-   Python 3.11.x
-   Node.js 22.x
-   npm
-   Internet connection
-   Supabase credentials

Check versions:

``` powershell
python --version
node --version
npm --version
```

## Project Structure

``` text
smartwaste/
├── backend/
│   ├── app/
│   ├── model/
│   │   ├── waste_classifier.keras
│   │   ├── metadata.json
│   │   └── class_mapping.json
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.js
│   └── .env.example
└── README.md
```

## Backend Setup

Open PowerShell:
3.11 version recommended
``` powershell
cd smartwaste\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Configure `backend\.env`:

``` env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY
STORAGE_BUCKET=YOUR_STORAGE_BUCKET
```

Do not share the real `.env` file or the service-role key.

### Verify the Model

These files must exist:

``` text
backend\model\waste_classifier.keras
backend\model\metadata.json
backend\model\class_mapping.json
```

The trained model is already included. **Do not run model training just
to start the application.**

### Start Backend

``` powershell
uvicorn app.main:app --reload --port 8000
```

Backend:

``` text
http://127.0.0.1:8000
```

Keep this terminal running.

## Frontend Setup

Open a second PowerShell window:

``` powershell
cd smartwaste\frontend
npm install
copy .env.example .env.local
```

Configure `frontend\.env.local`:

``` env
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
```

**Important:** Do not add `/rest/v1/` to the Supabase URL.

Correct:

``` text
https://YOUR_PROJECT.supabase.co
```

Incorrect:

``` text
https://YOUR_PROJECT.supabase.co/rest/v1/
```

Start the frontend:

``` powershell
npm run dev
```

Open:

``` text
http://localhost:3000
```

## Running the Application

Two terminals must remain running.

### Terminal 1 --- Backend

``` powershell
cd smartwaste\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 --- Frontend

``` powershell
cd smartwaste\frontend
npm run dev
```

Then open:

``` text
http://localhost:3000
```

## Application Workflow

1.  Open `http://localhost:3000`.
2.  Register or log in.
3.  Go to **Classify**.
4.  Upload an image or use the webcam.
5.  View the prediction and confidence.
6.  Check **History** for previous predictions.
7.  Check **Dashboard** for prediction statistics.

## Supabase

Supabase is used for:

-   Authentication
-   User profiles
-   Prediction history
-   Dashboard prediction data

Backend:

``` env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY
```

Frontend:

``` env
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
```

Keep the service-role key private.

## Model Information

``` text
Architecture: EfficientNetB0
Input size: 224 × 224
Classes: 5
```

Classes:

``` text
glass
metal
other
paper_cardboard
plastic
```

Model file:

``` text
backend/model/waste_classifier.keras
```

No dataset download or model training is required for normal application
execution.

## Files NOT to Share

Do not include:

``` text
backend/venv/
frontend/node_modules/
frontend/.next/
backend/.env
frontend/.env.local
```

Instead, include:

``` text
backend/.env.example
frontend/.env.example
```

## Recommended .gitignore

``` gitignore
# Python
venv/
__pycache__/
*.pyc

# Environment variables
.env
.env.local
.env.*.local

# Node.js
node_modules/
.next/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

## Troubleshooting

### Backend does not start

Check:

``` powershell
python --version
```

Use Python 3.11.x.

Activate the environment:

``` powershell
.\venv\Scripts\Activate.ps1
```

Reinstall dependencies if necessary:

``` powershell
pip install -r requirements.txt
```

### Frontend does not start

``` powershell
npm install
npm run dev
```

### Model not found

Verify:

``` text
backend\model\waste_classifier.keras
```

### History does not update

Check the backend terminal. Successful authentication and prediction
saving should show requests similar to:

``` text
GET .../auth/v1/user "200 OK"
POST .../rest/v1/predictions "201 Created"
```

### Prediction shows Unknown

The classifier returns `Unknown` when the highest model probability is
below its uncertainty threshold.

The current model is an image classifier, not an object detector. Images
that are very different from the training data, contain many overlapping
objects, or have substantially different visual conditions may produce
lower-confidence predictions.

## Quick Start

### Terminal 1

``` powershell
cd smartwaste\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Configure `backend\.env`, then:

``` powershell
uvicorn app.main:app --reload --port 8000
```

### Terminal 2

``` powershell
cd smartwaste\frontend
npm install
copy .env.example .env.local
```

Configure `frontend\.env.local`, then:

``` powershell
npm run dev
```

Open:

``` text
http://localhost:3000
```

## Security

Never share publicly:

``` text
SUPABASE_SERVICE_ROLE_KEY
```

Do not commit:

``` text
backend/.env
frontend/.env.local
```

## Architecture

``` text
                 ┌─────────────────────┐
                 │      Next.js         │
                 │      Frontend        │
                 │   localhost:3000     │
                 └──────────┬──────────┘
                            │
                            │ HTTP
                            ▼
                 ┌─────────────────────┐
                 │       FastAPI       │
                 │       Backend       │
                 │   localhost:8000    │
                 └──────────┬──────────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
                  ▼                   ▼
        ┌──────────────────┐   ┌──────────────────┐
        │ EfficientNetB0   │   │    Supabase      │
        │ Waste Classifier │   │ Auth + Database  │
        └──────────────────┘   └──────────────────┘
```

## Final Checklist

-   [ ] Model files are present
-   [ ] `requirements.txt` is present
-   [ ] `package.json` and `package-lock.json` are present
-   [ ] `.env.example` files are present
-   [ ] Actual `.env` files are excluded
-   [ ] `venv` is excluded
-   [ ] `node_modules` is excluded
-   [ ] `.next` is excluded
-   [ ] Supabase configuration is available to the team
-   [ ] Backend starts successfully
-   [ ] Frontend starts successfully
-   [ ] Login works
-   [ ] Image classification works
-   [ ] History updates
-   [ ] Dashboard updates
