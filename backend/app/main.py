from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from .agent.graph import complaint_graph
from .config import get_settings
from .database import Base, engine, get_db
from .models import Complaint
from .schemas import ComplaintCreate, ComplaintData, ComplaintResponse, CopilotRequest, CopilotResponse
from .services.document_parser import extract_document_text


settings = get_settings()
app = FastAPI(title="AIVOA Complaint Copilot API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_mode": "groq" if settings.groq_api_key else "demo"}


def run_copilot(message: str, current_data: dict | None = None) -> CopilotResponse:
    try:
        result = complaint_graph.invoke({"message": message, "current_data": current_data or {}})
        return CopilotResponse(
            extracted_data=ComplaintData(**result["complaint_data"]),
            missing_fields=result["missing_fields"],
            follow_up_question=result.get("follow_up_question"),
            assistant_message=result["assistant_message"],
            mode=result.get("mode", "groq"),
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Complaint analysis failed: {exc}") from exc


@app.post("/api/copilot/process", response_model=CopilotResponse)
def process_complaint(request: CopilotRequest):
    current = request.current_data.model_dump() if request.current_data else {}
    return run_copilot(request.message, current)


@app.post("/api/copilot/upload", response_model=CopilotResponse)
async def upload_complaint(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File must be smaller than 10 MB.")
    try:
        text = extract_document_text(file.filename or "upload", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if len(text) < 2:
        raise HTTPException(status_code=400, detail="No readable complaint text was found.")
    return run_copilot(text)


@app.post("/api/complaints", response_model=ComplaintResponse, status_code=201)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    complaint = Complaint(**payload.model_dump())
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@app.get("/api/complaints", response_model=list[ComplaintResponse])
def list_complaints(db: Session = Depends(get_db)):
    return db.scalars(select(Complaint).order_by(Complaint.created_at.desc())).all()


@app.get("/api/complaints/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

