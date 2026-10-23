# app.py - Ne Yiyorum - PREMIUM VERSION (FIXED)
import streamlit as st
from ultralytics import YOLO
from PIL import Image
import plotly.graph_objects as go
from nutrition_db import (
    get_nutrition_info, 
    calculate_macros_percentage, 
    calculate_portion, 
    get_portion_info,
    NUTRITION_DATA
)
import hashlib
import sqlite3
from datetime import date, datetime, timedelta
import pandas as pd
import time
import base64
from pathlib import Path

# ==================== ADMIN AYARLARI ====================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ==================== DOSYA YOLLARI (WINDOWS) ====================
LOGO_PATH = Path(r"C:\Users\Lenovo\Desktop\BitirmeProjesi\Gemini_Generated_Image_ok6uf0ok6uf0ok6u.png")
BG_LIGHT_PATH = Path(r"C:\Users\Lenovo\Desktop\BitirmeProjesi\bg_light.png")
BG_DARK_PATH = Path(r"C:\Users\Lenovo\Desktop\BitirmeProjesi\bg_dark.png")

# ==================== HELPER FUNCTIONS ====================
def load_image_base64(image_path: Path) -> str:
    """Görseli base64'e çevir"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

def get_logo_html(width: int = 200) -> str:
    """Logo HTML döndür"""
    if LOGO_PATH.exists():
        logo_b64 = load_image_base64(LOGO_PATH)
        return f'<img src="data:image/png;base64,{logo_b64}" width="{width}px" style="margin: 0 auto; display: block;">'
    return ""

# ==================== SAYFA AYARLARI ====================
st.set_page_config(
    page_title="Ne Yiyorum - AI Beslenme Asistanı",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SESSION STATE İNİT ====================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'image' not in st.session_state:
    st.session_state.image = None
if 'class_name' not in st.session_state:
    st.session_state.class_name = None
if 'confidence' not in st.session_state:
    st.session_state.confidence = None
if 'portion_amount' not in st.session_state:
    st.session_state.portion_amount = None
if 'show_landing' not in st.session_state:
    st.session_state.show_landing = True
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# ==================== TEMA UYGULA ====================
def apply_theme(theme: str):
    """Tema CSS'ini uygula"""
    
    # Arka plan görselleri
    bg_light_b64 = load_image_base64(BG_LIGHT_PATH) if BG_LIGHT_PATH.exists() else ""
    bg_dark_b64 = load_image_base64(BG_DARK_PATH) if BG_DARK_PATH.exists() else ""
    
    if theme == 'dark':
        # DARK THEME - İYİLEŞTİRİLMİŞ
        bg_image = f"data:image/png;base64,{bg_dark_b64}" if bg_dark_b64 else ""
        bg_overlay = "rgba(18, 18, 18, 0.85)"
        primary_color = "#66BB6A"
        secondary_color = "#81C784"
        accent_color = "#FFB74D"
        text_color = "#FFFFFF"  # Beyaz yazı
        card_bg = "rgba(40, 40, 40, 0.85)"  # Daha koyu kart
        card_border = "rgba(102, 187, 106, 0.3)"
        sidebar_bg = "linear-gradient(180deg, #1B5E20 0%, #2E7D32 100%)"
        plot_bg = "rgba(30, 30, 30, 0.9)"
        plot_text = "#FFFFFF"  # Beyaz yazı
    else:
        # LIGHT THEME
        bg_image = f"data:image/png;base64,{bg_light_b64}" if bg_light_b64 else ""
        bg_overlay = "rgba(232, 245, 233, 0.80)"
        primary_color = "#4CAF50"
        secondary_color = "#81C784"
        accent_color = "#FFB74D"
        text_color = "#1B5E20"
        card_bg = "rgba(255, 255, 255, 0.75)"
        card_border = "rgba(76, 175, 80, 0.35)"
        sidebar_bg = "linear-gradient(180deg, #4CAF50 0%, #81C784 100%)"
        plot_bg = "rgba(255, 255, 255, 0.5)"
        plot_text = "#1B5E20"
    
    css = f"""
    <style>
    /* ==================== GLOBAL ==================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* Arka Plan */
    .stApp {{
        background: {bg_overlay};
        {'background-image: url("' + bg_image + '");' if bg_image else ''}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Max Width Container - GERÇEKSİZ BOŞLUKLARI KALDIRDIK */
    .block-container {{
        max-width: 1100px;
        padding-top: 1.5rem !important;  /* 3rem → 1.5rem */
        padding-bottom: 2rem !important;
    }}
    
    /* ==================== GLASSMORPHISM ==================== */
    .glass {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.90)) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 2px solid rgba(76, 175, 80, 0.3) !important;
        box-shadow: 
            0 25px 80px rgba(76, 175, 80, 0.12),
            0 10px 40px rgba(76, 175, 80, 0.08),
            0 0 1px rgba(255, 255, 255, 0.8) inset;
        padding: 30px;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
    }}
    
    .glass::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(76, 175, 80, 0.2), transparent);
        border-radius: 24px 24px 0 0;
    }}
    
    .glass:hover {{
        transform: translateY(-8px);
        box-shadow: 
            0 40px 120px rgba(76, 175, 80, 0.18),
            0 20px 60px rgba(76, 175, 80, 0.12),
            0 0 1px rgba(255, 255, 255, 0.9) inset;
        border-color: #4CAF50 !important;
    }}
    
    .glass-sm {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        border: 1px solid {card_border};
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        padding: 20px;
    }}
    
    /* Logo Wrap - MERKEZLENDİ */
    .logo-wrap {{
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 2px solid rgba(76, 175, 80, 0.3);
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        display: block !important;  /* inline-block → block */
        margin: 0 auto !important;
        text-align: center !important;
        width: fit-content !important;
    }}
    
    /* ==================== ANIMASYONLAR ==================== */
    @keyframes fadeUp {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
    }}
    
    .anim-1 {{
        animation: fadeUp 0.6s ease-out;
    }}
    
    .anim-2 {{
        animation: fadeUp 0.8s ease-out 0.2s both;
    }}
    
    .anim-3 {{
        animation: fadeUp 1.0s ease-out 0.4s both;
    }}
    
    /* ==================== BAŞLIKLAR ==================== */
    h1, h2, h3, h4 {{
        color: {text_color} !important;
        font-weight: 700;
    }}
    
    h1 {{
        font-size: 3.5rem;
        line-height: 1.2;
        background: linear-gradient(135deg, {primary_color}, {secondary_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
    }}
    
    /* ==================== BUTONLAR ==================== */
    .stButton>button {{
        background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
        color: white;
        border-radius: 14px;
        padding: 16px 32px;
        font-weight: 600;
        font-size: 16px;
        border: none;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.35);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .stButton>button:hover {{
        transform: scale(1.05) translateY(-3px);
        box-shadow: 0 15px 50px rgba(76, 175, 80, 0.6);
        background: linear-gradient(135deg, #388E3C 0%, #66BB6A 100%);
    }}
    
    .stButton>button:active {{
        transform: translateY(-1px);
    }}
    
    /* ==================== METRİK KARTLARI ==================== */
    div[data-testid="metric-container"] {{
        background: white !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 30px;
        border-radius: 18px;
        border: 3px solid #4CAF50 !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }}
    
    div[data-testid="metric-container"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 60px rgba(0, 0, 0, 0.25);
    }}
    
    div[data-testid="metric-container"] label {{
        color: #1B5E20 !important;
        font-weight: 700;
        font-size: 16px !important;
    }}
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
        font-size: 42px !important;
        font-weight: 900 !important;
        color: #2E7D32 !important;
    }}
    
    /* ==================== TABS ==================== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: transparent;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 12px 12px 0 0;
        padding: 14px 26px;
        font-weight: 600;
        color: {text_color};
        border: 1px solid {card_border};
        transition: all 0.2s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(76, 175, 80, 0.15);
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
        color: white !important;
        border-color: {primary_color};
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }}
    
    /* ==================== INPUT ==================== */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {{
        border-radius: 12px;
        border: 2px solid {card_border};
        padding: 14px;
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        color: {text_color};
        font-weight: 500;
    }}
    
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus {{
        border-color: {primary_color};
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.15);
    }}
    
    /* ==================== SIDEBAR - YAZI BOYUTLARI DÜZELTİLDİ ==================== */
    section[data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.97) !important;
        backdrop-filter: blur(40px) !important;
        -webkit-backdrop-filter: blur(40px) !important;
        border-right: 1px solid rgba(76, 175, 80, 0.2);
    }}
    
    section[data-testid="stSidebar"] * {{
        color: #1B5E20 !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
        letter-spacing: 0.3px;
    }}
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: #1B5E20 !important;
        font-weight: 900 !important;
        letter-spacing: 0.5px;
        font-size: 1.3rem !important;  /* Başlık küçültüldü */
    }}
    
    /* SİDEBAR METRİK DEĞERLERİ - ... ÇIKMASIN DİYE KÜÇÜLTÜLDÜ */
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {{
        font-size: 28px !important;  /* 48px → 28px */
        font-weight: 900 !important;
        color: #2E7D32 !important;
        letter-spacing: -0.5px !important;
        line-height: 1.2 !important;
    }}
    
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {{
        font-size: 11px !important;  /* 14px → 11px */
        font-weight: 700 !important;
        color: #4CAF50 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 4px !important;
    }}
    
    section[data-testid="stSidebar"] .glass-sm {{
        background: rgba(255, 255, 255, 0.99) !important;
        border: 2px solid #4CAF50 !important;
        border-radius: 16px;
        box-shadow: 0 12px 40px rgba(76, 175, 80, 0.1), inset 0 0 20px rgba(255,255,255,0.8) !important;
        backdrop-filter: none;
        padding: 18px !important;  /* 24px → 18px */
        transition: all 0.3s ease;
    }}
    
    section[data-testid="stSidebar"] .glass-sm:hover {{
        box-shadow: 0 15px 50px rgba(76, 175, 80, 0.2), inset 0 0 30px rgba(255,255,255,0.9) !important;
        border-color: #66BB6A !important;
    }}
    
    /* ==================== PROGRESS BAR ==================== */
    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}
    
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #4CAF50 0%, #81C784 50%, #4CAF50 100%);
        background-size: 200% 100%;
        animation: shimmer 3s infinite;
    }}
    
    /* ==================== MESAJLAR ==================== */
    .element-container .stSuccess {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-left: 5px solid {primary_color};
        border-radius: 12px;
        padding: 16px;
        color: {text_color} !important;
    }}
    
    .element-container .stWarning {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-left: 5px solid {accent_color};
        border-radius: 12px;
        padding: 16px;
        color: {text_color} !important;
    }}
    
    .element-container .stError {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-left: 5px solid #F44336;
        border-radius: 12px;
        padding: 16px;
        color: {text_color} !important;
    }}
    
    .element-container .stInfo {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-left: 5px solid #03A9F4;
        border-radius: 12px;
        padding: 16px;
        color: {text_color} !important;
    }}
    
    /* ==================== FILE UPLOADER ==================== */
    section[data-testid="stFileUploadDropzone"] {{
        background: {card_bg};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 3px dashed {primary_color};
        border-radius: 18px;
        padding: 35px;
    }}
    
    /* ==================== LANDING PAGE HERO ==================== */
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px) scale(1); }}
        50% {{ transform: translateY(-20px) scale(1.02); }}
    }}
    
    @keyframes glow-text {{
        0%, 100% {{ text-shadow: 0 0 20px rgba(76, 175, 80, 0.5); }}
        50% {{ text-shadow: 0 0 40px rgba(76, 175, 80, 0.8); }}
    }}
    
    .hero-section {{
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.08));
        padding: 100px 40px;
        border-radius: 32px;
        text-align: center;
        margin: 40px 0;
        position: relative;
        overflow: hidden;
    }}
    
    .hero-section::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(76, 175, 80, 0.1), transparent);
        animation: float 6s ease-in-out infinite;
    }}
    
    .logo-wrap {{
        animation: float 4s ease-in-out infinite;
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #4CAF50 !important;
        box-shadow: 0 20px 80px rgba(76, 175, 80, 0.25), inset 0 0 30px rgba(255,255,255,0.8) !important;
        border-radius: 32px;
    }}
    
    .hero-title {{
        background: linear-gradient(135deg, #4CAF50, #81C784, #4CAF50);
        background-size: 300% 300%;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        animation: gradient-rotate 8s ease infinite;
        font-size: 4.5rem !important;
        font-weight: 900 !important;
        letter-spacing: -1px;
    }}
    
    /* ==================== CUSTOM CLASSES ==================== */
    @keyframes mega-pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
    }}
    
    @keyframes gradient-rotate {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    @keyframes glow-pulse {{
        0%, 100% {{ box-shadow: 0 30px 120px rgba(76, 175, 80, 0.6), 0 50px 150px rgba(255, 183, 77, 0.4), inset 0 0 60px rgba(255,255,255,0.3); }}
        50% {{ box-shadow: 0 40px 150px rgba(76, 175, 80, 0.9), 0 60px 200px rgba(255, 183, 77, 0.6), inset 0 0 80px rgba(255,255,255,0.4); }}
    }}
    
    @keyframes shine {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}
    
    /* KALORİ BADGE - TEXT SHADOW İYİLEŞTİRİLDİ */
    .calorie-badge {{
        background: linear-gradient(-45deg, #4CAF50, #81C784, #FFB74D, #4CAF50);
        background-size: 400% 400%;
        min-height: 350px;
        padding: 80px 60px;
        border-radius: 32px;
        text-align: center;
        margin: 50px 0;
        box-shadow: 0 30px 120px rgba(76, 175, 80, 0.9), inset 0 0 60px rgba(255,255,255,0.3);
        animation: glow-pulse 3s ease-in-out infinite, gradient-rotate 8s ease infinite;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        overflow: hidden;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }}
    
    .calorie-badge::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.15) 50%, transparent 70%);
        animation: shine 4s infinite;
        pointer-events: none;
    }}
    
    .calorie-badge::after {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.2), transparent 70%);
        pointer-events: none;
    }}
    
    /* YAZI DAHA NET GÖRÜNSÜN - GELİŞTİRİLDİ */
    .calorie-badge h1 {{
        font-size: 8rem;
        color: #FFFFFF !important;
        text-shadow: 
            0 0 20px rgba(0,0,0,0.8),
            0 2px 10px rgba(0,0,0,0.6), 
            0 10px 40px rgba(0,0,0,0.7), 
            0 30px 80px rgba(0,0,0,0.8),
            0 0 100px rgba(76, 175, 80, 0.5) !important;
        font-weight: 900 !important;
        position: relative;
        z-index: 2;
        letter-spacing: -2px;
        line-height: 1;
        -webkit-text-stroke: 2px rgba(0, 0, 0, 0.3);
    }}
    
    .calorie-badge p {{
        font-size: 2.4rem;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        position: relative;
        z-index: 2;
        margin-top: 10px;
        text-shadow: 
            0 0 15px rgba(0,0,0,0.8),
            0 2px 8px rgba(0,0,0,0.6),
            0 10px 30px rgba(0,0,0,0.7) !important;
        letter-spacing: 0.5px;
        -webkit-text-stroke: 1px rgba(0, 0, 0, 0.2);
    }}
    
    .feature-card {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.90)) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 40px;
        border-radius: 28px;
        text-align: center;
        box-shadow: 
            0 20px 80px rgba(76, 175, 80, 0.15),
            0 10px 40px rgba(76, 175, 80, 0.1),
            0 0 1px rgba(255, 255, 255, 0.8) inset;
        border: 2px solid rgba(76, 175, 80, 0.25) !important;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
    }}
    
    .feature-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(76, 175, 80, 0.3), transparent);
        border-radius: 28px 28px 0 0;
    }}
    
    .feature-card:hover {{
        transform: translateY(-16px) scale(1.02);
        box-shadow: 
            0 40px 120px rgba(76, 175, 80, 0.25),
            0 20px 60px rgba(76, 175, 80, 0.2),
            0 0 1px rgba(255, 255, 255, 0.9) inset;
        border-color: #4CAF50 !important;
    }}
    
    .how-it-works {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.90)) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 50px;
        border-radius: 28px;
        box-shadow: 
            0 25px 100px rgba(76, 175, 80, 0.15),
            0 10px 40px rgba(76, 175, 80, 0.1),
            0 0 1px rgba(255, 255, 255, 0.8) inset;
        border: 2px solid rgba(76, 175, 80, 0.25) !important;
        margin: 50px 0;
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
    }}
    
    .how-it-works::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #4CAF50, transparent);
        border-radius: 28px 28px 0 0;
    }}
    
    .how-it-works:hover {{
        transform: translateY(-8px);
        box-shadow: 
            0 40px 140px rgba(76, 175, 80, 0.25),
            0 15px 60px rgba(76, 175, 80, 0.15),
            0 0 1px rgba(255, 255, 255, 0.9) inset;
    }}
    
    /* ==================== EXPANDER ==================== */
    .streamlit-expanderHeader {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 12px;
        border: 1px solid {card_border};
        font-weight: 600;
        color: {text_color} !important;
        padding: 16px;
    }}
    
    /* ==================== CHART CONTAINER ==================== */
    @keyframes depth-float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-8px); }}
    }}
    
    .chart-container {{
        padding: 60px;
        margin: 50px 0;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(255, 255, 255, 0.95)) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 32px;
        border: 2px solid rgba(76, 175, 80, 0.3) !important;
        box-shadow: 
            0 50px 120px rgba(76, 175, 80, 0.2),
            0 30px 60px rgba(76, 175, 80, 0.15),
            0 0 40px rgba(255, 255, 255, 0.8) inset,
            0 0 80px rgba(76, 175, 80, 0.05);
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        animation: depth-float 4s ease-in-out infinite;
    }}
    
    .chart-container:hover {{
        transform: translateY(-12px);
        box-shadow: 
            0 70px 160px rgba(76, 175, 80, 0.3),
            0 40px 80px rgba(76, 175, 80, 0.25),
            0 0 60px rgba(255, 255, 255, 0.9) inset,
            0 0 100px rgba(76, 175, 80, 0.1);
        border-color: #4CAF50 !important;
    }}
    
    .chart-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.4), rgba(255,255,255,0));
        border-radius: 32px;
        pointer-events: none;
    }}
    
    /* ==================== THEME TOGGLE BUTTON - SADELEŞTİRİLDİ ==================== */
    .theme-toggle {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 12px;
        border-radius: 50%;
        border: 2px solid rgba(76, 175, 80, 0.3);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        cursor: pointer;
        transition: all 0.3s ease;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    .theme-toggle:hover {{
        transform: scale(1.1) rotate(15deg);
        box-shadow: 0 8px 24px rgba(76, 175, 80, 0.3);
    }}
    
    /* ==================== MOBİL UYUMLULUK ==================== */
    @media (max-width: 768px) {{
        h1 {{
            font-size: 2.5rem;
        }}
        
        .calorie-badge {{
            min-height: 250px;
            padding: 50px 30px;
        }}
        
        .calorie-badge h1 {{
            font-size: 4rem;
        }}
        
        .calorie-badge p {{
            font-size: 1.5rem;
        }}
        
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 1.5rem !important;
        }}
        
        .glass {{
            padding: 20px;
        }}
        
        .feature-card {{
            padding: 25px;
        }}
        
        .how-it-works {{
            padding: 30px;
        }}
        
        .chart-container {{
            padding: 30px;
            margin: 30px 0;
        }}
        
        .stButton>button {{
            width: 100%;
            padding: 14px 24px;
        }}
        
        /* Sidebar mobilde daha kompakt */
        section[data-testid="stSidebar"] [data-testid="stMetricValue"] {{
            font-size: 22px !important;
        }}
        
        section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {{
            font-size: 10px !important;
        }}
    }}
    
    /* ==================== DATAFRAME ==================== */
    .dataframe {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 12px;
        overflow: hidden;
    }}
    
    /* ==================== PLOTLY ==================== */
    .js-plotly-plot {{
        background: transparent !important;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    
    # Plotly için global ayar
    st.session_state.plot_config = {
        'paper_bgcolor': plot_bg,
        'plot_bgcolor': plot_bg,
        'font_color': plot_text
    }

# Temayı uygula
apply_theme(st.session_state.theme)

# ==================== VERİTABANI FONKSİYONLARI ====================
def get_db_connection():
    return sqlite3.connect('users.db')

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        age INTEGER,
        weight REAL,
        height REAL,
        gender TEXT,
        activity_level TEXT,
        goal TEXT,
        daily_calorie_target REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meal_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        food_name TEXT,
        portion REAL,
        calories REAL,
        protein REAL,
        carbs REAL,
        fat REAL,
        fiber REAL,
        date DATE,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def calculate_daily_calorie(weight, height, age, gender, activity_level, goal):
    if gender == 'Erkek':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    
    activity_multipliers = {
        'Sedanter (Hareketsiz)': 1.2,
        'Az Aktif (Haftada 1-3 gün)': 1.375,
        'Orta Aktif (Haftada 3-5 gün)': 1.55,
        'Çok Aktif (Haftada 6-7 gün)': 1.725,
        'Aşırı Aktif (Her gün yoğun)': 1.9
    }
    
    tdee = bmr * activity_multipliers.get(activity_level, 1.2)
    
    if goal == 'Kilo Ver':
        return round(tdee - 500)
    elif goal == 'Kilo Al':
        return round(tdee + 300)
    else:
        return round(tdee)

def register_user(username, password, age, weight, height, gender, activity_level, goal):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        daily_calorie = calculate_daily_calorie(weight, height, age, gender, activity_level, goal)
        hashed_password = hash_password(password)
        
        cursor.execute('''
        INSERT INTO users (username, password, age, weight, height, gender, 
                         activity_level, goal, daily_calorie_target)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, hashed_password, age, weight, height, gender, 
              activity_level, goal, daily_calorie))
        
        conn.commit()
        conn.close()
        return True, "Kayıt başarılı!"
    except sqlite3.IntegrityError:
        return False, "Bu kullanıcı adı zaten alınmış!"
    except Exception as e:
        return False, f"Hata: {str(e)}"

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = hash_password(password)
    
    cursor.execute('''
    SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, hashed_password))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return True, {
            'id': user[0],
            'username': user[1],
            'age': user[3],
            'weight': user[4],
            'height': user[5],
            'gender': user[6],
            'activity_level': user[7],
            'goal': user[8],
            'daily_calorie_target': user[9]
        }
    else:
        return False, None

def add_meal_log(user_id, username, food_name, portion, calories, protein, carbs, fat, fiber):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = date.today()
    
    cursor.execute('''
    INSERT INTO meal_logs (user_id, username, food_name, portion, calories, 
                          protein, carbs, fat, fiber, date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, food_name, portion, calories, protein, carbs, fat, fiber, today))
    
    conn.commit()
    conn.close()

def get_today_totals(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = date.today()
    
    cursor.execute('''
    SELECT 
        COALESCE(SUM(calories), 0) as total_calories,
        COALESCE(SUM(protein), 0) as total_protein,
        COALESCE(SUM(carbs), 0) as total_carbs,
        COALESCE(SUM(fat), 0) as total_fat,
        COALESCE(SUM(fiber), 0) as total_fiber
    FROM meal_logs 
    WHERE user_id = ? AND date = ?
    ''', (user_id, today))
    
    result = cursor.fetchone()
    conn.close()
    
    return {
        'total_calories': result[0],
        'total_protein': result[1],
        'total_carbs': result[2],
        'total_fat': result[3],
        'total_fiber': result[4]
    }

def get_today_meals(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = date.today()
    
    cursor.execute('''
    SELECT food_name, portion, calories, protein, carbs, fat, timestamp
    FROM meal_logs 
    WHERE user_id = ? AND date = ?
    ORDER BY timestamp DESC
    ''', (user_id, today))
    
    meals = cursor.fetchall()
    conn.close()
    
    return meals

def get_weekly_stats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = []
    for i in range(7):
        target_date = (datetime.now() - timedelta(days=6-i)).date()
        
        cursor.execute('''
        SELECT COALESCE(SUM(calories), 0)
        FROM meal_logs
        WHERE user_id = ? AND date = ?
        ''', (user_id, target_date))
        
        calories = cursor.fetchone()[0]
        stats.append({
            'date': target_date.strftime('%d.%m'),
            'calories': calories
        })
    
    conn.close()
    return stats

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, username, age, weight, height, gender, activity_level, goal, 
           daily_calorie_target, created_at
    FROM users ORDER BY created_at DESC
    ''')
    users = cursor.fetchall()
    conn.close()
    return users

def get_all_meal_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT ml.id, ml.username, ml.food_name, ml.portion, ml.calories,
           ml.protein, ml.carbs, ml.fat, ml.date, ml.timestamp
    FROM meal_logs ml ORDER BY ml.timestamp DESC LIMIT 100
    ''')
    logs = cursor.fetchall()
    conn.close()
    return logs

def get_user_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM meal_logs')
    total_meals = cursor.fetchone()[0]
    
    today = date.today()
    cursor.execute('SELECT COUNT(*) FROM meal_logs WHERE date = ?', (today,))
    today_meals = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(calories) FROM meal_logs WHERE date = ?', (today,))
    today_calories = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_meals': total_meals,
        'today_meals': today_meals,
        'today_calories': today_calories
    }

def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM meal_logs WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

create_tables()

# ==================== THEME TOGGLE (SAĞ ÜST) - SADELEŞTİRİLDİ ====================
if st.session_state.logged_in or not st.session_state.show_landing:
    # Sadece ikon göster
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    
    # HTML ile custom buton
    st.markdown(f"""
    <div class="theme-toggle" onclick="window.location.href='?theme_toggle=true'">
        <span style="font-size: 24px;">{theme_icon}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # URL parametresi kontrolü ile tema değiştir
    try:
        import urllib.parse
        query_params = st.query_params
        if 'theme_toggle' in query_params:
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
            st.query_params.clear()
            st.rerun()
    except:
        # Fallback: Normal buton
        if st.button(theme_icon, key="theme_btn"):
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
            st.rerun()

# ==================== LANDING PAGE ====================
if st.session_state.show_landing and not st.session_state.logged_in:
    st.markdown('<div class="anim-1">', unsafe_allow_html=True)
    # LOGO MERKEZLENDİ
    st.markdown(f'<div class="logo-wrap" style="text-align: center; display: block; margin: 0 auto; width: fit-content;">{get_logo_html(280)}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; padding: 30px;' class='anim-2'>
        <h1 style='font-size: 4rem; margin: 20px 0;'>Ne Yiyorum?</h1>
        <p style='font-size: 1.5rem; margin-bottom: 50px; opacity: 0.9;'>
            🤖 Yapay Zeka ile Akıllı Beslenme Asistanınız
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="anim-3">', unsafe_allow_html=True)
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("""
        <div class='feature-card'>
            <div style='font-size: 3.5rem; margin-bottom: 15px;'>🤖</div>
            <h3>Yapay Zeka</h3>
            <p style='opacity: 0.85; font-size: 14px;'>
                YOLOv8 ile<br>%93.4 doğruluk<br>5.2ms hız
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
        <div class='feature-card'>
            <div style='font-size: 3.5rem; margin-bottom: 15px;'>🎯</div>
            <h3>Kişisel Hedef</h3>
            <p style='opacity: 0.85; font-size: 14px;'>
                Size özel kalori<br>BMR/TDEE hesaplama<br>Bilimsel formüller
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
        <div class='feature-card'>
            <div style='font-size: 3.5rem; margin-bottom: 15px;'>📊</div>
            <h3>Takip Sistemi</h3>
            <p style='opacity: 0.85; font-size: 14px;'>
                Günlük rapor<br>İnteraktif grafikler<br>Real-time güncelleme
            </p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='how-it-works'>
        <h2 style='text-align: center; margin-bottom: 35px;'>🚀 Nasıl Çalışır?</h2>
        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 25px; text-align: center;'>
            <div>
                <div style='font-size: 3rem; margin-bottom: 12px;'>📸</div>
                <h4>1. Fotoğraf</h4>
                <p style='opacity: 0.8; font-size: 13px;'>Yemeğinizin fotoğrafını çekin</p>
            </div>
            <div>
                <div style='font-size: 3rem; margin-bottom: 12px;'>🤖</div>
                <h4>2. AI Analizi</h4>
                <p style='opacity: 0.8; font-size: 13px;'>5.2ms'de yemek tanıma</p>
            </div>
            <div>
                <div style='font-size: 3rem; margin-bottom: 12px;'>📊</div>
                <h4>3. Besin Değeri</h4>
                <p style='opacity: 0.8; font-size: 13px;'>Otomatik hesaplama</p>
            </div>
            <div>
                <div style='font-size: 3rem; margin-bottom: 12px;'>✅</div>
                <h4>4. Takip</h4>
                <p style='opacity: 0.8; font-size: 13px;'>Günlük raporlama</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    start_col1, start_col2, start_col3 = st.columns([1, 1, 1])
    with start_col2:
        if st.button("🚀 HEMEN BAŞLA", type="primary", use_container_width=True):
            st.session_state.show_landing = False
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; opacity: 0.7; padding: 30px; font-size: 14px;'>
        <p>Made with ❤️ by Computer Engineering Students</p>
        <p style='font-weight: bold;'>Tekirdağ Namık Kemal Üniversitesi</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# ==================== GİRİŞ/KAYIT EKRANI ====================
if not st.session_state.logged_in:
    st.markdown("<br>", unsafe_allow_html=True)
    # LOGO MERKEZLENDİ - GERÇEKSİZ BOŞLUKLAR KALDIRILDI
    st.markdown(f'<div class="logo-wrap" style="text-align: center; display: block; margin: 20px auto; width: fit-content;">{get_logo_html(220)}</div>', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; margin-top: 20px;'>Hoş Geldiniz! 👋</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Giriş Yap", "📝 Kayıt Ol", "👔 Admin"])
    
    with tab1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Giriş Yap")
        login_username = st.text_input("Kullanıcı Adı", key="login_user")
        login_password = st.text_input("Şifre", type="password", key="login_pass")
        
        if st.button("🔓 Giriş Yap", type="primary", use_container_width=True):
            if login_username and login_password:
                with st.spinner("Giriş yapılıyor..."):
                    success, user_data = login_user(login_username, login_password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = user_data
                        st.success("✅ Giriş başarılı!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Kullanıcı adı veya şifre hatalı!")
            else:
                st.warning("⚠️ Lütfen tüm alanları doldurun!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("Yeni Hesap Oluştur")
        
        col1, col2 = st.columns(2)
        
        with col1:
            reg_username = st.text_input("Kullanıcı Adı", key="reg_user")
            reg_password = st.text_input("Şifre", type="password", key="reg_pass")
            reg_age = st.number_input("Yaş", min_value=10, max_value=100, value=25)
            reg_weight = st.number_input("Kilo (kg)", min_value=30, max_value=200, value=70)
        
        with col2:
            reg_height = st.number_input("Boy (cm)", min_value=100, max_value=250, value=170)
            reg_gender = st.selectbox("Cinsiyet", ["Erkek", "Kadın"])
            reg_activity = st.selectbox("Aktivite Seviyesi", 
                                       ["Sedanter (Hareketsiz)", 
                                        "Az Aktif (Haftada 1-3 gün)", 
                                        "Orta Aktif (Haftada 3-5 gün)", 
                                        "Çok Aktif (Haftada 6-7 gün)",
                                        "Aşırı Aktif (Her gün yoğun)"])
            reg_goal = st.selectbox("Hedefin", ["Kilo Ver", "Kilonu Koru", "Kilo Al"])
        
        preview_calorie = calculate_daily_calorie(
            reg_weight, reg_height, reg_age, reg_gender, reg_activity, reg_goal
        )
        st.info(f"💡 Günlük kalori hedefiniz: **{preview_calorie} kcal** olacak")
        
        if st.button("✅ Kayıt Ol", type="primary", use_container_width=True):
            if reg_username and reg_password:
                with st.spinner("Kaydediliyor..."):
                    success, message = register_user(
                        reg_username, reg_password, reg_age, reg_weight, 
                        reg_height, reg_gender, reg_activity, reg_goal
                    )
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Lütfen kullanıcı adı ve şifre girin!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("👨‍💼 Admin Girişi")
        admin_user = st.text_input("Admin Kullanıcı Adı", key="admin_user")
        admin_pass = st.text_input("Admin Şifre", type="password", key="admin_pass")
        
        if st.button("🔓 Admin Girişi", type="primary", use_container_width=True):
            if admin_user == ADMIN_USERNAME and admin_pass == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.user = {'username': 'ADMIN', 'is_admin': True}
                st.success("✅ Admin girişi başarılı!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ Admin bilgileri hatalı!")
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== ANA UYGULAMA ====================
else:
    # ADMIN PANELİ
    if st.session_state.user.get('is_admin', False):
        st.title("👨‍💼 ADMIN PANELİ")
        
        if st.button("🚪 Çıkış Yap"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
        
        st.markdown("---")
        
        stats = get_user_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Toplam Kullanıcı", stats['total_users'])
        with col2:
            st.metric("🍽️ Toplam Kayıt", stats['total_meals'])
        with col3:
            st.metric("📅 Bugünkü Kayıt", stats['today_meals'])
        with col4:
            st.metric("🔥 Bugünkü Kalori", f"{stats['today_calories']:.0f}")
        
        st.markdown("---")
        
        admin_tab1, admin_tab2 = st.tabs(["👥 Kullanıcılar", "🍽️ Yemek Kayıtları"])
        
        with admin_tab1:
            st.subheader("👥 Tüm Kullanıcılar")
            users = get_all_users()
            
            if users:
                users_df = pd.DataFrame(users, columns=[
                    'ID', 'Kullanıcı', 'Yaş', 'Kilo', 'Boy', 'Cinsiyet', 
                    'Aktivite', 'Hedef', 'Kalori Hedefi', 'Kayıt Tarihi'
                ])
                st.dataframe(users_df, use_container_width=True)
                
                st.markdown("---")
                col_del1, col_del2 = st.columns([3, 1])
                with col_del1:
                    user_to_delete = st.selectbox(
                        "Silinecek Kullanıcı",
                        options=[f"{u[1]} (ID: {u[0]})" for u in users]
                    )
                with col_del2:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ SİL", type="secondary"):
                        user_id = int(user_to_delete.split("ID: ")[1].replace(")", ""))
                        delete_user(user_id)
                        st.success("✅ Kullanıcı silindi!")
                        time.sleep(0.5)
                        st.rerun()
            else:
                st.info("🔭 Henüz kullanıcı yok.")
        
        with admin_tab2:
            st.subheader("🍽️ Son 100 Yemek Kaydı")
            logs = get_all_meal_logs()
            
            if logs:
                logs_df = pd.DataFrame(logs, columns=[
                    'ID', 'Kullanıcı', 'Yemek', 'Porsiyon', 'Kalori',
                    'Protein', 'Karbonhidrat', 'Yağ', 'Tarih', 'Zaman'
                ])
                st.dataframe(logs_df, use_container_width=True)
            else:
                st.info("🔭 Henüz yemek kaydı yok.")
        
        st.stop()
    
    # NORMAL KULLANICI
    with st.sidebar:
        st.markdown(f'<div class="glass-sm">{get_logo_html(160)}</div>', unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; margin-top: 15px; font-size: 1.2rem !important;'>👤 {st.session_state.user['username']}</h3>", unsafe_allow_html=True)
        st.success("✅ YOLOv8 Aktif")
        
        st.markdown("---")
        st.markdown('<div class="glass-sm">', unsafe_allow_html=True)
        st.subheader("📊 Profiliniz")
        st.info(f"**Hedef:** {st.session_state.user['goal']}")
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("Yaş", st.session_state.user['age'])
            st.metric("Boy", f"{st.session_state.user['height']} cm")
        with col_info2:
            st.metric("Kilo", f"{st.session_state.user['weight']} kg")
            st.metric("Cinsiyet", st.session_state.user['gender'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<div class="glass-sm">', unsafe_allow_html=True)
        st.subheader("🎯 Günlük Hedef")
        target = st.session_state.user['daily_calorie_target']
        today_totals = get_today_totals(st.session_state.user['id'])
        consumed = today_totals['total_calories']
        remaining = target - consumed
        
        st.metric("Hedef", f"{target:.0f} kcal")
        st.metric("Tüketilen", f"{consumed:.0f} kcal")
        st.metric("Kalan", f"{remaining:.0f} kcal")
        
        progress = min(consumed / target, 1.0) if target > 0 else 0
        st.progress(progress)
        
        if remaining < 0:
            st.error(f"⚠️ {abs(remaining):.0f} kcal aştınız!")
        elif remaining < 200:
            st.warning("⚠️ Hedefe yaklaştınız!")
        else:
            st.success(f"✅ {remaining:.0f} kcal hakkınız var!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown('<div class="glass-sm">', unsafe_allow_html=True)
        total_meals_count = len(get_today_meals(st.session_state.user['id']))
        st.subheader("🏆 Başarılar")
        
        if total_meals_count >= 1:
            st.success("🥉 İlk Adım")
        if total_meals_count >= 3:
            st.success("🥈 Düzenli Takip")
        if total_meals_count >= 5:
            st.success("🥇 Profesyonel")
        if remaining > 0 and consumed > 0:
            st.success("✅ Hedefte")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🚪 Çıkış", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.show_landing = True
            st.rerun()
    
    st.title("🥗 Ne Yiyorum?")
    st.markdown("**Yapay zeka ile yemek tanıma ve detaylı besin değeri analizi!**")
    
    @st.cache_resource
    def load_model():
        return YOLO("runs/detect/food101_model24/weights/best.pt")
    
    model = load_model()
    
    tab1, tab2, tab3 = st.tabs(["📸 Analiz Et", "📊 Günlük Rapor", "📚 Yemek Listesi"])
    
    # TAB 1: ANALİZ
    with tab1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("📷 Fotoğraf Yükle")
        
        upload_option = st.radio("Nasıl yüklemek istersiniz?", 
                                ["📁 Dosyadan Yükle", "📸 Kamera ile Çek"],
                                horizontal=True)
        
        if upload_option == "📁 Dosyadan Yükle":
            uploaded_file = st.file_uploader("Yemek fotoğrafı seçin", type=['jpg', 'jpeg', 'png'])
        else:
            uploaded_file = st.camera_input("Yemeğinizin fotoğrafını çekin")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file and (st.session_state.image is None or uploaded_file != st.session_state.image):
            st.session_state.analyzed = False
            st.session_state.image = uploaded_file
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Yüklenen Fotoğraf", use_container_width=True)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                analyze_button = st.button("🔍 ANALİZ ET", type="primary", use_container_width=True)
            
            if analyze_button:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("📸 Görsel yükleniyor...")
                progress_bar.progress(20)
                time.sleep(0.3)
                
                status_text.text("🤖 YOLOv8 modeli aktif...")
                progress_bar.progress(40)
                time.sleep(0.3)
                
                status_text.text("🔍 Yemek tespit ediliyor...")
                progress_bar.progress(60)
                results = model.predict(image, conf=0.5)
                
                status_text.text("📊 Besin değerleri hesaplanıyor...")
                progress_bar.progress(80)
                time.sleep(0.3)
                
                if len(results[0].boxes) > 0:
                    box = results[0].boxes[0]
                    st.session_state.class_name = results[0].names[int(box.cls[0])]
                    st.session_state.confidence = float(box.conf[0])
                    st.session_state.results = results
                    st.session_state.analyzed = True
                    
                    portion_info = get_portion_info(st.session_state.class_name)
                    st.session_state.portion_amount = portion_info['default']
                    
                    status_text.text("✅ Tamamlandı!")
                    progress_bar.progress(100)
                    time.sleep(0.5)
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success("✅ Yemek başarıyla tespit edildi!")
                    st.balloons()
                    time.sleep(0.5)
                    st.rerun()
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("❌ Yemek tespit edilemedi. Farklı bir fotoğraf deneyin.")
            
            if st.session_state.analyzed and st.session_state.class_name:
                st.markdown("---")
                
                nutrition = get_nutrition_info(st.session_state.class_name)
                
                if nutrition:
                    st.markdown('<div class="glass">', unsafe_allow_html=True)
                    portion_info = get_portion_info(st.session_state.class_name)
                    
                    col_portion1, col_portion2 = st.columns([2, 1])
                    
                    with col_portion1:
                        st.subheader(f"{nutrition['emoji']} {st.session_state.class_name.replace('_', ' ').title()}")
                        st.caption(f"Referans: {nutrition['portion_size']}")
                    
                    with col_portion2:
                        if st.session_state.portion_amount is None:
                            st.session_state.portion_amount = portion_info['default']
                        
                        if portion_info['type'] == 'gram':
                            portion_amount = st.number_input(
                                f"Miktar (gram)",
                                min_value=10,
                                max_value=portion_info['max'],
                                value=int(st.session_state.portion_amount),
                                step=10,
                                key='input_gram'
                            )
                            base_amount = nutrition.get('base_amount', 100)
                            multiplier = portion_amount / base_amount
                        else:
                            portion_amount = st.number_input(
                                f"Miktar ({portion_info['type']})",
                                min_value=1,
                                max_value=portion_info['max'],
                                value=int(st.session_state.portion_amount),
                                step=1,
                                key='input_other'
                            )
                            unit_weight = portion_info['unit_weight']
                            base_amount = nutrition.get('base_amount', unit_weight)
                            multiplier = (portion_amount * unit_weight) / base_amount
                    
                    adjusted_nutrition = calculate_portion(nutrition, multiplier)
                    
                    st.markdown(f"""
                    <div class="calorie-badge">
                        <h1 style='color: white; margin: 0; font-size: 3.5rem;'>{adjusted_nutrition['calories']} kcal</h1>
                        <p style='color: white; margin: 5px 0; font-size: 1.2rem; opacity: 0.95;'>Toplam Kalori</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.metric("🥩 Protein", f"{adjusted_nutrition['protein']}g")
                    with col_b:
                        st.metric("🍞 Karbonhidrat", f"{adjusted_nutrition['carbs']}g")
                    with col_c:
                        st.metric("🧈 Yağ", f"{adjusted_nutrition['fat']}g")
                    with col_d:
                        st.metric("🌾 Lif", f"{adjusted_nutrition['fiber']}g")
                    
                    st.markdown("---")
                    col_save1, col_save2, col_save3 = st.columns([1, 1, 1])
                    with col_save2:
                        if st.button("💾 KAYDET VE EKLE", type="primary", use_container_width=True):
                            with st.spinner("Kaydediliyor..."):
                                add_meal_log(
                                    st.session_state.user['id'],
                                    st.session_state.user['username'],
                                    st.session_state.class_name,
                                    portion_amount,
                                    adjusted_nutrition['calories'],
                                    adjusted_nutrition['protein'],
                                    adjusted_nutrition['carbs'],
                                    adjusted_nutrition['fat'],
                                    adjusted_nutrition['fiber']
                                )
                                time.sleep(0.5)
                            
                            st.success("✅ Yemek başarıyla kaydedildi!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                    
                    st.markdown("---")
                    st.subheader("📊 Makro Besin Dağılımı")
                    
                    protein_pct, carbs_pct, fat_pct = calculate_macros_percentage(
                        adjusted_nutrition['protein'],
                        adjusted_nutrition['carbs'],
                        adjusted_nutrition['fat']
                    )
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=['Protein', 'Karbonhidrat', 'Yağ'],
                        values=[protein_pct, carbs_pct, fat_pct],
                        hole=.5,
                        marker_colors=['#4CAF50', '#FFB74D', '#FF6B6B'],
                        textinfo='label+percent',
                        textfont_size=18
                    )])
                    
                    plot_config = st.session_state.get('plot_config', {})
                    fig.update_layout(
                        showlegend=True,
                        height=600,
                        margin=dict(t=40, b=40, l=40, r=40),
                        paper_bgcolor=plot_config.get('paper_bgcolor', 'rgba(0,0,0,0)'),
                        plot_bgcolor=plot_config.get('plot_bgcolor', 'rgba(0,0,0,0)'),
                        font=dict(color=plot_config.get('font_color', '#1B5E20'))
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Bu yemek için besin bilgisi henüz yok.")
        else:
            st.info("👆 Lütfen bir yemek fotoğrafı yükleyin")
    
    # TAB 2: GÜNLÜK RAPOR
    with tab2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("📊 Bugünkü Besin Takibiniz")
        
        today_totals = get_today_totals(st.session_state.user['id'])
        today_meals = get_today_meals(st.session_state.user['id'])
        
        target = st.session_state.user['daily_calorie_target']
        consumed = today_totals['total_calories']
        remaining = target - consumed
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Hedef", f"{target:.0f} kcal")
        with col2:
            st.metric("✅ Tüketilen", f"{consumed:.0f} kcal")
        with col3:
            st.metric("⏳ Kalan", f"{remaining:.0f} kcal")
        with col4:
            st.metric("🥩 Protein", f"{today_totals['total_protein']:.1f}g")
        
        st.markdown("### Günlük İlerleme")
        progress = min(consumed / target, 1.0) if target > 0 else 0
        st.progress(progress)
        
        if remaining < 0:
            st.error(f"⚠️ Hedefi {abs(remaining):.0f} kcal aştınız!")
        elif remaining < 200:
            st.warning("⚠️ Hedefinize yaklaştınız! Dikkatli olun.")
        else:
            st.success(f"✅ Harika! {remaining:.0f} kcal hakkınız var!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if consumed > 0:
            st.markdown("---")
            col_graph1, col_graph2 = st.columns(2)
            
            with col_graph1:
                st.markdown('<div class="glass-sm">', unsafe_allow_html=True)
                st.subheader("📈 Kalori Karşılaştırması")
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Hedef',
                    x=['Kalori'],
                    y=[target],
                    marker_color='rgba(76, 175, 80, 0.7)',
                    text=[f'{target:.0f} kcal'],
                    textposition='auto',
                    textfont_size=18
                ))
                fig.add_trace(go.Bar(
                    name='Tüketilen',
                    x=['Kalori'],
                    y=[consumed],
                    marker_color='rgba(255, 183, 77, 0.7)',
                    text=[f'{consumed:.0f} kcal'],
                    textposition='auto',
                    textfont_size=18
                ))
                
                plot_config = st.session_state.get('plot_config', {})
                fig.update_layout(
                    barmode='group',
                    height=600,
                    margin=dict(t=40, b=40, l=40, r=40),
                    showlegend=True,
                    paper_bgcolor=plot_config.get('paper_bgcolor', 'rgba(0,0,0,0)'),
                    plot_bgcolor=plot_config.get('plot_bgcolor', 'rgba(0,0,0,0)'),
                    font=dict(color=plot_config.get('font_color', '#1B5E20'), size=14)
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_graph2:
                st.markdown('<div class="glass-sm">', unsafe_allow_html=True)
                st.subheader("🥧 Makro Dağılımı")
                protein_pct, carbs_pct, fat_pct = calculate_macros_percentage(
                    today_totals['total_protein'],
                    today_totals['total_carbs'],
                    today_totals['total_fat']
                )
                
                fig = go.Figure(data=[go.Pie(
                    labels=['Protein', 'Karbonhidrat', 'Yağ'],
                    values=[protein_pct, carbs_pct, fat_pct],
                    hole=.5,
                    marker_colors=['#4CAF50', '#FFB74D', '#FF6B6B'],
                    textfont_size=18
                )])
                
                plot_config = st.session_state.get('plot_config', {})
                fig.update_layout(
                    height=600,
                    margin=dict(t=40, b=40, l=40, r=40),
                    paper_bgcolor=plot_config.get('paper_bgcolor', 'rgba(0,0,0,0)'),
                    plot_bgcolor=plot_config.get('plot_bgcolor', 'rgba(0,0,0,0)'),
                    font=dict(color=plot_config.get('font_color', '#1B5E20'))
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown('<div class="glass-sm">', unsafe_allow_html=True)
            st.subheader("📈 Son 7 Gün Trendi")
            weekly_stats = get_weekly_stats(st.session_state.user['id'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[s['date'] for s in weekly_stats],
                y=[s['calories'] for s in weekly_stats],
                mode='lines+markers',
                name='Günlük Kalori',
                line=dict(color='#4CAF50', width=4),
                marker=dict(size=12, color='#81C784')
            ))
            
            fig.add_hline(
                y=target,
                line_dash="dash",
                line_color="#FF6B6B",
                annotation_text="Hedef"
            )
            
            plot_config = st.session_state.get('plot_config', {})
            fig.update_layout(
                xaxis_title='Tarih',
                yaxis_title='Kalori (kcal)',
                height=600,
                margin=dict(t=40, b=40, l=40, r=40),
                showlegend=True,
                paper_bgcolor=plot_config.get('paper_bgcolor', 'rgba(0,0,0,0)'),
                plot_bgcolor=plot_config.get('plot_bgcolor', 'rgba(0,0,0,0)'),
                font=dict(color=plot_config.get('font_color', '#1B5E20'), size=14)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if today_meals:
            st.markdown("---")
            st.markdown('<div class="glass-sm">', unsafe_allow_html=True)
            st.subheader("🍽️ Bugün Tükettiğiniz Yemekler")
            
            meals_df = pd.DataFrame(today_meals, columns=[
                'Yemek', 'Porsiyon (g)', 'Kalori', 'Protein (g)', 
                'Karbonhidrat (g)', 'Yağ (g)', 'Zaman'
            ])
            st.dataframe(meals_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("🔭 Henüz bugün yemek eklemediniz. Hemen ekleyin!")
    
    # TAB 3: YEMEK LİSTESİ
    with tab3:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.subheader("📚 Tanıyabildiğim Yemekler")
        st.markdown("Toplam **30 yemek** kategorisi")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        categories = {}
        for key, value in NUTRITION_DATA.items():
            cat = value['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(value)
        
        for category, foods in sorted(categories.items()):
            with st.expander(f"🍽️ {category} ({len(foods)} yemek)"):
                cols = st.columns(3)
                for idx, food in enumerate(sorted(foods, key=lambda x: x['name'])):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class='glass-sm' style='text-align: center; margin-bottom: 15px;'>
                            <div style='font-size: 3rem; margin-bottom: 10px;'>{food['emoji']}</div>
                            <h4 style='margin: 10px 0;'>{food['name']}</h4>
                            <p style='opacity: 0.85; font-size: 14px; margin: 5px 0;'>
                                🔥 {food['calories']} kcal
                            </p>
                            <p style='opacity: 0.75; font-size: 12px; margin: 5px 0;'>
                                🥩 {food['protein']}g | 🍞 {food['carbs']}g
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style='text-align: center; opacity: 0.7; padding: 20px; font-size: 14px;'>
    <p>Made with ❤️ by Computer Engineering Students</p>
    <p style='font-weight: bold;'>Tekirdağ Namık Kemal Üniversitesi - 2024/2025</p>
</div>
""", unsafe_allow_html=True)