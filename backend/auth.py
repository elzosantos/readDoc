"""
Sistema de autenticação para a API com banco de dados de usuários.
"""

import os
from typing import Dict, Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from database import db_manager

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de segurança
security = HTTPBearer()

# Manter compatibilidade com tokens antigos (para transição)
LEGACY_TOKENS = {
    "seu_token_secreto_aqui": {"role": "admin", "permissions": ["read_documents", "write_documents", "manage_users"]},
    "admin_token_123": {"role": "admin", "permissions": ["read_documents", "write_documents", "manage_users"]},
    "user_token_456": {"role": "user", "permissions": ["read_documents", "write_documents"]},
}

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Verifica se o token é válido (novo sistema de usuários ou tokens legados).
    
    Args:
        credentials: Credenciais de autorização HTTP
        
    Returns:
        Dict: Dados do usuário autenticado
        
    Raises:
        HTTPException: Se o token for inválido
    """
    token = credentials.credentials
    
    # Primeiro, tentar verificar como token de usuário
    user_result = db_manager.verify_token(token)
    if user_result["success"]:
        user = user_result["user"]
        permissions = db_manager.get_user_permissions(user["role"])
        return {
            "user_id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "permissions": permissions,
            "token_type": "user",
            "token": token
        }
    
    # Se não for token de usuário, verificar tokens legados
    if token in LEGACY_TOKENS:
        legacy_user = LEGACY_TOKENS[token]
        return {
            "user_id": None,
            "name": "Legacy User",
            "email": "legacy@system.com",
            "role": legacy_user["role"],
            "permissions": legacy_user["permissions"],
            "token_type": "legacy",
            "token": token
        }
    
    # Token inválido
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_user(current_user: Dict = Depends(verify_token)) -> Dict:
    """
    Obtém informações do usuário atual.
    
    Args:
        current_user: Usuário atual verificado
        
    Returns:
        Dict: Informações do usuário
    """
    return current_user

def require_permission(permission: str):
    """
    Decorator para verificar permissão específica.
    
    Args:
        permission: Nome da permissão requerida
        
    Returns:
        function: Função de verificação de permissão
    """
    def permission_checker(current_user: Dict = Depends(verify_token)) -> Dict:
        if permission not in current_user["permissions"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado: Requer permissão '{permission}'",
            )
        return current_user
    return permission_checker

def require_admin_role(current_user: Dict = Depends(verify_token)) -> Dict:
    """
    Verifica se o usuário tem permissões de administrador.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        Dict: Usuário com permissões de admin
        
    Raises:
        HTTPException: Se o usuário não tiver permissões de admin
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Requer privilégios de administrador",
        )
    return current_user

def require_read_permission(current_user: Dict = Depends(verify_token)) -> Dict:
    """
    Verifica se o usuário tem permissão de leitura.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        Dict: Usuário com permissões de leitura
        
    Raises:
        HTTPException: Se o usuário não tiver permissões de leitura
    """
    if "read_documents" not in current_user["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Requer permissão de leitura",
        )
    return current_user

def require_write_permission(current_user: Dict = Depends(verify_token)) -> Dict:
    """
    Verifica se o usuário tem permissão de escrita.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        Dict: Usuário com permissões de escrita
        
    Raises:
        HTTPException: Se o usuário não tiver permissões de escrita
    """
    if "write_documents" not in current_user["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Requer permissão de escrita",
        )
    return current_user

def require_user_management_permission(current_user: Dict = Depends(verify_token)) -> Dict:
    """
    Verifica se o usuário tem permissão de gerenciamento de usuários.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        Dict: Usuário com permissões de gerenciamento
        
    Raises:
        HTTPException: Se o usuário não tiver permissões de gerenciamento
    """
    if "manage_users" not in current_user["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Requer permissão de gerenciamento de usuários",
        )
    return current_user

def require_admin_panel_permission(current_user: Dict = Depends(verify_token)) -> Dict:
    """
    Verifica se o usuário tem permissão para acessar painel administrativo.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        Dict: Usuário com permissões de painel admin
        
    Raises:
        HTTPException: Se o usuário não tiver permissões de painel admin
    """
    if "view_admin_panel" not in current_user["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Requer permissão para acessar painel administrativo",
        )
    return current_user