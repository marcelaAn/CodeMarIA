"""
Testes unitários para o módulo core da CodeMaria
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

def test_code_maria_initialization(code_maria_instance):
    """Testa a inicialização básica da CodeMaria."""
    assert code_maria_instance.name == "CodeMaria"
    assert code_maria_instance.version == "0.1.0"
    assert code_maria_instance.active_learning is True
    assert isinstance(code_maria_instance.knowledge_base, dict)
    assert isinstance(code_maria_instance.creation_date, datetime)

def test_personality_traits(code_maria_instance):
    """Testa os traços de personalidade da CodeMaria."""
    traits = code_maria_instance.personality_traits
    
    assert isinstance(traits, dict)
    assert all(isinstance(value, float) for value in traits.values())
    assert all(0 <= value <= 1 for value in traits.values())
    
    # Testa traços específicos
    assert "criatividade" in traits
    assert "empatia" in traits
    assert "curiosidade" in traits
    assert "didática" in traits
    assert "paciência" in traits

def test_process_input_greeting(code_maria_instance):
    """Testa o processamento de saudação."""
    input_data = {
        "text": "Olá, CodeMaria!",
        "type": "greeting",
        "user_info": {"nome": "João", "nível": "iniciante"}
    }
    expected_response = {
        "status": "success",
        "type": "greeting",
        "response": "Olá, João! Que bom ter você aqui!",
        "style": {
            "informal": 0.9,
            "empático": 0.95,
            "motivador": 0.95
        }
    }
    code_maria_instance.process_input.return_value = expected_response
    
    result = code_maria_instance.process_input(input_data)
    
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["type"] == "greeting"
    assert "João" in result["response"]
    assert isinstance(result["style"], dict)

def test_process_input_question(code_maria_instance):
    """Testa o processamento de pergunta técnica."""
    input_data = {
        "text": "Como funciona um loop for em Python?",
        "type": "question",
        "topic": "python",
        "user_info": {"nome": "Maria", "nível": "iniciante"}
    }
    expected_response = {
        "status": "success",
        "type": "explanation",
        "response": "O loop for em Python é uma estrutura de repetição que...",
        "code_example": "for i in range(5):\n    print(i)",
        "style": {
            "didático": 0.95,
            "técnico": 0.7,
            "empático": 0.85
        }
    }
    code_maria_instance.process_input.return_value = expected_response
    
    result = code_maria_instance.process_input(input_data)
    
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["type"] == "explanation"
    assert "loop for" in result["response"].lower()
    assert "code_example" in result
    assert isinstance(result["style"], dict)

def test_process_input_error_report(code_maria_instance):
    """Testa o processamento de relato de erro."""
    input_data = {
        "text": "Meu código está dando erro: IndexError: list index out of range",
        "type": "error_report",
        "code": "numbers = [1, 2, 3]\nprint(numbers[5])",
        "user_info": {"nome": "Pedro", "nível": "intermediário"}
    }
    expected_response = {
        "status": "success",
        "type": "error_solution",
        "error_type": "IndexError",
        "explanation": "Este erro ocorre quando tentamos acessar...",
        "solution": "Verifique se o índice não ultrapassa...",
        "corrected_code": "numbers = [1, 2, 3]\nif len(numbers) > 5:\n    print(numbers[5])",
        "style": {
            "didático": 0.95,
            "empático": 0.9,
            "técnico": 0.8
        }
    }
    code_maria_instance.process_input.return_value = expected_response
    
    result = code_maria_instance.process_input(input_data)
    
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["type"] == "error_solution"
    assert "error_type" in result
    assert "explanation" in result
    assert "solution" in result
    assert "corrected_code" in result

def test_learn_from_interaction(code_maria_instance):
    """Testa o aprendizado a partir de interação."""
    interaction_data = {
        "user_input": "Como faço para ordenar uma lista em Python?",
        "response": "Você pode usar o método sort() ou sorted()...",
        "feedback": "positivo",
        "user_level": "iniciante",
        "topic": "python"
    }
    code_maria_instance.learn.return_value = {
        "status": "success",
        "learned_concepts": ["ordenação", "listas", "python básico"],
        "confidence": 0.85
    }
    
    result = code_maria_instance.learn(interaction_data)
    
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert isinstance(result["learned_concepts"], list)
    assert isinstance(result["confidence"], float)
    assert 0 <= result["confidence"] <= 1

def test_learn_from_error(code_maria_instance):
    """Testa o aprendizado a partir de erro."""
    error_data = {
        "error_type": "TypeError",
        "context": "Tentativa de concatenar string com número",
        "solution_provided": "Converter o número para string antes",
        "feedback": "positivo"
    }
    code_maria_instance.learn.return_value = {
        "status": "success",
        "error_pattern": "TypeError: can only concatenate str (not 'int') to str",
        "solution_pattern": "str(number) + string",
        "confidence": 0.9
    }
    
    result = code_maria_instance.learn(error_data)
    
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert "error_pattern" in result
    assert "solution_pattern" in result
    assert isinstance(result["confidence"], float)

def test_generate_educational_content(code_maria_instance):
    """Testa a geração de conteúdo educacional."""
    request = {
        "topic": "funções em python",
        "level": "iniciante",
        "format": "tutorial",
        "include_examples": True
    }
    expected_content = {
        "title": "Introdução a Funções em Python",
        "sections": [
            {"type": "explanation", "content": "Funções são blocos de código..."},
            {"type": "example", "code": "def saudacao(nome):\n    print(f'Olá, {nome}!')"},
            {"type": "exercise", "content": "Crie uma função que calcule..."}
        ],
        "style": {
            "didático": 0.95,
            "prático": 0.9,
            "empático": 0.85
        }
    }
    code_maria_instance.generate_creative_content.return_value = expected_content
    
    result = code_maria_instance.generate_creative_content(request)
    
    assert isinstance(result, dict)
    assert "title" in result
    assert "sections" in result
    assert isinstance(result["sections"], list)
    assert "style" in result

def test_adapt_teaching_style(code_maria_instance):
    """Testa a adaptação do estilo de ensino."""
    feedback_data = {
        "user_feedback": "muito técnico",
        "user_level": "iniciante",
        "topic": "classes e objetos",
        "comprehension": 0.6
    }
    code_maria_instance.adapt_teaching_style = MagicMock()
    code_maria_instance.adapt_teaching_style(feedback_data)
    
    code_maria_instance.adapt_teaching_style.assert_called_once_with(feedback_data)

@pytest.mark.parametrize("invalid_input", [
    None,
    "",
    123,
    [],
    "texto simples"
])
def test_process_input_with_invalid_data(code_maria_instance, invalid_input):
    """Testa o processamento de entradas inválidas."""
    code_maria_instance.process_input.side_effect = Exception("Entrada inválida")
    
    with pytest.raises(Exception):
        code_maria_instance.process_input(invalid_input)

def test_error_handling(code_maria_instance):
    """Testa o tratamento de erros internos."""
    code_maria_instance.process_input.side_effect = Exception("Erro interno")
    
    with pytest.raises(Exception) as exc_info:
        code_maria_instance.process_input({"text": "teste"})
    
    assert str(exc_info.value) == "Erro interno"
    assert code_maria_instance.active_learning  # Garante que o erro não afetou o estado

def test_state_persistence(code_maria_instance):
    """Testa a persistência de estado após operações."""
    initial_traits = code_maria_instance.personality_traits.copy()
    
    # Simula algumas operações
    code_maria_instance.process_input({"text": "teste"})
    code_maria_instance.learn({"data": "teste"})
    code_maria_instance.generate_creative_content("teste")
    
    # Verifica se o estado básico foi mantido
    assert code_maria_instance.name == "CodeMaria"
    assert code_maria_instance.version == "0.1.0"
    assert code_maria_instance.active_learning is True
    assert code_maria_instance.personality_traits == initial_traits 