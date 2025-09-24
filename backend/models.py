"""
Modelos Pydantic para a API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class LoadDocumentRequest(BaseModel):
    """Modelo para requisição de carregamento de documento."""
    file_path: str = Field(..., description="Caminho para o arquivo a ser carregado")
    chunk_size: Optional[int] = Field(600, description="Tamanho dos chunks de texto")
    chunk_overlap: Optional[int] = Field(200, description="Sobreposição entre chunks")


class LoadDocumentResponse(BaseModel):
    """Modelo para resposta de carregamento de documento."""
    success: bool = Field(..., description="Indica se o carregamento foi bem-sucedido")
    message: str = Field(..., description="Mensagem de status")
    documents_count: int = Field(..., description="Número de documentos processados")


class QueryRequest(BaseModel):
    """Modelo para requisição de consulta."""
    query: str = Field(..., description="Pergunta ou consulta a ser executada")
    lambda_mult: Optional[float] = Field(0.8, description="Parâmetro para Max Marginal Relevance Search")
    k_documents: Optional[int] = Field(4, description="Número de documentos a retornar")


class QueryResponse(BaseModel):
    """Modelo para resposta de consulta."""
    success: bool = Field(..., description="Indica se a consulta foi bem-sucedida")
    query: str = Field(..., description="Pergunta original")
    answer: str = Field(..., description="Resposta gerada")
    documents_used: Any = Field(..., description="Documentos utilizados na resposta")


class HealthResponse(BaseModel):
    """Modelo para resposta de health check."""
    status: str = Field(..., description="Status da API")
    message: str = Field(..., description="Mensagem de status")
    version: str = Field(..., description="Versão da API")


class ErrorResponse(BaseModel):
    """Modelo para resposta de erro."""
    error: str = Field(..., description="Tipo do erro")
    message: str = Field(..., description="Mensagem de erro")
    details: Optional[str] = Field(None, description="Detalhes adicionais do erro")


# Modelos para autenticação
class LoginRequest(BaseModel):
    """Modelo para requisição de login."""
    email: str = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")


class RegisterRequest(BaseModel):
    """Modelo para requisição de cadastro."""
    name: str = Field(..., description="Nome completo do usuário")
    email: str = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")
    role: Optional[str] = Field("user", description="Role do usuário (user/admin)")


class AuthResponse(BaseModel):
    """Modelo para resposta de autenticação."""
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem de status")
    token: Optional[str] = Field(None, description="Token de autenticação")
    user: Optional[dict] = Field(None, description="Dados do usuário")


class UserInfo(BaseModel):
    """Modelo para informações do usuário."""
    id: int = Field(..., description="ID do usuário")
    name: str = Field(..., description="Nome do usuário")
    email: str = Field(..., description="Email do usuário")
    role: str = Field(..., description="Role do usuário")
    is_active: bool = Field(..., description="Status ativo do usuário")
    created_at: str = Field(..., description="Data de criação")


class UserUpdateRequest(BaseModel):
    """Modelo para atualização de usuário."""
    name: Optional[str] = Field(None, description="Nome do usuário")
    email: Optional[str] = Field(None, description="Email do usuário")
    role: Optional[str] = Field(None, description="Role do usuário")
    is_active: Optional[bool] = Field(None, description="Status ativo do usuário")


class UserListResponse(BaseModel):
    """Modelo para resposta de lista de usuários."""
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    users: List[UserInfo] = Field(..., description="Lista de usuários")


class UserResponse(BaseModel):
    """Modelo para resposta de usuário."""
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem de status")
    user: Optional[UserInfo] = Field(None, description="Dados do usuário")


class LogoutResponse(BaseModel):
    """Modelo para resposta de logout."""
    success: bool = Field(..., description="Indica se o logout foi bem-sucedido")
    message: str = Field(..., description="Mensagem de status")
