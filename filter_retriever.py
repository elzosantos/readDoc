"""
Módulo para implementação de retriever personalizado com filtro de redundância.
"""

from typing import List
from langchain.schema import BaseRetriever, Document
from langchain.embeddings.base import Embeddings
from langchain_chroma import Chroma

from config import LAMBDA_MULT, K_DOCUMENTS


class RedundantFilterRetriever(BaseRetriever):
    """
    Retriever personalizado que utiliza Max Marginal Relevance Search
    para reduzir redundância nos documentos retornados.
    """
    
    embedding: Embeddings
    chroma: Chroma
    lambda_mult: float = LAMBDA_MULT
    k_documents: int = K_DOCUMENTS
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Busca documentos relevantes usando Max Marginal Relevance Search.
        
        Args:
            query (str): Consulta de busca
            
        Returns:
            List[Document]: Lista de documentos relevantes
        """
        # Gerar embedding da consulta
        query_embedding = self.embedding.embed_query(query)
        
        # Buscar documentos usando Max Marginal Relevance Search
        documents = self.chroma.max_marginal_relevance_search_by_vector(
            embedding=query_embedding,
            lambda_mult=self.lambda_mult,
            k=self.k_documents
        )
        
        return documents
    
    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """
        Versão assíncrona do método de busca.
        
        Args:
            query (str): Consulta de busca
            
        Returns:
            List[Document]: Lista vazia (não implementado)
        """
        # TODO: Implementar versão assíncrona se necessário
        return []
    