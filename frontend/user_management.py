"""
Página de gestão de usuários para administradores
"""

import streamlit as st
import requests
from typing import Optional, Dict, List
from auth_pages import make_auth_request, get_auth_headers, is_admin

def render_user_management_page():
    """Renderiza a página de gestão de usuários"""
    if not is_admin():
        st.error("❌ Acesso negado. Apenas administradores podem gerenciar usuários.")
        return
    
    st.title("👥 Gerenciamento de Usuários")
    st.markdown("Gerencie usuários do sistema")
    
    # Botões de ação
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Atualizar Lista", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("➕ Novo Usuário", use_container_width=True):
            st.session_state.show_create_user = True
            st.rerun()
    
    with col3:
        if st.button("📊 Estatísticas", use_container_width=True):
            st.session_state.show_user_stats = True
            st.rerun()
    
    # Mostrar formulário de criação de usuário
    if st.session_state.get("show_create_user", False):
        render_create_user_form()
        return
    
    # Mostrar estatísticas
    if st.session_state.get("show_user_stats", False):
        render_user_statistics()
        return
    
    # Lista de usuários
    render_users_list()

def render_create_user_form():
    """Renderiza formulário de criação de usuário"""
    st.subheader("➕ Criar Novo Usuário")
    
    with st.form("create_user_form"):
        name = st.text_input("👤 Nome Completo", placeholder="Nome do usuário")
        email = st.text_input("📧 Email", placeholder="email@exemplo.com")
        password = st.text_input("🔒 Senha", type="password", placeholder="Senha temporária")
        role = st.selectbox("👑 Perfil", ["user", "admin"], help="user: Usuário comum, admin: Administrador")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            create_button = st.form_submit_button("✅ Criar Usuário", use_container_width=True)
        
        with col2:
            cancel_button = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if create_button:
            if name and email and password:
                with st.spinner("Criando usuário..."):
                    headers = get_auth_headers()
                    if not headers:
                        st.error("❌ Você precisa estar logado para criar usuários")
                        return
                    
                    try:
                        response = requests.post("http://localhost:8000/auth/register", 
                                               json={"name": name, "email": email, "password": password, "role": role},
                                               headers=headers)
                        if response.status_code == 200:
                            result = response.json()
                            if result.get("success"):
                                st.success("✅ Usuário criado com sucesso!")
                                st.session_state.show_create_user = False
                                st.rerun()
                            else:
                                st.error("❌ Erro ao criar usuário")
                        else:
                            st.error(f"❌ Erro: {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
            else:
                st.error("❌ Preencha todos os campos obrigatórios")
        
        if cancel_button:
            st.session_state.show_create_user = False
            st.rerun()

def render_user_statistics():
    """Renderiza estatísticas dos usuários"""
    st.subheader("📊 Estatísticas dos Usuários")
    
    with st.spinner("Carregando estatísticas..."):
        users = get_users_list()
        
        if users:
            # Calcular estatísticas
            total_users = len(users)
            active_users = len([u for u in users if u.get("is_active", True)])
            admin_users = len([u for u in users if u.get("role") == "admin"])
            regular_users = len([u for u in users if u.get("role") == "user"])
            
            # Mostrar métricas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👥 Total de Usuários", total_users)
            
            with col2:
                st.metric("✅ Usuários Ativos", active_users)
            
            with col3:
                st.metric("👑 Administradores", admin_users)
            
            with col4:
                st.metric("👤 Usuários Comuns", regular_users)
            
            # Gráfico de distribuição por role
            st.subheader("📈 Distribuição por Perfil")
            
            import pandas as pd
            df = pd.DataFrame({
                "Perfil": ["Administradores", "Usuários Comuns"],
                "Quantidade": [admin_users, regular_users]
            })
            
            st.bar_chart(df.set_index("Perfil"))
            
            # Lista de usuários inativos
            inactive_users = [u for u in users if not u.get("is_active", True)]
            if inactive_users:
                st.subheader("⚠️ Usuários Inativos")
                for user in inactive_users:
                    st.warning(f"👤 {user['name']} ({user['email']}) - {user['role']}")
        else:
            st.error("❌ Não foi possível carregar as estatísticas")
    
    if st.button("🔙 Voltar à Lista"):
        st.session_state.show_user_stats = False
        st.rerun()

def render_users_list():
    """Renderiza lista de usuários"""
    st.subheader("👥 Lista de Usuários")
    
    with st.spinner("Carregando usuários..."):
        users = get_users_list()
        
        if users:
            # Filtros
            col1, col2 = st.columns([2, 1])
            
            with col1:
                search_term = st.text_input("🔍 Buscar usuário", placeholder="Nome ou email...")
            
            with col2:
                role_filter = st.selectbox("👑 Filtrar por perfil", ["Todos", "admin", "user"])
            
            # Aplicar filtros
            filtered_users = users
            
            if search_term:
                filtered_users = [
                    u for u in filtered_users 
                    if search_term.lower() in u.get("name", "").lower() 
                    or search_term.lower() in u.get("email", "").lower()
                ]
            
            if role_filter != "Todos":
                filtered_users = [u for u in filtered_users if u.get("role") == role_filter]
            
            # Mostrar usuários
            if filtered_users:
                for user in filtered_users:
                    with st.expander(f"👤 {user['name']} ({user['email']})"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**📧 Email:** {user['email']}")
                            st.write(f"**👑 Perfil:** {user['role']}")
                            st.write(f"**📅 Criado em:** {user.get('created_at', 'N/A')}")
                            
                            status = "✅ Ativo" if user.get("is_active", True) else "❌ Inativo"
                            st.write(f"**Status:** {status}")
                        
                        with col2:
                            if st.button(f"✏️ Editar", key=f"edit_{user['id']}"):
                                st.session_state.edit_user_id = user['id']
                                st.session_state.edit_user_data = user
                                st.rerun()
                            
                            if st.button(f"🗑️ Remover", key=f"delete_{user['id']}"):
                                st.session_state.delete_user_id = user['id']
                                st.session_state.delete_user_name = user['name']
                                st.rerun()
            else:
                st.info("🔍 Nenhum usuário encontrado com os filtros aplicados")
        else:
            st.error("❌ Não foi possível carregar a lista de usuários")
    
    # Mostrar formulário de edição
    if st.session_state.get("edit_user_id"):
        render_edit_user_form()
    
    # Mostrar confirmação de exclusão
    if st.session_state.get("delete_user_id"):
        render_delete_user_confirmation()

def render_edit_user_form():
    """Renderiza formulário de edição de usuário"""
    user_id = st.session_state.edit_user_id
    user_data = st.session_state.edit_user_data
    
    st.subheader(f"✏️ Editar Usuário: {user_data['name']}")
    
    with st.form("edit_user_form"):
        name = st.text_input("👤 Nome Completo", value=user_data.get("name", ""))
        email = st.text_input("📧 Email", value=user_data.get("email", ""))
        role = st.selectbox("👑 Perfil", ["user", "admin"], 
                           index=0 if user_data.get("role") == "user" else 1)
        is_active = st.checkbox("✅ Usuário Ativo", value=user_data.get("is_active", True))
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            save_button = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
        
        with col2:
            cancel_button = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if save_button:
            with st.spinner("Salvando alterações..."):
                headers = get_auth_headers()
                if not headers:
                    st.error("❌ Você precisa estar logado para atualizar usuários")
                    return
                
                try:
                    response = requests.put(f"http://localhost:8000/admin/users/{user_id}", 
                                          json={"name": name, "email": email, "role": role, "is_active": is_active},
                                          headers=headers)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            st.success("✅ Usuário atualizado com sucesso!")
                            st.session_state.edit_user_id = None
                            st.session_state.edit_user_data = None
                            st.rerun()
                        else:
                            st.error("❌ Erro ao atualizar usuário")
                    else:
                        st.error(f"❌ Erro: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        
        if cancel_button:
            st.session_state.edit_user_id = None
            st.session_state.edit_user_data = None
            st.rerun()

def render_delete_user_confirmation():
    """Renderiza confirmação de exclusão de usuário"""
    user_id = st.session_state.delete_user_id
    user_name = st.session_state.delete_user_name
    
    st.warning(f"⚠️ Tem certeza que deseja remover o usuário **{user_name}**?")
    st.error("🚨 Esta ação não pode ser desfeita!")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("✅ Confirmar Exclusão", use_container_width=True):
            with st.spinner("Removendo usuário..."):
                headers = get_auth_headers()
                if not headers:
                    st.error("❌ Você precisa estar logado para remover usuários")
                    return
                
                try:
                    response = requests.delete(f"http://localhost:8000/admin/users/{user_id}", headers=headers)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            st.success("✅ Usuário removido com sucesso!")
                            st.session_state.delete_user_id = None
                            st.session_state.delete_user_name = None
                            st.rerun()
                        else:
                            st.error("❌ Erro ao remover usuário")
                    else:
                        st.error(f"❌ Erro: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
    
    with col2:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state.delete_user_id = None
            st.session_state.delete_user_name = None
            st.rerun()

def get_users_list() -> List[Dict]:
    """Obtém lista de usuários da API"""
    headers = get_auth_headers()
    if not headers:
        return []
    
    try:
        response = requests.get("http://localhost:8000/admin/users", headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get("users", [])
    except:
        pass
    return []
