"""
Testes unitários para o RateLimiter
"""

import pytest
import time
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
from threading import Event
from code_maria.rate_limiter import (
    RateLimiter,
    RateLimitError,
    ConfigurationError,
    ValidationError
)

@pytest.fixture
def temp_config_file(tmp_path):
    """Cria um arquivo de configuração temporário para testes."""
    config = {
        "test_api": {"calls": 10, "period": 60},
        "another_api": {"calls": 5, "period": 30}
    }
    config_file = tmp_path / "test_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)
    return str(config_file)

@pytest.fixture
def rate_limiter(temp_config_file):
    """Cria uma instância do RateLimiter para testes."""
    limiter = RateLimiter(temp_config_file)
    yield limiter
    # Cleanup após cada teste
    limiter._running = False
    if hasattr(limiter, '_queue_processor'):
        limiter._queue_processor.join(timeout=1.0)

def test_initialization(temp_config_file):
    """Testa a inicialização do RateLimiter."""
    limiter = RateLimiter(temp_config_file)
    assert limiter.limits["test_api"]["calls"] == 10
    assert limiter.limits["test_api"]["period"] == 60
    assert limiter.stats["total_requests"] == 0
    assert limiter.stats["throttled_requests"] == 0
    limiter._running = False
    limiter._queue_processor.join(timeout=1.0)

def test_initialization_without_config():
    """Testa a inicialização sem arquivo de configuração."""
    limiter = RateLimiter()
    try:
        assert "default" in limiter.limits
        assert limiter.limits["default"]["calls"] == 60
        assert limiter.limits["default"]["period"] == 60
    finally:
        limiter._running = False
        limiter._queue_processor.join(timeout=1.0)

def test_invalid_config_file():
    """Testa o comportamento com arquivo de configuração inválido."""
    with pytest.raises(ConfigurationError):
        RateLimiter("nonexistent_file.json")

def test_load_yaml_config(tmp_path):
    """Testa carregamento de configuração YAML."""
    config = {
        "test_api": {"calls": 10, "period": 60}
    }
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    
    limiter = RateLimiter(str(config_file))
    try:
        assert limiter.limits["test_api"]["calls"] == 10
    finally:
        limiter._running = False
        limiter._queue_processor.join(timeout=1.0)

def test_acquire_basic(rate_limiter):
    """Testa aquisição básica de permissão."""
    assert rate_limiter.acquire("test_api") is True
    stats = rate_limiter.get_stats()
    assert stats["total_requests"] == 1
    assert stats["successful_requests"] == 1

def test_acquire_invalid_api():
    """Testa aquisição com API inválida."""
    limiter = RateLimiter()
    try:
        with pytest.raises(ValidationError):
            limiter.acquire("")
    finally:
        limiter._running = False
        limiter._queue_processor.join(timeout=1.0)

def test_throttling(rate_limiter):
    """Testa o comportamento de throttling."""
    # Define um período curto para o teste
    rate_limiter.limits["test_api"]["period"] = 1
    
    # Faz requisições até atingir o limite
    for i in range(10):
        assert rate_limiter.acquire("test_api") is True, f"Falha na requisição {i+1}"
    
    # Próxima requisição deve ser throttled
    assert rate_limiter.acquire("test_api") is False
    stats = rate_limiter.get_stats()
    assert stats["throttled_requests"] == 1
    
    # Aguarda o reset do período
    time.sleep(1.1)
    assert rate_limiter.acquire("test_api") is True

def test_callback_execution(rate_limiter):
    """Testa execução de callbacks."""
    done = Event()
    def callback():
        done.set()
    
    assert rate_limiter.acquire("test_api", callback=callback) is True
    assert done.wait(timeout=1.0), "Callback não foi executado no tempo esperado"

def test_callback_error_handling(rate_limiter):
    """Testa tratamento de erros em callbacks."""
    done = Event()
    def failing_callback():
        done.set()
        raise ValueError("Teste de erro")
    
    assert rate_limiter.acquire("test_api", callback=failing_callback) is True
    assert done.wait(timeout=1.0), "Callback não foi executado no tempo esperado"
    
    stats = rate_limiter.get_detailed_stats()
    assert stats["api_metrics"]["test_api"]["requests"]["error_count"] == 1

def test_timeout_handling(rate_limiter):
    """Testa tratamento de timeout."""
    done = Event()
    callback = Mock(side_effect=lambda: done.set())
    
    # Força throttling
    for _ in range(10):
        rate_limiter.acquire("test_api")
    
    # Tenta com timeout curto
    assert rate_limiter.acquire("test_api", callback=callback, timeout=0.1) is True
    assert not done.wait(timeout=0.2), "Callback não deveria ter sido executado"
    callback.assert_not_called()

def test_update_limits(rate_limiter):
    """Testa atualização de limites."""
    assert rate_limiter.update_limits("new_api", 20, 30) is True
    assert rate_limiter.limits["new_api"]["calls"] == 20
    assert rate_limiter.limits["new_api"]["period"] == 30

def test_update_limits_validation():
    """Testa validação na atualização de limites."""
    limiter = RateLimiter()
    try:
        with pytest.raises(ValidationError):
            limiter.update_limits("test", -1, 60)
        with pytest.raises(ValidationError):
            limiter.update_limits("test", 100, 0)
    finally:
        limiter._running = False
        limiter._queue_processor.join(timeout=1.0)

def test_reset_counts(rate_limiter):
    """Testa reset de contadores."""
    rate_limiter.acquire("test_api")
    assert rate_limiter.reset_counts("test_api") is True
    stats = rate_limiter.get_stats()
    assert "test_api" not in stats["current_counts"]

def test_detailed_stats(rate_limiter):
    """Testa estatísticas detalhadas."""
    done = Event()
    callback = Mock(side_effect=lambda: done.set())
    
    rate_limiter.acquire("test_api", callback=callback)
    assert done.wait(timeout=1.0), "Callback não foi executado no tempo esperado"
    
    stats = rate_limiter.get_detailed_stats()
    assert "api_metrics" in stats
    assert "queue_stats" in stats
    assert "test_api" in stats["api_metrics"]

def test_queue_priority(rate_limiter):
    """Testa priorização na fila."""
    done1 = Event()
    done2 = Event()
    
    def callback1():
        done1.set()
    
    def callback2():
        done2.set()
    
    # Força throttling
    for _ in range(10):
        rate_limiter.acquire("test_api")
    
    # Enfileira duas requisições
    rate_limiter.acquire("test_api", callback=callback1)
    rate_limiter.acquire("test_api", callback=callback2)
    
    # Aguarda execução com timeout
    assert done1.wait(timeout=1.0), "Primeira callback não executou"
    assert done2.wait(timeout=1.0), "Segunda callback não executou"
    assert done1.is_set() and done2.is_set(), "Ambos callbacks devem executar"

def test_cleanup(rate_limiter):
    """Testa limpeza de recursos."""
    rate_limiter.__del__()
    assert not rate_limiter._running
    assert rate_limiter._queue_processor.join(timeout=1.0) is None

@pytest.fixture(autouse=True)
def cleanup_after_test(rate_limiter):
    """Garante limpeza após cada teste."""
    yield
    rate_limiter._running = False
    rate_limiter._queue_processor.join(timeout=1.0)

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 