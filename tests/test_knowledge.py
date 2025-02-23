"""
Testes para verificar o conhecimento adquirido pela CodeMaria
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from code_maria.learning import LearningEngine
from code_maria.pdf_processor import PDFProcessor
from code_maria.pdf_trainer import PDFTrainer
from pathlib import Path
import json

@pytest.fixture
def learning_engine():
    """Fixture para criar uma instância do LearningEngine."""
    return LearningEngine()

@pytest.fixture
def pdf_trainer():
    """Fixture para criar uma instância do PDFTrainer."""
    return PDFTrainer()

def test_knowledge_base_structure(learning_engine):
    """Testa a estrutura da base de conhecimento."""
    assert hasattr(learning_engine, 'knowledge_base')
    assert isinstance(learning_engine.knowledge_base, dict)
    assert hasattr(learning_engine, 'learning_history')
    assert isinstance(learning_engine.learning_history, list)

def test_sentiment_analyzer_initialization(learning_engine):
    """Testa se o analisador de sentimentos foi inicializado corretamente."""
    assert learning_engine.sentiment_analyzer is not None
    assert hasattr(learning_engine.sentiment_analyzer, '__call__')

def test_pdf_knowledge_retention(pdf_trainer):
    """Testa se o conhecimento dos PDFs está sendo retido."""
    stats = pdf_trainer.get_training_stats()
    assert stats["status"] == "success"
    assert "statistics" in stats
    
    # Verifica estatísticas básicas
    statistics = stats["statistics"]
    assert statistics["total_files"] > 0
    assert statistics["successful"] > 0
    assert statistics["success_rate"] > 0
    
    # Verifica distribuição de sentimentos
    assert "sentiment_distribution" in statistics
    sentiment_dist = statistics["sentiment_distribution"]
    assert isinstance(sentiment_dist, dict)
    assert sum(sentiment_dist.values()) == statistics["total_files"]
    
    # Verifica estatísticas gramaticais
    assert "grammar_statistics" in statistics
    grammar_stats = statistics["grammar_statistics"]
    assert "total_sentences" in grammar_stats
    assert "total_words" in grammar_stats
    assert "avg_sentence_length" in grammar_stats

def test_learning_from_processed_pdfs(learning_engine, pdf_trainer):
    """Testa o aprendizado a partir dos PDFs processados."""
    # Obtém resultados do treinamento
    training_stats = pdf_trainer.get_training_stats()
    assert training_stats["status"] == "success"
    
    # Verifica se os PDFs processados foram incorporados à base de conhecimento
    if "pdf_learning" in learning_engine.knowledge_base:
        pdf_knowledge = learning_engine.knowledge_base["pdf_learning"]
        assert isinstance(pdf_knowledge, list)
        assert len(pdf_knowledge) > 0
        
        # Verifica estrutura do conhecimento
        for entry in pdf_knowledge:
            assert "file" in entry
            assert "grammar_analysis" in entry
            assert "sentiment" in entry
            assert "timestamp" in entry

def test_grammar_analysis_quality(pdf_trainer):
    """Testa a qualidade da análise gramatical."""
    stats = pdf_trainer.get_training_stats()
    grammar_stats = stats["statistics"]["grammar_statistics"]
    
    # Verifica métricas de qualidade
    assert grammar_stats["total_sentences"] > 0
    assert grammar_stats["total_words"] > 0
    assert 10 <= grammar_stats["avg_sentence_length"] <= 50  # Média razoável para português

def test_sentiment_analysis_distribution(pdf_trainer):
    """Testa a distribuição da análise de sentimentos."""
    stats = pdf_trainer.get_training_stats()
    sentiment_dist = stats["statistics"]["sentiment_distribution"]
    
    # Verifica se temos uma distribuição válida
    total_docs = stats["statistics"]["total_files"]
    assert sum(sentiment_dist.values()) == total_docs
    
    # Verifica categorias de sentimento
    assert all(category in ["POSITIVE", "NEGATIVE", "NEUTRAL"] 
              for category in sentiment_dist.keys())

def test_learning_history_persistence(pdf_trainer):
    """Testa a persistência do histórico de aprendizado."""
    # Verifica arquivo de histórico
    history_file = Path(pdf_trainer.training_dir) / "training_history.json"
    assert history_file.exists()
    
    # Carrega e verifica histórico
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    assert isinstance(history, list)
    if history:
        entry = history[0]
        assert "file" in entry
        assert "timestamp" in entry
        assert "status" in entry

def test_cache_effectiveness(pdf_trainer):
    """Testa a efetividade do cache."""
    # Verifica se o cache está configurado
    assert hasattr(pdf_trainer, 'cache')
    assert isinstance(pdf_trainer.cache, dict)
    
    # Verifica se o diretório de cache existe
    cache_dir = pdf_trainer.cache_dir
    assert cache_dir.exists()
    
    # Verifica TTL do cache
    assert hasattr(pdf_trainer, 'cache_ttl')
    assert pdf_trainer.cache_ttl.total_seconds() == 24 * 3600  # 24 horas
    
    # Verifica se o cache é salvo
    cache_file = pdf_trainer.cache_file
    assert cache_file.exists()
    
    # Verifica se podemos carregar o cache
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
        assert isinstance(cache_data, dict)

def test_knowledge_evolution(learning_engine):
    """Testa a evolução do conhecimento ao longo do tempo."""
    if learning_engine.learning_history:
        # Ordena histórico por timestamp
        sorted_history = sorted(
            learning_engine.learning_history,
            key=lambda x: x.get("timestamp", "")
        )
        
        # Verifica progressão temporal
        first_entry = sorted_history[0]
        last_entry = sorted_history[-1]
        assert first_entry["timestamp"] <= last_entry["timestamp"]

def test_error_handling_and_recovery(pdf_trainer):
    """Testa o tratamento e recuperação de erros."""
    # Simula um PDF problemático
    result = pdf_trainer._process_single_pdf("arquivo_inexistente.pdf")
    assert "error" in result
    
    # Verifica se o erro foi registrado mas não afetou o sistema
    stats = pdf_trainer.get_training_stats()
    assert stats["status"] == "success"  # Sistema continua funcionando

@pytest.mark.parametrize("text_sample", [
    "Este é um texto positivo sobre programação.",
    "Erro grave detectado no sistema.",
    "O programa está funcionando normalmente."
])
def test_sentiment_analysis_consistency(learning_engine, text_sample):
    """Testa a consistência da análise de sentimentos."""
    sentiment = learning_engine.analyze_sentiment(text_sample)
    assert "label" in sentiment
    assert "score" in sentiment
    assert 0 <= sentiment["score"] <= 1

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 