import re

regex = r"\~\w{1,20}\|\w{1,20}\~"


def parse_genero(texto: str, genero: str) -> str:
    """Faz a conversão dos textos aplicando a opção de gênero
    template: {texto_masculino|texto_feminino}"""
    matches = re.finditer(regex, texto, re.MULTILINE | re.DOTALL)
    for _, match in enumerate(matches, start=1):
        if genero.upper() == "M":
            change = match.group().split("|", 1)[0][1:]
        else:
            change = match.group().split("|", 1)[1][:-1]

        texto = texto.replace(match.group(), change)

    return texto


if __name__ == "__main__":
    print(
        parse_genero(
            "Este é um teste de menin~o|a~ para correção de ~homem|mulher~", "M"
        )
    )
    print(
        parse_genero(
            "Este é um teste de menin~o|a~ para correção de ~homem|mulher~", "F"
        )
    )
