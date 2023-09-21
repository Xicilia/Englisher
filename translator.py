"""
Translator from RU to EN and from EN to RU using easygoogletranslate
"""

from easygoogletranslate import EasyGoogleTranslate

_toRUTranslator = EasyGoogleTranslate(
    source_language='en',
    target_language='ru',
    timeout=10
)

_toENTranslator = EasyGoogleTranslate(
    source_language='ru',
    target_language='en',
    timeout=10
)

def toRU(text: str) -> str:
    """
    gets English text and translates it to Russian.
    """
    
    return _toRUTranslator.translate(text)

def toEN(text: str) -> str:
    """
    gets Russian text and translates it to English.
    """
    
    return _toENTranslator.translate(text)