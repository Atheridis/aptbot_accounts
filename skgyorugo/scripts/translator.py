from deep_translator import GoogleTranslator


def translate(text: str) -> str:
    trans = GoogleTranslator(source="auto", target="en").translate(text)
    return trans
