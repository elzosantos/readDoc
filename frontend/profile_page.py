"""
Página de perfil do usuário
"""

import streamlit as st
import requests
from typing import Dict, Optional
from auth_pages import get_auth_headers, is_authenticated, get_current_user

API_BASE_URL = "http://localhost:8000"

def render_profile_page():
    """Renderiza a página de perfil do usuário"""
    if not is_authenticated():
        st.error("❌ Você precisa estar logado para acessar esta página.")
        return
    
    user = get_current_user()
    
    st.title("👤 Meu Perfil")
    st.markdown("Gerencie suas informações pessoais e configurações da conta.")
    
    # Informações do usuário
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Informações Pessoais")
        
        with st.form("profile_form"):
            name = st.text_input(
                "Nome Completo",
                value=user.get("name", ""),
                help="Seu nome completo"
            )
            
            email = st.text_input(
                "Email",
                value=user.get("email", ""),
                disabled=True,
                help="Email não pode ser alterado"
            )
            
            role = st.text_input(
                "Perfil",
                value=user.get("role", "").title(),
                disabled=True,
                help="Perfil do usuário"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                save_button = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
            
            with col_btn2:
                cancel_button = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if save_button:
                if name and name != user.get("name", ""):
                    with st.spinner("Salvando alterações..."):
                        headers = get_auth_headers()
                        if headers:
                            try:
                                response = requests.put(
                                    f"{API_BASE_URL}/admin/users/{user['id']}",
                                    json={"name": name},
                                    headers=headers
                                )
                                if response.status_code == 200:
                                    result = response.json()
                                    if result.get("success"):
                                        st.success("✅ Perfil atualizado com sucesso!")
                                        # Atualizar dados na sessão
                                        st.session_state.user["name"] = name
                                        st.rerun()
                                    else:
                                        st.error("❌ Erro ao atualizar perfil")
                                else:
                                    st.error(f"❌ Erro: {response.status_code}")
                            except Exception as e:
                                st.error(f"❌ Erro: {str(e)}")
                        else:
                            st.error("❌ Erro de autenticação")
                else:
                    st.info("ℹ️ Nenhuma alteração foi feita")
            
            if cancel_button:
                st.rerun()
    
    with col2:
        st.subheader("🔐 Segurança")
        
        with st.form("password_form"):
            current_password = st.text_input(
                "Senha Atual",
                type="password",
                help="Digite sua senha atual"
            )
            
            new_password = st.text_input(
                "Nova Senha",
                type="password",
                help="Digite sua nova senha (mínimo 6 caracteres)"
            )
            
            confirm_password = st.text_input(
                "Confirmar Nova Senha",
                type="password",
                help="Confirme sua nova senha"
            )
            
            change_password_button = st.form_submit_button("🔑 Alterar Senha", use_container_width=True)
            
            if change_password_button:
                if not current_password:
                    st.error("❌ Digite sua senha atual")
                elif not new_password:
                    st.error("❌ Digite uma nova senha")
                elif len(new_password) < 6:
                    st.error("❌ A nova senha deve ter pelo menos 6 caracteres")
                elif new_password != confirm_password:
                    st.error("❌ As senhas não coincidem")
                else:
                    st.info("ℹ️ Funcionalidade de alteração de senha será implementada em breve")
    
    # Estatísticas da conta
    st.divider()
    st.subheader("📊 Estatísticas da Conta")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Perfil",
            user.get("role", "").title(),
            help="Tipo de usuário"
        )
    
    with col2:
        st.metric(
            "Status",
            "✅ Ativo",
            help="Status da conta"
        )
    
    with col3:
        # Simular data de criação (em um sistema real, viria do banco)
        st.metric(
            "Membro desde",
            "2024",
            help="Data de criação da conta"
        )
    
    # Informações adicionais
    st.divider()
    st.subheader("ℹ️ Informações Adicionais")
    
    with st.expander("🔧 Configurações Avançadas"):
        st.info("Configurações avançadas serão implementadas em versões futuras.")
    
    with st.expander("📱 Preferências de Interface"):
        st.info("Preferências de interface serão implementadas em versões futuras.")
    
    with st.expander("🔔 Notificações"):
        st.info("Configurações de notificação serão implementadas em versões futuras.")
