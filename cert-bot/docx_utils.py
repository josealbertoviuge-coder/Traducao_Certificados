from pdf2docx import Converter
from docx import Document
from translator import traduzir
import subprocess


# =========================
# PDF → DOCX
# =========================
def pdf_para_docx(pdf_path, docx_path):

    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()


# =========================
# TRADUZIR DOCX
# =========================
def traduzir_docx(docx_entrada, docx_saida):

    doc = Document(docx_entrada)

    # traduz parágrafos
    for p in doc.paragraphs:
        if p.text.strip():
            p.text = traduzir(p.text)

    # traduz tabelas
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    cell.text = traduzir(cell.text)

    doc.save(docx_saida)


# =========================
# DOCX → PDF (LINUX/RENDER)
# =========================
def docx_para_pdf(docx_path):

    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        docx_path
    ])
