import base64
import logging
import os
import re
from pathlib import Path

from openai import OpenAI

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

logger = logging.getLogger(__name__)

DEFAULT_OCR_MODEL = "tencent/HunyuanOCR"
DEFAULT_BASE_URL = "http://localhost:8000/v1"
DEFAULT_OCR_PROMPT = "Detect and recognize the text in the picture, format and output the text coordinates."
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}
TEXT_EXTENSIONS = {".txt", ".md"}
PDF_EXTENSIONS = {".pdf"}


class OCRHandler:
    def __init__(
        self,
        model_name: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int = 3600
    ) -> None:
        self.model_name = model_name or os.getenv("OCR_MODEL_NAME", DEFAULT_OCR_MODEL)
        self.base_url = base_url or os.getenv("OCR_BASE_URL", DEFAULT_BASE_URL)
        self.api_key = api_key or os.getenv("OCR_API_KEY", "EMPTY")

        self.client = OpenAI(
            api_key = self.api_key,
            base_url = self.base_url,
            timeout = timeout
        )

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _create_messages(self, image_path: str, prompt: str) -> list[dict]:
        return [
            {"role": "system", "content": ""},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{self._encode_image(image_path)}"
                        }
                    },
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    
    def ocr_image(
        self,
        image_path: str,
        prompt: str | None = None,
        temperature: float = 0.0,
        top_p: float = 0.95,
        seed: int = 1234,
        top_k: int = 1,
        repetition_penalty: float = 1.0
    ) -> str:
        if prompt is None:
            prompt = DEFAULT_OCR_PROMPT

        messages = self._create_messages(image_path, prompt)
        response = self.client.chat.completions.create(
            model = self.model_name,
            messages = messages,
            temperature = temperature,
            top_p = top_p,
            seed = seed,
            stream = False,
            extra_body = {
                "top_k": top_k,
                "repetition_penalty": repetition_penalty
            }
        ),
        text = re.sub(r"\(\d+,\d+\),\(\d+,\d+\)", "\n", response.choices[0].message.content)
        return 

    def _read_text_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            return file.read()

    def _pdf_to_images(self, pdf_path: str, dpi: int = 200) -> list[Path]:
        if fitz is None:
            raise RuntimeError("PyMuPDF (fitz) is not installed")

        doc = fitz.open(pdf_path)
        images: list[Path] = []
        pdf_dir = Path(pdf_path).parent
        stem = Path(pdf_path).stem

        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi)
            img_path = pdf_dir / f"{stem}_page_{i + 1}.png"
            pix.save(img_path.as_posix())
            images.append(img_path)

        return images

    def _read_pdf_text(self, file_path: str, prompt: str | None) -> str:
        # 1) Попробовать вытащить текст обычным способом
        raw_text = ""
        if PdfReader is not None:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    raw_text += page_text + "\n"

        if raw_text.strip():
            return raw_text.strip()

        # 2) Если текст не извлекся — fallback на OCR по страницам
        pages_text: list[str] = []
        for img_path in self._pdf_to_images(file_path):
            page_text = self.ocr_image(str(img_path), prompt=prompt)
            pages_text.append(page_text)

        return "\n\n".join(pages_text)

    def _process_file(self, file_path: str, prompt: str | None) -> dict[str, str | None]:
        path = Path(file_path)
        extension = path.suffix.lower()
        try:
            if extension in TEXT_EXTENSIONS:
                text = self._read_text_file(file_path)
            elif extension in PDF_EXTENSIONS:
                text = self._read_pdf_text(file_path, prompt=prompt)
            elif extension in IMAGE_EXTENSIONS:
                text = self.ocr_image(file_path, prompt=prompt)
            else:
                return {
                    "path": str(path),
                    "filename": path.name,
                    "extension": extension,
                    "text": None,
                    "error": "unsupported_extension"
                }
        except Exception as error:
            logger.exception("Failed to process file %s: %s", file_path, error)
            return {
                "path": str(path),
                "filename": path.name,
                "extension": extension,
                "text": None,
                "error": str(error)
            }

        return {
            "path": str(path),
            "filename": path.name,
            "extension": extension,
            "text": text,
            "error": None
        }

    def process_path(
        self,
        input_path: str,
        prompt: str | None = None,
        recursive: bool = False
    ) -> list[dict[str, str | None]]:
        if os.path.isfile(input_path):
            return [self._process_file(input_path, prompt)]
        
        if not os.path.isdir(input_path):
            raise ValueError(f"{input_path} is not a file or directory")
        
        
        results: list[dict[str, str | None]] = []
        if recursive:
            for root, _, files in os.walk(input_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    results.append(self._process_file(file_path, prompt))
        else:
            for filename in os.listdir(input_path):
                file_path = os.path.join(input_path, filename)
                if os.path.isfile(file_path):
                    results.append(self._process_file(file_path, prompt))
        
        return results