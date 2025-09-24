"""
Modelos Pydantic para a API de busca de documentos.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class LoadDocumentRequest(BaseModel):
    """Modelo para requisição de carregamento de documento."""
    
    file_path: str = Field(
        ...,
        description="Caminho para o arquivo a ser carregado",
        example="historia.txt"
    )
    chunk_size: Optional[int] = Field(
        default=600,
        description="Tamanho dos chunks de texto",
        ge=100,
        le=2000
    )
    chunk_overlap: Optional[int] = Field(
        default=200,
        description="Sobreposição entre chunks",
        ge=0,
        le=500
    )


class LoadDocumentResponse(BaseModel):
    """Modelo para resposta de carregamento de documento."""
    
    success: bool = Field(..., description="Indica se o carregamento foi bem-sucedido")
    message: str = Field(..., description="Mensagem de status")
    documents_count: Optional[int] = Field(
        default=None,
        description="Número de documentos carregados"
    )


class QueryRequest(BaseModel):
    """Modelo para requisição de consulta."""
    
    query: str = Field(
        ...,
        description="Pergunta ou consulta a ser executada",
        min_length=1,
        max_length=1000,
        example="Quem foi Pedro Alvares Cabral?"
    )
    lambda_mult: Optional[float] = Field(
        default=0.8,
        description="Parâmetro para Max Marginal Relevance Search",
        ge=0.0,
        le=1.0
    )
    k_documents: Optional[int] = Field(
        default=4,
        description="Número de documentos a retornar",
        ge=1,
        le=10
    )


class QueryResponse(BaseModel):
    """Modelo para resposta de consulta."""
    
    success: bool = Field(..., description="Indica se a consulta foi bem-sucedida")
    query: str = Field(..., description="Consulta original")
    answer: str = Field(..., description="Resposta da consulta")
    documents_used: Optional[int] = Field(
        default=None,
        description="Número de documentos utilizados na resposta"
    )


class HealthResponse(BaseModel):
    """Modelo para resposta de health check."""
    
    status: str = Field(..., description="Status da API")
    message: str = Field(..., description="Mensagem de status")
    version: str = Field(..., description="Versão da API")


class ErrorResponse(BaseModel):
    """Modelo para resposta de erro."""
    
    success: bool = Field(default=False, description="Indica que houve erro")
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem de erro detalhada")
    details: Optional[str] = Field(
        default=None,
        description="Detalhes adicionais do erro"
    )

