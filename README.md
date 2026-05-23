# AI Dataset Cleaner

AI Dataset Cleaner is a Streamlit and FastAPI application that helps users upload CSV datasets, analyze data quality, generate visualizations, clean datasets, receive ML algorithm recommendations, and view AI-generated explanations.

The frontend is designed as a guided workflow: users login or register first, upload a CSV file, and the application automatically runs analysis, visualization, cleaning, recommendation, and explanation steps.

## Features

- Login and registration with JWT authentication
- CSV upload with dataset metadata stored in the database
- Dataset analysis for rows, columns, missing values, duplicates, data types, correlations, unique values, and task detection
- Automatic visualization data for histograms, missing-value summaries, categorical distributions, and correlation matrices
- Dataset cleaning with missing-value handling, duplicate removal, categorical encoding, numeric scaling, and outlier handling
- ML recommendation engine for classification, regression, clustering, NLP, and unknown datasets
- Gemini-powered AI explanation with a local fallback when Gemini is unavailable
- Cleaned dataset download as CSV
- SQLite development database by default, with PostgreSQL support through `DATABASE_URL`

## User Workflow

```text
User opens Streamlit frontend
        |
        v
Login or Register
        |
        v
Upload CSV dataset
        |
        v
Backend stores raw file in uploads/raw/
        |
        v
Automatic processing pipeline:
  1. Analyze dataset
  2. Generate visualization payload
  3. Clean dataset
  4. Recommend ML algorithms
  5. Generate AI explanation
        |
        v
Frontend displays:
  - Dataset summary
  - Visualizations
  - Recommendations
  - Brief reasoning
  - Download button for cleaned CSV
```

## Architecture

```text
Streamlit Frontend
        |
        | HTTP API calls
        v
FastAPI Backend
        |
        |-- Authentication
        |-- File Upload
        |-- Dataset Analysis
        |-- Visualization
        |-- Cleaning Engine
        |-- ML Recommendation
        |-- AI Explanation
        |-- Cleaned File Download
        |
        v
Database + Local File Storage
```

## Project Structure

```text
backend/
  ai/
    dataset_chat.py        # AI explanation orchestration
    llm_explainer.py       # Gemini API client
    prompts.py             # Prompt builder for dataset explanation
  auth/
    auth_handler.py        # User authentication logic
    dependencies.py        # JWT current-user dependency
    hashing.py             # Password hashing helpers
    jwt_handler.py         # JWT encode/decode helpers
  config/
    settings.py            # Environment and database settings
  database/
    crud.py                # Database CRUD operations
    db.py                  # SQLAlchemy engine/session
    models.py              # SQLAlchemy models
    schemas.py             # Pydantic schemas
  ml/
    dataset_detector.py    # Dataset task detection
    preprocessing.py       # Cleaning/preprocessing functions
    recommendation_engine.py
  routes/
    ai_routes.py
    analysis_routes.py
    auth_routes.py
    cleaning_routes.py
    dataset_routes.py
    download_routes.py
    ml_routes.py
    upload_routes.py
    users_routes.py
  services/
    cleaning_service.py
    dataset_service.py
    file_service.py
    visualization_service.py
  main.py                  # FastAPI application entry point

frontend/
  streamlit_app.py         # Main guided Streamlit workflow
  pages/                   # Optional legacy/debug pages
  utils/
    api_client.py          # Shared HTTP client helpers
    session.py             # Streamlit session/auth helpers

uploads/raw/               # Uploaded CSV files
cleaned/processed_files/   # Cleaned CSV outputs
```

## Backend API

### Authentication

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/auth/signup` | Register a user and return JWT token |
| `POST` | `/auth/login` | Login and return JWT token |
| `GET` | `/auth/me` | Return current authenticated user |

### Dataset and Upload

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/datasets/upload` | Upload CSV file and create dataset metadata |
| `POST` | `/datasets/` | Create dataset metadata |
| `GET` | `/datasets/` | List datasets |
| `GET` | `/datasets/{dataset_id}` | Get dataset metadata |
| `PUT` | `/datasets/{dataset_id}` | Update dataset metadata |
| `DELETE` | `/datasets/{dataset_id}` | Delete dataset metadata |

### Analysis and Visualization

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/analysis/run` | Analyze CSV dataset |
| `POST` | `/analysis/visualize` | Generate visualization payload |

### Cleaning and Download

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/cleaning/run` | Clean CSV dataset and save cleaned output |
| `GET` | `/download/cleaned?file_path=...` | Download cleaned CSV by path or filename |
| `GET` | `/download/cleaned/{filename}` | Download cleaned CSV by filename |

### ML and AI

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/ml/recommend` | Recommend ML algorithms |
| `POST` | `/ai/explain` | Generate AI dataset explanation |

## Processing Pipeline

After a user uploads a CSV file, `frontend/streamlit_app.py` automatically calls these backend endpoints:

```text
POST /datasets/upload
POST /analysis/run
POST /analysis/visualize
POST /cleaning/run
POST /ml/recommend
POST /ai/explain
GET  /download/cleaned
```

The cleaned dataset is written to:

```text
cleaned/processed_files/
```

Uploaded raw datasets are written to:

```text
uploads/raw/
```

## Dataset Analysis

The analysis service returns:

- Dataset shape
- Column names
- Missing values per column
- Null percentage per column
- Duplicate row count
- Data types
- Unique value counts
- Numeric correlation matrix
- Detected task type

Task detection is heuristic-based and can classify datasets as:

- `classification`
- `regression`
- `clustering`
- `nlp`
- `unknown`

## Visualization

The visualization service returns JSON-friendly chart data:

- Histograms for numeric columns
- Missing-value summary data
- Pie chart data for categorical columns
- Correlation matrix for numeric columns

Streamlit renders this payload with native Streamlit chart components.

## Cleaning Engine

Default cleaning operations:

```text
fill_missing_values
duplicate_removal
encoding
scaling
outlier_handling
```

The cleaning service returns:

- Cleaned file path
- Rows before and after cleaning
- Columns before and after cleaning
- Operations selected
- Step-by-step cleaning report

## AI Explanation

The AI workflow lives in `backend/ai/`:

```text
Analysis results collected
        |
        v
Prompt generated
        |
        v
Gemini API called
        |
        v
AI explanation returned:
  - cleaning reasoning
  - model recommendation reasoning
  - dataset insights
```

Gemini is optional at runtime. If `GEMINI_API_KEY` is missing, invalid, or the API cannot be reached, the backend returns a local fallback explanation instead of failing the full workflow.

## Environment Variables

Create a `.env` file in the project root for local configuration:

```env
DATABASE_URL=sqlite:///backend/dev.db
JWT_SECRET_KEY=replace-this-with-a-secure-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash
```

Notes:

- `DATABASE_URL` is optional. If it is not set, the app falls back to SQLite at `backend/dev.db`.
- PostgreSQL is supported by setting `DATABASE_URL` to a PostgreSQL connection string.
- `GEMINI_API_KEY` is optional. Without it, AI explanation uses the local fallback.

Example PostgreSQL URL:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/ai_dataset_cleaner
```

## Installation

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## Running The App

Start the FastAPI backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Start the Streamlit frontend:

```powershell
.\.venv\Scripts\streamlit.exe run frontend\streamlit_app.py
```

Open the frontend:

```text
http://localhost:8501
```

Open the backend API docs:

```text
http://127.0.0.1:8000/docs
```

## Typical Usage

1. Open the Streamlit app.
2. Register a new account or login.
3. Upload a CSV file.
4. Click `Upload And Process`.
5. Review the dataset summary, visualizations, recommendations, and brief reasoning.
6. Download the cleaned CSV file.
7. Use `Logout` when finished.

## Data Storage

The project intentionally ignores generated data files in Git:

```text
uploads/raw/
uploads/temp/
cleaned/processed_files/
reports/analysis_reports/
reports/model_reports/
```

This keeps uploaded datasets, cleaned outputs, reports, logs, local databases, and secrets out of version control.

## Security Notes

- Passwords are hashed before storage.
- JWT tokens are used for authenticated frontend requests.
- `.env` files are ignored by Git.
- Cleaned file downloads are restricted to `cleaned/processed_files`.
- Raw Gemini API error bodies are not shown to users.

## Current Limitations

- Model recommendation is implemented, but actual model training is not yet implemented.
- Visualization uses Streamlit-native charts from JSON payloads, not Plotly images.
- Upload requires an authenticated user id, which is stored in Streamlit session state after login.
- The current Streamlit guided flow is in `frontend/streamlit_app.py`; files in `frontend/pages/` remain useful for development/debugging.

## Verification Commands

Compile-check backend and frontend:

```powershell
python -m compileall backend frontend
```

List FastAPI routes:

```powershell
@'
from backend.main import app
for route in app.routes:
    methods = getattr(route, "methods", None)
    if methods:
        print(",".join(sorted(methods)), route.path)
'@ | .\.venv\Scripts\python.exe -
```
