import json
import os

def create_notebook_with_cells(filename, cells):
    """Cria um notebook Jupyter com as células especificadas."""
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    with open(f"notebooks/{filename}", "w", encoding="utf-8") as f:
        json.dump(notebook, f, ensure_ascii=False, indent=2)

# Células para o notebook de aprendizado
learning_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Motor de Aprendizado da CodeMaria\n\n",
            "Este notebook demonstra o funcionamento do motor de aprendizado da CodeMaria, apresentando exemplos práticos de cada funcionalidade.\n\n",
            "## Configuração Inicial\n\n",
            "Primeiro, vamos importar os módulos necessários e inicializar o motor de aprendizado."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "from code_maria.learning import LearningEngine\n",
            "from code_maria.core import CodeMaria\n\n",
            "# Inicializa o motor de aprendizado\n",
            "learning_engine = LearningEngine()\n",
            "code_maria = CodeMaria()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Processamento de Contexto\n\n",
            "O processamento de contexto é fundamental para entender o ambiente cultural e educacional do aluno.\n\n",
            "### 1.1 Análise de Contexto Cultural"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de análise de contexto cultural\n",
            "texto = \"Como é o mercado de tecnologia em São Paulo?\"\n",
            "resultado = learning_engine._detect_user_input_context(texto)\n",
            "print(\"Análise de Contexto:\")\n",
            "print(f\"- Contexto Principal: {resultado['main_context']}\")\n",
            "print(f\"- Referências Culturais: {resultado['cultural_references']}\")\n",
            "print(f\"- Localização: {resultado['location']}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 1.2 Detecção de Idioma\n\n",
            "A CodeMaria pode identificar e processar diferentes idiomas, com foco especial no português brasileiro."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de detecção de idioma\n",
            "textos = [\n",
            "    \"Como aprender programação?\",\n",
            "    \"How to learn programming?\",\n",
            "    \"¿Cómo aprender programación?\"\n",
            "]\n\n",
            "for texto in textos:\n",
            "    idioma = learning_engine._detect_language(texto)\n",
            "    print(f\"Texto: {texto}\")\n",
            "    print(f\"Idioma detectado: {idioma}\\n\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 1.3 Identificação de Temas\n\n",
            "A CodeMaria pode identificar temas específicos em textos e recursos educacionais."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de identificação de temas\n",
            "texto = \"\"\"\n",
            "Python é uma linguagem de programação muito usada em ciência de dados \n",
            "e inteligência artificial. Com ela, podemos criar análises estatísticas \n",
            "e modelos de machine learning.\n",
            "\"\"\"\n\n",
            "temas = learning_engine._classify_topics(texto)\n",
            "print(\"Temas Identificados:\")\n",
            "for tema, confianca in temas.items():\n",
            "    print(f\"- {tema}: {confianca:.2%}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Análise de Sentimentos\n\n",
            "A análise de sentimentos ajuda a entender a receptividade e dificuldades dos alunos."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de análise de sentimentos\n",
            "feedbacks = [\n",
            "    \"Adorei a explicação sobre funções!\",\n",
            "    \"Não entendi nada sobre classes...\",\n",
            "    \"O exemplo ajudou muito a entender.\"\n",
            "]\n\n",
            "for feedback in feedbacks:\n",
            "    sentimento = learning_engine.analyze_sentiment(feedback)\n",
            "    print(f\"Feedback: {feedback}\")\n",
            "    print(f\"Sentimento: {sentimento['label']}\")\n",
            "    print(f\"Confiança: {sentimento['score']:.2%}\\n\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Aprendizado Web\n\n",
            "A CodeMaria pode aprender continuamente através de recursos web."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de aprendizado web\n",
            "url = \"https://docs.python.org/pt-br/3/tutorial/\"\n",
            "resultado = learning_engine.learn_from_web(url)\n\n",
            "print(\"Aprendizado da Web:\")\n",
            "print(f\"- Título: {resultado['title']}\")\n",
            "print(f\"- Contexto: {resultado['context']}\")\n",
            "print(\"- Conceitos Extraídos:\")\n",
            "for conceito in resultado['concepts'][:5]:\n",
            "    print(f\"  • {conceito}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Base de Conhecimento\n\n",
            "A base de conhecimento é atualizada dinamicamente com novas informações."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de gestão da base de conhecimento\n",
            "novo_conhecimento = {\n",
            "    \"tema\": \"Python\",\n",
            "    \"conceitos\": [\"funções\", \"classes\", \"módulos\"],\n",
            "    \"exemplos\": [\"def soma(a, b): return a + b\"],\n",
            "    \"dificuldade\": \"iniciante\"\n",
            "}\n\n",
            "learning_engine.update_knowledge_base(\"python_basico\", novo_conhecimento)\n\n",
            "# Verifica o estado da base\n",
            "resumo = learning_engine.get_learning_summary()\n",
            "print(\"Resumo da Base de Conhecimento:\")\n",
            "print(f\"- Total de Entradas: {resumo['total_entries']}\")\n",
            "print(f\"- Categorias: {', '.join(resumo['knowledge_categories'])}\")\n",
            "print(f\"- Última Atualização: {resumo['last_learning']}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Métricas e Análises\n\n",
            "Vamos visualizar algumas métricas do processo de aprendizado."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n\n",
            "# Obtém distribuição de tópicos\n",
            "distribuicao = learning_engine._get_topics_distribution()\n\n",
            "# Cria visualização\n",
            "plt.figure(figsize=(10, 6))\n",
            "sns.barplot(x=list(distribuicao.keys()), y=list(distribuicao.values()))\n",
            "plt.title(\"Distribuição de Tópicos na Base de Conhecimento\")\n",
            "plt.xticks(rotation=45)\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    }
]

# Células para o notebook de criatividade
creativity_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Motor de Criatividade da CodeMaria\n\n",
            "Este notebook demonstra as capacidades criativas da CodeMaria, apresentando exemplos práticos de geração de conteúdo educacional.\n\n",
            "## Configuração Inicial\n\n",
            "Primeiro, vamos importar os módulos necessários e inicializar o motor de criatividade."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "from code_maria.creativity import CreativityEngine\n",
            "from code_maria.core import CodeMaria\n\n",
            "# Inicializa o motor de criatividade\n",
            "creativity_engine = CreativityEngine()\n",
            "code_maria = CodeMaria()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Geração de Conteúdo\n\n",
            "O motor de criatividade pode gerar diferentes tipos de conteúdo educacional.\n\n",
            "### 1.1 Tutoriais Personalizados"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de geração de tutorial\n",
            "tutorial = creativity_engine.generate_educational_content(\n",
            "    topic=\"Estruturas de Repetição em Python\",\n",
            "    difficulty=\"basic\",\n",
            "    language=\"python\"\n",
            ")\n\n",
            "print(\"Tutorial Gerado:\")\n",
            "print(f\"Título: {tutorial['título']}\\n\")\n",
            "for secao in tutorial['seções']:\n",
            "    print(f\"Seção: {secao['título']}\")\n",
            "    print(f\"Conteúdo: {secao['conteúdo']}\\n\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 1.2 Exemplos Contextualizados\n\n",
            "A CodeMaria gera exemplos que fazem sentido no contexto brasileiro."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de código contextualizado\n",
            "exemplo = creativity_engine._generate_code_example(\n",
            "    topic=\"Listas em Python\",\n",
            "    language=\"python\",\n",
            "    difficulty=\"basic\"\n",
            ")\n\n",
            "print(\"Exemplo Contextualizado:\")\n",
            "print(exemplo)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 1.3 Exercícios Adaptativos\n\n",
            "Os exercícios são adaptados ao nível e contexto do aluno."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Geração de exercícios\n",
            "exercicios = creativity_engine.generate_educational_content(\n",
            "    topic=\"Funções em Python\",\n",
            "    content_type=\"quiz\",\n",
            "    difficulty=\"intermediate\"\n",
            ")\n\n",
            "print(\"Exercícios Gerados:\")\n",
            "for i, exercicio in enumerate(exercicios['questões'], 1):\n",
            "    print(f\"\\nExercício {i}:\")\n",
            "    print(f\"Pergunta: {exercicio['pergunta']}\")\n",
            "    if exercicio['tipo'] == 'múltipla escolha':\n",
            "        print(\"Alternativas:\")\n",
            "        for alt in exercicio['alternativas']:\n",
            "            print(f\"- {alt}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Adaptação Cultural\n\n",
            "### 2.1 Referências Brasileiras"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo com referências culturais\n",
            "exemplo_cultural = creativity_engine.generate_text(\n",
            "    prompt=\"Explique arrays usando elementos da cultura brasileira\",\n",
            "    creative_level=0.8\n",
            ")\n\n",
            "print(\"Explicação Culturalmente Adaptada:\")\n",
            "print(exemplo_cultural)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 2.2 Linguagem Regional\n\n",
            "A CodeMaria adapta a linguagem para diferentes regiões do Brasil."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplos com variações regionais\n",
            "regioes = ['nordeste', 'sul', 'sudeste']\n",
            "texto_base = \"Como usar loops em Python\"\n\n",
            "for regiao in regioes:\n",
            "    texto_adaptado = creativity_engine.generate_text(\n",
            "        prompt=texto_base,\n",
            "        region=regiao\n",
            "    )\n",
            "    print(f\"\\nAdaptação para {regiao}:\")\n",
            "    print(texto_adaptado)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Personalização\n\n",
            "### 3.1 Ajuste por Nível"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de conteúdo com diferentes níveis\n",
            "niveis = ['basic', 'intermediate', 'advanced']\n",
            "topico = \"Orientação a Objetos\"\n\n",
            "for nivel in niveis:\n",
            "    conteudo = creativity_engine.generate_educational_content(\n",
            "        topic=topico,\n",
            "        difficulty=nivel\n",
            "    )\n",
            "    print(f\"\\nNível: {nivel}\")\n",
            "    print(f\"Título: {conteudo['título']}\")\n",
            "    print(\"Principais conceitos:\")\n",
            "    for conceito in conteudo['conceitos'][:3]:\n",
            "        print(f\"- {conceito}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Interatividade\n\n",
            "### 4.1 Quizzes Dinâmicos"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Geração de quiz interativo\n",
            "quiz = creativity_engine.generate_educational_content(\n",
            "    topic=\"Dicionários em Python\",\n",
            "    content_type=\"quiz\",\n",
            "    interactive=True\n",
            ")\n\n",
            "print(\"Quiz Interativo:\")\n",
            "print(f\"Título: {quiz['título']}\\n\")\n",
            "for questao in quiz['questões']:\n",
            "    print(f\"Pergunta: {questao['pergunta']}\")\n",
            "    if questao['tipo'] == 'múltipla escolha':\n",
            "        print(\"Alternativas:\")\n",
            "        for i, alt in enumerate(questao['alternativas']):\n",
            "            print(f\"{i+1}) {alt}\")\n",
            "    print(f\"Dica: {questao['dica']}\\n\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 5. Métricas de Criatividade\n\n",
            "Vamos analisar as métricas do motor de criatividade."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Análise de métricas\n",
            "metricas = creativity_engine.get_metrics()\n\n",
            "print(\"Métricas de Criatividade:\")\n",
            "print(f\"Total de conteúdos gerados: {metricas['total_creations']}\")\n",
            "print(f\"Nível médio de criatividade: {metricas['avg_creativity_level']:.2f}\")\n",
            "print(\"\\nDistribuição por tipo:\")\n",
            "for tipo, count in metricas['type_distribution'].items():\n",
            "    print(f\"- {tipo}: {count}\")\n\n",
            "# Visualização\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n\n",
            "plt.figure(figsize=(10, 6))\n",
            "sns.barplot(\n",
            "    x=list(metricas['type_distribution'].keys()),\n",
            "    y=list(metricas['type_distribution'].values())\n",
            ")\n",
            "plt.title(\"Distribuição de Tipos de Conteúdo\")\n",
            "plt.xticks(rotation=45)\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    }
]

# Células para o notebook de processamento de PDFs
pdf_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Processamento de PDFs na CodeMaria\n\n",
            "Este notebook demonstra as capacidades de processamento de PDFs da CodeMaria, incluindo extração de texto, análise de conteúdo e contextualização.\n\n",
            "## Configuração Inicial\n\n",
            "Primeiro, vamos importar os módulos necessários e inicializar o processador de PDFs."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "from code_maria.pdf_processor import PDFProcessor\n",
            "from code_maria.pdf_trainer import PDFTrainer\n",
            "from code_maria.core import CodeMaria\n\n",
            "# Inicializa os processadores\n",
            "pdf_processor = PDFProcessor()\n",
            "pdf_trainer = PDFTrainer()\n",
            "code_maria = CodeMaria()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Extração de Texto\n\n",
            "### 1.1 Processamento de Layout\n",
            "A CodeMaria pode extrair texto preservando a estrutura do documento."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de processamento de PDF\n",
            "resultado = pdf_processor.process_pdf('exemplos/tutorial_python.pdf')\n\n",
            "print(\"Informações Extraídas:\")\n",
            "print(f\"Título: {resultado['metadata']['title']}\")\n",
            "print(f\"Autor: {resultado['metadata']['author']}\")\n",
            "print(f\"Data: {resultado['metadata']['creation_date']}\")\n",
            "print(\"\\nPrimeiros parágrafos:\")\n",
            "for i, paragrafo in enumerate(resultado['paragraphs'][:3], 1):\n",
            "    print(f\"\\nParágrafo {i}:\")\n",
            "    print(paragrafo)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 1.2 Reconhecimento de Estrutura\n",
            "O processador identifica diferentes elementos do documento."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Análise estrutural do documento\n",
            "estrutura = pdf_processor.analyze_structure('exemplos/artigo_tecnico.pdf')\n\n",
            "print(\"Estrutura do Documento:\")\n",
            "print(f\"Total de seções: {len(estrutura['sections'])}\")\n",
            "print(\"\\nSeções principais:\")\n",
            "for secao in estrutura['sections']:\n",
            "    print(f\"- {secao['title']}\")\n",
            "print(f\"\\nTotal de figuras: {len(estrutura['figures'])}\")\n",
            "print(f\"Total de tabelas: {len(estrutura['tables'])}\")\n",
            "print(f\"Total de referências: {len(estrutura['references'])}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Análise de Conteúdo\n\n",
            "### 2.1 Identificação de Temas"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Análise temática\n",
            "analise = pdf_processor.analyze_content('exemplos/material_didatico.pdf')\n\n",
            "print(\"Análise de Conteúdo:\")\n",
            "print(\"\\nTemas principais:\")\n",
            "for tema, relevancia in analise['main_topics'].items():\n",
            "    print(f\"- {tema}: {relevancia:.2%}\")\n\n",
            "print(\"\\nPalavras-chave:\")\n",
            "for palavra in analise['keywords'][:10]:\n",
            "    print(f\"- {palavra}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 2.2 Análise de Complexidade\n",
            "Avaliação do nível de complexidade do conteúdo."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Análise de complexidade\n",
            "complexidade = pdf_processor.analyze_complexity('exemplos/apostila.pdf')\n\n",
            "print(\"Análise de Complexidade:\")\n",
            "print(f\"Nível geral: {complexidade['overall_level']}\")\n",
            "print(f\"Índice de legibilidade: {complexidade['readability_score']:.2f}\")\n",
            "print(\"\\nDistribuição de complexidade por seção:\")\n",
            "for secao, nivel in complexidade['section_levels'].items():\n",
            "    print(f\"- {secao}: {nivel}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Contextualização\n\n",
            "### 3.1 Detecção de Referências Culturais"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Análise de contexto cultural\n",
            "contexto = pdf_processor._analyze_cultural_context('exemplos/material_brasileiro.pdf')\n\n",
            "print(\"Análise de Contexto Cultural:\")\n",
            "print(\"\\nReferências culturais identificadas:\")\n",
            "for ref in contexto['cultural_references']:\n",
            "    print(f\"- {ref}\")\n\n",
            "print(\"\\nLocalizações mencionadas:\")\n",
            "for local in contexto['locations']:\n",
            "    print(f\"- {local}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Processamento em Lote\n\n",
            "### 4.1 Análise de Múltiplos Documentos"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Processamento em lote\n",
            "resultados = pdf_processor.process_pdf_folder('exemplos/pdfs/')\n\n",
            "print(\"Processamento em Lote:\")\n",
            "print(f\"Total de documentos: {len(resultados)}\")\n",
            "print(\"\\nResumo por documento:\")\n",
            "for doc in resultados:\n",
            "    print(f\"\\nArquivo: {doc['file_name']}\")\n",
            "    print(f\"Tamanho: {doc['size']} bytes\")\n",
            "    print(f\"Páginas: {doc['pages']}\")\n",
            "    print(f\"Status: {doc['status']}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 4.2 Estatísticas Agregadas\n",
            "Análise estatística do conjunto de documentos."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Análise estatística\n",
            "stats = pdf_processor.get_processing_summary()\n\n",
            "print(\"Estatísticas de Processamento:\")\n",
            "print(f\"Total de arquivos processados: {stats['total_files']}\")\n",
            "print(f\"Taxa de sucesso: {stats['success_rate']:.2%}\")\n",
            "print(f\"Tempo médio de processamento: {stats['avg_processing_time']:.2f}s\")\n\n",
            "# Visualização\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n\n",
            "plt.figure(figsize=(10, 6))\n",
            "sns.barplot(\n",
            "    x=list(stats['content_types'].keys()),\n",
            "    y=list(stats['content_types'].values())\n",
            ")\n",
            "plt.title(\"Distribuição de Tipos de Conteúdo\")\n",
            "plt.xticks(rotation=45)\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    }
]

# Células para o notebook de integrações com APIs
api_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Integrações com APIs na CodeMaria\n\n",
            "Este notebook demonstra as capacidades de integração da CodeMaria com APIs externas, incluindo buscas contextualizadas e processamento de conteúdo web.\n\n",
            "## Configuração Inicial\n\n",
            "Primeiro, vamos importar os módulos necessários e inicializar os gerenciadores de API."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "from code_maria.api_integrations import APIIntegrations\n",
            "from code_maria.rate_limiter import RateLimiter\n",
            "from code_maria.cache_manager import CacheManager\n",
            "from code_maria.core import CodeMaria\n\n",
            "# Inicializa os gerenciadores\n",
            "api_manager = APIIntegrations()\n",
            "rate_limiter = RateLimiter()\n",
            "cache_manager = CacheManager()\n",
            "code_maria = CodeMaria()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Buscas Contextualizadas\n\n",
            "### 1.1 Busca Web com Contexto Cultural"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de busca contextualizada\n",
            "query = \"história da programação no Brasil\"\n",
            "resultados = api_manager.search_with_context(query, context_type='cultural')\n\n",
            "print(\"Resultados da Busca:\")\n",
            "for i, resultado in enumerate(resultados[:5], 1):\n",
            "    print(f\"\\nResultado {i}:\")\n",
            "    print(f\"Título: {resultado['title']}\")\n",
            "    print(f\"Relevância cultural: {resultado['cultural_relevance']:.2%}\")\n",
            "    print(f\"URL: {resultado['url']}\")\n",
            "    print(f\"Resumo: {resultado['summary']}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 1.2 Busca de Artigos Científicos com Contexto Geográfico"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Busca de artigos científicos\n",
            "query = \"desenvolvimento de software em São Paulo\"\n",
            "artigos = api_manager.search_scientific_articles(query, location='São Paulo')\n\n",
            "print(\"Artigos Encontrados:\")\n",
            "for i, artigo in enumerate(artigos[:3], 1):\n",
            "    print(f\"\\nArtigo {i}:\")\n",
            "    print(f\"Título: {artigo['title']}\")\n",
            "    print(f\"Autores: {', '.join(artigo['authors'])}\")\n",
            "    print(f\"Instituição: {artigo['institution']}\")\n",
            "    print(f\"Ano: {artigo['year']}\")\n",
            "    print(f\"Citações: {artigo['citations']}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Processamento de Conteúdo Web\n\n",
            "### 2.1 Extração e Análise de Conteúdo"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Processamento de página web\n",
            "url = \"https://exemplo.com.br/artigo-tecnologia\"\n",
            "conteudo = api_manager.process_web_content(url)\n\n",
            "print(\"Análise de Conteúdo Web:\")\n",
            "print(f\"Título da página: {conteudo['title']}\")\n",
            "print(f\"Idioma detectado: {conteudo['language']}\")\n",
            "print(\"\\nPalavras-chave principais:\")\n",
            "for palavra, relevancia in conteudo['keywords'].items():\n",
            "    print(f\"- {palavra}: {relevancia:.2%}\")\n",
            "print(\"\\nReferências externas:\")\n",
            "for ref in conteudo['external_references']:\n",
            "    print(f\"- {ref}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 2.2 Análise de Sentimento em Comentários"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Análise de sentimento\n",
            "comentarios = api_manager.get_comments('https://exemplo.com.br/post')\n",
            "analise = api_manager.analyze_sentiment(comentarios)\n\n",
            "print(\"Análise de Sentimento:\")\n",
            "print(f\"Total de comentários: {analise['total_comments']}\")\n",
            "print(f\"Sentimento médio: {analise['average_sentiment']:.2f}\")\n",
            "print(\"\\nDistribuição de sentimentos:\")\n",
            "for sentimento, percentual in analise['sentiment_distribution'].items():\n",
            "    print(f\"- {sentimento}: {percentual:.1%}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Gerenciamento de Taxa e Cache\n\n",
            "### 3.1 Controle de Requisições"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Verificação de limites de API\n",
            "status = rate_limiter.check_api_status()\n\n",
            "print(\"Status das APIs:\")\n",
            "for api, info in status.items():\n",
            "    print(f\"\\nAPI: {api}\")\n",
            "    print(f\"Requisições restantes: {info['remaining_requests']}\")\n",
            "    print(f\"Tempo até reset: {info['time_to_reset']}s\")\n",
            "    print(f\"Status: {info['status']}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 3.2 Gerenciamento de Cache"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Estatísticas de cache\n",
            "cache_stats = cache_manager.get_statistics()\n\n",
            "print(\"Estatísticas de Cache:\")\n",
            "print(f\"Total de itens em cache: {cache_stats['total_items']}\")\n",
            "print(f\"Taxa de acerto: {cache_stats['hit_rate']:.2%}\")\n",
            "print(f\"Economia de requisições: {cache_stats['requests_saved']}\")\n",
            "print(f\"Tamanho total do cache: {cache_stats['total_size_mb']:.2f} MB\")\n\n",
            "# Visualização\n",
            "import matplotlib.pyplot as plt\n\n",
            "plt.figure(figsize=(10, 6))\n",
            "plt.pie(\n",
            "    [cache_stats['hits'], cache_stats['misses']],\n",
            "    labels=['Cache Hits', 'Cache Misses'],\n",
            "    autopct='%1.1f%%'\n",
            ")\n",
            "plt.title(\"Distribuição de Cache Hits vs Misses\")\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Exemplo Completo\n\n",
            "### 4.1 Busca e Processamento de Cursos"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo completo de uso\n",
            "query = \"cursos de programação em São Paulo\"\n",
            "\n",
            "# Busca cursos\n",
            "resultados = api_manager.search_with_context(\n",
            "    query,\n",
            "    context_type='educational',\n",
            "    location='São Paulo'\n",
            ")\n\n",
            "print(\"Análise de Cursos:\")\n",
            "for resultado in resultados[:3]:\n",
            "    print(f\"\\nCurso: {resultado['title']}\")\n",
            "    \n",
            "    # Processa página do curso\n",
            "    conteudo = api_manager.process_web_content(resultado['url'])\n",
            "    print(f\"Instituição: {conteudo['institution']}\")\n",
            "    print(f\"Duração: {conteudo['duration']}\")\n",
            "    print(f\"Modalidade: {conteudo['modality']}\")\n",
            "    \n",
            "    # Analisa avaliações\n",
            "    avaliacoes = api_manager.get_reviews(resultado['url'])\n",
            "    sentimento = api_manager.analyze_sentiment(avaliacoes)\n",
            "    print(f\"Avaliação média: {sentimento['average_rating']:.1f}/5.0\")\n",
            "    print(f\"Satisfação geral: {sentimento['satisfaction_rate']:.1%}\")"
        ]
    }
]

# Células para o notebook de exemplos práticos
examples_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Exemplos Práticos da CodeMaria\n\n",
            "Este notebook apresenta exemplos práticos de uso da CodeMaria em diferentes cenários, demonstrando suas capacidades de processamento, análise e geração de conteúdo.\n\n",
            "## Configuração Inicial\n\n",
            "Primeiro, vamos importar os módulos necessários e inicializar a CodeMaria."
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "from code_maria.core import CodeMaria\n",
            "from code_maria.pdf_processor import PDFProcessor\n",
            "from code_maria.api_integrations import APIIntegrations\n",
            "from code_maria.learning_engine import LearningEngine\n",
            "from code_maria.creativity_engine import CreativityEngine\n\n",
            "# Inicializa os componentes\n",
            "code_maria = CodeMaria()\n",
            "pdf_processor = PDFProcessor()\n",
            "api_manager = APIIntegrations()\n",
            "learning_engine = LearningEngine()\n",
            "creativity_engine = CreativityEngine()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 1. Consulta Cultural\n\n",
            "### 1.1 Evolução da Tecnologia no Brasil"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de consulta cultural\n",
            "query = \"Como a tecnologia evoluiu no Brasil desde os anos 90?\"\n",
            "\n",
            "# Busca informações\n",
            "resultados = api_manager.search_with_context(\n",
            "    query,\n",
            "    context_type='historical',\n",
            "    location='Brasil',\n",
            "    time_period='1990-2024'\n",
            ")\n\n",
            "# Processa e analisa os resultados\n",
            "analise = learning_engine.analyze_historical_context(resultados)\n\n",
            "print(\"Análise Histórica:\")\n",
            "print(\"\\nPrincipais marcos:\")\n",
            "for ano, eventos in analise['timeline'].items():\n",
            "    print(f\"\\n{ano}:\")\n",
            "    for evento in eventos:\n",
            "        print(f\"- {evento}\")\n\n",
            "print(\"\\nTendências identificadas:\")\n",
            "for tendencia in analise['trends']:\n",
            "    print(f\"- {tendencia}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 1.2 Geração de Conteúdo Contextualizado"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Geração de conteúdo com contexto cultural\n",
            "tema = \"Estruturas de Dados\"\n",
            "contexto = {\n",
            "    \"país\": \"Brasil\",\n",
            "    \"nível\": \"intermediário\",\n",
            "    \"área\": \"tecnologia\"\n",
            "}\n\n",
            "tutorial = creativity_engine.generate_tutorial(\n",
            "    tema,\n",
            "    context=contexto,\n",
            "    include_examples=True\n",
            ")\n\n",
            "print(\"Tutorial Gerado:\")\n",
            "print(f\"\\nTítulo: {tutorial['title']}\")\n",
            "print(\"\\nIntrodução:\")\n",
            "print(tutorial['introduction'])\n",
            "print(\"\\nTópicos:\")\n",
            "for topico in tutorial['topics']:\n",
            "    print(f\"\\n{topico['title']}\")\n",
            "    print(f\"Descrição: {topico['description']}\")\n",
            "    if topico['example']:\n",
            "        print(\"Exemplo:\")\n",
            "        print(topico['example'])"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 2. Processamento Regional\n\n",
            "### 2.1 Análise de Documento Local"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Processamento de documento regional\n",
            "arquivo = \"exemplos/artigo_regional.pdf\"\n",
            "resultado = pdf_processor.process_pdf(arquivo)\n\n",
            "# Análise de contexto regional\n",
            "contexto = learning_engine.analyze_regional_context(resultado['content'])\n\n",
            "print(\"Análise Regional:\")\n",
            "print(f\"\\nRegião principal: {contexto['main_region']}\")\n",
            "print(\"\\nReferências regionais:\")\n",
            "for ref in contexto['regional_references']:\n",
            "    print(f\"- {ref}\")\n",
            "print(\"\\nTermos específicos da região:\")\n",
            "for termo, significado in contexto['regional_terms'].items():\n",
            "    print(f\"- {termo}: {significado}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 2.2 Adaptação de Conteúdo"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Adaptação de conteúdo para contexto regional\n",
            "conteudo_original = resultado['content']\n",
            "regiao_alvo = \"Nordeste\"\n\n",
            "adaptacao = creativity_engine.adapt_content(\n",
            "    conteudo_original,\n",
            "    target_region=regiao_alvo,\n",
            "    preserve_technical=True\n",
            ")\n\n",
            "print(\"Conteúdo Adaptado:\")\n",
            "print(f\"\\nVersão para {regiao_alvo}:\")\n",
            "print(adaptacao['adapted_content'])\n",
            "print(\"\\nModificações realizadas:\")\n",
            "for mod in adaptacao['modifications']:\n",
            "    print(f\"- {mod}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 3. Análise de Feedback\n\n",
            "### 3.1 Processamento de Comentários"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Análise de feedback de usuários\n",
            "comentarios = api_manager.get_user_feedback('projeto-exemplo')\n",
            "analise = learning_engine.analyze_feedback(comentarios)\n\n",
            "print(\"Análise de Feedback:\")\n",
            "print(f\"\\nTotal de comentários: {analise['total_comments']}\")\n",
            "print(f\"Sentimento geral: {analise['overall_sentiment']:.2f}/5.0\")\n",
            "print(\"\\nTemas principais:\")\n",
            "for tema, freq in analise['main_topics'].items():\n",
            "    print(f\"- {tema}: {freq:.1%}\")\n",
            "print(\"\\nSugestões mais frequentes:\")\n",
            "for sugestao in analise['top_suggestions']:\n",
            "    print(f\"- {sugestao}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 4. Fluxo Completo\n\n",
            "### 4.1 Processo Integrado"
        ]
    },
    {
        "cell_type": "code",
        "metadata": {},
        "source": [
            "# Exemplo de fluxo completo\n",
            "# 1. Recebe entrada do usuário\n",
            "query = \"Como ensinar programação para iniciantes no Brasil?\"\n\n",
            "# 2. Detecta contexto\n",
            "contexto = learning_engine.detect_context(query)\n",
            "print(\"Contexto Detectado:\")\n",
            "print(f\"Tipo: {contexto['type']}\")\n",
            "print(f\"Região: {contexto['region']}\")\n",
            "print(f\"Nível: {contexto['level']}\")\n\n",
            "# 3. Busca e processa informações\n",
            "resultados = api_manager.search_with_context(\n",
            "    query,\n",
            "    context_type=contexto['type'],\n",
            "    location=contexto['region']\n",
            ")\n\n",
            "# 4. Gera resposta personalizada\n",
            "resposta = creativity_engine.generate_response(\n",
            "    query,\n",
            "    context=contexto,\n",
            "    search_results=resultados\n",
            ")\n\n",
            "print(\"\\nResposta Gerada:\")\n",
            "print(resposta['content'])\n\n",
            "# 5. Analisa feedback\n",
            "feedback = {\n",
            "    \"clareza\": 4.5,\n",
            "    \"relevancia\": 4.8,\n",
            "    \"utilidade\": 4.6,\n",
            "    \"comentario\": \"Excelente explicação com exemplos práticos!\"\n",
            "}\n\n",
            "analise = learning_engine.process_feedback(feedback)\n",
            "print(\"\\nAnálise de Feedback:\")\n",
            "print(f\"Pontuação média: {analise['average_score']:.1f}/5.0\")\n",
            "print(f\"Aspectos positivos: {', '.join(analise['positive_aspects'])}\")\n",
            "if analise['suggestions']:\n",
            "    print(f\"Sugestões de melhoria: {', '.join(analise['suggestions'])}\")"
        ]
    }
]

# Cria o notebook de aprendizado
create_notebook_with_cells("01_Learning.ipynb", learning_cells)

# Cria o notebook de criatividade
create_notebook_with_cells("02_Creativity.ipynb", creativity_cells)

# Cria o notebook de processamento de PDFs
create_notebook_with_cells("03_PDF_Processing.ipynb", pdf_cells)

# Cria o notebook de integrações com APIs
create_notebook_with_cells("04_API_Integrations.ipynb", api_cells)

# Cria o notebook de exemplos práticos
create_notebook_with_cells("05_Examples.ipynb", examples_cells) 