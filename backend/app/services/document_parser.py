from io import BytesIO
from pathlib import Path
from PIL import Image
from pypdf import PdfReader


def extract_document_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if suffix in {".png", ".jpg", ".jpeg"}:
        try:
            import pytesseract
            return pytesseract.image_to_string(Image.open(BytesIO(content))).strip()
        except Exception as exc:
            raise ValueError("Image OCR requires Tesseract OCR to be installed on the computer.") from exc
    if suffix in {".txt", ".eml"}:
        return content.decode("utf-8", errors="ignore").strip()
    raise ValueError("Supported files are PDF, TXT, EML, PNG, JPG, and JPEG.")

