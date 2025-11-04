# Estudo de Caso 3 - Sistema de IA Generativa com Agentes de IA, MCP (Model Context Protocol), LangGraph e PydanticAI
# Servidor MCP com Streamable HTTP e SSE

# Importa o módulo sqlite3 para interação com bancos SQLite
import sqlite3

# Importa o módulo json para manipulação de JSON
import json

# Importa a classe FastMCP para criar o servidor MCP
from mcp.server.fastmcp import FastMCP

# Importa BaseModel e EmailStr do Pydantic para validação de dados
from pydantic import BaseModel, EmailStr, Field

# Importa List e Optional para tipagem
from typing import List, Optional 

# Cria uma instância do servidor FastMCP com o namespace "Clientes"
mcp = FastMCP("Clientes")

# Abre uma conexão com o banco de dados SQLite, desabilitando a verificação de thread
conn = sqlite3.connect("clientes.db", check_same_thread=False)

# Cria um cursor para executar comandos SQL
cursor = conn.cursor()

# Executa comando SQL para criar a tabela de clientes, caso não exista
cursor.execute("""
CREATE TABLE IF NOT EXISTS tb_clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
)
""")

# Grava as alterações no banco de dados
conn.commit()

# --- Modelos Pydantic para Validação ---
class ClienteBase(BaseModel):
    """Modelo base para um cliente, usado para entrada de criação."""
    name: str = Field(..., min_length=1, description="Nome do cliente")
    email: EmailStr = Field(..., description="Email do cliente")

class ClienteDB(ClienteBase):
    """Modelo para um cliente como armazenado no banco de dados, inclui o ID."""
    id: int = Field(..., description="ID único do cliente")

class ClienteResponse(BaseModel):
    """Modelo para respostas de cliente, pode incluir dados ou erro."""
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    error: Optional[str] = None

class ListaClientesResponse(BaseModel):
    """Modelo para a lista de todos os clientes."""
    clientes: List[ClienteDB]


# --- Ferramentas MCP com Validação Pydantic ---

@mcp.tool()
def create_customer(cliente_data: ClienteBase) -> str:
    # Documentação: cadastrar um cliente com nome e email
    """Cadastrar um cliente com nome e email.
    Espera um objeto JSON com 'name' (string) e 'email' (string de email válida).
    Retorna os dados do cliente criado em formato JSON ou um erro.
    """
    try:
        # Os dados já são validados pelo Pydantic através da anotação de tipo
        # Insere o novo cliente na tabela tb_clientes
        cursor.execute(
            "INSERT INTO tb_clientes (name, email) VALUES (?, ?)",
            (cliente_data.name, cliente_data.email)
        )
        conn.commit()
        customer_id = cursor.lastrowid
        response_data = ClienteDB(id=customer_id, name=cliente_data.name, email=cliente_data.email)
        return response_data.model_dump_json()
    except sqlite3.IntegrityError: # Captura erro de email duplicado, por exemplo
        error_response = ClienteResponse(error="Erro ao criar cliente: email já existe ou dados inválidos.")
        return error_response.model_dump_json()
    except Exception as e:
        error_response = ClienteResponse(error=f"Erro inesperado: {str(e)}")
        return error_response.model_dump_json()

@mcp.tool()
def get_customer(customer_id: int) -> str:
    # Documentação: ler dados de um cliente pelo ID
    """Ler dados de um cliente pelo ID.
    Espera um 'customer_id' (inteiro).
    Retorna os dados do cliente em formato JSON ou um erro se não encontrado.
    """
    if not isinstance(customer_id, int) or customer_id <= 0:
        error_response = ClienteResponse(error="ID do cliente inválido. Deve ser um inteiro positivo.")
        return error_response.model_dump_json()

    cursor.execute(
        "SELECT id, name, email FROM tb_clientes WHERE id = ?", (customer_id,)
    )
    row = cursor.fetchone()

    if row:
        cliente = ClienteDB(id=row[0], name=row[1], email=row[2])
        return cliente.model_dump_json()
    
    error_response = ClienteResponse(error="Cliente não encontrado")
    return error_response.model_dump_json()

@mcp.tool()
def list_clientes() -> str:
    # Documentação: listar todos os clientes
    """Listar todos os clientes.
    Retorna uma lista de todos os clientes em formato JSON.
    """
    cursor.execute("SELECT id, name, email FROM tb_clientes")
    rows = cursor.fetchall()
    clientes_db = [ClienteDB(id=r[0], name=r[1], email=r[2]) for r in rows]
    response_data = ListaClientesResponse(clientes=clientes_db)
    return response_data.model_dump_json()

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":

    # Inicia o servidor MCP com transporte HTTP streaming (deve ser usado quando executar o script mcp_app_langgraph.py)
    mcp.run(transport="streamable-http")

    # Inicia o servidor MCP com transporte SSE (deve ser usado quando executar o script mcp_app_pydantic_ai.py)
    #mcp.run(transport="sse")



    
