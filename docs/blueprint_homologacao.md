# Blueprint de Homologação Local: SocioEcoInsight

Siga os passos abaixo para preparar, popular e executar a aplicação em ambiente de desenvolvimento local.

## 1. Pré-requisitos
- **Python 3.11+**
- **Docker e Docker Compose** (Para subir o PostgreSQL com a extensão `pgvector`)
- **Chave da API da OpenAI** (Para os embeddings e Chat Completion)

## 2. Inicialização do Banco de Dados com pgvector
Crie um arquivo `docker-compose.yml` na raiz do projeto contendo:

```yaml
version: '3.8'
services:
  db:
    image: ankane/pgvector:latest
    environment:
      POSTGRES_USER: socio_user
      POSTGRES_PASSWORD: socio_password
      POSTGRES_DB: socio_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

Rode o container:
```bash
docker-compose up -d
```

## 3. Configuração do Ambiente e Migrations
Crie um arquivo `.env` na raiz contendo:
```env
OPENAI_API_KEY=sk-sua-chave-aqui
DATABASE_URL=postgres://socio_user:socio_password@localhost:5432/socio_db
```

Ative a Virtualenv, instale os pacotes (descritos em `requirements.txt`) e rode as migrações (o campo `VectorField` cuidará de habilitar a extensão no banco via Django, certifique-se de que a migration correta exista para `CREATE EXTENSION vector` ou rode manualmente se preferir).

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
```

## 4. Executando o Pipeline de Ingestão (ETL)
Injete os dados reais da API SIDRA do IBGE na base rodando nosso comando customizado:

```bash
python manage.py ingest_ibge
```
*Este comando puxará as séries temporais do IPCA e Desemprego, limpará os dados e fará um `bulk_create` na tabela `metrica_socioeconomica`.*

Para popular os embeddings dos documentos, você pode utilizar o Django Shell:
```python
from core.models import DocumentoMetodologico
from openai import Client

client = Client()
texto = "O IPCA tem por objetivo medir a inflação de um conjunto de produtos e serviços..."
embedding = client.embeddings.create(input=[texto], model="text-embedding-3-small").data[0].embedding

DocumentoMetodologico.objects.create(
    titulo="Metodologia IPCA",
    conteudo_texto=texto,
    embedding=embedding
)
```

## 5. Rodando a Aplicação
Inicie o servidor de desenvolvimento do Django:

```bash
python manage.py runserver
```

Acesse `http://localhost:8000` em seu navegador.
1. O painel central renderizará o Chart.js listando o Índice de Miséria ao longo do tempo.
2. Utilize o Sidebar lateral com HTMX para interagir com o agente RAG ("Como o índice é composto?", "Qual a taxa em 2023?").
