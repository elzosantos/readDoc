"""
Sistema de busca de documentos usando LangChain e ChromaDB.
Permite carregar documentos e fazer consultas usando IA.
"""

import argparse
import sys
from typing import Optional

import langchain
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma

from config import *
from filter_retriever import RedundantFilterRetriever


class DocumentSearchSystem:
    """Sistema principal para busca de documentos."""
    
    def __init__(self):
        """Inicializa o sistema de busca."""
        self.embedding_function = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        self.chat_model = ChatOpenAI(model=CHAT_MODEL)
        self.db: Optional[Chroma] = None
        
        # Configurar debug se necessário
        if DEBUG_MODE:
            langchain.debug = True
    
    def load_documents(self, file_path: str) -> None:
        """
        Carrega documentos de um arquivo para o banco de dados.
        
        Args:
            file_path (str): Caminho para o arquivo a ser carregado
        """
        try:
            print(f"Carregando arquivo: {file_path}")
            
            # Criar o text splitter
            splitter = CharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separator=SEPARATOR
            )
            
            # Carregar e dividir o arquivo
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load_and_split(splitter)
            
            # Criar banco de dados Chroma
            self.db = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_function,
                persist_directory=PERSIST_DIRECTORY
            )
            
            print("Arquivo carregado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
            sys.exit(1)
    
    def load_existing_database(self) -> None:
        """Carrega banco de dados existente."""
        try:
            self.db = Chroma(
                persist_directory=PERSIST_DIRECTORY,
                embedding_function=self.embedding_function
            )
        except Exception as e:
            print(f"Erro ao carregar banco de dados: {e}")
            sys.exit(1)
    
    def query_documents(self, query: str) -> str:
        """
        Executa uma consulta nos documentos.
        
        Args:
            query (str): Consulta a ser executada
            
        Returns:
            str: Resposta da consulta
        """
        if self.db is None:
            print("Erro: Banco de dados não carregado. Execute primeiro o modo 'load'.")
            return ""
        
        try:
            print(f"Executando consulta: {query}")
            
            # Criar retriever personalizado
            retriever = RedundantFilterRetriever(
                embedding=self.embedding_function,
                chroma=self.db
            )
            
            # Criar chain de recuperação e resposta
            chain = RetrievalQA.from_chain_type(
                llm=self.chat_model,
                chain_type="stuff",
                retriever=retriever
            )
            
            # Executar consulta
            result = chain.invoke(query)
            return result.get('result', 'Nenhuma resposta encontrada.')
            
        except Exception as e:
            print(f"Erro ao executar consulta: {e}")
            return ""


def setup_argument_parser() -> argparse.ArgumentParser:
    """Configura o parser de argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Sistema de busca de documentos usando IA"
    )
    parser.add_argument(
        "--load",
        choices=["load", "query"],
        default=DEFAULT_LOAD_MODE,
        help="Modo de operação: 'load' para carregar documentos, 'query' para consultar"
    )
    parser.add_argument(
        "--file",
        default=DEFAULT_FILE,
        help="Caminho para o arquivo a ser carregado"
    )
    parser.add_argument(
        "--task",
        default=DEFAULT_QUERY,
        help="Consulta a ser executada"
    )
    return parser


def main():
    """Função principal do programa."""
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurar parser de argumentos
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Criar sistema de busca
    search_system = DocumentSearchSystem()
    
    # Executar ação baseada no argumento
    if args.load == "load":
        search_system.load_documents(args.file)
    elif args.load == "query":
        search_system.load_existing_database()
        result = search_system.query_documents(args.task)
        print(f"\nResposta: {result}")


if __name__ == "__main__":
    main() 