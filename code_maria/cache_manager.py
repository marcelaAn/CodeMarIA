"""
Módulo de Gerenciamento de Cache da CodeMaria
Responsável por implementar o cache de requisições e dados.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
import os
from pathlib import Path
import tempfile
import time
import threading
import shutil

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CacheManager:
    """Gerenciador de cache em camadas com suporte a memória e disco."""
    
    def __init__(self, ttl: int = 3600, max_size: int = 100, cache_dir: Optional[str] = None):
        """
        Inicializa o gerenciador de cache.
        
        Args:
            ttl: Tempo de vida dos itens em segundos
            max_size: Tamanho máximo do cache
            cache_dir: Diretório para persistência do cache
            
        Raises:
            ValueError: Se ttl ou max_size forem inválidos
        """
        if ttl <= 0:
            logger.error("TTL inválido: deve ser positivo")
            raise ValueError("TTL deve ser positivo")
        if max_size <= 0:
            logger.error("Tamanho máximo inválido: deve ser positivo")
            raise ValueError("Tamanho máximo deve ser positivo")
            
        self.ttl = ttl
        self.max_size = max_size
        
        try:
            self.cache_dir = Path(cache_dir) if cache_dir else Path(tempfile.gettempdir()) / "code_maria_cache"
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório de cache configurado: {self.cache_dir}")
        except Exception as e:
            logger.error(f"Erro ao configurar diretório de cache: {str(e)}")
            raise
        
        # Cache em memória (L1) - acesso rápido
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Lock para operações thread-safe
        self._lock = threading.Lock()
        
        # Inicializa estatísticas
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
            "total_saved": 0,
            "disk_hits": 0,
            "disk_errors": 0,
            "last_cleanup": time.time()
        }
        
        # Carrega cache persistido
        try:
            self._load_from_disk()
            logger.info("Cache carregado do disco com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar cache do disco: {str(e)}")
            self.stats["disk_errors"] += 1
        
        # Configura limpeza periódica
        self._setup_cleanup()
        
        logger.info(f"Cache inicializado: TTL={ttl}s, max_size={max_size}")
    
    def _setup_cleanup(self) -> None:
        """Configura a limpeza periódica do cache."""
        def cleanup():
            while True:
                time.sleep(self.ttl / 2)  # Executa limpeza na metade do TTL
                self._cleanup_expired()
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_expired(self) -> None:
        """Remove itens expirados do cache."""
        now = time.time()
        with self._lock:
            expired_keys = [
                key for key, item in self.memory_cache.items()
                if now > item.get("expiry", 0)
            ]
            
            for key in expired_keys:
                self._remove_item(key)
                self.stats["evictions"] += 1
    
    def _remove_item(self, key: str) -> None:
        """Remove um item do cache em memória e disco."""
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                cache_file.unlink()
            except Exception as e:
                logger.error(f"Erro ao remover arquivo de cache: {str(e)}")
    
    def get(self, key: str, namespace: Optional[str] = None) -> Any:
        """
        Recupera um valor do cache.
        
        Args:
            key: Chave do item
            namespace: Namespace opcional
            
        Returns:
            Valor armazenado ou None se não encontrado/expirado
        """
        full_key = f"{namespace}:{key}" if namespace else key
        
        with self._lock:
            # Tenta recuperar da memória
            if full_key in self.memory_cache:
                item = self.memory_cache[full_key]
                if time.time() <= item.get("expiry", 0):
                    self.stats["hits"] += 1
                    return item.get("value")
                else:
                    self._remove_item(full_key)
            
            # Tenta recuperar do disco
            try:
                cache_file = self.cache_dir / f"{full_key}.json"
                if cache_file.exists():
                    with open(cache_file, "r") as f:
                        item = json.load(f)
                        if time.time() <= item.get("expiry", 0):
                            # Promove para memória
                            self.memory_cache[full_key] = item
                            self.stats["hits"] += 1
                            return item.get("value")
                        else:
                            self._remove_item(full_key)
            except Exception as e:
                logger.error(f"Erro ao ler do cache em disco: {str(e)}")
            
            self.stats["misses"] += 1
            return None
    
    def set(self, key: str, value: Any, namespace: Optional[str] = None, persist: bool = False) -> bool:
        """
        Armazena um valor no cache.
        
        Args:
            key: Chave do item
            value: Valor a armazenar
            namespace: Namespace opcional
            persist: Se deve persistir em disco
            
        Returns:
            bool: True se sucesso, False se erro
        """
        try:
            full_key = f"{namespace}:{key}" if namespace else key
            
            with self._lock:
                # Remove item mais antigo se cache cheio
                if len(self.memory_cache) >= self.max_size:
                    oldest_key = min(
                        self.memory_cache.keys(),
                        key=lambda k: self.memory_cache[k].get("expiry", 0)
                    )
                    self._remove_item(oldest_key)
                    self.stats["evictions"] += 1
                
                # Prepara o item
                item = {
                    "value": value,
                    "expiry": time.time() + self.ttl,
                    "namespace": namespace
                }
                
                # Armazena em memória
                self.memory_cache[full_key] = item
                self.stats["sets"] += 1
                self.stats["total_saved"] += 1
                
                # Persiste em disco se solicitado
                if persist:
                    try:
                        cache_file = self.cache_dir / f"{full_key}.json"
                        with open(cache_file, "w") as f:
                            json.dump(item, f)
                    except Exception as e:
                        logger.error(f"Erro ao persistir em disco: {str(e)}")
                        return False
                
                return True
                
        except Exception as e:
            logger.error(f"Erro ao salvar no cache: {str(e)}")
            return False
    
    def invalidate(self, key: str, namespace: Optional[str] = None) -> None:
        """
        Invalida um item do cache.
        
        Args:
            key: Chave do item
            namespace: Namespace opcional
        """
        full_key = f"{namespace}:{key}" if namespace else key
        with self._lock:
            self._remove_item(full_key)
    
    def clear_namespace(self, namespace: str) -> None:
        """
        Remove todos os itens de um namespace.
        
        Args:
            namespace: Namespace a limpar
        """
        with self._lock:
            # Remove da memória
            keys_to_remove = [
                key for key, item in self.memory_cache.items()
                if item.get("namespace") == namespace
            ]
            for key in keys_to_remove:
                self._remove_item(key)
            
            # Remove do disco
            try:
                for cache_file in self.cache_dir.glob(f"{namespace}:*.json"):
                    cache_file.unlink()
            except Exception as e:
                logger.error(f"Erro ao limpar namespace do disco: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache.
        
        Returns:
            Dict com estatísticas
        """
        with self._lock:
            stats = self.stats.copy()
            total_requests = stats["hits"] + stats["misses"]
            stats["hit_ratio"] = stats["hits"] / total_requests if total_requests > 0 else 0.0
            return stats
    
    def _load_from_disk(self) -> None:
        """Carrega o cache do disco."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r") as f:
                        item = json.load(f)
                        if time.time() <= item.get("expiry", 0):
                            key = cache_file.stem
                            self.memory_cache[key] = item
                        else:
                            cache_file.unlink()
                except Exception as e:
                    logger.error(f"Erro ao carregar arquivo {cache_file}: {str(e)}")
                    try:
                        cache_file.unlink()
                    except:
                        pass
        except Exception as e:
            logger.error(f"Erro ao carregar cache do disco: {str(e)}")
            self.memory_cache = {}
    
    def __del__(self):
        """Limpa recursos ao destruir o objeto."""
        try:
            # Remove arquivos temporários se usando diretório temporário
            if str(self.cache_dir).startswith(tempfile.gettempdir()):
                shutil.rmtree(self.cache_dir, ignore_errors=True)
        except:
            pass 