import os
from PyPDF2 import PdfReader


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extracts text from a pdf file.
    Args:
        file_path (str): The path to the pdf file.
    """
    reader = PdfReader(file_path, strict=False)
    text = ''
    for page in reader.pages:
        try:
            page_text = page.extract_text()
        except Exception as exc:
            raise ValueError(f"Could not extract text from the PDF: {exc}") from exc
        if page_text:
            text += page_text + "\n"
    return {'text': text.strip(), 'page_count': str(len(reader.pages)), "word_count": str(len(text.split()))}


def extract_text_from_txt(file_path: str) -> str:
    """
    Extracts text from a TXT file.

    Args:
        file_path (str): The path to the TXT file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text =  f.read()
    return {
        "text": text.strip(),
        "page_count": "1",
        "word_count": str(len(text.split()))
    }

# def extract_text_from_txt(file_path: str):



def extract_text(file_path: str) -> str:
    """
    Extracts text from a document file.

    Args:
        file_path (str): The path to the document file.
    """

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else: 
        raise ValueError("Unsupported file type. Only PDF and TXT files are allowed")