# Estudo de Caso 3 - Sistema de IA Generativa com Agentes de IA, MCP (Model Context Protocol), LangGraph e PydanticAI
# Módulo da App com Agente de IA via LangGraph

# Importa o módulo os para acesso ao sistema de arquivos e variáveis de ambiente
import os

# Importa o módulo asyncio para programação assíncrona
import asyncio

# Carrega variáveis de ambiente do arquivo .env
from dotenv import load_dotenv

# Importa o tipo List para tipagem de listas
from typing import List

# Importa TypedDict para definir dicionários tipados
from typing_extensions import TypedDict

# Importa Annotated para anotar tipos com metadados adicionais
from typing import Annotated

# Importa ChatPromptTemplate e MessagesPlaceholder para templates de prompts
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# Importa o LLM da Google Generative AI para gerar respostas de chat
from langchain_google_genai import ChatGoogleGenerativeAI

# Importa ferramentas predefinidas para controlar fluxo condicional no grafo
from langgraph.prebuilt import tools_condition, ToolNode

# Importa StateGraph, START e END para construção do grafo de estados
from langgraph.graph import StateGraph, START, END

# Importa AnyMessage e add_messages para manipulação de mensagens no grafo
from langgraph.graph.message import AnyMessage, add_messages

# Importa MemorySaver para persistir checkpoints de memória do agente
from langgraph.checkpoint.memory import MemorySaver

# Importa o cliente MCP que suporta múltiplos servidores
from langchain_mcp_adapters.client import MultiServerMCPClient

# Importa funções para carregar ferramentas definidas no servidor MCP
from langchain_mcp_adapters.tools import load_mcp_tools

# Importa função para carregar prompts definidos no servidor MCP
from langchain_mcp_adapters.prompts import load_mcp_prompt

# Carrega efetivamente as variáveis de ambiente do arquivo .env
load_dotenv()

# Cria um cliente MCP configurado para servidores "math" e "customers"
client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            "args": ["mcp_server_math.py"],
            "transport": "stdio",
        },
        "customers": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        }
    }
)

# Define função assíncrona para criar e compilar o grafo de estados do agente
async def create_graph(math_session, clientes_session):
    
    # Instancia o modelo LLM da Google Generative AI com chave de API
    llm = ChatGoogleGenerativeAI(
        model = "gemini-2.0-flash",
        temperature = 0,
        api_key = os.getenv("GOOGLE_API_KEY")
    )
    
    # Carrega as ferramentas MCP do servidor de matemática
    math_tools = await load_mcp_tools(math_session)
    
    # Carrega as ferramentas MCP do servidor de clientes
    customer_tools = await load_mcp_tools(clientes_session)
    
    # Combina todas as ferramentas em uma única lista
    tools = math_tools + customer_tools
    
    # Vincula as ferramentas ao LLM para uso durante a execução
    llm_with_tool = llm.bind_tools(tools)
    
    # Carrega o prompt do sistema definido no servidor de matemática
    system_prompt = await load_mcp_prompt(math_session, "system_prompt")
    
    # Cria um template de prompt de chat incluindo o prompt do sistema
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt[0].content),
        MessagesPlaceholder("messages")
    ])
    
    # Combina o template de prompt com o LLM que possui as ferramentas
    chat_llm = prompt_template | llm_with_tool

    # Define o tipo de estado do grafo, agregando mensagens ao estado
    class State(TypedDict):
        messages: Annotated[List[AnyMessage], add_messages]

    # Função que representa o nó de chat no grafo
    def chat_node(state: State) -> State:
        
        # Atualiza as mensagens do estado com a resposta do LLM
        state["messages"] = chat_llm.invoke({"messages": state["messages"]})
        
        return state

    # Inicia o construtor de grafo com o tipo de estado
    graph_builder = StateGraph(State)
    
    # Adiciona nó de chat
    graph_builder.add_node("chat_node", chat_node)
    
    # Adiciona nó de ferramenta que executa chamadas MCP
    graph_builder.add_node("tool_node", ToolNode(tools=tools))
    
    # Conecta início do grafo ao nó de chat
    graph_builder.add_edge(START, "chat_node")
    
    # Define arestas condicionais: se ferramentas forem solicitadas, vai para tool_node, senão, termina
    graph_builder.add_conditional_edges("chat_node", tools_condition, {"tools": "tool_node", "__end__": END})
    
    # Conecta nó de ferramenta de volta ao nó de chat
    graph_builder.add_edge("tool_node", "chat_node")
    
    # Compila o grafo e configura o salvamento de memória
    graph = graph_builder.compile(checkpointer = MemorySaver())
    
    return graph

# Define a função principal que inicia o loop de interação do agente
async def main():

    # Configuração onde podemos passar parâmetros configuráveis ao agente
    config = {"configurable": {"thread_id": 1234}}
    
    # Abre sessões MCP para os dois servidores
    async with client.session("math") as math_session, client.session("customers") as cust_session:
        
        # Cria o grafo de estados usando as sessões MCP abertas
        agent = await create_graph(math_session, cust_session)

        # Imprime mensagem de inicialização
        print("\nIniciando o Sistema de IA...\n")
        
        # Loop infinito para receber e responder a mensagens do usuário
        while True:
            
            # Lê input do usuário
            message = input("\nUser: ")
            
            # Invoca o agente com a mensagem do usuário e configurações
            response = await agent.ainvoke({"messages": message}, config=config)
            
            # Exibe a resposta do agente na tela
            print("Assistant: " + response["messages"][-1].content)

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":

    # Executa a função principal usando asyncio
    asyncio.run(main())
