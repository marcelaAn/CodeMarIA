# CodeMaria - IA Autônoma e Criativa

CodeMaria é uma inteligência artificial autônoma e criativa, desenvolvida com foco em aprendizado contínuo e geração de conteúdo. Ela possui uma persona feminina brasileira e é capaz de evoluir através de auto-treinamento utilizando recursos da internet e documentos PDF.

## Características Principais

- 🧠 Aprendizado autônomo e contínuo
- 🎨 Criatividade e geração de conteúdo personalizado
- 📚 Processamento e análise de documentos PDF
- 🌐 Integração com diversas APIs (Google, OpenAI, etc.)
- 🔄 Cache inteligente e controle de rate limiting
- 👩‍🏫 Personalidade única e contextualizada
- 🇧🇷 Interface em português do Brasil

## Requisitos

- Python 3.9+
- Docker (opcional)
- Acesso à internet para auto-treinamento
- APIs necessárias:
  - OpenAI API
  - Google Search API
  - News API
  - SerpAPI (para busca acadêmica)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/marcelaAn/CodeMarIA.git
cd CodeMarIA
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
- Copie o arquivo `.env.example` para `.env`
- Preencha as chaves de API necessárias
- **IMPORTANTE**: Nunca compartilhe suas chaves de API ou informações sensíveis

## Notebooks Jupyter

A CodeMaria inclui uma série de notebooks Jupyter que demonstram suas funcionalidades e servem como tutoriais interativos:

### Como Utilizar os Notebooks

1. **Preparação do Ambiente**:
   ```bash
   pip install jupyter notebook
   jupyter notebook
   ```

2. **Estrutura dos Notebooks**:
   - `00_Introducao.ipynb`: Visão geral do projeto e configuração inicial
   - `01_Learning.ipynb`: Demonstração do módulo de aprendizado
   - `02_Creativity.ipynb`: Exemplos de geração de conteúdo criativo
   - `03_PDF_Processing.ipynb`: Tutorial de processamento de PDFs
   - `04_API_Integrations.ipynb`: Guia de integração com APIs
   - `05_Examples.ipynb`: Exemplos práticos de uso

3. **Executando os Notebooks**:
   - Navegue até a pasta `notebooks/`
   - Clique no notebook desejado
   - Execute as células em sequência (Shift + Enter)
   - Siga as instruções e exemplos em cada notebook

4. **Dicas de Uso**:
   - Certifique-se de ter todas as dependências instaladas
   - Configure o arquivo `.env` antes de executar os notebooks
   - Leia os comentários e documentação em cada célula
   - Experimente modificar os exemplos para aprender mais

5. **Ordem Recomendada de Estudo**:
   1. Comece pelo notebook de introdução
   2. Explore o módulo de aprendizado
   3. Avance para criatividade e geração de conteúdo
   4. Aprenda sobre processamento de PDFs
   5. Explore as integrações com APIs
   6. Pratique com os exemplos

## Estrutura do Projeto

```
code_maria/
├── __init__.py
├── core.py           # Lógica principal
├── learning.py       # Motor de aprendizado
├── creativity.py     # Geração de conteúdo
├── persona.py        # Definição da personalidade
├── api_integrations.py # Integrações com APIs
├── pdf_processor.py  # Processamento de PDFs
├── pdf_trainer.py    # Treinamento com PDFs
├── rate_limiter.py   # Controle de requisições
├── cache_manager.py  # Gerenciamento de cache
├── schemas.py        # Schemas de validação
└── server.py         # API REST

tests/               # Testes unitários e de integração
├── __init__.py
├── conftest.py
├── test_core.py
├── test_learning.py
├── test_creativity.py
├── test_persona.py
├── test_api_integrations.py
├── test_pdf_processor.py
├── test_pdf_trainer.py
├── test_rate_limiter.py
├── test_cache_manager.py
└── test_knowledge.py

notebooks/           # Notebooks Jupyter
├── 00_Introducao.ipynb
├── 01_Learning.ipynb
├── 02_Creativity.ipynb
├── 03_PDF_Processing.ipynb
├── 04_API_Integrations.ipynb
└── 05_Examples.ipynb

data/               # Dados de treinamento
├── pdfs/          # PDFs para processamento
└── cache/         # Cache persistente
```

## Funcionalidades

### Processamento de PDFs
- Análise de conteúdo e estrutura
- Extração de texto e metadados
- Análise gramatical
- Análise de sentimentos
- Cache de resultados

### Aprendizado
- Aprendizado contínuo com PDFs
- Análise de sentimentos
- Atualização da base de conhecimento
- Histórico de aprendizado
- Métricas de evolução

### Criatividade
- Geração de conteúdo educacional
- Tutoriais personalizados
- Quizzes interativos
- Exemplos de código
- Adaptação ao nível do usuário

### Personalidade
- Persona brasileira feminina
- Adaptação do estilo de comunicação
- Empatia e didática
- Valores educacionais

### APIs e Integrações
- Busca na web
- Busca de artigos científicos
- Processamento de conteúdo web
- Rate limiting inteligente
- Cache de requisições

## Uso via API REST

### Endpoints Principais

```bash
POST /process           # Processa entrada do usuário
POST /upload-pdf        # Upload de PDF
POST /process-pdf-folder # Processa pasta de PDFs
POST /train-pdfs        # Treina com PDFs
GET  /training-stats    # Estatísticas de treinamento
GET  /pdf-stats         # Estatísticas de PDFs
```

## Desenvolvimento

O projeto está em desenvolvimento ativo. Contribuições são bem-vindas!

### Checklist de Segurança

Antes de contribuir, certifique-se de:
- ✅ Remover todas as referências a caminhos locais
- ✅ Não incluir chaves de API ou senhas
- ✅ Remover informações pessoais dos logs
- ✅ Usar variáveis de ambiente para configurações sensíveis
- ✅ Verificar arquivos de cache e logs antes do commit

### Executando Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_pdf_trainer.py
pytest tests/test_knowledge.py

# Com cobertura
pytest --cov=code_maria
```

### Docker

```bash
# Construir imagem
docker build -t codemaria .

# Executar container
docker run -p 8000:8000 codemaria
```

## Privacidade e Segurança

Este projeto segue as melhores práticas de segurança e privacidade:

1. **Dados Sensíveis**
   - Todas as chaves de API devem ser armazenadas em variáveis de ambiente
   - Nunca commite o arquivo `.env`
   - Use o `.gitignore` para excluir arquivos sensíveis

2. **Logs e Cache**
   - Limpe logs antes do commit
   - Não inclua dados pessoais nos logs
   - Mantenha o cache local

3. **Contribuições**
   - Verifique seus commits por informações sensíveis
   - Use ferramentas de sanitização quando necessário
   - Siga o guia de contribuição

## Licença

Este projeto está sob a licença MIT.

## Autores

- Equipe CodeMaria
- Contribuidores da comunidade

## Agradecimentos

Agradecemos a todos que contribuíram para o desenvolvimento deste projeto. 