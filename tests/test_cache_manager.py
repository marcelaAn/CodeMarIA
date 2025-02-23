"""
Testes unitários para o módulo cache_manager da CodeMaria
"""

import pytest
from unittest.mock import patch, MagicMock
from code_maria.cache_manager import CacheManager
import json
import time
from pathlib import Path
import shutil

@pytest.fixture
def cache_dir(tmp_path):
    """Fixture para criar um diretório temporário para o cache."""
    cache_path = tmp_path / "test_cache"
    cache_path.mkdir()
    yield cache_path
    # Limpa o diretório após os testes
    shutil.rmtree(cache_path)

@pytest.fixture
def cache_manager(cache_dir):
    """Fixture para criar uma instância do CacheManager."""
    return CacheManager(cache_dir=str(cache_dir), ttl=1)

def test_initialization(cache_manager, cache_dir):
    """Testa a inicialização do CacheManager."""
    assert isinstance(cache_manager.memory_cache, dict)
    assert cache_manager.cache_dir == Path(cache_dir)
    assert cache_manager.stats["hits"] == 0
    assert cache_manager.stats["misses"] == 0

def test_set_and_get(cache_manager):
    """Testa as operações básicas de set e get."""
    # Armazena um item
    cache_manager.set("test_key", "test_value")
    
    # Recupera o item
    value = cache_manager.get("test_key")
    assert value == "test_value"
    assert cache_manager.stats["hits"] == 1

def test_get_missing_key(cache_manager):
    """Testa a recuperação de uma chave inexistente."""
    value = cache_manager.get("missing_key")
    assert value is None
    assert cache_manager.stats["misses"] == 1

def test_set_with_namespace(cache_manager):
    """Testa o armazenamento em diferentes namespaces."""
    cache_manager.set("key1", "value1", namespace="ns1")
    cache_manager.set("key1", "value2", namespace="ns2")
    
    assert cache_manager.get("key1", namespace="ns1") == "value1"
    assert cache_manager.get("key1", namespace="ns2") == "value2"

def test_cache_expiration(cache_manager):
    """Testa a expiração do cache."""
    cache_manager.set("expire_key", "expire_value")
    
    # Aguarda a expiração
    time.sleep(1.1)
    
    value = cache_manager.get("expire_key")
    assert value is None
    assert cache_manager.stats["misses"] == 1

def test_invalidate(cache_manager):
    """Testa a invalidação de itens do cache."""
    cache_manager.set("invalid_key", "invalid_value")
    assert cache_manager.get("invalid_key") == "invalid_value"
    
    cache_manager.invalidate("invalid_key")
    assert cache_manager.get("invalid_key") is None

def test_clear_namespace(cache_manager):
    """Testa a limpeza de um namespace inteiro."""
    cache_manager.set("key1", "value1", namespace="test_ns")
    cache_manager.set("key2", "value2", namespace="test_ns")
    
    cache_manager.clear_namespace("test_ns")
    
    assert cache_manager.get("key1", namespace="test_ns") is None
    assert cache_manager.get("key2", namespace="test_ns") is None

def test_get_stats(cache_manager):
    """Testa as estatísticas do cache."""
    # Realiza algumas operações
    cache_manager.set("key1", "value1")
    cache_manager.get("key1")  # Hit
    cache_manager.get("missing")  # Miss
    
    stats = cache_manager.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["total_saved"] == 1
    assert isinstance(stats["hit_ratio"], float)

def test_persistence(cache_manager, cache_dir):
    """Testa a persistência do cache em disco."""
    test_data = {"test": "data"}
    cache_manager.set("persist_key", test_data, persist=True)
    
    # Verifica se o arquivo foi criado
    cache_file = list(cache_dir.glob("**/*.json"))[0]
    assert cache_file.exists()
    
    # Verifica o conteúdo do arquivo
    with open(cache_file, "r") as f:
        stored_data = json.load(f)
        assert stored_data["value"] == test_data

def test_load_from_disk(cache_manager):
    """Testa o carregamento do cache do disco."""
    test_data = {"test": "disk_data"}
    
    # Armazena no disco
    cache_manager.set("disk_key", test_data, persist=True)
    
    # Limpa o cache em memória
    cache_manager.memory_cache.clear()
    
    # Tenta recuperar do disco
    loaded_data = cache_manager.get("disk_key")
    assert loaded_data == test_data

@pytest.mark.parametrize("test_data", [
    "string_value",
    123,
    {"key": "value"},
    ["list", "of", "items"],
    True
])
def test_different_data_types(cache_manager, test_data):
    """Testa o cache com diferentes tipos de dados."""
    cache_manager.set("type_key", test_data)
    assert cache_manager.get("type_key") == test_data

def test_error_handling(cache_manager):
    """Testa o tratamento de erros."""
    # Simula um erro ao salvar no disco
    with patch("builtins.open") as mock_open:
        mock_open.side_effect = Exception("Disk error")
        success = cache_manager.set("error_key", "error_value", persist=True)
        assert not success
        
        # O item ainda deve estar no cache em memória
        assert cache_manager.get("error_key") == "error_value"

def test_concurrent_access(cache_manager):
    """Testa o acesso concorrente ao cache."""
    import threading
    
    def cache_operation():
        for i in range(100):
            cache_manager.set(f"concurrent_key_{i}", i)
            cache_manager.get(f"concurrent_key_{i}")
    
    threads = [
        threading.Thread(target=cache_operation)
        for _ in range(3)
    ]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Verifica se não houve erros
    stats = cache_manager.get_stats()
    assert stats["total_saved"] == 300  # 3 threads * 100 operações 