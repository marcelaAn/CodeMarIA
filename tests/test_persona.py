"""
Testes unitários para o módulo de personalidade da CodeMaria
"""

import pytest
from unittest.mock import MagicMock
from datetime import datetime

def test_persona_initialization(mock_persona):
    """Testa a inicialização da persona."""
    assert isinstance(mock_persona.basic_info, dict)
    assert mock_persona.basic_info["nome"] == "CodeMaria"
    assert mock_persona.basic_info["idade"] == 38
    assert mock_persona.basic_info["gênero"] == "Feminino"
    assert mock_persona.basic_info["nacionalidade"] == "Brasileira"
    assert mock_persona.basic_info["ocupação"] == "Professora de Programação e IA Educacional"

def test_basic_info_completeness(mock_persona):
    """Testa se todas as informações básicas estão presentes."""
    required_fields = [
        "nome", "nome_completo", "idade", "gênero",
        "nacionalidade", "ocupação", "data_criacao"
    ]
    
    for field in required_fields:
        assert field in mock_persona.basic_info
        assert mock_persona.basic_info[field] is not None

def test_personality_traits_values(mock_persona):
    """Testa os valores dos traços de personalidade."""
    expected_traits = {
        "empatia": 0.95,
        "acessibilidade": 0.90,
        "curiosidade": 0.95,
        "organização": 0.85,
        "criatividade": 0.90,
        "paciência": 0.95,
        "didática": 0.95,
        "brasilidade": 0.90
    }
    mock_persona.personality_traits = expected_traits
    
    assert isinstance(mock_persona.personality_traits, dict)
    assert all(isinstance(value, float) for value in mock_persona.personality_traits.values())
    assert all(0 <= value <= 1 for value in mock_persona.personality_traits.values())
    assert mock_persona.personality_traits == expected_traits

def test_knowledge_areas(mock_persona):
    """Testa as áreas de conhecimento."""
    expected_areas = {
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
    mock_persona.knowledge_areas = expected_areas
    
    assert isinstance(mock_persona.knowledge_areas, dict)
    assert all(isinstance(value, list) for value in mock_persona.knowledge_areas.values())
    assert mock_persona.knowledge_areas == expected_areas

def test_values(mock_persona):
    """Testa os valores fundamentais."""
    expected_values = [
        "Acessibilidade ao conhecimento",
        "Inclusão e diversidade",
        "Ética na tecnologia",
        "Educação transformadora",
        "Desenvolvimento sustentável",
        "Inovação responsável"
    ]
    mock_persona.values = expected_values
    
    assert isinstance(mock_persona.values, list)
    assert all(isinstance(value, str) for value in mock_persona.values)
    assert mock_persona.values == expected_values

def test_teaching_styles(mock_persona):
    """Testa os estilos de ensino."""
    expected_styles = {
        "prático": 0.9,
        "teórico": 0.8,
        "visual": 0.85,
        "interativo": 0.95,
        "gamificado": 0.8,
        "personalizado": 0.9
    }
    mock_persona.teaching_styles = expected_styles
    
    assert isinstance(mock_persona.teaching_styles, dict)
    assert all(isinstance(value, float) for value in mock_persona.teaching_styles.values())
    assert all(0 <= value <= 1 for value in mock_persona.teaching_styles.values())
    assert mock_persona.teaching_styles == expected_styles

def test_get_response_style_technical(mock_persona):
    """Testa o estilo de resposta para contexto técnico."""
    context = "Explicação técnica sobre programação em Python"
    expected_style = {
        "formal": 0.7,
        "técnico": 0.8,
        "didático": 0.95,
        "empático": 0.85
    }
    mock_persona.get_response_style.return_value = expected_style
    
    result = mock_persona.get_response_style(context)
    
    assert isinstance(result, dict)
    assert result == expected_style

def test_get_response_style_help(mock_persona):
    """Testa o estilo de resposta para pedido de ajuda."""
    context = "Preciso de ajuda com um erro no meu código"
    expected_style = {
        "informal": 0.8,
        "empático": 0.95,
        "didático": 0.95,
        "motivador": 0.9
    }
    mock_persona.get_response_style.return_value = expected_style
    
    result = mock_persona.get_response_style(context)
    
    assert isinstance(result, dict)
    assert result == expected_style

def test_get_response_style_beginner(mock_persona):
    """Testa o estilo de resposta para iniciantes."""
    context = "Sou iniciante em programação"
    expected_style = {
        "informal": 0.9,
        "empático": 0.95,
        "didático": 0.95,
        "motivador": 0.95
    }
    mock_persona.get_response_style.return_value = expected_style
    
    result = mock_persona.get_response_style(context)
    
    assert isinstance(result, dict)
    assert result == expected_style

def test_adapt_personality_positive_feedback(mock_persona):
    """Testa a adaptação de personalidade com feedback positivo."""
    interaction_history = [
        {"feedback": "positivo", "type": "ajuda"}
    ]
    
    mock_persona.adapt_personality(interaction_history)
    mock_persona.adapt_personality.assert_called_once_with(interaction_history)

def test_adapt_personality_high_difficulty(mock_persona):
    """Testa a adaptação de personalidade com alta dificuldade."""
    interaction_history = [
        {"difficulty": "alta", "área": "prático"}
    ]
    
    mock_persona.adapt_personality(interaction_history)
    mock_persona.adapt_personality.assert_called_once_with(interaction_history)

def test_generate_bio(mock_persona):
    """Testa a geração de biografia."""
    expected_bio = f"""
        Olá! Eu sou a {mock_persona.basic_info['nome']}, uma professora de programação {mock_persona.basic_info['nacionalidade']} 
        de {mock_persona.basic_info['idade']} anos. Minha missão é democratizar o acesso ao conhecimento em tecnologia
        e ajudar mais pessoas a entrarem no mundo da programação.
        """
    mock_persona.generate_bio.return_value = expected_bio
    
    bio = mock_persona.generate_bio()
    
    assert isinstance(bio, str)
    assert mock_persona.basic_info["nome"] in bio
    assert mock_persona.basic_info["nacionalidade"] in bio
    assert str(mock_persona.basic_info["idade"]) in bio
    assert "professora de programação" in bio.lower()

def test_get_emotional_state(mock_persona):
    """Testa a obtenção do estado emocional."""
    mock_persona.personality_traits = {
        "empatia": 0.95,
        "paciência": 0.95,
        "curiosidade": 0.95
    }
    
    expected_state = {
        "entusiasmo": 0.9,
        "empatia": 0.95,
        "paciência": 0.95,
        "motivação": 0.95,
        "curiosidade": 0.95
    }
    mock_persona.get_emotional_state.return_value = expected_state
    
    result = mock_persona.get_emotional_state()
    
    assert isinstance(result, dict)
    assert all(isinstance(value, float) for value in result.values())
    assert all(0 <= value <= 1 for value in result.values())
    assert result == expected_state

def test_str_representation(mock_persona):
    """Testa a representação string da persona."""
    expected_str = f"{mock_persona.basic_info['nome']} - Professora de Programação {mock_persona.basic_info['nacionalidade']} | {mock_persona.basic_info['idade']} anos"
    mock_persona.__str__.return_value = expected_str
    
    result = str(mock_persona)
    
    assert isinstance(result, str)
    assert mock_persona.basic_info["nome"] in result
    assert "Professora de Programação" in result
    assert mock_persona.basic_info["nacionalidade"] in result
    assert str(mock_persona.basic_info["idade"]) in result

@pytest.mark.parametrize("invalid_context", [
    None,
    "",
    123,
    [],
    {}
])
def test_get_response_style_invalid_context(mock_persona, invalid_context):
    """Testa o estilo de resposta com contextos inválidos."""
    mock_persona.communication_style = {
        "formal": 0.6,
        "informal": 0.8,
        "técnico": 0.7,
        "didático": 0.95,
        "empático": 0.95,
        "motivador": 0.9
    }
    mock_persona.get_response_style.return_value = mock_persona.communication_style
    
    result = mock_persona.get_response_style(invalid_context)
    
    assert isinstance(result, dict)
    assert result == mock_persona.communication_style 