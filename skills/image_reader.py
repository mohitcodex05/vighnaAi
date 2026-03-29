"""
skills/image_reader.py — OCR and image description
Uses pytesseract for OCR, Groq vision-capable model for description
"""

import os
import base64


def extract_text_from_image(image_path: str) -> str:
    """Extract text from image using pytesseract OCR."""
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img).strip()
        return text if text else "[No text found in image]"
    except ImportError:
        return "[OCR] pytesseract or Pillow not installed."
    except Exception as e:
        return f"[OCR] Error: {e}"


def describe_image(image_path: str, question: str, groq_client) -> str:
    """
    Describe an image or answer questions about it.
    Uses base64 encoding + Groq's vision-capable model.
    Falls back to OCR if vision model unavailable.
    """
    try:
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        ext = os.path.splitext(image_path)[1].lower().lstrip(".")
        if ext == "jpg":
            ext = "jpeg"
        mime = f"image/{ext}"

        response = groq_client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{image_data}"}
                        },
                        {
                            "type": "text",
                            "text": question or "Describe this image in detail."
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        # Fall back to OCR
        ocr_text = extract_text_from_image(image_path)
        if ocr_text and not ocr_text.startswith("["):
            return f"OCR extracted text:\n{ocr_text}"
        return f"[Image] Could not analyze image: {e}"

METADATA = {
    "name": "image",
    "description": "Analyze and describe images using Vision AI or OCR.",
    "intents": ["image", "picture", "photo", "describe image", "analyze image", "ocr"]
}

def execute(action: str, args: dict) -> str:
    path = args.get("path", "")
    question = args.get("question", "Describe this image.")
    client = args.get("groq_client")
    if not client: return "Groq client required for image analysis."
    
    return describe_image(path, question, client)
