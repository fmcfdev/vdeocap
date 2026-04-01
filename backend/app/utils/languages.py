"""
Vdeocap: Mapeamento de Idiomas Suportados
Este arquivo define as linguagens que o sistema pode processar.
É utilizado tanto pelo Backend para baixar pacotes de tradução,
quanto pelo Frontend para popular os campos de seleção (Select).
"""

# Mapeamento: Nome Exibido (UI) -> Código da Biblioteca (ISO 639-1)
SUPPORTED_LANGUAGES = {
    "Português": "pt",
    "Inglês": "en",
    "Espanhol": "es",
    "Francês": "fr",
    "Alemão": "de",
    "Italiano": "it",
    "Japonês": "ja",
    "Chinês": "zh"
}

def get_language_code(language_name):
    """
    Retorna o código de duas letras para um nome de idioma.
    Exemplo: "Inglês" -> "en"
    """
    return SUPPORTED_LANGUAGES.get(language_name, "en")

def get_all_languages():
    """
    Retorna apenas a lista de nomes para preencher menus no Frontend.
    """
    return list(SUPPORTED_LANGUAGES.keys())