import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Prompt Manager", layout="wide")

# ---------------------
# Session State: DB yerine memory
# ---------------------
if "prompts" not in st.session_state:
    st.session_state.prompts = []  # her prompt: dict
if "categories" not in st.session_state:
    st.session_state.categories = ["İş & Kariyer", "Ev & Yaşam", "Eğitim", "Yaratıcılık", "Araştırma"]

# ---------------------
# Yardımcı fonksiyonlar
# ---------------------
def add_prompt(title, content, category, tags, fav):
    st.session_state.prompts.append({
        "id": len(st.session_state.prompts) + 1,
        "title": title,
        "content": content,
        "category": category,
        "tags": tags,
        "favorite": fav,
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M")
    })

def delete_prompt(prompt_id):
    st.session_state.prompts = [p for p in st.session_state.prompts if p["id"] != prompt_id]

def toggle_favorite(prompt_id):
    for p in st.session_state.prompts:
        if p["id"] == prompt_id:
            p["favorite"] = not p["favorite"]

# ---------------------
# Sidebar: Kategori yönetimi
# ---------------------
st.sidebar.header("Kategoriler")
new_cat = st.sidebar.text_input("Yeni kategori ekle")
if st.sidebar.button("Kategori Ekle") and new_cat.strip():
    if new_cat not in st.session_state.categories:
        st.session_state.categories.append(new_cat.strip())
        st.sidebar.success("Kategori eklendi")

selected_cat = st.sidebar.selectbox("Kategori filtrele", ["(Hepsi)"] + st.session_state.categories)
search = st.sidebar.text_input("Ara (başlık/içerik)")

# ---------------------
# Ana sayfa
# ---------------------
st.title("📝 Prompt Manager")

tab1, tab2 = st.tabs(["Prompt Listesi", "Yeni Prompt Ekle"])

# --- Prompt Listesi ---
with tab1:
    prompts = st.session_state.prompts

    # filtre uygula
    if selected_cat != "(Hepsi)":
        prompts = [p for p in prompts if p["category"] == selected_cat]
    if search:
        prompts = [p for p in prompts if search.lower() in p["title"].lower() or search.lower() in p["content"].lower()]

    st.subheader("Kayıtlı Promptlar")
    if not prompts:
        st.info("Henüz prompt yok. Sağdaki sekmeden yeni prompt ekleyin.")
    else:
        for p in prompts:
            with st.container():
                col1, col2 = st.columns([6,1])
                with col1:
                    st.markdown(f"**{p['title']}** {'⭐' if p['favorite'] else ''}")
                    st.caption(f"Kategori: {p['category']} | Eklenme: {p['created_at']}")
                    st.write(p['content'])
                    if p['tags']:
                        st.caption("Etiketler: " + p['tags'])
                with col2:
                    if st.button("⭐", key=f"fav_{p['id']}"):
                        toggle_favorite(p["id"])
                        st.experimental_rerun()
                    if st.button("🗑️", key=f"del_{p['id']}"):
                        delete_prompt(p["id"])
                        st.experimental_rerun()
                st.divider()

# --- Yeni Prompt Ekle ---
with tab2:
    st.subheader("Yeni Prompt Ekle")
    with st.form("add_form"):
        title = st.text_input("Başlık")
        content = st.text_area("İçerik", height=150)
        category = st.selectbox("Kategori", st.session_state.categories)
        tags = st.text_input("Etiketler (virgülle)")
        fav = st.checkbox("Favori ⭐")
        submitted = st.form_submit_button("Kaydet")
        if submitted:
            if not title.strip() or not content.strip():
                st.error("Başlık ve içerik boş olamaz.")
            else:
                add_prompt(title.strip(), content.strip(), category, tags.strip(), fav)
                st.success("Prompt kaydedildi!")
