import streamlit as st
import sqlite3
import pandas as pd

# --- Veritabanı Fonksiyonları ---

# Veritabanı bağlantısı oluşturma
def get_db_connection():
    """Veritabanına bağlanır ve bağlantı nesnesini döndürür."""
    conn = sqlite3.connect('prompts.db')
    conn.row_factory = sqlite3.Row
    return conn

# Veritabanını ve tabloyu başlangıçta oluşturma
def init_db():
    """'prompts' adında bir veritabanı ve tablo oluşturur."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            prompt TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Yeni bir prompt ekleme
def add_prompt(title, prompt, category):
    """Veritabanına yeni bir prompt kaydeder."""
    conn = get_db_connection()
    conn.execute('INSERT INTO prompts (title, prompt, category) VALUES (?, ?, ?)',
                 (title, prompt, category))
    conn.commit()
    conn.close()

# Bir prompt'u güncelleme
def update_prompt(prompt_id, title, prompt, category):
    """Mevcut bir prompt'u günceller."""
    conn = get_db_connection()
    conn.execute('UPDATE prompts SET title = ?, prompt = ?, category = ? WHERE id = ?',
                 (title, prompt, category, prompt_id))
    conn.commit()
    conn.close()

# Bir prompt'u silme
def delete_prompt(prompt_id):
    """Bir prompt'u ID'sine göre siler."""
    conn = get_db_connection()
    conn.execute('DELETE FROM prompts WHERE id = ?', (prompt_id,))
    conn.commit()
    conn.close()

# Tüm prompt'ları getirme
def get_all_prompts(search_query="", category_filter="Tümü"):
    """Tüm prompt'ları arama ve kategori filtresine göre getirir."""
    conn = get_db_connection()
    query = 'SELECT * FROM prompts'
    conditions = []
    params = []

    if search_query:
        conditions.append('(title LIKE ? OR prompt LIKE ?)')
        params.extend([f'%{search_query}%', f'%{search_query}%'])

    if category_filter != "Tümü":
        conditions.append('category = ?')
        params.append(category_filter)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY created_at DESC'

    prompts = conn.execute(query, params).fetchall()
    conn.close()
    return prompts

# Kategorileri getirme
def get_categories():
    """Veritabanındaki tüm benzersiz kategorileri getirir."""
    conn = get_db_connection()
    categories = conn.execute('SELECT DISTINCT category FROM prompts WHERE category IS NOT NULL AND category != "" ORDER BY category').fetchall()
    conn.close()
    return [cat['category'] for cat in categories]

# --- Streamlit Arayüzü ---

# Sayfa yapılandırması
st.set_page_config(page_title="Prompt Yöneticisi", layout="wide", initial_sidebar_state="expanded")

# Veritabanını başlat
init_db()

# Session state (oturum durumu) yönetimi
if 'editing_prompt' not in st.session_state:
    st.session_state.editing_prompt = None

# --- Kenar Çubuğu (Sidebar) ---
with st.sidebar:
    st.title("📝 Prompt Yöneticisi")
    st.markdown("Prompt'larınızı kolayca organize edin.")
    
    # Yeni prompt ekleme formu
    with st.expander("🚀 Yeni Prompt Ekle", expanded=True):
        with st.form("new_prompt_form", clear_on_submit=True):
            new_title = st.text_input("Başlık", placeholder="Örn: Sosyal Medya İçerik Fikri")
            new_prompt = st.text_area("Prompt Metni", height=150, placeholder="İçerik fikri üretmek için...")
            new_category = st.text_input("Kategori", placeholder="Örn: Pazarlama")
            
            submitted = st.form_submit_button("Ekle")
            if submitted:
                if new_title and new_prompt:
                    add_prompt(new_title, new_prompt, new_category.strip())
                    st.success("Prompt başarıyla eklendi!")
                else:
                    st.warning("Başlık ve prompt metni alanları zorunludur.")

# --- Ana İçerik ---

# Prompt düzenleme formu (eğer düzenleme modundaysa)
if st.session_state.editing_prompt:
    st.header("✍️ Prompt Düzenle")
    prompt_to_edit = st.session_state.editing_prompt
    
    with st.form("edit_prompt_form"):
        st.write(f"**ID: {prompt_to_edit['id']}**")
        edit_title = st.text_input("Başlık", value=prompt_to_edit['title'])
        edit_prompt = st.text_area("Prompt Metni", value=prompt_to_edit['prompt'], height=200)
        edit_category = st.text_input("Kategori", value=prompt_to_edit['category'])
        
        col1, col2 = st.columns(2)
        with col1:
            save_button = st.form_submit_button("Değişiklikleri Kaydet", use_container_width=True)
        with col2:
            cancel_button = st.form_submit_button("İptal", use_container_width=True)

        if save_button:
            update_prompt(prompt_to_edit['id'], edit_title, edit_prompt, edit_category.strip())
            st.success("Prompt başarıyla güncellendi!")
            st.session_state.editing_prompt = None
            st.experimental_rerun() # Sayfayı yenile
            
        if cancel_button:
            st.session_state.editing_prompt = None
            st.experimental_rerun() # Sayfayı yenile

# Prompt listesi (eğer düzenleme modunda değilse)
else:
    st.header("📚 Kayıtlı Prompt'lar")

    # Filtreleme ve arama
    categories = ["Tümü"] + get_categories()
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("Prompt'larda Ara", placeholder="Başlık veya içerikte ara...")
    with col2:
        category_selection = st.selectbox("Kategoriye Göre Filtrele", options=categories)

    # Prompt'ları getir ve göster
    prompts = get_all_prompts(search_term, category_selection)

    if not prompts:
        st.info("Henüz hiç prompt eklenmemiş veya arama kriterlerinize uygun sonuç bulunamadı.")
    else:
        for prompt in prompts:
            with st.expander(f"**{prompt['title']}** (Kategori: {prompt['category'] or 'Belirtilmemiş'})"):
                st.code(prompt['prompt'], language=None)
                
                # Eylem butonları
                btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 5])
                with btn_col1:
                    if st.button("Düzenle", key=f"edit_{prompt['id']}", use_container_width=True):
                        st.session_state.editing_prompt = prompt
                        st.experimental_rerun()
                with btn_col2:
                    if st.button("Sil", key=f"delete_{prompt['id']}", type="primary", use_container_width=True):
                        delete_prompt(prompt['id'])
                        st.success(f"'{prompt['title']}' başlıklı prompt silindi.")
                        st.experimental_rerun()
