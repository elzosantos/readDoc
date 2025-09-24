"""
Serviço de documentos para a API.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

from config import *
from filter_retriever import RedundantFilterRetriever


class DocumentService:
    """Serviço para gerenciar documentos e consultas."""
    
    def __init__(self):
        """Inicializa o serviço de documentos."""
        self.embedding_function = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.chat_model = ChatOpenAI(model=CHAT_MODEL)
        self.db: Optional[Chroma] = None
        self.documents_count: int = 0
        self.last_loaded: Optional[str] = None
        
        # Tentar carregar banco existente
        self._load_existing_database()
    
    def _load_existing_database(self) -> None:
        """Tenta carregar banco de dados existente."""
        try:
            if os.path.exists(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY):
                self.db = Chroma(
                    persist_directory=PERSIST_DIRECTORY,
                    embedding_function=self.embedding_function
                )
                # Contar documentos existentes
                self.documents_count = self.db._collection.count()
                print(f"✅ Banco de dados existente carregado com {self.documents_count} documentos")
        except Exception as e:
            print(f"⚠️ Não foi possível carregar banco existente: {e}")
            self.db = None
    
    async def load_document(
        self,
        file_path: str,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP
    ) -> int:
        """
        Carrega um documento no banco de dados.
        
        Args:
            file_path: Caminho para o arquivo
            chunk_size: Tamanho dos chunks
            chunk_overlap: Sobreposição entre chunks
            
        Returns:
            Número de documentos carregados
        """
        try:
            print(f"📄 Carregando documento: {file_path}")
            
            # Criar text splitter
            splitter = CharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separator=SEPARATOR
            )
            
            # Carregar e dividir documento
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load_and_split(splitter)
            
            # Criar ou atualizar banco de dados
            if self.db is None:
                self.db = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embedding_function,
                    persist_directory=PERSIST_DIRECTORY
                )
            else:
                # Adicionar documentos ao banco existente
                self.db.add_documents(documents)
            
            # Atualizar contadores
            self.documents_count = len(documents)
            self.last_loaded = datetime.now().isoformat()
            
            print(f"✅ Documento carregado: {self.documents_count} chunks")
            return self.documents_count
            
        except Exception as e:
            print(f"❌ Erro ao carregar documento: {e}")
            raise
    
    async def query_documents(
        self,
        query: str,
        lambda_mult: float = LAMBDA_MULT,
        k_documents: int = K_DOCUMENTS
    ) -> tuple[str, int]:
        """
        Executa uma consulta nos documentos.
        
        Args:
            query: Consulta a ser executada
            lambda_mult: Parâmetro para MMR
            k_documents: Número de documentos a retornar
            
        Returns:
            Tupla com (resposta, número de documentos usados)
        """
        if self.db is None:
            raise ValueError("Nenhum documento carregado")
        
        try:
            print(f"🔍 Executando consulta: {query}")
            
            # Criar retriever personalizado
            retriever = RedundantFilterRetriever(
                embedding=self.embedding_function,
                chroma=self.db,
                lambda_mult=lambda_mult,
                k_documents=k_documents
            )
            
            # Atualizar parâmetros do retriever se necessário
            # (Isso requer modificação no filter_retriever.py)
            
            # Criar chain de recuperação e resposta
            chain = RetrievalQA.from_chain_type(
                llm=self.chat_model,
                chain_type="stuff",
                retriever=retriever
            )
            
            # Executar consulta
            result = chain.invoke(query)
            answer = result.get('result', 'Nenhuma resposta encontrada.')
            
            # Obter número de documentos usados
            documents_used = k_documents  # Aproximação
            
            print(f"✅ Consulta executada com sucesso")
            return answer, documents_used
            
        except Exception as e:
            print(f"❌ Erro ao executar consulta: {e}")
            raise
    
    def has_documents(self) -> bool:
        """Verifica se há documentos carregados."""
        return self.db is not None and self.documents_count > 0
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna o status atual do serviço."""
        return {
            "has_documents": self.has_documents(),
            "documents_count": self.documents_count,
            "last_loaded": self.last_loaded,
            "database_path": PERSIST_DIRECTORY,
            "embedding_model": EMBEDDING_MODEL,
            "chat_model": CHAT_MODEL
        }
    
    async def clear_database(self) -> bool:
        """Limpa o banco de dados (cuidado!)."""
        try:
            if os.path.exists(PERSIST_DIRECTORY):
                import shutil
                shutil.rmtree(PERSIST_DIRECTORY)
                self.db = None
                self.documents_count = 0
                self.last_loaded = None
                print("🗑️ Banco de dados limpo")
                return True
            return False
        except Exception as e:
            print(f"❌ Erro ao limpar banco: {e}")
            return False
