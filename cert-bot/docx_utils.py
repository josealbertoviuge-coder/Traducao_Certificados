from pdf2docx import Converter
from docx import Document
from translator import traduzir_pagina


# =========================
# PDF → DOCX
# =========================
def pdf_para_docx(pdf_path, docx_path):

    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()


# =========================
# CRIAR DOCX POR PÁGINAS
# =========================
def criar_docx_paginas(paginas, saida):

    doc = Document()

    for i, pagina in enumerate(paginas, start=1):

        doc.add_heading(f"PAGE {i} - ORIGINAL", level=1)

        for linha in pagina.split("\n"):
            doc.add_paragraph(linha)

        doc.add_page_break()

        doc.add_heading(f"PAGE {i} - ENGLISH", level=1)

        traducao = traduzir_pagina(pagina)

        for linha in traducao.split("\n"):
            doc.add_paragraph(linha)

        doc.add_page_break()

    doc.save(saida)


# =========================
# DOCX A PARTIR DO OCR
# =========================
def criar_docx_ocr(texto, saida):

    doc = Document()

    doc.add_heading("ENGLISH TRANSLATION", level=1)

    for linha in texto.split("\n"):

        linha = linha.strip()

        if not linha:
            continue

        doc.add_paragraph(linha)

    doc.save(saida)
