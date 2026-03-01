from openai import OpenAI

client = OpenAI()

def traduzir(texto):
    resposta = client.responses.create(
        model="gpt-4.1-mini",
        input="Translate to English preserving technical terms:\n" + texto
    )
    return resposta.output[0].content[0].text
