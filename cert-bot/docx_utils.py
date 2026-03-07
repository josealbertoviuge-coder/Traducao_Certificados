from pdf2docx import Converter
from docx import Document
from translator import traduzir


# =========================
# PDF → DOCX
# =========================
def pdf_para_docx(pdf_path, docx_path):

    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()


# =========================
# COPIAR PARÁGRAFOS
# =========================
def copiar_paragrafos(origem, destino):

    for p in origem.paragraphs:
        destino.add_paragraph(p.text)


# =========================
# COPIAR TABELAS
# =========================
def copiar_tabelas(origem, destino):

    for table in origem.tables:

        nova = destino.add_table(
            rows=len(table.rows),
            cols=len(table.columns)
        )

        for i, row in enumerate(table.rows):
            for j, cell in enumerate(row.cells):
                nova.rows[i].cells[j].text = cell.text


# =========================
# TRADUZIR DOCX
# =========================
def traduzir_docx(docx_entrada, docx_saida):

    original = Document(docx_entrada)

    novo = Document()

    # -------------------------
    # PÁGINAS ORIGINAIS
    # -------------------------
    copiar_paragrafos(original, novo)
    copiar_tabelas(original, novo)

    # quebra de página
    novo.add_page_break()

    novo.add_paragraph("ENGLISH TRANSLATION")
    novo.add_page_break()

    # -------------------------
    # PÁGINAS TRADUZIDAS
    # -------------------------
    for p in original.paragraphs:

        if p.text.strip():
            texto = traduzir(p.text)
        else:
            texto = ""

        novo.add_paragraph(texto)

    for table in original.tables:

        nova = novo.add_table(
            rows=len(table.rows),
            cols=len(table.columns)
        )

        for i, row in enumerate(table.rows):
            for j, cell in enumerate(row.cells):

                if cell.text.strip():
                    nova.rows[i].cells[j].text = traduzir(cell.text)
                else:
                    nova.rows[i].cells[j].text = ""

    novo.save(docx_saida)
