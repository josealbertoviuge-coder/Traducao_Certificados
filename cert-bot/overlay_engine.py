import fitz
from translator import traduzir_pagina


def traduzir_pdf_overlay(pdf_entrada, pdf_saida):

    doc = fitz.open(pdf_entrada)

    for page in doc:

        blocks = page.get_text("blocks")

        print("Blocos encontrados:", len(blocks))

        for block in blocks:

            x0, y0, x1, y1, texto, block_no, block_type = block

            texto = texto.strip()

            if not texto:
                continue

            print("Texto original:", texto[:50])

            try:
                traducao = traduzir_pagina(texto)
                print("Tradução:", traducao[:50])
            except Exception as e:
                print("Erro tradução:", e)
                traducao = texto

            rect = fitz.Rect(x0, y0, x1, y1)

            # apagar texto original
            page.draw_rect(rect, fill=(1, 1, 1))

            # escrever tradução
            page.insert_textbox(
                rect,
                traducao,
                fontsize=8,
                fontname="helv",
                color=(0, 0, 0)
            )

    doc.save(pdf_saida)
