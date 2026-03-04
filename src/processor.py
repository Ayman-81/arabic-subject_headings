"""
معالج النصوص العربية الرئيسي
"""

class ArabicProcessor:
    """فئة لمعالجة النصوص العربية"""
    
    def __init__(self):
        """تهيئة المعالج"""
        self.stopwords = set()
        self.load_stopwords()
    
    def load_stopwords(self):
        """تحميل قائمة الكلمات الشائعة"""
        # سيتم تحميل الكلمات الشائعة العربية
        pass
    
    def process(self, text):
        """
        معالجة النص العربي
        
        Args:
            text (str): النص المراد معالجته
            
        Returns:
            dict: النتائج المعالجة
        """
        if not text:
            return {"error": "النص فارغ"}
        
        # تنظيف النص
        cleaned = self.clean_text(text)
        
        # تقسيم الكلمات
        words = self.tokenize(cleaned)
        
        return {
            "original": text,
            "cleaned": cleaned,
            "words": words,
            "word_count": len(words)
        }
    
    def clean_text(self, text):
        """تنظيف النص"""
        # إزالة المسافات الزائدة
        text = ' '.join(text.split())
        return text
    
    def tokenize(self, text):
        """تقسيم النص إلى كلمات"""
        return text.split()


# إنشاء instance عام
processor = ArabicProcessor()
