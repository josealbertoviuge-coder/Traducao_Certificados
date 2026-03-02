from openai import OpenAI

client = OpenAI()

def traduzir(texto):

    prompt = f"""
Translate the following material certificate to English.

RULES:
- preserve technical terminology
- keep standards (ASTM, DIN, ISO)
- keep units exactly
- keep chemical symbols unchanged
- do not translate steel grades
- keep numeric formatting

TEXT:
{texto}
"""

    resposta = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return resposta.output[0].content[0].text
