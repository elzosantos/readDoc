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
if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"
if "api_token" not in st.session_state:
    st.session_state.api_token = DEFAULT_TOKEN
if "documents_status" not in st.session_state:
    st.session_state.documents_status = None

def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
    """Faz requisição para a API com autenticação"""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.api_token}",
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
        
        # Configuração do token
        st.subheader("🔐 Autenticação")
        token = st.text_input(
            "Bearer Token",
            value=st.session_state.api_token,
            type="password",
            help="Token para autenticação na API"
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
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.current_page = "chat"
        if st.button("📁 Gerenciar Arquivos", use_container_width=True):
            st.session_state.current_page = "files"
        if st.button("⚙️ Configurações", use_container_width=True):
            st.session_state.current_page = "settings"
        
        st.divider()
        
        # Histórico de chat
        st.subheader("📚 Histórico de Chats")
        
        if st.session_state.chat_history:
            for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):
                with st.expander(f"Chat {len(st.session_state.chat_history) - i}"):
                    st.write(f"**Pergunta:** {chat['query'][:50]}...")
                    st.write(f"**Data:** {chat['timestamp']}")
                    if st.button(f"Ver Chat {len(st.session_state.chat_history) - i}", key=f"view_{i}"):
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
    st.title("💬 Chat com IA")
    st.markdown("Faça perguntas sobre os documentos carregados no sistema.")
    
    # Área de chat
    chat_container = st.container()
    
    with chat_container:
        # Exibir histórico de mensagens
        for message in st.session_state.chat_history:
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
                    
                    # Salvar no histórico
                    chat_entry = {
                        "query": prompt,
                        "answer": answer,
                        "documents_used": documents_used,
                        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    st.session_state.chat_history.append(chat_entry)
                    
                else:
                    st.error("❌ Não foi possível processar sua pergunta. Verifique se há documentos carregados.")

def render_files_page():
    """Renderiza a página de gerenciamento de arquivos"""
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
    
    with st.form("load_document_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            file_path = st.text_input(
                "Caminho do Arquivo",
                placeholder="ex: historia.txt ou C:/caminho/arquivo.pdf",
                help="Caminho completo para o arquivo a ser carregado"
            )
        
        with col2:
            chunk_size = st.number_input(
                "Tamanho do Chunk",
                min_value=100,
                max_value=2000,
                value=600,
                help="Tamanho dos pedaços de texto para processamento"
            )
        
        chunk_overlap = st.slider(
            "Sobreposição entre Chunks",
            min_value=0,
            max_value=200,
            value=200,
            help="Quantos caracteres se sobrepõem entre chunks consecutivos"
        )
        
        submitted = st.form_submit_button("📤 Carregar Documento", use_container_width=True)
        
        if submitted and file_path:
            if os.path.exists(file_path):
                with st.spinner("Carregando documento..."):
                    response = make_api_request(
                        "/documents/load",
                        "POST",
                        {
                            "file_path": file_path,
                            "chunk_size": chunk_size,
                            "chunk_overlap": chunk_overlap
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
            else:
                st.error("❌ Arquivo não encontrado. Verifique o caminho.")
        elif submitted and not file_path:
            st.error("❌ Por favor, informe o caminho do arquivo.")
    
    # Lista de arquivos disponíveis
    st.subheader("📋 Arquivos Disponíveis")
    
    # Mostrar arquivos na pasta atual
    current_files = []
    for file in os.listdir("."):
        if file.endswith(('.txt', '.pdf', '.docx', '.md')):
            current_files.append(file)
    
    if current_files:
        st.write("Arquivos encontrados na pasta atual:")
        for file in current_files:
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
                                "file_path": file,
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
        st.info("Nenhum arquivo de documento encontrado na pasta atual.")

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
    
    # Renderizar sidebar
    render_sidebar()
    
    # Renderizar página principal baseada na seleção
    if st.session_state.current_page == "chat":
        render_chat_page()
    elif st.session_state.current_page == "files":
        render_files_page()
    elif st.session_state.current_page == "settings":
        render_settings_page()

if __name__ == "__main__":
    main()
