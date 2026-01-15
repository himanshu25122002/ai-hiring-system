import pdfplumber
from docx import Document

def parse_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text.strip()


def parse_docx(file_path: str) -> str:
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()


def parse_resume(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        return parse_pdf(file_path)
    elif file_path.endswith(".docx"):
        return parse_docx(file_path)
    else:
        raise ValueError("Unsupported file format")
