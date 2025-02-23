"""
Configurações globais para testes da CodeMaria
"""

import pytest
from unittest.mock import MagicMock
from datetime import datetime

@pytest.fixture
def mock_api_keys():
    """Fixture para simular chaves de API."""
    return {
        "openai": "test_key_openai",
        "google": "test_key_google",
        "news_api": "test_key_news"
    }

@pytest.fixture
def mock_learning_engine():
    """Fixture para criar uma instância mockada do LearningEngine."""
    engine = MagicMock()
    engine.knowledge_base = {}
    engine.learning_history = []
    engine.sentiment_analyzer = MagicMock()
    engine.sentiment_analyzer.return_value = [{"label": "POSITIVE", "score": 0.9}]
    return engine

@pytest.fixture
def mock_creativity_engine():
    """Fixture para criar uma instância mockada do CreativityEngine."""
    engine = MagicMock()
    engine.text_generator = MagicMock()
    engine.text_generator.return_value = [{"generated_text": "Texto gerado para teste"}]
    engine.creative_memory = []
    engine.creativity_level = 0.9
    return engine

@pytest.fixture
def mock_persona():
    """Fixture para criar uma instância mockada da Persona."""
    persona = MagicMock()
    persona.basic_info = {
        "nome": "CodeMaria",
        "nome_completo": "CodeMaria - Professora de Programação",
        "idade": 38,
        "gênero": "Feminino",
        "nacionalidade": "Brasileira",
        "ocupação": "Professora de Programação e IA Educacional",
        "data_criacao": datetime.now()
    }
    
    persona.personality_traits = {
        "empatia": 0.95,
        "acessibilidade": 0.90,
        "curiosidade": 0.95,
        "organização": 0.85,
        "criatividade": 0.90,
        "paciência": 0.95,
        "didática": 0.95,
        "brasilidade": 0.90
    }
    
    persona.knowledge_areas = {
        "linguagens": [
            "Python", "JavaScript", "Java", "C++",
            "TypeScript", "Ruby", "Go", "Rust"
        ],
        "frameworks": [
            "React", "Angular", "Vue.js", "Django",
            "Flask", "Spring", "TensorFlow", "PyTorch"
        ],
        "areas": [
            "Desenvolvimento Web", "Mobile", "Ciência de Dados",
            "Inteligência Artificial", "DevOps", "Segurança"
        ]
    }
    
    persona.values = [
        "Acessibilidade ao conhecimento",
        "Inclusão e diversidade",
        "Ética na tecnologia",
        "Educação transformadora",
        "Desenvolvimento sustentável",
        "Inovação responsável"
    ]
    
    persona.teaching_styles = {
        "prático": 0.9,
        "teórico": 0.8,
        "visual": 0.85,
        "interativo": 0.95,
        "gamificado": 0.8,
        "personalizado": 0.9
    }
    
    persona.communication_style = {
        "formal": 0.6,
        "informal": 0.8,
        "técnico": 0.7,
        "didático": 0.95,
        "empático": 0.95,
        "motivador": 0.9
    }
    
    return persona

@pytest.fixture
def mock_api_integrations(mock_api_keys):
    """Fixture para criar uma instância mockada do APIIntegrations."""
    api = MagicMock()
    api.api_keys = mock_api_keys
    api.base_urls = {
        "news": "https://newsapi.org/v2",
        "google_search": "https://www.googleapis.com/customsearch/v1",
        "openai": "https://api.openai.com/v1"
    }
    return api

@pytest.fixture
def code_maria_instance(mock_learning_engine, mock_creativity_engine, mock_persona):
    """Fixture para criar uma instância mockada da CodeMaria."""
    instance = MagicMock()
    instance.name = "CodeMaria"
    instance.version = "0.1.0"
    instance.active_learning = True
    instance.creation_date = datetime.now()
    instance.knowledge_base = {}
    instance.personality_traits = mock_persona.personality_traits
    instance.knowledge_areas = mock_persona.knowledge_areas
    instance.teaching_styles = mock_persona.teaching_styles
    
    # Configura os módulos auxiliares
    instance.learning_engine = mock_learning_engine
    instance.creativity_engine = mock_creativity_engine
    instance.persona = mock_persona
    
    return instance 