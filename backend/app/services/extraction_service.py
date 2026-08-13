import fitz  # PyMuPDF
import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("talk_to_your_notes.extraction")


class ExtractedSegment:
    def __init__(
        self,
        content: str,
        page_number: Optional[int] = None,
        section_title: Optional[str] = None,
        parent_section: Optional[str] = None
    ):
        self.content = content.strip()
        self.page_number = page_number
        self.section_title = section_title
        self.parent_section = parent_section

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "page_number": self.page_number,
            "section_title": self.section_title,
            "parent_section": self.parent_section
        }


class ExtractionService:

    @staticmethod
    def extract_document(
        file_bytes: bytes,
        file_name: str,
        mime_type: str
    ) -> List[ExtractedSegment]:
        ext = file_name.lower().split('.')[-1]

        if ext == 'pdf' or mime_type == 'application/pdf':
            return ExtractionService.extract_pdf(file_bytes)
        elif ext in ['md', 'markdown'] or mime_type in ['text/markdown', 'text/x-markdown']:
            return ExtractionService.extract_markdown(file_bytes.decode('utf-8', errors='ignore'))
        elif ext == 'txt' or mime_type.startswith('text/'):
            return ExtractionService.extract_txt(file_bytes.decode('utf-8', errors='ignore'))
        else:
            raise ValueError(f"Unsupported file format for extraction: {file_name} ({mime_type})")

    @staticmethod
    def extract_pdf(file_bytes: bytes) -> List[ExtractedSegment]:
        segments = []
        # Try pypdf (pure Python, lightweight for Vercel) first, fallback to fitz
        try:
            import io
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            current_section = None
            for page_num, page in enumerate(reader.pages):
                page_number = page_num + 1
                text = page.extract_text() or ""
                if not text.strip():
                    continue

                lines = text.split('\n')
                page_text_blocks = []
                for line in lines:
                    clean_line = line.strip()
                    if not clean_line:
                        continue
                    if len(clean_line) < 60 and not clean_line.endswith(('.', ':', ';', ',')) and clean_line[0].isupper():
                        current_section = clean_line
                    page_text_blocks.append(clean_line)

                page_content = "\n".join(page_text_blocks)
                segments.append(
                    ExtractedSegment(
                        content=page_content,
                        page_number=page_number,
                        section_title=current_section,
                        parent_section=None
                    )
                )
            if segments:
                return segments
        except Exception as e:
            logger.info(f"pypdf extraction failed or unavailable, trying fitz: {e}")

        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            current_section = None

            for page_num in range(len(doc)):
                page = doc[page_num]
                page_number = page_num + 1
                text = page.get_text("text")

                if not text.strip():
                    continue

                lines = text.split('\n')
                page_text_blocks = []

                for line in lines:
                    clean_line = line.strip()
                    if not clean_line:
                        continue

                    if len(clean_line) < 60 and not clean_line.endswith(('.', ':', ';', ',')) and clean_line[0].isupper():
                        current_section = clean_line

                    page_text_blocks.append(clean_line)

                page_content = "\n".join(page_text_blocks)
                segments.append(
                    ExtractedSegment(
                        content=page_content,
                        page_number=page_number,
                        section_title=current_section,
                        parent_section=None
                    )
                )

            doc.close()
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")

        return segments

    @staticmethod
    def extract_markdown(text_content: str) -> List[ExtractedSegment]:
        segments = []
        # Split text into header blocks
        header_pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)

        matches = list(header_pattern.finditer(text_content))
        if not matches:
            return ExtractionService.extract_txt(text_content)

        last_h1 = None

        for i, match in enumerate(matches):
            level = len(match.group(1))
            title = match.group(2).strip()

            start_idx = match.end()
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(text_content)

            section_text = text_content[start_idx:end_idx].strip()

            if level == 1:
                last_h1 = title
                parent_section = None
            else:
                parent_section = last_h1

            if section_text:
                segments.append(
                    ExtractedSegment(
                        content=section_text,
                        page_number=1,
                        section_title=title,
                        parent_section=parent_section
                    )
                )

        if not segments:
            segments.append(
                ExtractedSegment(
                    content=text_content.strip(),
                    page_number=1,
                    section_title=None,
                    parent_section=None
                )
            )

        return segments

    @staticmethod
    def extract_txt(text_content: str) -> List[ExtractedSegment]:
        paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
        segments = []
        for p in paragraphs:
            segments.append(
                ExtractedSegment(
                    content=p,
                    page_number=1,
                    section_title=None,
                    parent_section=None
                )
            )
        return segments
