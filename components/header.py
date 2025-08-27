import streamlit as st

def set_custom_style():
    st.markdown("""
    <style>
      :root { --brand-fg:#17193b; --brand-accent:#d0e1f9; }

      /* header slim */
      .app-header-slim{
        margin: 6px 0 16px 0;
      }
      .hdr-line{
        position: relative;
        height: 1px;
        background: var(--brand-accent);
        margin: 0 0 14px 0;
      }
      .hdr-title{
        position: relative;
        display: inline-block;
        padding: 4px 14px;
        background: white;
        transform: translateY(-50%);
        color: var(--brand-fg);
        font-weight: 800;
        font-size: 28px;
        letter-spacing: .3px;
      }
      .hdr-wrap{
        display:flex; justify-content:center; align-items:center;
      }

      /* mobile */
      @media (max-width: 640px){
        .hdr-title{ font-size:20px; padding:3px 10px; }
      }

      /* streamlit polish */
      #MainMenu, footer {display:none;}
      .block-container{ padding-top: 0.6rem; }
    </style>
    """, unsafe_allow_html=True)

def render_header_centered(title:str="Broker Trading Barometer"):
    st.markdown("""
      <div class="app-header-slim">
        <div class="hdr-line"></div>
        <div class="hdr-wrap">
          <div class="hdr-title">""" + title + """</div>
        </div>
      </div>
    """, unsafe_allow_html=True)