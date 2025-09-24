"""
Serviço para gerenciamento de documentos e consultas.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from config import *


class DocumentService:
    """Serviço para gerenciamento de documentos e consultas."""
    
    def __init__(self):
        """Inicializa o serviço de documentos."""
        if not OPENAI_API_KEY:
            raise Exception("OPENAI_API_KEY não está configurada. Configure a variável de ambiente OPENAI_API_KEY.")
        
        self.llm = ChatOpenAI(
            model_name=MODEL_NAME,
            temperature=TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )
        
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        # Inicializar ou carregar banco de dados vetorial
        if os.path.exists(PERSIST_DIRECTORY):
            print("✅ Banco de dados existente carregado")
            self.vectorstore = Chroma(
                persist_directory=PERSIST_DIRECTORY,
                embedding_function=self.embeddings
            )
        else:
            print("📁 Criando novo banco de dados vetorial")
            self.vectorstore = Chroma(
                persist_directory=PERSIST_DIRECTORY,
                embedding_function=self.embeddings
            )
    
    async def load_document(self, file_path: str, chunk_size: int = 600, chunk_overlap: int = 200) -> int:
        """
        Carrega um documento no banco de dados vetorial.
        
        Args:
            file_path: Caminho para o arquivo
            chunk_size: Tamanho dos chunks
            chunk_overlap: Sobreposição entre chunks
            
        Returns:
            Número de documentos carregados
        """
        try:
            # Carregar documento baseado na extensão
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith('.docx'):
                loader = Docx2txtLoader(file_path)
            else:
                loader = TextLoader(file_path, encoding='utf-8')
            
            documents = loader.load()
            
            # Dividir em chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            chunks = text_splitter.split_documents(documents)
            
            # Adicionar ao banco vetorial
            self.vectorstore.add_documents(chunks)
            
            return len(chunks)
            
        except Exception as e:
            print(f"Erro detalhado ao carregar documento: {str(e)}")
            print(f"Tipo do erro: {type(e).__name__}")
            raise Exception(f"Erro ao carregar documento: {str(e)}")
    
    async def query_documents(self, query: str, lambda_mult: float = 0.8, k_documents: int = 4) -> tuple:
        """
        Executa uma consulta nos documentos.
        
        Args:
            query: Pergunta a ser respondida
            lambda_mult: Parâmetro para Max Marginal Relevance Search
            k_documents: Número de documentos a retornar
            
        Returns:
            Tupla com (resposta, documentos_utilizados)
        """
        try:
            # Criar retriever
            retriever = self.vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "lambda_mult": lambda_mult,
                    "k": k_documents
                }
            )
            
            # Criar prompt template
            prompt_template = """Use as seguintes informações do contexto para responder à pergunta.
            Se você não souber a resposta baseada no contexto, diga que não tem informações suficientes.

            Contexto: {context}

            Pergunta: {question}

            Resposta:"""

            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Criar chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": PROMPT}
            )
            
            # Executar consulta
            result = qa_chain({"query": query})
            
            # Obter documentos utilizados
            docs = retriever.get_relevant_documents(query)
            documents_used = [doc.page_content for doc in docs]
            
            return result["result"], documents_used
            
        except Exception as e:
            raise Exception(f"Erro ao executar consulta: {str(e)}")
    
    def has_documents(self) -> bool:
        """Verifica se há documentos carregados."""
        try:
            # Tentar fazer uma consulta simples para verificar se há documentos
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 1})
            docs = retriever.get_relevant_documents("test")
            return len(docs) > 0
        except:
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna o status do serviço."""
        try:
            has_docs = self.has_documents()
            
            if has_docs:
                # Contar documentos
                retriever = self.vectorstore.as_retriever(search_kwargs={"k": 1000})
                docs = retriever.get_relevant_documents("test")
                count = len(docs)
            else:
                count = 0
            
            return {
                "has_documents": has_docs,
                "documents_count": count,
                "last_loaded": datetime.now().isoformat() if has_docs else None
            }
        except Exception as e:
            return {
                "has_documents": False,
                "documents_count": 0,
                "error": str(e)
            }
