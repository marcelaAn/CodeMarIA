"""
Testes unitários para o módulo creativity da CodeMaria
"""

import pytest
from unittest.mock import MagicMock, patch
from code_maria.creativity import CreativityEngine
import json
from pathlib import Path

@pytest.fixture
def creativity_engine():
    """Fixture para criar uma instância do CreativityEngine com mocks."""
    with patch("code_maria.creativity.pipeline") as mock_pipeline:
        mock_generator = MagicMock()
        mock_generator.return_value = [{"generated_text": "Texto gerado para teste"}]
        mock_pipeline.return_value = mock_generator
        
        engine = CreativityEngine()
        return engine

def test_initialization(creativity_engine):
    """Testa a inicialização do CreativityEngine."""
    assert creativity_engine.creativity_level == 0.8
    assert isinstance(creativity_engine.creative_memory, list)
    assert isinstance(creativity_engine.templates, dict)
    assert "tutorial" in creativity_engine.templates
    assert "quiz" in creativity_engine.templates
    assert "code_example" in creativity_engine.templates

def test_load_templates(creativity_engine):
    """Testa o carregamento de templates."""
    templates = creativity_engine.templates
    
    assert "tutorial" in templates
    assert "sections" in templates["tutorial"]
    assert "base" in templates["tutorial"]
    
    assert "quiz" in templates
    assert "question_types" in templates["quiz"]
    
    assert "code_example" in templates
    assert "sections" in templates["code_example"]

@pytest.mark.parametrize("content_type,difficulty,language", [
    ("tutorial", "iniciante", "python"),
    ("quiz", "intermediário", "python"),
    ("code_example", "avançado", "python")
])
def test_generate_educational_content(creativity_engine, content_type, difficulty, language):
    """Testa a geração de diferentes tipos de conteúdo educacional."""
    content = creativity_engine.generate_educational_content(
        topic="Funções em Python",
        content_type=content_type,
        difficulty=difficulty,
        language=language
    )
    
    assert isinstance(content, dict)
    assert "error" not in content
    
    if content_type == "tutorial":
        assert "título" in content
        assert "seções" in content
        assert isinstance(content["seções"], list)
        assert content["nível"] == difficulty
        assert content["linguagem"] == language
        
    elif content_type == "quiz":
        assert "título" in content
        assert "questões" in content
        assert isinstance(content["questões"], list)
        assert content["nível"] == difficulty
        
    elif content_type == "code_example":
        assert "título" in content
        assert "seções" in content
        assert content["linguagem"] == language
        assert content["nível"] == difficulty

def test_generate_tutorial(creativity_engine):
    """Testa a geração de tutorial em detalhes."""
    tutorial = creativity_engine._generate_tutorial(
        topic="Loops em Python",
        difficulty="iniciante",
        language="python",
        creative_level=0.8
    )
    
    assert isinstance(tutorial, dict)
    assert "título" in tutorial
    assert "Loops em Python" in tutorial["título"]
    assert "seções" in tutorial
    assert len(tutorial["seções"]) > 0
    
    # Verifica se todas as seções necessárias estão presentes
    section_types = [section["tipo"] for section in tutorial["seções"]]
    assert "introdução" in section_types
    assert "exemplos" in section_types
    assert "exercícios" in section_types
    
    # Verifica se exemplos e exercícios têm código
    for section in tutorial["seções"]:
        if section["tipo"] in ["exemplos", "exercícios"]:
            assert "código" in section

def test_generate_quiz(creativity_engine):
    """Testa a geração de quiz em detalhes."""
    quiz = creativity_engine._generate_quiz(
        topic="Variáveis em Python",
        difficulty="iniciante"
    )
    
    assert isinstance(quiz, dict)
    assert "título" in quiz
    assert "Variáveis em Python" in quiz["título"]
    assert "questões" in quiz
    assert len(quiz["questões"]) > 0
    
    # Verifica diferentes tipos de questões
    for questao in quiz["questões"]:
        assert "tipo" in questao
        assert questao["tipo"] in ["múltipla escolha", "verdadeiro/falso", "completar"]
        
        if questao["tipo"] == "múltipla escolha":
            assert "alternativas" in questao
            assert len(questao["alternativas"]) == 4
            assert "resposta_correta" in questao
        elif questao["tipo"] == "verdadeiro/falso":
            assert "resposta_correta" in questao
            assert isinstance(questao["resposta_correta"], bool)

def test_generate_code_example(creativity_engine):
    """Testa a geração de exemplo de código em detalhes."""
    example = creativity_engine._generate_code_example(
        topic="Classes",
        language="python",
        difficulty="intermediário"
    )
    
    assert isinstance(example, dict)
    assert "título" in example
    assert "Classes" in example["título"]
    assert "seções" in example
    
    # Verifica se todas as seções necessárias estão presentes
    section_types = [section["tipo"] for section in example["seções"]]
    assert "explicação" in section_types
    assert "código" in section_types
    assert "output" in section_types

def test_generate_code_snippet(creativity_engine):
    """Testa a geração de snippets de código."""
    snippet = creativity_engine._generate_code_snippet(
        topic="Funções",
        language="python",
        difficulty="iniciante"
    )
    
    assert isinstance(snippet, str)
    assert "def" in snippet
    assert "print" in snippet

def test_invalid_difficulty(creativity_engine):
    """Testa o tratamento de nível de dificuldade inválido."""
    with pytest.raises(ValueError) as exc_info:
        creativity_engine.generate_educational_content(
            topic="Funções",
            difficulty="expert"  # Nível inválido
        )
    assert "Nível de dificuldade inválido" in str(exc_info.value)

def test_invalid_content_type(creativity_engine):
    """Testa o tratamento de tipo de conteúdo inválido."""
    with pytest.raises(ValueError) as exc_info:
        creativity_engine.generate_educational_content(
            topic="Funções",
            content_type="invalid_type"
        )
    assert "Tipo de conteúdo não suportado" in str(exc_info.value)

def test_creativity_stats(creativity_engine):
    """Testa as estatísticas de criatividade."""
    # Gera algum conteúdo para ter estatísticas
    creativity_engine.generate_educational_content(
        topic="Funções",
        content_type="tutorial"
    )
    
    stats = creativity_engine.get_creativity_stats()
    
    assert isinstance(stats, dict)
    assert "total_creations" in stats
    assert stats["total_creations"] > 0
    assert "creativity_level" in stats
    assert stats["creativity_level"] == 0.8
    assert "templates_available" in stats
    assert "tutorial" in stats["templates_available"]
    assert "difficulty_levels" in stats
    assert "iniciante" in stats["difficulty_levels"]

def test_generate_text_with_creative_level(creativity_engine):
    """Testa a geração de texto com nível de criatividade personalizado."""
    text = creativity_engine.generate_text(
        prompt="Exemplo de teste",
        creative_level=0.9
    )
    
    assert isinstance(text, str)
    assert len(creativity_engine.creative_memory) > 0
    last_creation = creativity_engine.creative_memory[-1]
    assert last_creation["creative_level"] == 0.9

def test_error_handling(creativity_engine):
    """Testa o tratamento de erros na geração de conteúdo."""
    # Força um erro no gerador de texto
    creativity_engine.text_generator.side_effect = Exception("Erro de teste")
    
    result = creativity_engine.generate_educational_content(
        topic="Teste de Erro",
        content_type="tutorial"
    )
    
    assert "error" in result
    assert "Erro de teste" in result["error"] 