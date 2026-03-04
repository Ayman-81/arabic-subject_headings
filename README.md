# Arabic Subject Headings

مشروع لتطوير نظام عناوين موضوعية باللغة العربية.

## الميزات
- معالجة النصوص العربية
- تصنيف الموضوعات تلقائياً
- قاعدة بيانات شاملة للعناوين

## المتطلبات
- Python 3.8+
- pip

## التثبيت
```bash
pip install -r requirements.txt
```

## الاستخدام
```python
from src.processor import ArabicProcessor
processor = ArabicProcessor()
result = processor.process("النص العربي هنا")
```

## الهيكل
```
arabic-subject_headings/
├── src/                 # الكود الرئيسي
├── tests/               # الاختبارات
├── data/                # البيانات
├── docs/                # التوثيق
└── config/              # الإعدادات
```

## الترخيص
MIT
