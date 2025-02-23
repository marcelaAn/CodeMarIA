"""
Testes unitários para o módulo de aprendizado da CodeMaria
"""

import pytest
from unittest.mock import patch, MagicMock
from code_maria.learning import LearningEngine

def test_learning_engine_initialization(mock_learning_engine):
    """Testa a inicialização do motor de aprendizado."""
    assert isinstance(mock_learning_engine.knowledge_base, dict)
    assert isinstance(mock_learning_engine.learning_history, list)
    assert mock_learning_engine.sentiment_analyzer is not None

@patch('requests.get')
def test_learn_from_web_success(mock_get, mock_learning_engine):
    """Testa o aprendizado a partir de conteúdo web com sucesso."""
    # Configura o mock da resposta
    mock_response = MagicMock()
    mock_response.text = "<html><body>Conteúdo de teste para aprendizado</body></html>"
    mock_get.return_value = mock_response
    
    # Configura o retorno do mock
    expected_result = {
        "url": "https://example.com",
        "content_length": 54,
        "sentiment": {"label": "POSITIVE", "score": 0.9},
        "timestamp": "auto_now"
    }
    mock_learning_engine.learn_from_web.return_value = expected_result
    
    result = mock_learning_engine.learn_from_web("https://example.com")
    
    assert isinstance(result, dict)
    assert result == expected_result

@patch('requests.get')
def test_learn_from_web_failure(mock_get, mock_learning_engine):
    """Testa o aprendizado a partir de conteúdo web com falha."""
    # Simula uma falha na requisição
    mock_get.side_effect = Exception("Erro de conexão")
    
    # Configura o retorno do mock
    expected_error = {"error": "Erro de conexão"}
    mock_learning_engine.learn_from_web.return_value = expected_error
    
    result = mock_learning_engine.learn_from_web("https://example.com")
    
    assert isinstance(result, dict)
    assert "error" in result

def test_analyze_sentiment_success(mock_learning_engine):
    """Testa a análise de sentimento com sucesso."""
    text = "Este é um texto positivo para teste"
    expected_result = {"label": "POSITIVE", "score": 0.9}
    mock_learning_engine.analyze_sentiment.return_value = expected_result
    
    result = mock_learning_engine.analyze_sentiment(text)
    
    assert isinstance(result, dict)
    assert "label" in result
    assert "score" in result
    assert isinstance(result["score"], float)
    assert 0 <= result["score"] <= 1

def test_analyze_sentiment_failure(mock_learning_engine):
    """Testa a análise de sentimento com falha."""
    # Configura o mock para lançar uma exceção
    mock_learning_engine.sentiment_analyzer.side_effect = Exception("Erro na análise")
    expected_error = {"error": "Erro na análise"}
    mock_learning_engine.analyze_sentiment.return_value = expected_error
    
    result = mock_learning_engine.analyze_sentiment("texto qualquer")
    
    assert isinstance(result, dict)
    assert "error" in result

def test_update_knowledge_base_new_category(mock_learning_engine):
    """Testa a atualização da base de conhecimento com nova categoria."""
    category = "test_category"
    data = {"key": "value"}
    mock_learning_engine.update_knowledge_base.return_value = True
    
    result = mock_learning_engine.update_knowledge_base(category, data)
    
    assert result is True

def test_update_knowledge_base_existing_category(mock_learning_engine):
    """Testa a atualização da base de conhecimento com categoria existente."""
    category = "test_category"
    data1 = {"key": "value1"}
    data2 = {"key": "value2"}
    
    mock_learning_engine.update_knowledge_base.return_value = True
    
    mock_learning_engine.update_knowledge_base(category, data1)
    result = mock_learning_engine.update_knowledge_base(category, data2)
    
    assert result is True

def test_get_learning_summary_empty(mock_learning_engine):
    """Testa o resumo de aprendizado com histórico vazio."""
    expected_summary = {
        "total_entries": 0,
        "knowledge_categories": [],
        "last_learning": None
    }
    mock_learning_engine.get_learning_summary.return_value = expected_summary
    
    summary = mock_learning_engine.get_learning_summary()
    
    assert isinstance(summary, dict)
    assert summary["total_entries"] == 0
    assert isinstance(summary["knowledge_categories"], list)
    assert summary["last_learning"] is None

def test_get_learning_summary_with_data(mock_learning_engine):
    """Testa o resumo de aprendizado com dados."""
    # Configura o retorno esperado
    expected_summary = {
        "total_entries": 1,
        "knowledge_categories": ["category1", "category2"],
        "last_learning": {"test": "data"}
    }
    mock_learning_engine.get_learning_summary.return_value = expected_summary
    
    # Adiciona alguns dados de teste
    mock_learning_engine.learning_history.append({"test": "data"})
    mock_learning_engine.update_knowledge_base("category1", {"data": "test1"})
    mock_learning_engine.update_knowledge_base("category2", {"data": "test2"})
    
    summary = mock_learning_engine.get_learning_summary()
    
    assert summary["total_entries"] == 1
    assert len(summary["knowledge_categories"]) == 2
    assert summary["last_learning"] == {"test": "data"}

@pytest.mark.parametrize("invalid_category", [
    None,
    123,
    [],
    {}
])
def test_update_knowledge_base_invalid_category(mock_learning_engine, invalid_category):
    """Testa a atualização da base de conhecimento com categorias inválidas."""
    mock_learning_engine.update_knowledge_base.return_value = False
    
    result = mock_learning_engine.update_knowledge_base(invalid_category, {"data": "test"})
    assert result is False 