import json
import os

def create_notebook(filename, content):
    """Cria um notebook Jupyter com o conteúdo especificado."""
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": content
            }
        ],
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

# Conteúdo dos notebooks
notebooks = {
    "00_Introducao.ipynb": [
        "# CodeMaria - Introdução\n\n",
        "Bem-vindo ao notebook de introdução da CodeMaria, uma IA educacional brasileira focada em ensinar programação.\n\n",
        "## Quem é a CodeMaria?\n\n",
        "A CodeMaria é uma professora virtual de programação que combina:\n\n",
        "- 🎓 Expertise técnica em diversas linguagens e frameworks\n",
        "- 🌎 Contextualização cultural brasileira\n",
        "- 👩‍🏫 Abordagem didática personalizada\n",
        "- 🤖 Aprendizado contínuo e adaptativo\n\n",
        "## Principais Características\n\n",
        "### 1. Personalização do Ensino\n",
        "- Adapta o conteúdo ao nível do aluno\n",
        "- Considera o contexto cultural\n",
        "- Ajusta o estilo de comunicação\n\n",
        "### 2. Contextualização Cultural\n",
        "- Exemplos relevantes para o contexto brasileiro\n",
        "- Referências culturais locais\n",
        "- Linguagem adaptada ao público\n\n",
        "### 3. Aprendizado Contínuo\n",
        "- Processamento de PDFs e recursos web\n",
        "- Análise de feedback dos alunos\n",
        "- Evolução constante do conhecimento\n\n",
        "### 4. Criatividade e Inovação\n",
        "- Geração de conteúdo original\n",
        "- Exemplos práticos personalizados\n",
        "- Exercícios contextualizados\n\n",
        "## Como Usar Este Repositório\n\n",
        "Este repositório contém notebooks que demonstram as principais funcionalidades:\n\n",
        "1. **Aprendizado** - Motor de aprendizado e processamento de conhecimento\n",
        "2. **Criatividade** - Geração de conteúdo e exemplos\n",
        "3. **PDFs** - Processamento e análise de documentos\n",
        "4. **APIs** - Integrações com serviços externos\n",
        "5. **Exemplos** - Casos práticos de uso\n\n",
        "## Começando\n\n",
        "Para começar a usar a CodeMaria, você precisará:\n\n",
        "1. Configurar as variáveis de ambiente (.env)\n",
        "2. Instalar as dependências (requirements.txt)\n",
        "3. Executar os notebooks em sequência\n\n",
        "Vamos juntos nessa jornada de aprendizado! 🚀"
    ],
    "01_Learning.ipynb": [
        "# Motor de Aprendizado da CodeMaria\n\n",
        "Este notebook demonstra o funcionamento do motor de aprendizado da CodeMaria.\n\n",
        "## Funcionalidades Principais\n\n",
        "### 1. Processamento de Contexto\n",
        "- Análise de contexto cultural\n",
        "- Detecção de idioma\n",
        "- Identificação de temas\n",
        "- Extração de conceitos-chave\n\n",
        "### 2. Análise de Sentimentos\n",
        "- Avaliação de feedback\n",
        "- Detecção de dificuldades\n",
        "- Ajuste de abordagem\n\n",
        "### 3. Aprendizado Web\n",
        "- Coleta de recursos online\n",
        "- Validação de fontes\n",
        "- Extração de conhecimento\n\n",
        "### 4. Base de Conhecimento\n",
        "- Armazenamento estruturado\n",
        "- Categorização de informações\n",
        "- Atualização dinâmica\n\n",
        "## Exemplos Práticos\n\n",
        "1. Análise de contexto cultural\n",
        "2. Processamento de feedback\n",
        "3. Aprendizado de recursos web\n",
        "4. Gestão da base de conhecimento"
    ],
    "02_Creativity.ipynb": [
        "# Motor de Criatividade da CodeMaria\n\n",
        "Este notebook demonstra as capacidades criativas da CodeMaria.\n\n",
        "## Recursos Criativos\n\n",
        "### 1. Geração de Conteúdo\n",
        "- Tutoriais personalizados\n",
        "- Exemplos contextualizados\n",
        "- Exercícios adaptativos\n\n",
        "### 2. Adaptação Cultural\n",
        "- Referências brasileiras\n",
        "- Exemplos locais\n",
        "- Linguagem regional\n\n",
        "### 3. Personalização\n",
        "- Ajuste por nível\n",
        "- Preferências do aluno\n",
        "- Estilo de aprendizado\n\n",
        "### 4. Interatividade\n",
        "- Quizzes dinâmicos\n",
        "- Desafios práticos\n",
        "- Feedback instantâneo\n\n",
        "## Demonstrações\n\n",
        "1. Criação de tutorial\n",
        "2. Geração de exemplos\n",
        "3. Elaboração de exercícios\n",
        "4. Adaptação de conteúdo"
    ],
    "03_PDF_Processing.ipynb": [
        "# Processamento de PDFs na CodeMaria\n\n",
        "Este notebook demonstra as capacidades de processamento de PDFs.\n\n",
        "## Funcionalidades\n\n",
        "### 1. Extração de Texto\n",
        "- Processamento de layout\n",
        "- Reconhecimento de estrutura\n",
        "- Preservação de formatação\n\n",
        "### 2. Análise de Conteúdo\n",
        "- Identificação de temas\n",
        "- Extração de conceitos\n",
        "- Análise de complexidade\n\n",
        "### 3. Contextualização\n",
        "- Detecção de referências culturais\n",
        "- Identificação geográfica\n",
        "- Análise temporal\n\n",
        "### 4. Processamento em Lote\n",
        "- Múltiplos documentos\n",
        "- Análise comparativa\n",
        "- Estatísticas agregadas\n\n",
        "## Exemplos de Uso\n\n",
        "1. Processamento de material didático\n",
        "2. Análise de documentação técnica\n",
        "3. Extração de exemplos práticos\n",
        "4. Geração de resumos"
    ],
    "04_API_Integrations.ipynb": [
        "# Integrações com APIs na CodeMaria\n\n",
        "Este notebook demonstra as integrações com APIs externas.\n\n",
        "## Integrações Disponíveis\n\n",
        "### 1. Busca Web\n",
        "- Google Search\n",
        "- Artigos científicos\n",
        "- Documentação técnica\n\n",
        "### 2. Processamento de Linguagem\n",
        "- Análise de sentimentos\n",
        "- Detecção de idioma\n",
        "- Extração de entidades\n\n",
        "### 3. Recursos Educacionais\n",
        "- Repositórios de código\n",
        "- Plataformas de ensino\n",
        "- Fóruns técnicos\n\n",
        "### 4. Gestão de Cache\n",
        "- Armazenamento local\n",
        "- Controle de taxa\n",
        "- Otimização de requisições\n\n",
        "## Demonstrações\n\n",
        "1. Busca contextualizada\n",
        "2. Análise de recursos\n",
        "3. Integração de conteúdo\n",
        "4. Gestão de requisições"
    ],
    "05_Examples.ipynb": [
        "# Exemplos Práticos da CodeMaria\n\n",
        "Este notebook apresenta exemplos práticos de uso da CodeMaria.\n\n",
        "## Casos de Uso\n\n",
        "### 1. Ensino Personalizado\n",
        "- Detecção de nível\n",
        "- Adaptação de conteúdo\n",
        "- Feedback personalizado\n\n",
        "### 2. Contextualização Cultural\n",
        "- Exemplos brasileiros\n",
        "- Referências locais\n",
        "- Linguagem adaptada\n\n",
        "### 3. Processamento de Conteúdo\n",
        "- Análise de documentos\n",
        "- Extração de conhecimento\n",
        "- Geração de material\n\n",
        "### 4. Interação com APIs\n",
        "- Busca inteligente\n",
        "- Integração de recursos\n",
        "- Cache e otimização\n\n",
        "## Demonstrações Práticas\n\n",
        "1. Tutorial contextualizado\n",
        "2. Análise de feedback\n",
        "3. Processamento de PDF\n",
        "4. Integração de APIs"
    ]
}

# Cria diretório de notebooks se não existir
os.makedirs("notebooks", exist_ok=True)

# Cria cada notebook
for filename, content in notebooks.items():
    create_notebook(filename, content) 