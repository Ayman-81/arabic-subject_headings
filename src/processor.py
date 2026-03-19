"""
معالج النصوص العربية الرئيسي
"""
import re

class ArabicProcessor:
    """فئة لمعالجة النصوص العربية"""

    # قائمة الكلمات الشائعة العربية الأساسية
    ARABIC_STOPWORDS = {
        'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'تلك',
        'التي', 'الذي', 'الذين', 'اللذان', 'اللتان', 'وهو', 'وهي', 'كان',
        'كانت', 'يكون', 'تكون', 'قد', 'لقد', 'قال', 'قالت', 'أن', 'إن',
        'لأن', 'حتى', 'بعد', 'قبل', 'عند', 'حين', 'منذ', 'خلال', 'بين',
        'أو', 'أم', 'بل', 'لكن', 'غير', 'سوى', 'إلا', 'ما', 'لا', 'لم',
        'لن', 'ليس', 'هل', 'أي', 'كل', 'بعض', 'جميع', 'نفس', 'ذات',
        'أيضا', 'فقط', 'حيث', 'كما', 'مما', 'فيما', 'عما', 'وفي', 'وعلى',
        'وإلى', 'ومن', 'وعن', 'به', 'بها', 'بهم', 'له', 'لها', 'لهم',
        'هو', 'هي', 'هم', 'هن', 'أنا', 'نحن', 'أنت', 'أنتم', 'أنتن',
    }

    def __init__(self):
        """تهيئة المعالج"""
        self.stopwords = set()
        self.load_stopwords()

    def load_stopwords(self):
        """تحميل قائمة الكلمات الشائعة العربية"""
        self.stopwords = self.ARABIC_STOPWORDS.copy()

    def remove_diacritics(self, text):
        """إزالة التشكيل من النص العربي"""
        arabic_diacritics = re.compile(
            r'[\u0610-\u061A\u064B-\u065F\u0670]'
        )
        return arabic_diacritics.sub('', text)

    def normalize_arabic(self, text):
        """توحيد الكتابة العربية"""
        # توحيد الألف
        text = re.sub(r'[\u0622\u0623\u0625\u0671]', '\u0627', text)
        # توحيد الياء
        text = re.sub(r'\u0649', '\u064A', text)
        # توحيد التاء المربوطة
        text = re.sub(r'\u0629', '\u0647', text)
        return text

    def process(self, text):
        """
        معالجة النص العربي

        Args:
            text (str): النص المراد معالجته

        Returns:
            dict: النتائج المعالجة
        """
        if not text or not text.strip():
            return {"error": "النص فارغ"}

        # تنظيف النص
        cleaned = self.clean_text(text)

        # إزالة التشكيل
        no_diacritics = self.remove_diacritics(cleaned)

        # تقسيم الكلمات
        words = self.tokenize(no_diacritics)

        # إزالة الكلمات الشائعة
        filtered_words = [w for w in words if w not in self.stopwords]

        return {
            "original": text,
            "cleaned": cleaned,
            "words": words,
            "filtered_words": filtered_words,
            "word_count": len(words),
            "filtered_count": len(filtered_words)
        }

    def clean_text(self, text):
        """تنظيف النص من الرموز الخاصة والأرقام الأجنبية"""
        # إبقاء الحروف العربية والمسافات فقط
        text = re.sub(r'[^\u0600-\u06FF\s]', ' ', text)
        # إزالة المسافات الزائدة
        text = ' '.join(text.split())
        return text

    def tokenize(self, text):
        """تقسيم النص إلى كلمات مع تصفية الكلمات القصيرة"""
        words = text.split()
        # إزالة الكلمات أقل من حرفين
        return [w for w in words if len(w) >= 2]


# إنشاء instance عام
processor = ArabicProcessor()
