# Book PDF Chapter Splitter & Summarizer

## Features
- Upload a PDF book
- Split into chapters
- Extract and highlight important points
- Summarize each chapter
- Output a PDF per chapter with highlights and summary

## Requirements
- Python 3.8+
- PyPDF2
- pdfplumber
- fpdf
- transformers
- torch

## Setup
1. Install dependencies:
   pip install -r requirements.txt

2. Run the app:
   python main.py <path_to_pdf>

---

## Notes
- Summarization and note extraction use Hugging Face transformers (local models).
- For large PDFs, processing may take time.
