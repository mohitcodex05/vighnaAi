"""
skills/pdf_reader.py — Read PDFs, chunk text, answer questions via Groq
"""

import os
import textwrap


def extract_text(pdf_path: str) -> str:
    """Extract all text from a PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n\n".join(pages)
    except ImportError:
        return "[PDF] PyMuPDF not installed. Run: pip install PyMuPDF"
    except Exception as e:
        return f"[PDF] Error reading file: {e}"


def chunk_text(text: str, chunk_size: int = 3000) -> list[str]:
    """Split text into chunks for LLM context windows."""
    words = text.split()
    chunks = []
    current = []
    count = 0
    for word in words:
        current.append(word)
        count += len(word) + 1
        if count >= chunk_size:
            chunks.append(" ".join(current))
            current = []
            count = 0
    if current:
        chunks.append(" ".join(current))
    return chunks


def answer_pdf_question(pdf_path: str, question: str, groq_client) -> str:
    """Read PDF and answer a question using Groq AI."""
    text = extract_text(pdf_path)
    if text.startswith("[PDF]"):
        return text  # error

    chunks = chunk_text(text)
    # Use first 2 chunks as context (fits in LLM window)
    context = "\n\n".join(chunks[:2])

    prompt = (
        f"You are analyzing a PDF document. Based on the following content, "
        f"answer the user's question clearly and accurately.\n\n"
        f"DOCUMENT CONTENT:\n{context}\n\n"
        f"QUESTION: {question}"
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful document analysis assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[PDF] AI error: {e}"


def get_pdf_summary(pdf_path: str, groq_client) -> str:
    """Get a short summary of the PDF."""
    return answer_pdf_question(pdf_path, "Give me a concise summary of this document.", groq_client)

METADATA = {
    "name": "pdf",
    "description": "Read and analyze PDF documents.",
    "intents": ["pdf", "read pdf", "analyze pdf", "summarize pdf"]
}

def execute(action: str, args: dict) -> str:
    path = args.get("path", "")
    question = args.get("question", "What is this document about?")
    client = args.get("groq_client")
    if not client: return "Groq client required for PDF analysis."
    
    if action == "summary": return get_pdf_summary(path, client)
    return answer_pdf_question(path, question, client)
