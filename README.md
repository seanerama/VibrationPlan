# VME Compatibility Analyzer

A hosted, browser-based internal tool for US Signal Solutions Architects. Ingests RVTools or CloudPhysics VM inventory exports, classifies each VM against the HPE VM Essentials compatibility matrix, and produces a branded Excel report.

## Overview

SAs upload a VM inventory export and receive a color-coded spreadsheet with:
- Classification of each VM into one of 6 tiers (Officially Supported → Not Supported)
- Classification reason per VM
- Migration path guidance per tier
- Summary and executive summary tabs

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React (Vite) + CSS Custom Properties |
| Backend | Python (FastAPI) |
| Database | Azure SQL (Basic) — SQLite for local dev |
| File Processing | pandas + openpyxl |
| OS Matching | rapidfuzz |
| Hosting | Azure App Service (Linux, B1) |

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- (Optional) `pyodbc` requires ODBC driver for Azure SQL in production

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`
Health check: `http://localhost:8000/health`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI available at `http://localhost:5173`

### Environment Variables

Copy `.env.example` to `.env` in the `backend/` directory and fill in values:

```bash
cp .env.example backend/.env
```

Local dev works with default SQLite — no Azure SQL required.

## Project Structure

```
vme-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app
│   │   ├── config.py           # Settings from env vars
│   │   ├── routers/            # API route handlers
│   │   ├── services/           # Business logic
│   │   └── models/             # SQLAlchemy ORM models
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css           # Design system CSS variables
│   │   ├── pages/
│   │   └── components/
│   └── public/assets/
├── docs/
│   ├── project-state.md        # Living state doc (updated each stage)
│   ├── project-plan.md
│   └── design-system.md
├── .env.example
└── README.md
```

## Running Tests

```bash
cd backend
pytest
```

## Linting

```bash
# Backend
ruff check backend/

# Frontend
cd frontend && npm run lint
```

## Deployment

See `docs/deploy-instruct.md` for Azure App Service deployment instructions.
