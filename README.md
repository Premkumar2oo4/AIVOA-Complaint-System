# AIVOA AI Customer Complaint Management System

A full-stack internship assignment implementation for pharmaceutical QMS complaint intake. The application accepts typed complaints and document uploads, extracts structured fields through a LangGraph workflow, highlights missing details, recommends a risk level and action, and saves reviewed complaints to PostgreSQL.

## Technology

- React 19 and Redux Toolkit
- Python FastAPI
- LangGraph and Groq
- PostgreSQL and SQLAlchemy
- PDF, email, text, and optional image OCR ingestion

## Fastest setup on Windows

### 1. Install prerequisites

Install Node.js 20+, Python 3.11+, Git, Docker Desktop, and VS Code. Start Docker Desktop before continuing.

### 2. Start PostgreSQL

Open the project folder in VS Code, open Terminal, and run:

```bash
docker compose up -d
```

### 3. Start the backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Keep this terminal open. Verify the API at http://localhost:8000/docs.

The project works in local demo mode when `GROQ_API_KEY` is blank. To use real AI, create a key at https://console.groq.com/keys, open `backend/.env`, and set:

```env
GROQ_API_KEY=your_real_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Never upload the `.env` file or API key to GitHub.

### 4. Start the frontend

Open a second VS Code terminal:

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open http://localhost:5173.

## Check the project

1. Copy text from `sample-complaints/discoloration.txt`.
2. Paste it into AIVOA Copilot and click Send.
3. Confirm fields populate on the left.
4. If the Copilot requests missing information, enter it in the chat.
5. Review the risk assessment.
6. Click **Commit to QMS Ledger**.
7. Confirm a green success message appears.
8. Open http://localhost:8000/api/complaints to see saved database records.

You can also upload either sample TXT file using the attachment button.

## Backend tests

From the `backend` directory with the environment activated:

```bash
pytest
```

## API endpoints

- `GET /api/health` - health and AI mode
- `POST /api/copilot/process` - analyze complaint text or follow-up details
- `POST /api/copilot/upload` - analyze PDF, TXT, EML, PNG, JPG, or JPEG
- `POST /api/complaints` - commit a reviewed complaint
- `GET /api/complaints` - list committed complaints
- `GET /api/complaints/{id}` - retrieve one complaint

## Optional image OCR

PDF and text uploads work after installing Python requirements. Image OCR also requires the Tesseract application. Install Tesseract on Windows and ensure it is available in PATH.

## Troubleshooting

### Database connection error

Check that Docker Desktop is running, then execute:

```bash
docker compose ps
docker compose up -d
```

### Port already in use

Use a different backend port:

```bash
uvicorn app.main:app --reload --port 8001
```

Then change `frontend/.env` to `VITE_API_URL=http://localhost:8001/api` and restart Vite.

### Groq model error

Model availability can change. Set `GROQ_MODEL` in `backend/.env` to a currently available Groq chat model. The assignment mentions `gemma2-9b-it`, but the included default uses `llama-3.3-70b-versatile` as its permitted alternative.

## Submission demonstration

Record one product video showing typed input, upload, automatic form population, follow-up questions, risk assessment, and database commit. Record a second video explaining Redux, FastAPI routes, LangGraph nodes, Groq extraction, document parsing, and PostgreSQL persistence.
