from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from functools import wraps

@app.get("/ping")
def ping():
    return "pong"


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///prompt_manager.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Veritabanı Modelleri
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    prompts = db.relationship('Prompt', backref='user', lazy=True, cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='user', lazy=True, cascade='all, delete-orphan')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#3B82F6')  # Hex color
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prompts = db.relationship('Prompt', backref='category', lazy=True)

class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_favorite = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(500))  # JSON string of tags
    conversations = db.relationship('Conversation', backref='prompt', lazy=True)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    llm_model = db.Column(db.String(100), nullable=False)  # ChatGPT, Claude, etc.
    prompt_used = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer, default=0)  # 1-5 rating
    notes = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Yardımcı Fonksiyonlar
def get_user_categories():
    if current_user.is_authenticated:
        return Category.query.filter_by(user_id=current_user.id).all()
    return []

# Ana Sayfa
@app.route('/')
def index():
    if current_user.is_authenticated:
        recent_prompts = Prompt.query.filter_by(user_id=current_user.id).order_by(Prompt.updated_at.desc()).limit(5).all()
        recent_conversations = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.created_at.desc()).limit(5).all()
        stats = {
            'total_prompts': Prompt.query.filter_by(user_id=current_user.id).count(),
            'total_conversations': Conversation.query.filter_by(user_id=current_user.id).count(),
            'total_categories': Category.query.filter_by(user_id=current_user.id).count()
        }
        return render_template('dashboard.html', 
                             recent_prompts=recent_prompts, 
                             recent_conversations=recent_conversations,
                             stats=stats)
    return render_template('index.html')

# Kullanıcı Sistemi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Kullanıcı adı zaten kullanılıyor!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email adresi zaten kullanılıyor!', 'error')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        # Varsayılan kategoriler oluştur
        default_categories = [
            {'name': 'İş & Kariyer', 'color': '#3B82F6'},
            {'name': 'Ev & Yaşam', 'color': '#10B981'},
            {'name': 'Eğitim', 'color': '#F59E0B'},
            {'name': 'Yaratıcılık', 'color': '#EF4444'},
            {'name': 'Araştırma', 'color': '#8B5CF6'}
        ]
        
        for cat_data in default_categories:
            category = Category(name=cat_data['name'], color=cat_data['color'], user_id=user.id)
            db.session.add(category)
        
        db.session.commit()
        
        flash('Hesabınız başarıyla oluşturuldu!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Prompt Yönetimi
@app.route('/prompts')
@login_required
def prompts():
    category_id = request.args.get('category')
    search = request.args.get('search', '')
    
    query = Prompt.query.filter_by(user_id=current_user.id)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(Prompt.title.contains(search) | Prompt.content.contains(search))
    
    prompts = query.order_by(Prompt.updated_at.desc()).all()
    categories = get_user_categories()
    
    return render_template('prompts.html', prompts=prompts, categories=categories, 
                         selected_category=int(category_id) if category_id else None, search=search)

@app.route('/prompt/add', methods=['GET', 'POST'])
@login_required
def add_prompt():
    if request.method == 'POST':
        prompt = Prompt(
            title=request.form['title'],
            content=request.form['content'],
            category_id=request.form.get('category_id') or None,
            user_id=current_user.id,
            tags=request.form.get('tags', '')
        )
        db.session.add(prompt)
        db.session.commit()
        flash('Prompt başarıyla eklendi!', 'success')
        return redirect(url_for('prompts'))
    
    categories = get_user_categories()
    return render_template('add_prompt.html', categories=categories)

@app.route('/prompt/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_prompt(id):
    prompt = Prompt.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        prompt.title = request.form['title']
        prompt.content = request.form['content']
        prompt.category_id = request.form.get('category_id') or None
        prompt.tags = request.form.get('tags', '')
        prompt.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Prompt başarıyla güncellendi!', 'success')
        return redirect(url_for('prompts'))
    
    categories = get_user_categories()
    return render_template('edit_prompt.html', prompt=prompt, categories=categories)

@app.route('/prompt/<int:id>/delete', methods=['POST'])
@login_required
def delete_prompt(id):
    prompt = Prompt.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(prompt)
    db.session.commit()
    flash('Prompt başarıyla silindi!', 'success')
    return redirect(url_for('prompts'))

# Konuşma Yönetimi
@app.route('/conversations')
@login_required
def conversations():
    llm_filter = request.args.get('llm')
    search = request.args.get('search', '')
    
    query = Conversation.query.filter_by(user_id=current_user.id)
    
    if llm_filter:
        query = query.filter_by(llm_model=llm_filter)
    
    if search:
        query = query.filter(Conversation.title.contains(search) | Conversation.response.contains(search))
    
    conversations = query.order_by(Conversation.created_at.desc()).all()
    llm_models = db.session.query(Conversation.llm_model).filter_by(user_id=current_user.id).distinct().all()
    llm_models = [model[0] for model in llm_models]
    
    return render_template('conversations.html', conversations=conversations, 
                         llm_models=llm_models, selected_llm=llm_filter, search=search)

@app.route('/conversation/add', methods=['GET', 'POST'])
@login_required
def add_conversation():
    if request.method == 'POST':
        conversation = Conversation(
            title=request.form['title'],
            llm_model=request.form['llm_model'],
            prompt_used=request.form['prompt_used'],
            response=request.form['response'],
            prompt_id=request.form.get('prompt_id') or None,
            user_id=current_user.id,
            rating=int(request.form.get('rating', 0)),
            notes=request.form.get('notes', '')
        )
        db.session.add(conversation)
        db.session.commit()
        flash('Konuşma başarıyla eklendi!', 'success')
        return redirect(url_for('conversations'))
    
    prompts = Prompt.query.filter_by(user_id=current_user.id).all()
    return render_template('add_conversation.html', prompts=prompts)

@app.route('/conversation/<int:id>')
@login_required
def view_conversation(id):
    conversation = Conversation.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('view_conversation.html', conversation=conversation)

# Kategori Yönetimi
@app.route('/categories')
@login_required
def categories():
    categories = get_user_categories()
    return render_template('categories.html', categories=categories)

@app.route('/category/add', methods=['POST'])
@login_required
def add_category():
    category = Category(
        name=request.form['name'],
        color=request.form['color'],
        user_id=current_user.id
    )
    db.session.add(category)
    db.session.commit()
    flash('Kategori başarıyla eklendi!', 'success')
    return redirect(url_for('categories'))

# API Endpoints
@app.route('/api/prompts')
@login_required
def api_prompts():
    prompts = Prompt.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'content': p.content[:100] + '...' if len(p.content) > 100 else p.content
    } for p in prompts])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)