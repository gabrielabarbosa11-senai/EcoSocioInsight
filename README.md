# SocioEcoInsight

O **SocioEcoInsight** é uma plataforma analítica projetada para monitorar e explorar métricas socioeconômicas do Brasil em tempo real (como IPCA, Desemprego e o Índice de Miséria). Além dos gráficos interativos, o painel integra um chat com Inteligência Artificial (RAG Multi-Agente) capaz de responder perguntas complexas baseadas nos dados e metodologias oficiais do IBGE.

---

## 🏗️ Arquitetura e Tecnologias (Decomposição)

O projeto foi construído focando em robustez no backend e reatividade no frontend, sem a complexidade de frameworks SPA pesados.

*   **Django (Python):** O núcleo da aplicação. Escolhido por sua segurança, arquitetura MVC (MVT), robustez do ORM e facilidade na construção de rotas e integrações de backend pesadas (como o pipeline de dados ETL e a orquestração da IA).
*   **PostgreSQL via Supabase:** Nosso banco de dados relacional principal. O [Supabase](https://supabase.com/) é utilizado por ser uma alternativa robusta e em nuvem que empacota o PostgreSQL. A grande vantagem dessa escolha é o suporte nativo e facilitado ao **`pgvector`**, uma extensão essencial para armazenar embeddings (vetores de texto) e viabilizar o motor de busca semântica do nosso chat de IA.
*   **HTMX:** Traz reatividade ao frontend. Permite que o chat da IA e as interações do painel funcionem de forma assíncrona (sem recarregar a página) apenas trocando pedaços do HTML diretamente com o Django.
*   **TailwindCSS & Chart.js:** Utilizados para construir um "Admin Dashboard" moderno, responsivo (com suporte a Dark Mode) e plotar gráficos ricos das séries históricas.

---

## 🚀 Como Rodar o Projeto Localmente

**1. Clone o repositório:**
```bash
git clone https://github.com/gabrielabarbosa11-senai/EcoSocioInsight.git
cd EcoSocioInsight
```

**2. Crie e ative o ambiente virtual:**
```bash
python -m venv venv

# No Windows:
.\venv\Scripts\activate

# No Mac/Linux:
source venv/bin/activate
```

**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**4. Variáveis de Ambiente:**
Crie um arquivo `.env` na raiz do projeto contendo suas credenciais do Supabase (Database URL) e a chave da API da OpenAI para os agentes funcionarem.
```env
DATABASE_URL=postgres://usuario:senha@aws-0-regiao.pooler.supabase.com:6543/postgres
OPENAI_API_KEY=sk-sua_chave_aqui
```

**5. Execute o servidor de desenvolvimento:**
```bash
python manage.py runserver
```
Acesse `http://127.0.0.1:8000/` no seu navegador.
