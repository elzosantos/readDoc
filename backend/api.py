"""
API FastAPI para o sistema de busca de documentos.
"""

import os
import sys
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma

from config import *
from models import (
    LoadDocumentRequest,
    LoadDocumentResponse,
    QueryRequest,
    QueryResponse,
    HealthResponse,
    ErrorResponse,
    LoginRequest,
    RegisterRequest,
    AuthResponse,
    UserInfo,
    UserUpdateRequest,
    UserListResponse,
    UserResponse,
    LogoutResponse
)
from document_service import DocumentService
from auth import (
    verify_token,
    get_current_user,
    require_admin_role,
    require_read_permission,
    require_write_permission,
    require_user_management_permission,
    require_admin_panel_permission
)
from database import db_manager


# Carregar variáveis de ambiente
load_dotenv()


# Instância global do serviço de documentos
document_service: Optional[DocumentService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    global document_service
    
    # Inicialização
    print("🚀 Inicializando API de busca de documentos...")
    try:
        document_service = DocumentService()
        print("✅ Serviço de documentos inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar serviço: {e}")
        sys.exit(1)
    
    yield
    
    # Limpeza
    print("🔄 Finalizando API...")


# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Busca de Documentos com IA",
    description="""
    API para carregar documentos e fazer consultas inteligentes usando LangChain e OpenAI.
    
    ## Autenticação
    
    Esta API requer autenticação via Bearer Token. Inclua o token no header Authorization:
    
    ```
    Authorization: Bearer seu_token_aqui
    ```
    
    ## Tokens Disponíveis
    
    - **Admin Token**: `seu_token_secreto_aqui` (permissões completas)
    - **User Token**: `user_token_456` (apenas leitura)
    - **Admin Token 2**: `admin_token_123` (permissões completas)
    
    ## Permissões
    
    - **Leitura**: Consultar documentos e verificar status
    - **Escrita**: Carregar novos documentos
    - **Admin**: Acesso completo + gerenciamento de tokens
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Endpoint raiz com informações da API."""
    return HealthResponse(
        status="online",
        message="API de busca de documentos funcionando!",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check da API."""
    return HealthResponse(
        status="healthy",
        message="API funcionando corretamente",
        version="1.0.0"
    )


@app.post("/documents/load", response_model=LoadDocumentResponse)
async def load_document(
    request: LoadDocumentRequest,
    current_user: dict = Depends(require_write_permission)
):
    """
    Carrega um documento no banco de dados vetorial.
    
    - **file_path**: Caminho para o arquivo a ser carregado
    - **chunk_size**: Tamanho dos chunks de texto (opcional)
    - **chunk_overlap**: Sobreposição entre chunks (opcional)
    """
    try:
        if not os.path.exists(request.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arquivo não encontrado: {request.file_path}"
            )
        
        # Carregar documento usando o serviço
        documents_count = await document_service.load_document(
            file_path=request.file_path,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        
        return LoadDocumentResponse(
            success=True,
            message=f"Documento '{request.file_path}' carregado com sucesso!",
            documents_count=documents_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao carregar documento: {str(e)}"
        )


@app.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    current_user: dict = Depends(require_read_permission)
):
    """
    Executa uma consulta nos documentos carregados.
    
    - **query**: Pergunta ou consulta a ser executada
    - **lambda_mult**: Parâmetro para Max Marginal Relevance Search (opcional)
    - **k_documents**: Número de documentos a retornar (opcional)
    """
    try:
        # Verificar se há documentos carregados
        if not document_service.has_documents():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum documento carregado. Execute primeiro POST /documents/load"
            )
        
        # Executar consulta
        answer, documents_used = await document_service.query_documents(
            query=request.query,
            lambda_mult=request.lambda_mult,
            k_documents=request.k_documents
        )
        
        return QueryResponse(
            success=True,
            query=request.query,
            answer=answer,
            documents_used=documents_used
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao executar consulta: {str(e)}"
        )


@app.get("/documents/status")
async def get_documents_status(
    current_user: dict = Depends(require_read_permission)
):
    """Retorna o status dos documentos carregados."""
    try:
        status_info = await document_service.get_status()
        return {
            "has_documents": status_info["has_documents"],
            "documents_count": status_info.get("documents_count", 0),
            "last_loaded": status_info.get("last_loaded"),
            "database_path": PERSIST_DIRECTORY
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status: {str(e)}"
        )


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunk_size: int = Form(600),
    chunk_overlap: int = Form(200),
    current_user: dict = Depends(require_write_permission)
):
    """Carrega um documento via upload de arquivo."""
    try:
        # Verificar se o arquivo é válido
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome do arquivo não fornecido"
            )
        
        # Verificar extensão do arquivo
        allowed_extensions = ['.txt', '.pdf', '.docx', '.md']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não suportado. Tipos permitidos: {', '.join(allowed_extensions)}"
            )
        
        # Criar diretório temporário se não existir
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Salvar arquivo temporariamente
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        # Garantir que o arquivo seja salvo corretamente
        try:
            with open(temp_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
                buffer.flush()  # Garantir que os dados sejam escritos
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar arquivo temporário: {str(e)}"
            )
        
        try:
            # Carregar documento usando o serviço
            result = await document_service.load_document(
                file_path=temp_file_path,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            return LoadDocumentResponse(
                success=True,
                message=f"Documento '{file.filename}' carregado com sucesso!",
                documents_count=result
            )
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao carregar documento: {str(e)}"
        )


@app.get("/user/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Retorna informações do usuário atual."""
    return {
        "user": current_user,
        "message": "Informações do usuário obtidas com sucesso"
    }

@app.post("/test/upload")
async def test_upload(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_write_permission)
):
    """Endpoint de teste para upload de arquivos."""
    try:
        # Verificar se o arquivo é válido
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome do arquivo não fornecido"
            )
        
        # Verificar extensão do arquivo
        allowed_extensions = ['.txt', '.pdf', '.docx', '.md']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de arquivo não suportado. Tipos permitidos: {', '.join(allowed_extensions)}"
            )
        
        # Criar diretório temporário se não existir
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Salvar arquivo temporariamente
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        # Garantir que o arquivo seja salvo corretamente
        try:
            with open(temp_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
                buffer.flush()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao salvar arquivo temporário: {str(e)}"
            )
        
        # Verificar se o arquivo foi salvo
        if not os.path.exists(temp_file_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Arquivo não foi salvo corretamente"
            )
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(temp_file_path)
        
        # Limpar arquivo temporário
        try:
            os.remove(temp_file_path)
        except:
            pass
        
        return {
            "success": True,
            "message": f"Arquivo '{file.filename}' recebido com sucesso!",
            "file_size": file_size,
            "file_extension": file_extension,
            "user": current_user.get("name", "Unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no teste de upload: {str(e)}"
        )


@app.get("/admin/tokens")
async def list_valid_tokens(
    current_user: dict = Depends(require_admin_role)
):
    """Lista os tokens válidos (apenas para administradores)."""
    from auth import LEGACY_TOKENS
    return {
        "valid_tokens_count": len(LEGACY_TOKENS),
        "tokens": list(LEGACY_TOKENS.keys()),
        "message": "Lista de tokens legados (apenas para administradores)"
    }


# Endpoints de autenticação
@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Realiza login do usuário."""
    try:
        result = db_manager.authenticate_user(request.email, request.password)
        return AuthResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao realizar login: {str(e)}"
        )


@app.post("/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Registra um novo usuário."""
    try:
        result = db_manager.create_user(
            name=request.name,
            email=request.email,
            password=request.password,
            role=request.role
        )
        
        if result["success"]:
            return AuthResponse(
                success=True,
                message=result["message"],
                token=None,
                user=None
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao registrar usuário: {str(e)}"
        )


@app.post("/auth/logout", response_model=LogoutResponse)
async def logout(
    current_user: dict = Depends(get_current_user)
):
    """Realiza logout do usuário."""
    try:
        token = current_user.get("token")
        if token:
            result = db_manager.logout_user(token)
            return LogoutResponse(**result)
        else:
            return LogoutResponse(
                success=True,
                message="Logout realizado com sucesso"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao realizar logout: {str(e)}"
        )


@app.get("/auth/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Retorna informações do usuário atual."""
    try:
        user_info = {
            "id": current_user["user_id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "role": current_user["role"],
            "is_active": True,
            "created_at": "2024-01-01 00:00:00"  # TODO: Buscar do banco
        }
        
        return {
            "success": True,
            "message": "Informações do usuário obtidas com sucesso",
            "user": user_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao obter informações do usuário: {str(e)}"
        )


# Endpoints de gerenciamento de usuários (apenas para admin)
@app.get("/admin/users", response_model=UserListResponse)
async def list_users(
    current_user: dict = Depends(require_user_management_permission)
):
    """Lista todos os usuários (apenas para administradores)."""
    try:
        users = db_manager.get_all_users()
        return UserListResponse(
            success=True,
            users=users
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao listar usuários: {str(e)}"
        )


@app.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    current_user: dict = Depends(require_user_management_permission)
):
    """Atualiza um usuário (apenas para administradores)."""
    try:
        result = db_manager.update_user(
            user_id=user_id,
            name=request.name,
            email=request.email,
            role=request.role,
            is_active=request.is_active
        )
        
        if result["success"]:
            return UserResponse(
                success=True,
                message=result["message"],
                user=None
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao atualizar usuário: {str(e)}"
        )


@app.delete("/admin/users/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(require_user_management_permission)
):
    """Remove um usuário (apenas para administradores)."""
    try:
        result = db_manager.delete_user(user_id)
        
        if result["success"]:
            return UserResponse(
                success=True,
                message=result["message"],
                user=None
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao remover usuário: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções não tratadas."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="Erro interno do servidor",
            details=str(exc)
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

