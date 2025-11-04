# MCP + PydanticAI Reference Project

Este projeto demonstra, de ponta a ponta, como construir um ecossistema de agentes de IA utilizando o **Model Context Protocol (MCP)** aliado a **LangGraph** e **PydanticAI**. É um material pensado para servir como peça de portfólio e apoio a posts no LinkedIn, mostrando uma arquitetura moderna, extensível e pronta para integrar múltiplos servidores MCP.

## Destaques do Projeto

- **Dois clientes MCP**: uma aplicação em LangGraph e outra em PydanticAI consumindo os mesmos servidores.
- **Tipagem e validação com Pydantic**: modelos garantem segurança de dados ao expor ferramentas e recursos MCP.
- **Múltiplos transports**: demonstração de fluxo via STDIO, HTTP streamable e SSE.
- **Toolkit pronto**: servidor matemático e servidor de clientes (CRUD SQLite) ilustram como publicar diferentes domínios no MCP.
- **Foco em reutilização**: código organizado para servir como boilerplate em novos projetos MCP.

## Arquitetura em Alto Nível

- `mcp_server_math.py`: servidor MCP via STDIO com ferramentas matemáticas, prompts e recursos prontos para extensão.
- `mcp_server_database.py`: servidor MCP HTTP/SSE para gerenciar clientes com SQLite, utilizando modelos Pydantic para validação.
- `mcp_app_langgraph.py`: agente LangGraph que orquestra chamadas às ferramentas MCP usando um grafo de estados e memória persistente.
- `mcp_app_pydantic_ai.py`: agente PydanticAI que consome os mesmos servidores MCP com configuração declarativa e prompts amigáveis.

> **Stack**: Python 3.12, LangGraph, LangChain, PydanticAI, MCP (FastMCP), Google Gemini 2.0 Flash (via `langchain-google-genai`), SQLite, dotenv.

## Como Executar

```bash
conda create --name mcp_env python=3.12
conda activate mcp_env
conda install pip
pip install -r requirements.txt
```

Em seguida, suba o servidor MCP de clientes:

```bash
python mcp_server_database.py
```

Em outro terminal (com o ambiente ativo), escolha a aplicação de demonstração:

```bash
# Orquestração com LangGraph
python mcp_app_langgraph.py

# Interação direta com PydanticAI
python mcp_app_pydantic_ai.py
```

Para encerrar:

```bash
conda deactivate
conda remove --name mcp_env --all  # opcional
```

## Pontos para Destacar no LinkedIn

1. Valor de negócio: centralizar ferramentas MCP validadas por Pydantic e expô-las para qualquer agente compatível.
2. Escalabilidade: basta adicionar novos servidores MCP ou ferramentas para expandir o portfólio de automações.
3. Dev Experience: código limpo, comentado e pronto para forks ou adaptações em projetos corporativos.
4. Aprendizados: integração MCP + LangGraph, gestão de estado com `MemorySaver`, streaming SSE e configuração declarativa de agentes.

## Próximos Passos Sugeridos

- Adicionar dashboards de observabilidade com LangSmith ou OpenTelemetry.
- Criar ferramentas MCP adicionais (ex.: CRM, analytics, automação de marketing).
- Publicar um vídeo curto demonstrando o fluxo de interação dos agentes.
- Escrever um artigo médio explicando detalhes de implementação.

---

Se você utilizar este projeto em um post no LinkedIn, sinta-se à vontade para marcar e comentar quais adaptações realizou. Bons estudos com MCP! 🎯
