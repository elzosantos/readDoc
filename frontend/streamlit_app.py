"""
Frontend Streamlit para o Sistema de Busca de Documentos com IA
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import time

# Importar módulos de autenticação
from auth_pages import (
    render_auth_page, 
    logout_user, 
    is_authenticated, 
    get_current_user, 
    has_permission, 
    is_admin,
    get_auth_headers
)
from user_management import render_user_management_page

# Configuração da página
st.set_page_config(
    page_title="LLMChat - Sistema de Busca de Documentos",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações da API
API_BASE_URL = "http://localhost:8000"
DEFAULT_TOKEN = "seu_token_secreto_aqui"

# Inicializar estado da sessão
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "auth"  # Começar com página de autenticação
if "api_token" not in st.session_state:
    st.session_state.api_token = DEFAULT_TOKEN
if "documents_status" not in st.session_state:
    st.session_state.documents_status = None
if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None

def generate_chat_name(query: str) -> str:
    """Gera um nome para o chat baseado na consulta (máximo 15 caracteres)"""
    # Palavras-chave importantes para identificar o contexto
    keywords = {
        "brasil": "Brasil",
        "descobriu": "Descoberta",
        "capital": "Capital",
        "pedro": "Pedro",
        "cabral": "Cabral",
        "história": "História",
        "colônia": "Colônia",
        "independência": "Independência",
        "império": "Império",
        "república": "República",
        "guerra": "Guerra",
        "revolução": "Revolução",
        "governo": "Governo",
        "presidente": "Presidente",
        "economia": "Economia",
        "cultura": "Cultura",
        "arte": "Arte",
        "literatura": "Literatura",
        "religião": "Religião",
        "educação": "Educação"
    }
    
    query_lower = query.lower()
    
    # Procurar por palavras-chave
    for keyword, name in keywords.items():
        if keyword in query_lower:
            return name[:15]
    
    # Se não encontrar palavra-chave, usar as primeiras palavras
    words = query.split()[:3]
    name = " ".join(words)
    return name[:15]

def save_current_chat_to_history():
    """Salva o chat atual no histórico"""
    if st.session_state.current_chat:
        # Gerar nome baseado na primeira pergunta
        first_query = st.session_state.current_chat[0].get("query", "Chat")
        chat_name = generate_chat_name(first_query)
        
        # Criar entrada do histórico
        chat_entry = {
            "name": chat_name,
            "messages": st.session_state.current_chat.copy(),
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "id": len(st.session_state.chat_history) + 1
        }
        
        # Adicionar ao histórico
        st.session_state.chat_history.append(chat_entry)
        
        # Limpar chat atual
        st.session_state.current_chat = []

def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
    """Faz requisição para a API com autenticação"""
    try:
        # Usar token de autenticação se disponível, senão usar token legado
        token = st.session_state.get("auth_token") or st.session_state.api_token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("❌ Token inválido! Verifique sua autenticação.")
            return None
        else:
            st.error(f"❌ Erro na API: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Não foi possível conectar à API. Verifique se o servidor está rodando.")
        return None
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
        return None

def render_sidebar():
    """Renderiza a sidebar com histórico e configurações"""
    with st.sidebar:
        st.title("🤖 LLMChat")
        
        # Informações do usuário
        if is_authenticated():
            user = get_current_user()
            st.subheader("👤 Usuário")
            st.write(f"**Nome:** {user.get('name', 'N/A')}")
            st.write(f"**Email:** {user.get('email', 'N/A')}")
            st.write(f"**Perfil:** {user.get('role', 'N/A').title()}")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
            
            st.divider()
        else:
            st.subheader("🔐 Autenticação")
            st.info("Faça login para acessar o sistema")
            
            if st.button("🔐 Fazer Login", use_container_width=True):
                st.session_state.current_page = "auth"
                st.rerun()
            
            st.divider()
        
        # Configuração do token (apenas para tokens legados)
        if not is_authenticated():
            st.subheader("🔧 Token Legado")
            token = st.text_input(
                "Bearer Token",
                value=st.session_state.api_token,
                type="password",
                help="Token legado para autenticação na API"
            )
            st.session_state.api_token = token
            
            # Botão para testar conexão
            if st.button("🔍 Testar Conexão"):
                with st.spinner("Testando conexão..."):
                    result = make_api_request("/health")
                    if result:
                        st.success("✅ Conexão estabelecida!")
                    else:
                        st.error("❌ Falha na conexão")
            
            st.divider()
        
        # Navegação
        st.subheader("📋 Navegação")
        
        # Botão Novo Chat
        if st.button("🆕 Novo Chat", use_container_width=True):
            # Salvar chat atual no histórico se houver mensagens
            save_current_chat_to_history()
            st.rerun()
        
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.current_page = "chat"
        if st.button("📁 Gerenciar Arquivos", use_container_width=True):
            st.session_state.current_page = "files"
        if st.button("⚙️ Configurações", use_container_width=True):
            st.session_state.current_page = "settings"
        
        # Página de gestão de usuários (apenas para admin)
        if is_authenticated() and is_admin():
            if st.button("👥 Gerenciar Usuários", use_container_width=True):
                st.session_state.current_page = "user_management"
        
        st.divider()
        
        # Histórico de chat
        st.subheader("📚 Histórico de Chats")
        
        if st.session_state.chat_history:
            for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):
                chat_name = chat.get('name', f"Chat {len(st.session_state.chat_history) - i}")
                with st.expander(f"{chat_name}"):
                    st.write(f"**Data:** {chat['timestamp']}")
                    if len(chat['messages']) > 0:
                        first_query = chat['messages'][0].get('query', '')
                        st.write(f"**Primeira pergunta:** {first_query[:50]}...")
                    if st.button(f"Ver {chat_name}", key=f"view_{i}"):
                        st.session_state.current_page = "chat"
                        st.session_state.selected_chat = chat
        else:
            st.info("Nenhum chat ainda")
        
        st.divider()
        
        # Informações do sistema
        st.subheader("ℹ️ Sistema")
        if st.button("🔄 Atualizar Status"):
            with st.spinner("Atualizando..."):
                status = make_api_request("/documents/status")
                if status:
                    st.session_state.documents_status = status
                    st.success("Status atualizado!")
        
        if st.session_state.documents_status:
            st.metric("Documentos Carregados", st.session_state.documents_status.get("documents_count", 0))
            if st.session_state.documents_status.get("last_loaded"):
                st.caption(f"Último carregamento: {st.session_state.documents_status['last_loaded']}")
        
        st.divider()
        
        # Footer
        st.caption("LLMChat v1.0.0")
        st.caption("Sistema de Busca de Documentos com IA")

def render_chat_page():
    """Renderiza a página principal de chat"""
    # Verificar permissão de leitura
    if not has_permission("read_documents"):
        st.error("❌ Você não tem permissão para acessar esta funcionalidade.")
        return
    
    st.title("💬 Chat com IA")
    st.markdown("Faça perguntas sobre os documentos carregados no sistema.")
    
    # Verificar se há um chat selecionado do histórico
    if hasattr(st.session_state, 'selected_chat') and st.session_state.selected_chat:
        # Exibir chat selecionado
        st.info(f"📚 Visualizando: {st.session_state.selected_chat.get('name', 'Chat')}")
        
        # Botão para voltar ao chat atual
        if st.button("🆕 Voltar ao Chat Atual"):
            st.session_state.selected_chat = None
            st.rerun()
        
        # Exibir mensagens do chat selecionado
        for message in st.session_state.selected_chat['messages']:
            with st.chat_message("user"):
                st.write(message["query"])
            
            with st.chat_message("assistant"):
                st.write(message["answer"])
                documents_used = message.get("documents_used", [])
                
                # Garantir que documents_used seja sempre uma lista
                if not isinstance(documents_used, list):
                    documents_used = []
                
                if documents_used and len(documents_used) > 0:
                    with st.expander("📄 Documentos utilizados"):
                        for doc in documents_used:
                            if isinstance(doc, str):
                                st.text(doc[:200] + "..." if len(doc) > 200 else doc)
                            else:
                                st.text(str(doc)[:200] + "..." if len(str(doc)) > 200 else str(doc))
    else:
        # Área de chat atual
        chat_container = st.container()
        
        with chat_container:
            # Exibir mensagens do chat atual
            for message in st.session_state.current_chat:
                with st.chat_message("user"):
                    st.write(message["query"])
                
                with st.chat_message("assistant"):
                    st.write(message["answer"])
                    documents_used = message.get("documents_used", [])
                    
                    # Garantir que documents_used seja sempre uma lista
                    if not isinstance(documents_used, list):
                        documents_used = []
                    
                    if documents_used and len(documents_used) > 0:
                        with st.expander("📄 Documentos utilizados"):
                            for doc in documents_used:
                                if isinstance(doc, str):
                                    st.text(doc[:200] + "..." if len(doc) > 200 else doc)
                                else:
                                    st.text(str(doc)[:200] + "..." if len(str(doc)) > 200 else str(doc))
    
    # Input para nova pergunta
    if prompt := st.chat_input("Digite sua pergunta aqui..."):
        # Adicionar pergunta do usuário
        with st.chat_message("user"):
            st.write(prompt)
        
        # Processar pergunta
        with st.chat_message("assistant"):
            with st.spinner("Processando sua pergunta..."):
                response = make_api_request("/query", "POST", {"query": prompt})
                
                if response and response.get("success"):
                    answer = response.get("answer", "Não foi possível obter uma resposta.")
                    documents_used = response.get("documents_used", [])
                    
                    # Garantir que documents_used seja sempre uma lista
                    if not isinstance(documents_used, list):
                        documents_used = []
                    
                    st.write(answer)
                    
                    if documents_used and len(documents_used) > 0:
                        with st.expander("📄 Documentos utilizados"):
                            for doc in documents_used:
                                if isinstance(doc, str):
                                    st.text(doc[:200] + "..." if len(doc) > 200 else doc)
                                else:
                                    st.text(str(doc)[:200] + "..." if len(str(doc)) > 200 else str(doc))
                    
                    # Salvar no chat atual
                    chat_entry = {
                        "query": prompt,
                        "answer": answer,
                        "documents_used": documents_used,
                        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    st.session_state.current_chat.append(chat_entry)
                    
                else:
                    st.error("❌ Não foi possível processar sua pergunta. Verifique se há documentos carregados.")

def render_files_page():
    """Renderiza a página de gerenciamento de arquivos"""
    # Verificar permissão de escrita
    if not has_permission("write_documents"):
        st.error("❌ Você não tem permissão para gerenciar arquivos.")
        return
    
    st.title("📁 Gerenciar Arquivos")
    st.markdown("Visualize e carregue documentos no sistema.")
    
    # Status dos documentos
    st.subheader("📊 Status dos Documentos")
    
    if st.button("🔄 Atualizar Status", key="refresh_status"):
        with st.spinner("Atualizando status..."):
            status = make_api_request("/documents/status")
            if status:
                st.session_state.documents_status = status
                st.rerun()
    
    if st.session_state.documents_status:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Documentos Carregados",
                st.session_state.documents_status.get("documents_count", 0)
            )
        
        with col2:
            st.metric(
                "Sistema Ativo",
                "✅ Sim" if st.session_state.documents_status.get("has_documents") else "❌ Não"
            )
        
        with col3:
            last_loaded = st.session_state.documents_status.get("last_loaded", "Nunca")
            st.metric("Último Carregamento", last_loaded)
    
    st.divider()
    
    # Carregar novos documentos
    st.subheader("📤 Carregar Novo Documento")
    
    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "Escolha um arquivo para carregar",
        type=['txt', 'pdf', 'docx', 'md'],
        help="Selecione um arquivo de texto, PDF, Word ou Markdown"
    )
    
    if uploaded_file is not None:
        st.info(f"📄 Arquivo selecionado: {uploaded_file.name}")
        
        with st.form("load_document_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                chunk_size = st.number_input(
                    "Tamanho do Chunk",
                    min_value=100,
                    max_value=2000,
                    value=600,
                    help="Tamanho dos pedaços de texto para processamento"
                )
            
            with col2:
                chunk_overlap = st.slider(
                    "Sobreposição entre Chunks",
                    min_value=0,
                    max_value=200,
                    value=200,
                    help="Quantos caracteres se sobrepõem entre chunks consecutivos"
                )
            
            submitted = st.form_submit_button("📤 Carregar Documento", use_container_width=True)
            
            if submitted:
                with st.spinner("Carregando documento..."):
                    # Ler o conteúdo do arquivo
                    file_content = uploaded_file.read()
                    
                    # Enviar para o backend
                    try:
                        headers = get_auth_headers()
                        if not headers:
                            st.error("❌ Você precisa estar logado para carregar documentos")
                            return
                        
                        # Preparar dados para envio
                        files = {
                            'file': (uploaded_file.name, file_content, uploaded_file.type)
                        }
                        data = {
                            'chunk_size': chunk_size,
                            'chunk_overlap': chunk_overlap
                        }
                        
                        # Fazer requisição para o backend
                        response = requests.post(
                            "http://localhost:8000/documents/upload",
                            files=files,
                            data=data,
                            headers={"Authorization": headers["Authorization"]}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if result.get("success"):
                                st.success(f"✅ {result.get('message')}")
                                st.info(f"📊 {result.get('documents_count')} documentos processados")
                                # Atualizar status
                                status = make_api_request("/documents/status")
                                if status:
                                    st.session_state.documents_status = status
                                st.rerun()
                            else:
                                st.error("❌ Falha ao carregar documento")
                        else:
                            st.error(f"❌ Erro: {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Erro ao carregar documento: {str(e)}")
    
    # Alternativa: carregar por caminho (para arquivos no backend)
    st.subheader("📁 Ou carregar arquivo do servidor")
    
    with st.form("load_server_file_form"):
        file_path = st.text_input(
            "Caminho do Arquivo no Servidor",
            placeholder="ex: historia.txt ou /caminho/arquivo.pdf",
            help="Caminho do arquivo no servidor backend"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            chunk_size_server = st.number_input(
                "Tamanho do Chunk",
                min_value=100,
                max_value=2000,
                value=600,
                help="Tamanho dos pedaços de texto para processamento",
                key="chunk_size_server"
            )
        
        with col2:
            chunk_overlap_server = st.slider(
                "Sobreposição entre Chunks",
                min_value=0,
                max_value=200,
                value=200,
                help="Quantos caracteres se sobrepõem entre chunks consecutivos",
                key="chunk_overlap_server"
            )
        
        submitted_server = st.form_submit_button("📤 Carregar do Servidor", use_container_width=True)
        
        if submitted_server and file_path:
            with st.spinner("Carregando documento do servidor..."):
                response = make_api_request(
                    "/documents/load",
                    "POST",
                    {
                        "file_path": file_path,
                        "chunk_size": chunk_size_server,
                        "chunk_overlap": chunk_overlap_server
                    }
                )
                
                if response and response.get("success"):
                    st.success(f"✅ {response.get('message')}")
                    st.info(f"📊 {response.get('documents_count')} documentos processados")
                    # Atualizar status
                    status = make_api_request("/documents/status")
                    if status:
                        st.session_state.documents_status = status
                    st.rerun()
                else:
                    st.error("❌ Falha ao carregar documento")
        elif submitted_server and not file_path:
            st.error("❌ Por favor, informe o caminho do arquivo.")
    
    # Lista de arquivos disponíveis no backend
    st.subheader("📋 Arquivos Disponíveis no Servidor")
    
    # Mostrar arquivos na pasta backend
    try:
        backend_files = []
        backend_path = "../backend"
        if os.path.exists(backend_path):
            for file in os.listdir(backend_path):
                if file.endswith(('.txt', '.pdf', '.docx', '.md')):
                    backend_files.append(file)
        
        if backend_files:
            st.write("Arquivos encontrados na pasta backend:")
            for file in backend_files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {file}")
                with col2:
                    if st.button(f"Carregar", key=f"load_{file}"):
                        with st.spinner(f"Carregando {file}..."):
                            response = make_api_request(
                                "/documents/load",
                                "POST",
                                {
                                    "file_path": f"../backend/{file}",
                                    "chunk_size": 600,
                                    "chunk_overlap": 200
                                }
                            )
                            
                            if response and response.get("success"):
                                st.success(f"✅ {file} carregado com sucesso!")
                                st.rerun()
                            else:
                                st.error(f"❌ Falha ao carregar {file}")
        else:
            st.info("Nenhum arquivo de documento encontrado na pasta backend.")
    except Exception as e:
        st.error(f"❌ Erro ao listar arquivos: {str(e)}")

def render_settings_page():
    """Renderiza a página de configurações"""
    st.title("⚙️ Configurações")
    
    st.subheader("🔐 Autenticação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Token Atual:**")
        st.code(st.session_state.api_token)
    
    with col2:
        st.write("**Tokens Disponíveis:**")
        st.code("""
seu_token_secreto_aqui (Admin)
admin_token_123 (Admin)
user_token_456 (User)
        """)
    
    st.subheader("🌐 Configurações da API")
    
    api_url = st.text_input(
        "URL da API",
        value=API_BASE_URL,
        help="URL base da API backend"
    )
    
    st.subheader("💾 Gerenciar Histórico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Limpar Histórico", use_container_width=True):
            st.session_state.chat_history = []
            st.success("Histórico limpo!")
            st.rerun()
    
    with col2:
        if st.button("💾 Exportar Histórico", use_container_width=True):
            if st.session_state.chat_history:
                # Criar arquivo JSON com histórico
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_history_{timestamp}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.chat_history, f, ensure_ascii=False, indent=2)
                
                st.success(f"Histórico exportado para {filename}")
            else:
                st.info("Nenhum histórico para exportar")
    
    st.subheader("ℹ️ Informações do Sistema")
    
    # Testar conexão com API
    if st.button("🔍 Testar Conexão com API"):
        with st.spinner("Testando..."):
            health = make_api_request("/health")
            user_info = make_api_request("/user/me")
            
            if health and user_info:
                st.success("✅ API funcionando corretamente")
                
                with st.expander("Informações do Usuário"):
                    st.json(user_info)
            else:
                st.error("❌ Problemas na conexão com a API")

def main():
    """Função principal da aplicação"""
    
    # Verificar autenticação
    if not is_authenticated() and st.session_state.current_page != "auth":
        st.session_state.current_page = "auth"
    
    # Renderizar página de autenticação se necessário
    if st.session_state.current_page == "auth":
        render_auth_page()
        return
    
    # Renderizar sidebar apenas se autenticado
    render_sidebar()
    
    # Renderizar página principal baseada na seleção
    if st.session_state.current_page == "chat":
        render_chat_page()
    elif st.session_state.current_page == "files":
        render_files_page()
    elif st.session_state.current_page == "settings":
        render_settings_page()
    elif st.session_state.current_page == "user_management":
        render_user_management_page()
    else:
        # Página padrão
        render_chat_page()

if __name__ == "__main__":
    main()
