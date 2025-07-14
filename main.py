import sys
import os
import pdfplumber
from PyPDF2 import PdfWriter
from fpdf import FPDF
from transformers import pipeline

# --- CONFIG ---
SUMMARY_MODEL = "sshleifer/distilbart-cnn-12-6"  # You can change to another summarization model

# --- FUNCTIONS ---
def extract_chapters(pdf_path):
    """Extracts chapters from the PDF based on headings (simple heuristic)."""
    chapters = []
    with pdfplumber.open(pdf_path) as pdf:
        current_chapter = {'title': 'Introduction', 'pages': []}
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            # Simple heuristic: Chapter headings start with 'Chapter' or 'CHAPTER'
            if text.strip().lower().startswith('chapter'):
                if current_chapter['pages']:
                    chapters.append(current_chapter)
                current_chapter = {'title': text.split('\n')[0], 'pages': [i]}
            else:
                current_chapter['pages'].append(i)
        if current_chapter['pages']:
            chapters.append(current_chapter)
    return chapters

def extract_text_from_pages(pdf_path, page_numbers):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i in page_numbers:
            text += pdf.pages[i].extract_text() or ""
            text += "\n"
    return text

def summarize_text(text, summarizer):
    # Hugging Face pipeline expects <=1024 tokens, so chunk if needed
    max_chunk = 1000
    sentences = text.split('. ')
    current_chunk = ''
    chunks = []
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk:
            current_chunk += sentence + '. '
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + '. '
    if current_chunk:
        chunks.append(current_chunk)
    summary = ''
    for chunk in chunks:
        summary += summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text'] + '\n'
    return summary

def highlight_important_points(text, summarizer):
    # For demo: Use summarizer to extract key points (could use a keyword extractor instead)
    summary = summarizer(text, max_length=60, min_length=10, do_sample=False)[0]['summary_text']
    return summary

def create_chapter_pdf(chapter_title, chapter_text, highlights, summary, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"{chapter_title}\n\n", align='L')
    pdf.set_text_color(0, 0, 255)
    pdf.multi_cell(0, 10, f"Highlights: {highlights}\n\n", align='L')
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 10, chapter_text, align='L')
    pdf.set_text_color(255, 0, 0)
    pdf.multi_cell(0, 10, f"\nSummary: {summary}", align='L')
    pdf.output(output_path)

def main(pdf_path):
    print(f"Processing: {pdf_path}")
    chapters = extract_chapters(pdf_path)
    print(f"Found {len(chapters)} chapters.")
    summarizer = pipeline("summarization", model=SUMMARY_MODEL)
    out_dir = os.path.splitext(pdf_path)[0] + "_chapters"
    os.makedirs(out_dir, exist_ok=True)
    for idx, chapter in enumerate(chapters):
        print(f"Processing {chapter['title']}...")
        chapter_text = extract_text_from_pages(pdf_path, chapter['pages'])
        highlights = highlight_important_points(chapter_text, summarizer)
        summary = summarize_text(chapter_text, summarizer)
        output_path = os.path.join(out_dir, f"chapter_{idx+1}.pdf")
        create_chapter_pdf(chapter['title'], chapter_text, highlights, summary, output_path)
        print(f"Saved: {output_path}")
    print("Done!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_pdf>")
        sys.exit(1)
    main(sys.argv[1])
