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
# استخدام DATABASE_URL من البيئة (PostgreSQL) أو SQLite كبديل
database_url = os.environ.get('DATABASE_URL', '')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
elif database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # استخدام /tmp لضمان الكتابة على Railway
    db_path = '/tmp/subjects.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'

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
        if source_id:
            q = q.filter(Subject.source_id == source_id)
        if category_id:
            q = q.filter(Subject.category_id == category_id)
        results = q.limit(per_page).offset((page - 1) * per_page).all()
        total = q.count()
        # حفظ سجل البحث
        try:
            history = SearchHistory(query=query, results_count=len(results))
            db.session.add(history)
            db.session.commit()
        except Exception:
            db.session.rollback()
        return jsonify({
            'query': query,
            'results': [s.to_dict() for s in results],
            'count': len(results),
            'total': total,
            'page': page
        })
    except Exception as e:
        return jsonify({'error': str(e), 'results': [], 'count': 0}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify({
            'categories': [c.to_dict() for c in categories],
            'count': len(categories)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'categories': [], 'count': 0}), 500

@app.route('/api/sources', methods=['GET'])
def get_sources():
    try:
        sources = Source.query.all()
        return jsonify({
            'sources': [s.to_dict() for s in sources],
            'count': len(sources)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'sources': [], 'count': 0}), 500

@app.route('/api/subjects/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        return jsonify(subject.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        return jsonify({
            'total_subjects': Subject.query.count(),
            'total_categories': Category.query.count(),
            'total_sources': Source.query.count(),
            'total_searches': SearchHistory.query.count()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import', methods=['POST'])
def import_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        subjects_data = data.get('subjects', [])
        imported = 0
        for item in subjects_data:
            subject = Subject(
                title_ar=item.get('title_ar', ''),
                title_en=item.get('title_en', ''),
                description=item.get('description', ''),
                category_id=item.get('category_id'),
                source_id=item.get('source_id')
            )
            db.session.add(subject)
            imported += 1
        db.session.commit()
        return jsonify({'message': f'Imported {imported} subjects', 'count': imported})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def init_db():
    with app.app_context():
        db.create_all()
        if Source.query.count() == 0:
            sources_data = [
                Source(name_ar='قائمة شعبان خليفة', name_en='Shaaban Khalifa List',
                       description='قائمة رؤوس الموضوعات العربية الكبرى'),
                Source(name_ar='رؤوس موضوعات مكتبة الكونجرس', name_en='LCSH',
                       description='ترجمات عربية لرؤوس موضوعات الكونجرس'),
                Source(name_ar='المجموعة العربية الموحدة', name_en='GASH',
                       description='قائمة موحدة معتمدة من المكتبات العربية')
            ]
            for source in sources_data:
                db.session.add(source)
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
            for category in categories_data:
                db.session.add(category)
            db.session.commit()

init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
