#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import os
import json

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/subjects.db'
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
        return {'id': self.id, 'name_ar': self.name_ar, 'name_en': self.name_en}

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
            'source': self.source.to_dict() if self.source else None
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
    
    results = q.limit(20).all()
    
    history = SearchHistory(query=query, results_count=len(results))
    db.session.add(history)
    db.session.commit()
    
    return jsonify({
        'query': query,
        'results': [s.to_dict() for s in results],
        'count': len(results)
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

def init_db():
    with app.app_context():
        db.create_all()
        
        if Source.query.count() == 0:
            sources_data = [
                Source(name_ar='قائمة شعبان خليفة', name_en='Shaaban Khalifa List', description='قائمة رؤوس الموضوعات العربية الكبرى'),
                Source(name_ar='رؤوس موضوعات مكتبة الكونجرس', name_en='LCSH', description='ترجمات عربية لرؤوس موضوعات الكونجرس'),
                Source(name_ar='المجموعة العربية الموحدة', name_en='GASH', description='قائمة موحدة معتمدة من المكتبات العربية')
            ]
            for source in sources_data:
                db.session.add(source)
            db.session.commit()
        
        if Category.query.count() == 0:
            categories_data = [
                Category(name_ar='معالجة اللغة الطبيعية', name_en='NLP'),
                Category(name_ar='التعلم الآلي', name_en='Machine Learning'),
                Category(name_ar='رؤية حاسوبية', name_en='Computer Vision'),
                Category(name_ar='ذكاء اصطناعي', name_en='Artificial Intelligence'),
                Category(name_ar='علوم إنسانية واجتماعية', name_en='Humanities'),
                Category(name_ar='علوم طبية وصحية', name_en='Medical Sciences')
            ]
            for category in categories_data:
                db.session.add(category)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
