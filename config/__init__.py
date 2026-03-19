"""
حزمة إعدادات مشروع رؤوس الموضوعات العربية
"""
from config.settings import (
    DATABASE,
    LANGUAGE,
    ENCODING,
    MIN_WORD_LENGTH,
    MAX_WORD_LENGTH,
    REMOVE_STOPWORDS,
    API_PORT,
    API_HOST,
    DEBUG,
    MODELS
)

__all__ = [
    'DATABASE',
    'LANGUAGE',
    'ENCODING',
    'MIN_WORD_LENGTH',
    'MAX_WORD_LENGTH',
    'REMOVE_STOPWORDS',
    'API_PORT',
    'API_HOST',
    'DEBUG',
    'MODELS'
]
