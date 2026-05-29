import os
from openai import OpenAI
from django.db import connection
from core.models import MetricaSocioEconomica

class RouterAgent:
    """Agent 1: Analisa a intenção e decide a estratégia de roteamento"""
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def classify(self, query: str) -> str:
        prompt = f"""Você é o RouterAgent de um sistema de análises socioeconômicas.
Classifique a intenção da pergunta do usuário em UMA das opções:
1. 'analytical': busca por dados quantitativos, índices, comparações históricas de IPCA e Desemprego.
2. 'semantic': busca por definições de indicadores, como os cálculos são feitos, notas metodológicas do IBGE.
3. 'mixed': requer tanto dados exatos quanto o entendimento conceitual.
4. 'unrelated': qualquer pergunta fora do escopo de economia, dados do IBGE, métricas como inflação e desemprego, ou o painel SocioEcoInsight.

Pergunta: "{query}"

Retorne APENAS a palavra da classificação (analytical, semantic, mixed, ou unrelated)."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip().lower()

class ExtractorAgent:
    """Agent 2: Realiza as consultas no banco (Relacional ORM + pgvector nativo via raw SQL)"""
    def __init__(self, client: OpenAI):
        self.client = client

    def fetch_analytical(self) -> str:
        metrics = MetricaSocioEconomica.objects.all().order_by('-data')[:120]
        if not metrics:
            return "Nenhum dado analítico encontrado."
        
        context = "Série Histórica Recente do IBGE:\n"
        for m in metrics:
            context += f"- [{m.data.strftime('%Y-%m')}] {m.tipo_metrica}: {m.valor}%\n"
        return context

    def fetch_semantic(self, query: str) -> str:
        # Se não houver cliente OpenAI configurado, pula a busca semântica
        if not self.client:
            return "Busca semântica desabilitada (OpenAI Key ausente)."

        res = self.client.embeddings.create(
            input=[query], 
            model="text-embedding-3-small"
        )
        query_embedding = res.data[0].embedding
        
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        context = "Contexto Metodológico (IBGE):\n"
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT titulo, conteudo_texto, embedding <=> %s::vector AS distance 
                FROM documento_metodologico 
                ORDER BY distance ASC 
                LIMIT 2;
            """, [embedding_str])
            
            rows = cursor.fetchall()
            for row in rows:
                titulo, texto, dist = row
                context += f"\n[Doc: {titulo} | Distância: {dist:.4f}]\n{texto}\n"
                
        return context if len(context) > 50 else "Nenhuma nota metodológica encontrada."

class SynthesizerAgent:
    """Agent 3: Sintetiza a resposta final em linguagem natural"""
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def synthesize(self, query: str, context: str) -> str:
        system_prompt = """Você é um especialista em economia orquestrando dados do IBGE (SocioEcoInsight). 
Sua tarefa é responder a pergunta do usuário utilizando EXCLUSIVAMENTE o contexto fornecido abaixo.
Regras:
1. Nunca invente dados numéricos.
2. De maneira alguma responda perguntas que não estejam relacionadas ao contexto.
3. Nunca responda perguntas sobre política, mesmo que relacionado ao contexto do seu trabalho. Responda que você é somente um agente que analisa e responde os dados disponíveis.
4. Explique os dados encontrados de forma analítica e clara.
5. Se a informação não estiver no contexto, diga claramente que não possui esse dado em sua base.
6. Formate a resposta em HTML limpo, usando <strong> para destaques, e <ul><li> para listas, sem usar markdown."""
        
        user_prompt = f"Contexto Extraído:\n{context}\n\nPergunta do usuário: {query}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

class AntigravityOrchestrator:
    """Orquestrador Central: Define o fluxo dos sub-agentes"""
    def __init__(self):
        from django.conf import settings
        
        # 1. Cliente OpenAI (Específico para Embeddings no Extractor)
        # Se não houver chave real no settings, o cliente fica como None
        oa_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.openai_client = OpenAI(api_key=oa_key) if oa_key and "sua-chave" not in oa_key else None
        
        # 2. Cliente Groq (via SDK OpenAI compatível com base_url da Groq)
        groq_key = getattr(settings, 'GROQ_API_KEY', None)
        self.groq_client = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.groq_model = getattr(settings, 'GROQ_MODEL', "llama-3.3-70b-versatile")

        self.router = RouterAgent(self.groq_client, self.groq_model)
        self.extractor = ExtractorAgent(self.openai_client)
        self.synthesizer = SynthesizerAgent(self.groq_client, self.groq_model)

    def process_query(self, query: str) -> str:
        # Fase A: Classificação
        intent = self.router.classify(query)
        
        if 'unrelated' in intent:
            return "Desculpe, mas sou um agente focado exclusivamente em dados socioeconômicos (IBGE, IPCA, Desemprego). Não posso responder a perguntas fora desse contexto."
        
        # Fase B: Extração Dinâmica Híbrida
        context = ""
        if 'analytical' in intent or 'mixed' in intent:
            context += self.extractor.fetch_analytical() + "\n"
        if 'semantic' in intent or 'mixed' in intent:
            context += self.extractor.fetch_semantic(query)
            
        if not context.strip():
            context = "Banco de dados vazio no momento."
            
        # Fase C: Síntese e Formatação
        final_answer = self.synthesizer.synthesize(query, context)
        
        return final_answer
