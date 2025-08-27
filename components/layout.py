import os
import base64
import streamlit as st

# --- Design tokens ---
NAVY = "#0E1333"          # fundo da sidebar
TEXT = "#17193B"          # texto principal
BLUE_BG = "#F4F6FB"       # fundo de inputs
WHITE = "#FFFFFF"         # fundo do app
MUTED = "#C9D1E9"         # subtítulo claro


def set_global_styles():
    """Estilos globais e da sidebar."""
    st.markdown(f"""
    <style>
      /* === SIDEBAR === */
      section[data-testid="stSidebar"] {{
        background-color: {NAVY} !important;
        padding: 20px;
      }}

      /* === INPUTS COM FUNDO CLARO E TEXTO ESCURO === */
      section[data-testid="stSidebar"] input,
      section[data-testid="stSidebar"] textarea,
      section[data-testid="stSidebar"] select {{
        background-color: {BLUE_BG} !important;
        color: {TEXT} !important;
        border-radius: 10px !important;
      }}

      section[data-testid="stSidebar"] input::placeholder,
      section[data-testid="stSidebar"] textarea::placeholder {{
        color: rgba(23, 25, 59, 0.6) !important;
      }}

      /* === SELECTBOX (compatibilidade versões novas Streamlit) === */
      section[data-testid="stSidebar"] div[data-baseweb="select"],
      section[data-testid="stSidebar"] div[data-baseweb="select"] div[role="combobox"],
      section[data-testid="stSidebar"] div[data-baseweb="select"] input {{
        background-color: {BLUE_BG} !important;
        color: {TEXT} !important;
        border-radius: 10px !important;
      }}

      section[data-testid="stSidebar"] [role="listbox"] {{
        background-color: {WHITE} !important;
        color: {TEXT} !important;
        border-radius: 10px !important;
        box-shadow: 0 6px 24px rgba(0,0,0,0.12) !important;
      }}

      section[data-testid="stSidebar"] [role="option"] {{
        color: {TEXT} !important;
      }}

      section[data-testid="stSidebar"] [role="option"]:hover {{
        background-color: {BLUE_BG} !important;
      }}

      /* === SECTION TITLE (fora da sidebar) === */
      section:not([data-testid="stSidebar"]) .section-title {{
        margin: 6px 0 12px 0;
        font-size: 1.15rem;
        font-weight: 600;
        color: {TEXT};
      }}
    </style>
    """, unsafe_allow_html=True)


def render_sidebar_brand(
    title: str = "Broker Trading Barometer",
    subtitle: str | None = None,
    logo_path: str = "assets/logo.png",
):
    """Renderiza o brand fixo no topo da sidebar."""
    encoded = None
    if logo_path and os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
        except Exception:
            encoded = None

    if encoded:
        logo_html = f'<img src="data:image/png;base64,{encoded}" alt="Logo" style="max-width:180px;height:auto;margin-bottom:10px;" />'
    else:
        # fallback: só o título se logo não existir
        logo_html = f"<div style='font-weight:800;color:{WHITE};font-size:1.2rem;margin-bottom:10px;'>{title}</div>"

    st.sidebar.markdown(
        f"""
        <div style="position:sticky;top:0;z-index:999;background:{NAVY};
                    padding-bottom:12px;margin-bottom:12px;
                    display:flex;flex-direction:column;align-items:center;text-align:center;">
            {logo_html}
            <div style="font-weight:800;color:{WHITE};line-height:1.2;font-size:1.05rem;">
                {title}
            </div>
            {f'<div style="color:{MUTED};font-size:0.9rem;margin-top:6px;">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


def sidebar_divider():
    """Linha divisória discreta na sidebar."""
    st.sidebar.markdown(
        "<hr style='border:0;height:1px;background:rgba(255,255,255,0.2);margin:10px 0;'>",
        unsafe_allow_html=True,
    )


def section_title(text: str):
    """Título de seção padronizado no corpo da página."""
    st.markdown(f"<div class='section-title'>{text}</div>", unsafe_allow_html=True)
