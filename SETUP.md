# خطوات الإعداد الكاملة

## الخطوة 1: البيئة الافتراضية (Recommended)
```bash
python -m venv venv

# على Linux/Mac:
source venv/bin/activate

# على Windows:
venv\Scripts\activate
```

## الخطوة 2: تحديث pip
```bash
pip install --upgrade pip
```

## الخطوة 3: تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

## الخطوة 4: تثبيت متطلبات التطوير (اختياري)
```bash
pip install -r requirements-dev.txt
```

## الخطوة 5: تشغيل الاختبارات
```bash
pytest tests/
```

## الخطوة 6: الاستخدام الأساسي
```bash
python
>>> from src.processor import ArabicProcessor
>>> processor = ArabicProcessor()
>>> result = processor.process("مرحبا بك")
>>> print(result)
```

## معلومات إضافية
- للحصول على المساعدة: `python -m pytest --help`
- لتشغيل اختبار محدد: `pytest tests/test_processor.py::test_processor_creation`
