"""
اختبارات معالج النصوص
"""

import sys
sys.path.insert(0, '.')

from src.processor import ArabicProcessor


def test_processor_creation():
    """اختبار إنشاء معالج النصوص"""
    processor = ArabicProcessor()
    assert processor is not None


def test_process_text():
    """اختبار معالجة النص"""
    processor = ArabicProcessor()
    result = processor.process("السلام عليكم ورحمة الله")
    
    assert result is not None
    assert "original" in result
    assert "cleaned" in result
    assert "words" in result


def test_empty_text():
    """اختبار معالجة نص فارغ"""
    processor = ArabicProcessor()
    result = processor.process("")
    assert "error" in result


if __name__ == "__main__":
    test_processor_creation()
    test_process_text()
    test_empty_text()
    print("✅ جميع الاختبارات نجحت!")
