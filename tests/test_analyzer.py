"""
اختبارات محلل الموضوعات
"""
import sys
sys.path.insert(0, '.')

from src.analyzer import SubjectAnalyzer


def test_analyzer_creation():
    """اختبار إنشاء محلل الموضوعات"""
    analyzer = SubjectAnalyzer()
    assert analyzer is not None
    assert hasattr(analyzer, 'SUBJECT_KEYWORDS')
    assert len(analyzer.SUBJECT_KEYWORDS) > 0


def test_analyze_empty_text():
    """اختبار تحليل نص فارغ"""
    analyzer = SubjectAnalyzer()
    result = analyzer.analyze('')
    assert result == []


def test_analyze_computer_text():
    """اختبار تحليل نص علوم الحاسوب"""
    analyzer = SubjectAnalyzer()
    text = "تطوير برمجة حاسوب باستخدام خوارزمية فعالة ومعالجة بيانات"
    result = analyzer.analyze(text)
    assert isinstance(result, list)
    if result:
        assert 'subject' in result[0]
        assert 'score' in result[0]
        assert result[0]['score'] > 0


def test_analyze_library_text():
    """اختبار تحليل نص علم المكتبات"""
    analyzer = SubjectAnalyzer()
    text = "فهرسة المكتبة وتصنيف المقتنيات وتوثيق المعلومات"
    result = analyzer.analyze(text)
    assert isinstance(result, list)


def test_classify_returns_string_or_none():
    """اختبار أن classify ترجع نصا أو None"""
    analyzer = SubjectAnalyzer()
    result = analyzer.classify("تطوير برمجة حاسوب")
    assert result is None or isinstance(result, str)


def test_classify_empty_text():
    """اختبار classify مع نص فارغ"""
    analyzer = SubjectAnalyzer()
    result = analyzer.classify('')
    assert result is None


if __name__ == '__main__':
    test_analyzer_creation()
    test_analyze_empty_text()
    test_analyze_computer_text()
    test_analyze_library_text()
    test_classify_returns_string_or_none()
    test_classify_empty_text()
    print('✅ جميع اختبارات المحلل نجحت!')
