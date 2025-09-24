"""
Menu superior do sistema
"""

import streamlit as st
from auth_pages import is_authenticated, get_current_user, logout_user

def render_top_menu():
    """Renderiza o menu superior do sistema"""
    
    # Menu de navegação simples (sem header visual)
    if is_authenticated():
        # Botões de navegação em linha horizontal
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("👤 Perfil", key="profile_btn", help="Acessar perfil", use_container_width=True):
                st.session_state.current_page = "profile"
                st.rerun()
        
        with col2:
            if st.button("⚙️ Config", key="settings_btn", help="Configurações", use_container_width=True):
                st.session_state.current_page = "settings"
                st.rerun()
        
        with col3:
            if st.button("📊 Dashboard", key="dashboard_btn", help="Voltar ao dashboard", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
        
        with col4:
            if st.button("🚪 Logout", key="logout_btn", help="Sair do sistema", use_container_width=True):
                logout_user()