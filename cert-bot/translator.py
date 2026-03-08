from openai import OpenAI

client = OpenAI()


def traduzir_pagina(texto):

    if not texto.strip():
        return ""

    prompt = f"""
Translate this MATERIAL CERTIFICATE page to English.

RULES:

- Preserve ALL numbers
- Preserve ALL units (MPa, %, mm, °C)
- Preserve ALL standards (ASTM, EN, DIN, ISO)
- Preserve chemical symbols (C, Mn, Si, Cr, Ni)
- Preserve table structure
- Do not summarize
- Return clean technical English

TEXT:

{texto}
"""

    resposta = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return resposta.output_text
