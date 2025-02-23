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
git clone https://github.com/seu-usuario/CodeMarIA.git
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

## Licença

Este projeto está sob a licença MIT.

## Autores

- Equipe CodeMaria
- Contribuidores da comunidade

## Agradecimentos

Agradecemos a todos que contribuíram para o desenvolvimento deste projeto. 