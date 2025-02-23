"""
Testes para o módulo de treinamento com PDFs
"""

import pytest
from pathlib import Path
import json
from unittest.mock import MagicMock, patch
from code_maria.pdf_trainer import PDFTrainer

@pytest.fixture
def mock_pdf_processor():
    """Mock do processador de PDFs."""
    mock = MagicMock()
    mock.process_pdf.return_value = {
        "file_path": "test.pdf",
        "metadata": {"title": "Test PDF"},
        "text": "Sample text for testing",
        "error": None
    }
    mock.analyze_grammar.return_value = {
        "num_sentences": 1,
        "num_words": 4,
        "num_unique_words": 4,
        "avg_sentence_length": 4.0,
        "most_common_words": {"test": 1},
        "pos_distribution": {"NN": 2}
    }
    return mock

@pytest.fixture
def mock_learning_engine():
    """Mock do motor de aprendizado."""
    mock = MagicMock()
    mock.analyze_sentiment.return_value = {
        "label": "POSITIVE",
        "score": 0.9
    }
    mock.update_knowledge_base.return_value = True
    return mock

@pytest.fixture
def trainer(tmp_path, mock_pdf_processor, mock_learning_engine):
    """Instância do PDFTrainer para testes."""
    with patch("code_maria.pdf_trainer.PDFProcessor", return_value=mock_pdf_processor), \
         patch("code_maria.pdf_trainer.LearningEngine", return_value=mock_learning_engine):
        trainer = PDFTrainer(base_dir=str(tmp_path))
        return trainer

def test_initialization(tmp_path):
    """Testa inicialização do PDFTrainer."""
    trainer = PDFTrainer(base_dir=str(tmp_path))
    assert trainer.base_dir == Path(tmp_path)
    assert trainer.training_dir == trainer.base_dir / "training"
    assert trainer.training_history == []
    assert trainer.history_file == trainer.training_dir / "training_history.json"
    assert Path(tmp_path).exists()

def test_train_no_pdfs(trainer):
    """Testa treinamento sem PDFs disponíveis."""
    result = trainer.train()
    assert result["status"] == "error"
    assert "Nenhum arquivo PDF encontrado" in result["message"]

def test_train_with_pdf(trainer, tmp_path):
    """Testa treinamento com um PDF."""
    # Cria arquivo de teste com cabeçalho PDF válido
    pdf_path = tmp_path / "test.pdf"
    pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000015 00000 n\n0000000061 00000 n\n0000000114 00000 n\ntrailer\n<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
    pdf_path.write_bytes(pdf_content)
    
    result = trainer.train()
    assert result["status"] == "success"
    assert result["summary"]["total_files"] == 1
    assert result["summary"]["successful"] == 1
    assert result["summary"]["failed"] == 0
    
    # Verifica se histórico foi salvo
    assert trainer.training_history
    assert len(trainer.training_history) == 1
    assert trainer.history_file.exists()

def test_train_with_error(trainer, tmp_path, mock_pdf_processor):
    """Testa treinamento com erro no processamento."""
    # Configura mock para retornar erro
    mock_pdf_processor.process_pdf.return_value = {
        "file_path": "test.pdf",
        "metadata": {},
        "text": "",
        "error": "Erro de teste"
    }
    
    # Cria arquivo de teste
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"PDF test content")
    
    result = trainer.train()
    assert result["status"] == "success"
    assert result["summary"]["total_files"] == 1
    assert result["summary"]["successful"] == 0
    assert result["summary"]["failed"] == 1

def test_get_training_stats_empty(trainer):
    """Testa estatísticas sem treinamento."""
    stats = trainer.get_training_stats()
    assert stats["status"] == "info"
    assert "Nenhum treinamento realizado" in stats["message"]

def test_get_training_stats_with_data(trainer, tmp_path):
    """Testa estatísticas com dados de treinamento."""
    # Cria arquivo de teste com cabeçalho PDF válido
    pdf_path = tmp_path / "test.pdf"
    pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000015 00000 n\n0000000061 00000 n\n0000000114 00000 n\ntrailer\n<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
    pdf_path.write_bytes(pdf_content)
    
    trainer.train()
    
    stats = trainer.get_training_stats()
    assert stats["status"] == "success"
    assert "statistics" in stats
    assert stats["statistics"]["total_files"] == 1
    assert stats["statistics"]["successful"] == 1
    assert stats["statistics"]["failed"] == 0
    assert stats["statistics"]["success_rate"] == 100.0

def test_clear_history(trainer, tmp_path):
    """Testa limpeza do histórico."""
    # Realiza um treinamento
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"PDF test content")
    trainer.train()
    
    # Limpa histórico
    result = trainer.clear_history()
    assert result["status"] == "success"
    assert not trainer.training_history
    assert not trainer.history_file.exists()

def test_load_history(trainer, tmp_path):
    """Testa carregamento do histórico."""
    # Cria histórico de teste
    history = [{
        "file": "test.pdf",
        "timestamp": "2024-02-23T12:00:00",
        "status": "success"
    }]
    
    with open(trainer.history_file, 'w') as f:
        json.dump(history, f)
    
    # Recarrega histórico
    trainer._load_history()
    assert trainer.training_history == history 