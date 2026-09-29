"""
DocumentParser — extract plain text from uploaded files.

Supported: .pdf, .docx, .xlsx, .txt, .md, .json
"""
from __future__ import annotations

from pathlib import Path


class DocumentParser:
    def parse(self, path: str | Path) -> str:
        """Return extracted plain text from the file at `path`."""
        p = Path(path)
        suffix = p.suffix.lower()

        if suffix == ".pdf":
            return self._parse_pdf(p)
        if suffix in (".docx", ".doc"):
            return self._parse_docx(p)
        if suffix in (".xlsx", ".xls"):
            return self._parse_xlsx(p)
        if suffix in (".txt", ".md", ".json", ".csv"):
            return p.read_text(encoding="utf-8", errors="replace")
        raise ValueError(f"Unsupported file type: {suffix}")

    # ------------------------------------------------------------------ #

    def _parse_pdf(self, path: Path) -> str:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages)
        except ImportError:
            raise ImportError("pypdf is required for PDF parsing: pip install pypdf")

    def _parse_docx(self, path: Path) -> str:
        try:
            from docx import Document

            doc = Document(str(path))
            return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        except ImportError:
            raise ImportError("python-docx is required: pip install python-docx")

    def _parse_xlsx(self, path: Path) -> str:
        try:
            import openpyxl

            wb = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
            lines = []
            for sheet in wb.sheetnames:
                ws = wb[sheet]
                lines.append(f"## Sheet: {sheet}")
                for row in ws.iter_rows(values_only=True):
                    row_str = "\t".join("" if v is None else str(v) for v in row)
                    if row_str.strip():
                        lines.append(row_str)
            return "\n".join(lines)
        except ImportError:
            raise ImportError("openpyxl is required: pip install openpyxl")
