# Arabic Subject Headings Configuration

# القاعدة البيانات
DATABASE = {
    'type': 'sqlite',
    'path': 'data/subjects.db'
}

# اللغة والترميز
LANGUAGE = 'ar'
ENCODING = 'utf-8'

# معايير المعالجة
MIN_WORD_LENGTH = 2
MAX_WORD_LENGTH = 50
REMOVE_STOPWORDS = True

# API
API_PORT = 5000
API_HOST = '0.0.0.0'
DEBUG = True

# النماذج
MODELS = {
    'classifier': 'models/classifier_v1.pkl',
    'vectorizer': 'models/vectorizer_v1.pkl'
}
