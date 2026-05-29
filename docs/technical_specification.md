# Especificação Técnica: SocioEcoInsight

O **SocioEcoInsight** é uma plataforma web que expõe dashboards socioeconômicos reais do Brasil consumindo a API do IBGE, e integra um Chatbot RAG Multi-Agente orquestrado pelo framework Antigravity. O sistema permite realizar consultas analíticas e semânticas avançadas em linguagem natural, utilizando PostgreSQL com a extensão pgvector para armazenamento e busca híbrida (relacional e vetorial).

## Arquitetura de Componentes

O projeto segue os princípios de Clean Architecture adaptados para o ecossistema Django, separando responsabilidades em camadas distintas:

1. **Camada de Apresentação (Presentation)**:
   - Interface web utilizando Django Templates e HTMX para interações assíncronas.
   - Componentes visuais com TailwindCSS.
   - Renderização de gráficos com Chart.js.
   - Comunicação via SSE (Server-Sent Events) ou WebSocket para streaming da resposta da IA.

2. **Camada de Aplicação (Application / Infrastructure)**:
   - **Django Views**: `ChatView` (roteamento), `AnalysisView` (processamento do dashboard).
   - **Gerenciamento de Comandos (ETL)**: Pipeline assíncrono para ingestão de dados da API SIDRA do IBGE (Inflação, Desemprego).

3. **Camada de Orquestração de IA (Domain / Services)**:
   - **Antigravity Orchestrator**: Framework de coordenação Multi-Agente.
   - **RouterAgent**: Analisa a intenção da query e roteia para a ação adequada.
   - **ExtractorAgent**: Recupera o contexto no banco (buscas relacionais e de similaridade vetorial via embeddings).
   - **SynthesizerAgent**: Sintetiza a resposta em linguagem natural consolidando contexto e aplicando raciocínio.

4. **Camada de Persistência (PostgreSQL Híbrido)**:
   - Armazenamento relacional para métricas históricas (`MetricaSocioEconomica`).
   - Armazenamento vetorial via `pgvector` para notas metodológicas (`DocumentoMetodologico`).

---

### Diagrama 1: Arquitetura de Componentes

```mermaid
graph TB
    subgraph Apresentacao["Camada de Apresentação"]
        HTMX["Browser + HTMX"]
        Templates["Django Templates"]
        SSE["SSE / WebSocket"]
    end
    
    subgraph Aplicacao["Camada de Aplicação - Django"]
        ChatView["ChatView<br/>Roteamento de chat"]
        AnalysisView["AnalysisView<br/>Análise de dados"]
        DashboardView["DashboardView<br/>Painel e relatórios"]
        AuthView["AuthView"]
    end
    
    subgraph IA["Camada de Orquestração de IA"]
        Orchestrator["Antigravity Orchestrator<br/>Gerencia ciclo multi-agente"]
        Router["RouterAgent<br/>Classifica intenção"]
        Extractor["ExtractorAgent<br/>Busca e filtra dados"]
        Synthesizer["SynthesizerAgent<br/>Gera resposta final"]
        
        Orchestrator --> Router
        Orchestrator --> Extractor
        Orchestrator --> Synthesizer
    end
    
    subgraph Persistencia["Camada de Persistência - PostgreSQL Híbrido"]
        PG_Rel["PostgreSQL Relacional<br/>chat_session<br/>chat_message<br/>indicator_data"]
        PG_Vec["pgvector vetorial<br/>document_chunk<br/>embedding vector<br/>similarity_search"]
        
        PG_Rel <-.conexão híbrida.-> PG_Vec
    end
    
    Apresentacao --> Aplicacao
    Aplicacao --> IA
    IA --> Persistencia
    
    style IA fill:#EEEDFE,stroke:#534AB7
    style Aplicacao fill:#E1F5EE,stroke:#0F6E56
    style Persistencia fill:#FAEEDA,stroke:#854F0B
```

### Diagrama 2: Sequência do Fluxo Chat (RAG Multi-Agente)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant H as Frontend HTMX
    participant CV as ChatView Django
    participant O as Antigravity Orchestrator
    participant R as RouterAgent
    participant E as ExtractorAgent
    participant S as SynthesizerAgent
    participant DB as PostgreSQL + pgvector

    U->>H: POST /chat/send
    H->>CV: HTTP request
    CV->>DB: INSERT chat_message role user content
    CV->>O: run session_id query
    
    O->>R: classify_intent query
    R->>DB: SELECT chat_message WHERE session_id
    DB-->>R: histórico de mensagens
    R-->>O: intent analysis
    
    O->>E: extract query intent
    E->>DB: SELECT indicator_data
    E->>DB: similarity_search embedding
    DB-->>E: rows + doc_chunks
    E-->>O: context_payload
    
    O->>S: synthesize query context_payload
    Note over S: LLM call
    S->>DB: INSERT chat_message role assistant
    S-->>O: response_text
    
    O-->>CV: streamed_response
    CV-->>H: SSE chunk stream
    H-->>U: renderiza resposta
```
