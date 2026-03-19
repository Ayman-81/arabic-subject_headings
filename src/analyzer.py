"""
محلل الموضوعات العربية
"""
from src.processor import ArabicProcessor


class SubjectAnalyzer:
    """فئة لتحليل وتصنيف الموضوعات العربية"""

    # خريطة الكلمات المفتاحية لكل موضوع
    SUBJECT_KEYWORDS = {
        'علوم الحاسوب': ['حاسوب', 'برمجة', 'خوارزمية', 'بيانات', 'شبكة'],
        'اللغة والأدب': ['شعر', 'رواية', 'أدب', 'لغة', 'نحو', 'صرف'],
        'العلوم الطبية': ['طب', 'دواء', 'مرض', 'صحة', 'جراحة'],
        'العلوم الاجتماعية': ['مجتمع', 'سياسة', 'اقتصاد', 'قانون', 'تاريخ'],
        'علم المكتبات': ['مكتبة', 'فهرسة', 'تصنيف', 'مقتنيات', 'توثيق'],
        'الرياضيات': ['رياضيات', 'جبر', 'حساب', 'هندسة', 'إحصاء'],
        'الفيزياء والكيمياء': ['فيزياء', 'كيمياء', 'عنصر', 'مولكة', 'ذرة'],
        'التربية': ['تربية', 'تعليم', 'مدرسة', 'جامعة', 'طالب'],
    }

    def __init__(self):
        """تهيئة المحلل"""
        self.subjects = {}
        self.processor = ArabicProcessor()

    def analyze(self, text):
        """
        تحليل النص واستخراج الموضوعات المناسبة

        Args:
            text (str): النص المراد تحليله

        Returns:
            list: قائمة الموضوعات المقترحة مع درجة التطابق
        """
        if not text or not text.strip():
            return []

        # معالجة النص أولاً
        processed = self.processor.process(text)
        if 'error' in processed:
            return []

        words = set(processed.get('filtered_words', []))
        subjects_found = []

        # تطابق الكلمات مع خريطة الموضوعات
        for subject, keywords in self.SUBJECT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in words or any(kw in w for w in words))
            if score > 0:
                subjects_found.append({
                    'subject': subject,
                    'score': score,
                    'matched_keywords': [kw for kw in keywords if kw in words or any(kw in w for w in words)]
                })

        # ترتيب حسب درجة التطابق
        subjects_found.sort(key=lambda x: x['score'], reverse=True)
        return subjects_found

    def classify(self, text):
        """
        تصنيف النص وإرجاع أفضل تصنيف مناسب

        Args:
            text (str): النص المراد تصنيفه

        Returns:
            str: اسم الموضوع الأنسب أو None
        """
        results = self.analyze(text)
        if results:
            return results[0]['subject']
        return None
