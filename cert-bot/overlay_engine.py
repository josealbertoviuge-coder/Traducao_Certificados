import fitz
from translator import traduzir_pagina


def traduzir_pdf_overlay(pdf_entrada, pdf_saida):

    doc = fitz.open(pdf_entrada)

    for page in doc:

        blocks = page.get_text("blocks")

        print("Blocos encontrados:", len(blocks))

        for block in blocks:

            x0, y0, x1, y1, texto, *_ = block

            texto = texto.strip()

            if not texto:
                continue

            try:
                traducao = traduzir_pagina(texto)
            except:
                traducao = texto

            rect = fitz.Rect(x0, y0, x1, y1)

            page.draw_rect(rect, fill=(1, 1, 1))

            page.insert_textbox(
                rect,
                traducao,
                fontsize=8
            )

    doc.save(pdf_saida)
