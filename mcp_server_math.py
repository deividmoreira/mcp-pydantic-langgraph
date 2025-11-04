# Estudo de Caso 3 - Sistema de IA Generativa com Agentes de IA, MCP (Model Context Protocol), LangGraph e PydanticAI
# Servidor MCP com STDIO

# Importa a classe FastMCP do módulo que fornece a funcionalidade MCP
from mcp.server.fastmcp import FastMCP

# Cria uma instância do servidor FastMCP com o namespace "Math"
mcp = FastMCP("Math")

# Define um prompt de usuário com o decorator mcp.prompt()
@mcp.prompt()
def example_prompt(question: str) -> str:
    # Retorna o template de prompt para o assistente de matemática
    return f"""
    Você é um assistente de matemática. Responda à questão.
    Questão: {question}
    """

# Define o prompt do sistema com instruções gerais
@mcp.prompt()
def system_prompt() -> str:
    # Retorna o template de prompt para o sistema
    return """
    Você é um assistente de IA, use as ferramentas se necessário.
    """

# Registra um recurso de saudação usando URI template greeting://{name}
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    # Retorna uma saudação personalizada
    return f"Hello, {name}!"

# Registra um recurso de configuração usando URI config://app
@mcp.resource("config://app")
def get_config() -> str:
    # Retorna a configuração da aplicação (exemplo)
    return "Config da App"

# Define uma ferramenta de soma com o decorator mcp.tool()
@mcp.tool()
def add(a: int, b: int) -> int:
    """Some 2 números"""
    # Calcula e retorna a soma de dois inteiros
    return a + b

# Define uma ferramenta de multiplicação com o decorator mcp.tool()
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiplique 2 números"""
    # Calcula e retorna o produto de dois inteiros
    return a * b

# Verifica se este módulo está sendo executado como script principal
if __name__ == "__main__":
    
    # Inicia o loop de execução do MCP via STDIO
    mcp.run()





