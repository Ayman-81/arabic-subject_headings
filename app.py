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
os.makedirs('data', exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/subjects.db'
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
    history = SearchHistory(query=query, results_count=len(results))
    db.session.add(history)
    db.session.commit()

    return jsonify({
        'query': query,
        'results': [s.to_dict() for s in results],
        'count': len(results),
        'total': total,
        'page': page
    })


@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify({
        'categories': [c.to_dict() for c in categories],
        'count': len(categories)
    })


@app.route('/api/sources', methods=['GET'])
def get_sources():
    sources = Source.query.all()
    return jsonify({
        'sources': [s.to_dict() for s in sources],
        'count': len(sources)
    })


@app.route('/api/subjects/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return jsonify(subject.to_dict())


@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'total_subjects': Subject.query.count(),
        'total_categories': Category.query.count(),
        'total_sources': Source.query.count(),
        'total_searches': SearchHistory.query.count()
    })


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


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
