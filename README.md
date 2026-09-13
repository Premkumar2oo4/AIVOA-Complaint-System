# AIVOA Complaint Copilot

An AI-powered pharmaceutical complaint intake and risk-triage application. AIVOA converts unstructured customer complaints into structured QMS records, asks targeted follow-up questions for missing information, recommends an initial risk level, and stores reviewed complaints in PostgreSQL.

## Live Application

- **Frontend:** [aivoa-complaint-system-three.vercel.app](https://aivoa-complaint-system-three.vercel.app)
- **API documentation:** [aivoa-backend-xas2.onrender.com/docs](https://aivoa-backend-xas2.onrender.com/docs)
- **API health check:** [aivoa-backend-xas2.onrender.com/api/health](https://aivoa-backend-xas2.onrender.com/api/health)

> The backend uses Render's free service tier and may need a short time to wake up after inactivity.

## Project Overview

Pharmaceutical complaint intake often requires staff to manually read free-form reports, locate important product and batch information, request missing details, and transfer the final record into a quality-management system. AIVOA streamlines that workflow with an AI copilot while keeping the user in control of the final submission.

### Key Features

- Accepts typed complaints and uploaded documents.
- Extracts customer, product, batch, facility, material, defect, and risk details.
- Highlights incomplete fields in the complaint form.
- Asks conversational follow-up questions for missing information.
- Produces a concise complaint description and preliminary risk assessment.
- Allows human review before committing a complaint.
- Persists approved records in PostgreSQL.
- Exposes REST endpoints for listing and retrieving complaints.

## How It Works

1. The user types a complaint or uploads a document.
2. The React frontend sends the content to the FastAPI backend.
3. LangGraph coordinates extraction, validation, missing-field detection, and risk triage.
4. Groq-hosted AI returns structured complaint information.
5. The interface fills known fields and requests missing details.
6. The user reviews the record and commits it to the QMS ledger.
7. SQLAlchemy saves the approved complaint in PostgreSQL.

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 19, Vite, Redux Toolkit, Axios, Lucide React |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| AI workflow | LangGraph, Groq API |
| Database | PostgreSQL, SQLAlchemy, Psycopg |
| File processing | PDF, TXT, EML and optional image OCR |
| Deployment | Vercel, Render |
| Testing | Pytest |

## Project Structure

```text
AIVOA-Complaint-System/
├── backend/
│   ├── app/
│   │   ├── agent/              # LangGraph complaint workflow
│   │   ├── services/           # Document parsing services
│   │   ├── config.py           # Environment configuration
│   │   ├── database.py         # SQLAlchemy connection
│   │   ├── main.py             # FastAPI routes
│   │   ├── models.py           # Database models
│   │   └── schemas.py          # Request and response schemas
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── store/              # Redux state and API actions
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── .env.example
│   └── package.json
├── sample-complaints/
├── docker-compose.yml
└── README.md
```

## Local Setup

### Prerequisites

- Git
- Node.js 20 or newer
- Python 3.11, 3.12, or 3.13
- Docker Desktop
- A Groq API key for live AI processing

Python 3.14 may not be compatible with all pinned binary packages. Python 3.11 or 3.12 is recommended.

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd AIVOA-Complaint-System
```

### 2. Start PostgreSQL

Start Docker Desktop and run:

```bash
docker compose up -d
```

The development database will be available on port `5432`.

### 3. Configure and run the backend

#### Windows PowerShell

```powershell
cd backend
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `backend/.env` and configure:

```env
DATABASE_URL=postgresql+psycopg://aivoa:aivoa_password@localhost:5432/aivoa_complaints
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
FRONTEND_URL=http://localhost:5173
```

Then start the API:

```powershell
python -m uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs).

> Never commit the `.env` file or expose API keys and database passwords.

### 4. Configure and run the frontend

Open a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

The frontend environment file should contain:

```env
VITE_API_URL=http://localhost:8000/api
```

Open [http://localhost:5173](http://localhost:5173).

## Testing the Application

1. Paste a complaint into the AIVOA Copilot chat box or upload a supported file.
2. Confirm that recognized information appears in the form.
3. Answer any follow-up questions requested by the copilot.
4. Review the populated fields and initial risk assessment.
5. Click **Commit to QMS Ledger**.
6. Confirm that a success message and complaint ID appear.
7. Open [http://localhost:8000/api/complaints](http://localhost:8000/api/complaints) to inspect saved records.

Example complaint:

```text
The product arrived damaged and customer support has not responded for five
days. I need a replacement urgently.
```

### Run backend tests

From the `backend` directory with the virtual environment activated:

```bash
pytest
```

## API Reference

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Check API and AI mode |
| POST | `/api/copilot/process` | Analyze complaint text or follow-up details |
| POST | `/api/copilot/upload` | Analyze an uploaded complaint file |
| POST | `/api/complaints` | Save a reviewed complaint |
| GET | `/api/complaints` | List saved complaints |
| GET | `/api/complaints/{complaint_id}` | Retrieve one complaint |

Interactive OpenAPI documentation is available at `/docs`.

## Supported Uploads

- PDF
- TXT
- EML
- PNG
- JPG/JPEG

Uploaded files must be smaller than 10 MB. Image extraction requires the Tesseract OCR application to be installed and available in the system `PATH`.

## Deployment Configuration

### Render backend

| Setting | Value |
| --- | --- |
| Root directory | `backend` |
| Build command | `pip install -r requirements.txt` |
| Start command | `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

Required Render environment variables:

```env
DATABASE_URL=postgresql+psycopg://...
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
FRONTEND_URL=https://your-frontend.vercel.app
```

When using Render PostgreSQL, copy its **Internal Database URL** and change only the protocol from `postgresql://` to `postgresql+psycopg://`.

### Vercel frontend

Set the project root directory to `frontend` and add:

```env
VITE_API_URL=https://your-backend.onrender.com/api
```

Redeploy the frontend after changing a Vite environment variable because it is embedded during the build.

## Troubleshooting

### Database connection timeout

For local development, confirm Docker Desktop and PostgreSQL are running:

```bash
docker compose ps
docker compose up -d
```

For Render, use the database's Internal Database URL when the backend and database are hosted in the same region.

### Groq model not found

Groq model availability can change. List the models available to your API key and update `GROQ_MODEL`. This deployment currently uses:

```env
GROQ_MODEL=openai/gpt-oss-20b
```

### Frontend receives `{"detail":"Not Found"}`

Ensure the frontend URL ends with `/api`:

```env
VITE_API_URL=https://your-backend.onrender.com/api
```

### CORS error

Set the backend's `FRONTEND_URL` to the exact deployed frontend origin without a trailing slash:

```env
FRONTEND_URL=https://your-frontend.vercel.app
```

## Security Notes

- Keep `GROQ_API_KEY`, database passwords, and connection URLs outside source control.
- Validate uploaded file types and enforce the existing 10 MB size limit.
- Treat AI-generated extraction and risk recommendations as decision support.
- Require human review before committing regulated QMS records.

## Future Improvements

- Authentication and role-based access control.
- Audit trails and electronic signatures.
- Complaint status dashboards and advanced filtering.
- Notifications and escalation workflows.
- Cloud file storage and malware scanning.
- Automated integration and end-to-end tests.
- Export to PDF, CSV, or an external enterprise QMS.

## Author

**Premkumar Bhadagave**  
B.Tech in Artificial Intelligence and Data Science  
Full-Stack Developer

## License

This project was created as an internship assignment and portfolio demonstration. Add an appropriate open-source license before redistributing it.
