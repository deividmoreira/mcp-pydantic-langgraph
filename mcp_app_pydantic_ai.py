# Estudo de Caso 3 - Sistema de IA Generativa com Agentes de IA, MCP (Model Context Protocol), LangGraph e PydanticAI
# Módulo da App com Agente de IA via PydanticAI

# Imports
import os
import asyncio
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio, MCPServerHTTP

# Carrega variáveis de ambiente
load_dotenv()

# Configurações dos servidores MCP
math_server = MCPServerStdio('python', args = ['mcp_server_math.py'], tool_prefix = 'math')
cust_server = MCPServerHTTP(url = "http://localhost:8000/sse", tool_prefix = "customers")

# Define o agente
agent = Agent(
    "google-gla:gemini-2.0-flash",
    mcp_servers = [math_server, cust_server]
)

# Função main
async def main():
    print("\nIniciando o Sistema com PydanticAI + MCP\n")
    async with agent.run_mcp_servers():
        while True:
            pergunta = input("User: ")
            resultado = await agent.run(pergunta)
            print("Assistant:   ", resultado.output)

# Execução
if __name__ == "__main__":
    asyncio.run(main())
