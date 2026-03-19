#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# إعدادات قاعدة البيانات
database_url = os.environ.get('DATABASE_URL', '')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
elif database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)

if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    db_path = '/tmp/subjects.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Source(db.Model):
    __tablename__ = 'sources'
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(255), nullable=False)
    name_en = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    subjects = db.relationship('Subject', backref='source', lazy=True)
    def to_dict(self):
        return {'id': self.id, 'name_ar': self.name_ar, 'name_en': self.name_en, 'description': self.description}

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(255), nullable=False)
    name_en = db.Column(db.String(255), nullable=False)
    subjects = db.relationship('Subject', backref='category', lazy=True)
    def to_dict(self):
        return {'id': self.id, 'name_ar': self.name_ar, 'name_en': self.name_en}

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    title_ar = db.Column(db.String(500), nullable=False)
    title_en = db.Column(db.String(500))
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {
            'id': self.id,
            'title_ar': self.title_ar,
            'title_en': self.title_en,
            'description': self.description,
            'category': self.category.to_dict() if self.category else None,
            'source': self.source.to_dict() if self.source else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(500))
    results_count = db.Column(db.Integer)
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search():
    try:
        query = request.args.get('q', '').strip()
        source_id = request.args.get('source')
        category_id = request.args.get('category')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        if not query or len(query) < 2:
            return jsonify({'error': 'البحث قصير جداً', 'results': [], 'count': 0}), 400
        q = Subject.query.filter(
            db.or_(
                Subject.title_ar.ilike(f'%{query}%'),
                Subject.title_en.ilike(f'%{query}%'),
                Subject.description.ilike(f'%{query}%')
            )
        )
        if source_id: q = q.filter(Subject.source_id == source_id)
        if category_id: q = q.filter(Subject.category_id == category_id)
        results = q.limit(per_page).offset((page - 1) * per_page).all()
        total = q.count()
        try:
            history = SearchHistory(query=query, results_count=len(results))
            db.session.add(history)
            db.session.commit()
        except Exception: db.session.rollback()
        return jsonify({
            'query': query, 'results': [s.to_dict() for s in results],
            'count': len(results), 'total': total, 'page': page
        })
    except Exception as e: return jsonify({'error': str(e), 'results': [], 'count': 0}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify({'categories': [c.to_dict() for c in categories], 'count': len(categories)})
    except Exception as e: return jsonify({'error': str(e), 'categories': [], 'count': 0}), 500

@app.route('/api/sources', methods=['GET'])
def get_sources():
    try:
        sources = Source.query.all()
        return jsonify({'sources': [s.to_dict() for s in sources], 'count': len(sources)})
    except Exception as e: return jsonify({'error': str(e), 'sources': [], 'count': 0}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        return jsonify({
            'total_subjects': Subject.query.count(),
            'total_categories': Category.query.count(),
            'total_sources': Source.query.count(),
            'total_searches': db.session.query(SearchHistory).count()
        })
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route('/api/import', methods=['POST'])
def import_data():
    try:
        data = request.get_json()
        if not data: return jsonify({'error': 'No data provided'}), 400
        subjects_data = data.get('subjects', [])
        imported = 0
        for item in subjects_data:
            subject = Subject(
                title_ar=item.get('title_ar', ''), title_en=item.get('title_en', ''),
                description=item.get('description', ''),
                category_id=item.get('category_id'), source_id=item.get('source_id')
            )
            db.session.add(subject)
            imported += 1
        db.session.commit()
        return jsonify({'message': f'Imported {imported} subjects', 'count': imported})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/seed-subjects', methods=['POST'])
def seed_subjects():
    """إضافة عينة شاملة من رؤوس الموضوعات العربية"""
    try:
        # حذف الموضوعات الموجودة
        Subject.query.delete()
        
        sources = Source.query.all()
        categories = Category.query.all()
        
        if not sources or not categories:
            return jsonify({'error': 'المصادر أو التصنيفات غير موجودة'}), 400
        
        # قائمة رؤوس الموضوعات الشاملة
        subjects_data = [
            # علوم الحاسوب
            ('الذكاء الاصطناعي', 'Artificial Intelligence', 'تقنية صنع الآلات الذكية'),
            ('تعلم الآلة', 'Machine Learning', 'تعليم الحواسيب من البيانات'),
            ('الشبكات العصبية', 'Neural Networks', 'نماذج حاسوبية تحاكي الدماغ'),
            ('البيانات الضخمة', 'Big Data', 'معالجة مجموعات بيانات ضخمة'),
            ('علم البيانات', 'Data Science', 'تحليل واستخلاص المعرفة من البيانات'),
            ('أمن المعلومات', 'Information Security', 'حماية المعلومات والأنظمة'),
            ('الأمن السيبراني', 'Cybersecurity', 'حماية الأنظمة من الهجمات الرقمية'),
            ('إنترنت الأشياء', 'Internet of Things', 'شبكة الأجهزة المتصلة'),
            ('الحوسبة السحابية', 'Cloud Computing', 'خدمات الحوسبة عبر الإنترنت'),
            ('البرمجة الشيئية', 'Object-Oriented Programming', 'نموذج برمجي يعتمد على الكائنات'),
            # المكتبات والمعلومات  
            ('علم المكتبات', 'Library Science', 'علم تنظيم وإدارة المكتبات'),
            ('الفهرسة', 'Cataloging', 'تنظيم ووصف الموارد المكتبية'),
            ('التصنيف', 'Classification', 'تصنيف المواد حسب الموضوعات'),
            ('مارك 21', 'MARC 21', 'معيار الفهرسة المقروءة آلياً'),
            ('دبلن كور', 'Dublin Core', 'معيار البيانات الوصفية'),
            ('المكتبات الرقمية', 'Digital Libraries', 'مجموعات رقمية منظمة'),
            ('المستودعات الرقمية', 'Digital Repositories', 'أنظمة حفظ المحتوى الرقمي'),
            ('إدارة المعرفة', 'Knowledge Management', 'إدارة وتنظيم المعرفة المؤسسية'),
            ('الأرشفة الإلكترونية', 'Electronic Archiving', 'حفظ الوثائق إلكترونياً'),
            ('نظم استرجاع المعلومات', 'Information Retrieval Systems', 'أنظمة البحث والاسترجاع'),
            # العلوم الطبية
            ('الطب الباطني', 'Internal Medicine', 'تشخيص وعلاج الأمراض الداخلية'),
            ('الجراحة', 'Surgery', 'العمليات الجراحية العلاجية'),
            ('طب الأطفال', 'Pediatrics', 'صحة وأمراض الأطفال'),
            ('الصحة العامة', 'Public Health', 'علم صحة المجتمعات'),
            ('علم الأوبئة', 'Epidemiology', 'دراسة انتشار الأمراض'),
            ('علم الصيدلة', 'Pharmacology', 'علم الأدوية وتأثيراتها'),
            ('التمريض', 'Nursing', 'الرعاية الصحية التمريضية'),
            ('الطب النفسي', 'Psychiatry', 'تشخيص وعلاج الأمراض النفسية'),
            ('علم التشريح', 'Anatomy', 'علم بنية الجسم البشري'),
            ('علم وظائف الأعضاء', 'Physiology', 'علم وظائف أعضاء الجسم'),
            # العلوم الإنسانية
            ('علم الاجتماع', 'Sociology', 'دراسة المجتمعات البشرية'),
            ('علم النفس', 'Psychology', 'علم العقل والسلوك البشري'),
            ('الأنثروبولوجيا', 'Anthropology', 'علم الإنسان والثقافات'),
            ('التاريخ', 'History', 'دراسة الأحداث الماضية'),
            ('الجغرافيا', 'Geography', 'علم دراسة الأرض'),
            ('العلوم السياسية', 'Political Science', 'دراسة النظم السياسية'),
            ('الاقتصاد', 'Economics', 'علم إنتاج وتوزيع الثروة'),
            ('إدارة الأعمال', 'Business Administration', 'إدارة المنظمات والشركات'),
            ('القانون', 'Law', 'القواعد والأنظمة القانونية'),
            ('الفلسفة', 'Philosophy', 'البحث في الوجود والمعرفة'),
            # اللغة والأدب
            ('اللغة العربية', 'Arabic Language', 'اللغة العربية وقواعدها'),
            ('النحو', 'Grammar', 'قواعد اللغة العربية'),
            ('البلاغة', 'Rhetoric', 'علم البيان والبديع'),
            ('الأدب العربي', 'Arabic Literature', 'الشعر والنثر العربي'),
            ('الشعر العربي', 'Arabic Poetry', 'الشعر في الأدب العربي'),
            ('النقد الأدبي', 'Literary Criticism', 'تحليل ونقد الأعمال الأدبية'),
            ('اللسانيات', 'Linguistics', 'العلم الذي يدرس اللغة'),
            ('الترجمة', 'Translation', 'نقل المعنى بين اللغات'),
            ('اللغة الإنجليزية', 'English Language', 'اللغة الإنجليزية وآدابها'),
            ('علم المصطلحات', 'Terminology', 'علم المصطلحات العلمية'),
            # العلوم الطبيعية
            ('الفيزياء', 'Physics', 'علم المادة والطاقة'),
            ('الكيمياء', 'Chemistry', 'علم تركيب المادة وخواصها'),
            ('الأحياء', 'Biology', 'علم الكائنات الحية'),
            ('الرياضيات', 'Mathematics', 'علم الأعداد والكميات'),
            ('الجبر', 'Algebra', 'فرع من الرياضيات'),
            ('الهندسة', 'Geometry', 'دراسة الأشكال الهندسية'),
            ('الإحصاء', 'Statistics', 'علم جمع وتحليل البيانات'),
            ('علم الفلك', 'Astronomy', 'علم دراسة الأجرام السماوية'),
            ('الجيولوجيا', 'Geology', 'علم طبقات الأرض'),
            ('علم البيئة', 'Ecology', 'علم العلاقات بين الكائنات'),
        ]
        
        added = 0
        for idx, (title_ar, title_en, desc) in enumerate(subjects_data):
            # توزيع الموضوعات على التصنيفات بشكل منطقي
            if idx < 10: cat_id = categories[0].id  # حاسوب
            elif idx < 20: cat_id = categories[3].id  # مكتبات
            elif idx < 30: cat_id = categories[1].id  # طب
            elif idx < 40: cat_id = categories[2].id  # إنسانيات
            elif idx < 50: cat_id = categories[5].id  # لغة وأدب
            else: cat_id = categories[4].id  # علوم طبيعية
            
            subject = Subject(
                title_ar=title_ar,
                title_en=title_en,
                description=desc,
                category_id=cat_id,
                source_id=sources[0].id
            )
            db.session.add(subject)
            added += 1
        
        db.session.commit()
        return jsonify({'message': f'تم إضافة {added} موضوعاً', 'count': added})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def init_db():
    with app.app_context():
        db.create_all()

        
        if Source.query.count() == 0:
            sources_data = [
                Source(name_ar='قائمة شعبان خليفة', name_en='Shaaban Khalifa List', description='قائمة رؤوس الموضوعات العربية الكبرى'),
                Source(name_ar='رؤوس موضوعات مكتبة الكونجرس', name_en='LCSH', description='ترجمات عربية لرؤوس موضوعات الكونجرس'),
                Source(name_ar='المجموعة العربية الموحدة', name_en='GASH', description='قائمة موحدة معتمدة من المكتبات العربية')
            ]
            for s in sources_data: db.session.add(s)
            db.session.commit()

        if Category.query.count() == 0:
            categories_data = [
                Category(name_ar='علوم الحاسوب وتكنولوجيا المعلومات', name_en='Computer Science & IT'),
                Category(name_ar='العلوم الطبية والصحية', name_en='Medical Sciences'),
                Category(name_ar='العلوم الإنسانية والاجتماعية', name_en='Humanities & Social Sciences'),
                Category(name_ar='علوم المكتبات والمعلومات', name_en='Library & Information Science'),
                Category(name_ar='العلوم الطبيعية والرياضيات', name_en='Natural Sciences & Mathematics'),
                Category(name_ar='اللغة والأدب العربي', name_en='Arabic Language & Literature'),
                Category(name_ar='الفنون والتربية', name_en='Arts & Education'),
                Category(name_ar='الدين والفلسفة', name_en='Religion & Philosophy'),
            ]
            for c in categories_data: db.session.add(c)
            db.session.commit()
        
        # إضافة عينة من رؤوس الموضوعات
        if Subject.query.count() == 0:
            s1 = Source.query.first()
            c1 = Category.query.first()
            subjects_sample = [
                Subject(title_ar='الذكاء الاصطناعي', title_en='Artificial Intelligence', description='العلم والتقنية لصنع آلات ذكية', category_id=c1.id, source_id=s1.id),
                Subject(title_ar='الشبكات العصبية', title_en='Neural Networks', description='نماذج حاسوبية تحاكي الدماغ البشري', category_id=c1.id, source_id=s1.id),
                Subject(title_ar='البيانات الضخمة', title_en='Big Data', description='مجموعات بيانات كبيرة ومعقدة', category_id=c1.id, source_id=s1.id),
                Subject(title_ar='علم المكتبات الرقمية', title_en='Digital Library Science', description='تنظيم وإدارة المجموعات الرقمية', category_id=4, source_id=s1.id),
                Subject(title_ar='مارك 21', title_en='MARC 21', description='معيار الفهرسة المقروءة آلياً', category_id=4, source_id=s1.id),
            ]
            for sub in subjects_sample: db.session.add(sub)
            db.session.commit()

init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
