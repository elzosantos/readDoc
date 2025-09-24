"""
Sistema de banco de dados para autenticação e gestão de usuários
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import os

class DatabaseManager:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados e cria as tabelas necessárias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de usuários
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de sessões/tokens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Tabela de permissões
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    permission TEXT NOT NULL,
                    granted BOOLEAN DEFAULT 1,
                    UNIQUE(role, permission)
                )
            """)
            
            conn.commit()
            
            # Limpar sessões expiradas
            self._cleanup_expired_sessions()
            
            # Inserir permissões padrão
            self._insert_default_permissions(cursor)
            
            # Criar usuário admin padrão se não existir
            self._create_default_admin(cursor)
            
            conn.commit()
    
    def _cleanup_expired_sessions(self):
        """Remove sessões expiradas do banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_sessions WHERE expires_at < ?", (datetime.now(),))
                conn.commit()
        except Exception as e:
            print(f"Erro ao limpar sessões expiradas: {e}")
    
    def _insert_default_permissions(self, cursor):
        """Insere as permissões padrão para cada role"""
        permissions = [
            # Admin - todas as permissões
            ('admin', 'read_documents', True),
            ('admin', 'write_documents', True),
            ('admin', 'manage_users', True),
            ('admin', 'view_admin_panel', True),
            ('admin', 'delete_documents', True),
            ('admin', 'view_system_logs', True),
            
            # User - permissões limitadas
            ('user', 'read_documents', True),
            ('user', 'write_documents', True),
            ('user', 'manage_users', False),
            ('user', 'view_admin_panel', False),
            ('user', 'delete_documents', False),
            ('user', 'view_system_logs', False),
        ]
        
        for role, permission, granted in permissions:
            cursor.execute("""
                INSERT OR IGNORE INTO permissions (role, permission, granted)
                VALUES (?, ?, ?)
            """, (role, permission, granted))
    
    def _create_default_admin(self, cursor):
        """Cria o usuário admin padrão se não existir"""
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # Criar admin padrão
            admin_password = "admin123"  # Senha padrão
            password_hash = self._hash_password(admin_password)
            
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            """, ("Administrador", "admin@system.com", password_hash, "admin"))
            
            print("✅ Usuário admin padrão criado:")
            print("   Email: admin@system.com")
            print("   Senha: admin123")
    
    def _hash_password(self, password: str) -> str:
        """Gera hash da senha usando SHA-256 com salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verifica se a senha está correta"""
        try:
            salt, password_hash = stored_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except:
            return False
    
    def create_user(self, name: str, email: str, password: str, role: str = "user") -> Dict:
        """Cria um novo usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar se email já existe
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    return {"success": False, "message": "Email já cadastrado"}
                
                # Criar usuário
                password_hash = self._hash_password(password)
                cursor.execute("""
                    INSERT INTO users (name, email, password_hash, role)
                    VALUES (?, ?, ?, ?)
                """, (name, email, password_hash, role))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                return {
                    "success": True,
                    "message": "Usuário criado com sucesso",
                    "user_id": user_id
                }
        except Exception as e:
            return {"success": False, "message": f"Erro ao criar usuário: {str(e)}"}
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """Autentica um usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, name, email, password_hash, role, is_active
                    FROM users WHERE email = ?
                """, (email,))
                
                user = cursor.fetchone()
                if not user:
                    return {"success": False, "message": "Email ou senha incorretos"}
                
                user_id, name, email, password_hash, role, is_active = user
                
                if not is_active:
                    return {"success": False, "message": "Usuário desativado"}
                
                if not self._verify_password(password, password_hash):
                    return {"success": False, "message": "Email ou senha incorretos"}
                
                # Gerar token de sessão
                token = secrets.token_urlsafe(32)
                expires_at = datetime.now() + timedelta(hours=8)
                
                cursor.execute("""
                    INSERT INTO user_sessions (user_id, token, expires_at)
                    VALUES (?, ?, ?)
                """, (user_id, token, expires_at))
                
                conn.commit()
                
                return {
                    "success": True,
                    "message": "Login realizado com sucesso",
                    "token": token,
                    "user": {
                        "id": user_id,
                        "name": name,
                        "email": email,
                        "role": role
                    }
                }
        except Exception as e:
            return {"success": False, "message": f"Erro na autenticação: {str(e)}"}
    
    def verify_token(self, token: str) -> Dict:
        """Verifica se o token é válido e retorna dados do usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT u.id, u.name, u.email, u.role, u.is_active, s.expires_at
                    FROM users u
                    JOIN user_sessions s ON u.id = s.user_id
                    WHERE s.token = ? AND s.expires_at > ?
                """, (token, datetime.now()))
                
                user = cursor.fetchone()
                if not user:
                    return {"success": False, "message": "Token inválido ou expirado"}
                
                user_id, name, email, role, is_active, expires_at = user
                
                if not is_active:
                    return {"success": False, "message": "Usuário desativado"}
                
                # Renovar token se estiver próximo do vencimento (menos de 2 horas)
                time_until_expiry = expires_at - datetime.now()
                if time_until_expiry.total_seconds() < 7200:  # 2 horas em segundos
                    new_expires_at = datetime.now() + timedelta(hours=8)
                    cursor.execute("""
                        UPDATE user_sessions 
                        SET expires_at = ?
                        WHERE token = ?
                    """, (new_expires_at, token))
                    conn.commit()
                
                return {
                    "success": True,
                    "user": {
                        "id": user_id,
                        "name": name,
                        "email": email,
                        "role": role
                    }
                }
        except Exception as e:
            return {"success": False, "message": f"Erro na verificação: {str(e)}"}
    
    def get_user_permissions(self, role: str) -> List[str]:
        """Retorna as permissões de um role"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT permission FROM permissions
                    WHERE role = ? AND granted = 1
                """, (role,))
                
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            return []
    
    def has_permission(self, role: str, permission: str) -> bool:
        """Verifica se um role tem uma permissão específica"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT granted FROM permissions
                    WHERE role = ? AND permission = ?
                """, (role, permission))
                
                result = cursor.fetchone()
                return result and result[0]
        except:
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Retorna todos os usuários (apenas para admin)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, name, email, role, is_active, created_at
                    FROM users
                    ORDER BY created_at DESC
                """)
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        "id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "role": row[3],
                        "is_active": bool(row[4]),
                        "created_at": row[5]
                    })
                
                return users
        except Exception as e:
            return []
    
    def update_user(self, user_id: int, name: str = None, email: str = None, 
                   role: str = None, is_active: bool = None) -> Dict:
        """Atualiza dados de um usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = ?")
                    params.append(name)
                
                if email is not None:
                    updates.append("email = ?")
                    params.append(email)
                
                if role is not None:
                    updates.append("role = ?")
                    params.append(role)
                
                if is_active is not None:
                    updates.append("is_active = ?")
                    params.append(is_active)
                
                if not updates:
                    return {"success": False, "message": "Nenhum campo para atualizar"}
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(user_id)
                
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                
                conn.commit()
                
                return {"success": True, "message": "Usuário atualizado com sucesso"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao atualizar usuário: {str(e)}"}
    
    def delete_user(self, user_id: int) -> Dict:
        """Remove um usuário (apenas para admin)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar se é o último admin
                cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1")
                admin_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
                user_role = cursor.fetchone()
                
                if user_role and user_role[0] == 'admin' and admin_count <= 1:
                    return {"success": False, "message": "Não é possível remover o último administrador"}
                
                # Remover sessões do usuário
                cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
                
                # Remover usuário
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                
                conn.commit()
                
                return {"success": True, "message": "Usuário removido com sucesso"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao remover usuário: {str(e)}"}
    
    def logout_user(self, token: str) -> Dict:
        """Remove a sessão do usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
                conn.commit()
                
                return {"success": True, "message": "Logout realizado com sucesso"}
        except Exception as e:
            return {"success": False, "message": f"Erro no logout: {str(e)}"}

# Instância global do gerenciador de banco
db_manager = DatabaseManager()
