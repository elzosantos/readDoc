"""
Sistema de autenticação para a API.
"""

import os
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de segurança
security = HTTPBearer()

# Token de autenticação (em produção, use um sistema mais robusto)
API_TOKEN = os.getenv("API_TOKEN", "seu_token_secreto_aqui")

# Lista de tokens válidos (em produção, use um banco de dados)
VALID_TOKENS = {
    API_TOKEN,
    # Adicione mais tokens aqui se necessário
    "admin_token_123",
    "user_token_456"
}


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verifica se o token Bearer é válido.
    
    Args:
        credentials: Credenciais de autorização HTTP
        
    Returns:
        str: O token verificado
        
    Raises:
        HTTPException: Se o token for inválido
    """
    token = credentials.credentials
    
    if token not in VALID_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


def get_current_user(token: str = Depends(verify_token)) -> dict:
    """
    Obtém informações do usuário atual baseado no token.
    
    Args:
        token: Token verificado
        
    Returns:
        dict: Informações do usuário
    """
    # Em produção, você buscaria as informações do usuário no banco de dados
    user_info = {
        "token": token,
        "role": "admin" if token == API_TOKEN else "user",
        "permissions": ["read", "write"] if token == API_TOKEN else ["read"]
    }
    
    return user_info


def require_admin_role(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Verifica se o usuário tem permissões de administrador.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        dict: Usuário com permissões de admin
        
    Raises:
        HTTPException: Se o usuário não tiver permissões de admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissões insuficientes. Acesso de administrador necessário."
        )
    
    return current_user


def require_read_permission(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Verifica se o usuário tem permissão de leitura.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        dict: Usuário com permissões de leitura
        
    Raises:
        HTTPException: Se o usuário não tiver permissões de leitura
    """
    if "read" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissões insuficientes. Acesso de leitura necessário."
        )
    
    return current_user


def require_write_permission(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Verifica se o usuário tem permissão de escrita.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        dict: Usuário com permissões de escrita
        
    Raises:
        HTTPException: Se o usuário não tiver permissões de escrita
    """
    if "write" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissões insuficientes. Acesso de escrita necessário."
        )
    
    return current_user
