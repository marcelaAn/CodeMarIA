"""
Módulo de Rate Limiting da CodeMaria
Responsável por controlar a taxa de requisições às APIs externas.
"""

import logging
from typing import Dict, Any, Optional, Callable, List, Tuple, Union
from datetime import datetime, timedelta
import time
import json
from pathlib import Path
import threading
from queue import PriorityQueue, Empty
import statistics
from dataclasses import dataclass, field
from threading import Lock, Event
import yaml
from typing import TypedDict
from collections import defaultdict
from queue import Queue
import re

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RateLimitError(Exception):
    """Exceção base para erros de rate limiting."""
    pass

class ConfigurationError(RateLimitError):
    """Exceção para erros de configuração."""
    pass

class ValidationError(RateLimitError):
    """Exceção para erros de validação."""
    pass

class FileError(RateLimitError):
    """Exceção para erros de arquivo."""
    pass

class QueueFullError(RateLimitError):
    """
    Exceção lançada quando a fila de requisições está cheia.
    Indica que o sistema está sobrecarregado e não pode aceitar mais requisições no momento.
    """
    pass

class APILimit(TypedDict):
    """Tipo para definir limites de API."""
    calls: int
    period: int

class APIMetrics(TypedDict):
    """Tipo para métricas de API."""
    count: int
    window_start: float
    avg_response_time: float
    error_count: int
    success_count: int
    last_error: Optional[str]
    last_success_time: Optional[float]

@dataclass(order=True)
class QueuedRequest:
    """Representa uma requisição na fila de espera."""
    api_name: str = field(compare=False)
    timestamp: float = field(compare=False, default_factory=time.time)
    priority: float = field(default_factory=time.time)
    callback: Optional[Callable] = field(compare=False, default=None)
    timeout: Optional[float] = field(compare=False, default=None)
    start_time: float = field(compare=False, default_factory=time.time)
    completed: Event = field(compare=False, default_factory=Event)

class RateLimiter:
    """
    Implementa limitação de taxa para diferentes endpoints/operações
    """
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Inicializa o limitador de taxa.
        
        Args:
            requests_per_minute: Número máximo de requisições por minuto
        """
        self.requests_per_minute = requests_per_minute
        self.interval = 60.0 / requests_per_minute
        self.last_request = 0.0
        self.lock = Lock()
        self.queue = Queue()
        self.worker = threading.Thread(target=self._process_queue, daemon=True)
        self.worker.start()
        
    def _process_queue(self):
        """Processa a fila de requisições."""
        while True:
            try:
                # Pega próxima requisição da fila
                func, args, kwargs, callback = self.queue.get()
                
                # Espera o intervalo necessário
                with self.lock:
                    current_time = time.time()
                    wait_time = max(0, self.interval - (current_time - self.last_request))
                    time.sleep(wait_time)
                    self.last_request = time.time()
                
                # Executa a requisição
                try:
                    result = func(*args, **kwargs)
                    if callback:
                        callback(result)
                except Exception as e:
                    logger.error(f"Erro ao processar requisição: {str(e)}")
                    if callback:
                        callback(None, error=str(e))
                        
                # Marca tarefa como concluída
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Erro crítico no processador de fila: {str(e)}")
                time.sleep(1)  # Evita loop infinito em caso de erro
                
    def add_request(
        self,
        func: Callable,
        *args,
        callback: Optional[Callable] = None,
        **kwargs
    ) -> None:
        """
        Adiciona uma requisição à fila.
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            callback: Função de callback opcional
            **kwargs: Argumentos nomeados
        """
        try:
            self.queue.put((func, args, kwargs, callback))
        except Exception as e:
            logger.error(f"Erro ao adicionar requisição: {str(e)}")
            if callback:
                callback(None, error=str(e))
                
    def wait(self) -> None:
        """Aguarda todas as requisições serem processadas."""
        self.queue.join()

    def check_limit(self, api_name: str) -> bool:
        """
        Verifica se uma operação está dentro do limite de forma thread-safe.
        
        Args:
            api_name: Nome da API para verificar. Deve ser uma string não vazia contendo apenas
                     caracteres alfanuméricos, hífens ou underscores.
            
        Returns:
            bool: True se dentro do limite, False caso contrário
            
        Raises:
            ValidationError: Se o nome da API for inválido
            ConfigurationError: Se houver erro na configuração do limite
        """
        try:
            # Validação rigorosa do nome da API
            if not isinstance(api_name, str):
                raise ValidationError("Nome da API deve ser uma string")
            
            api_name = api_name.strip()
            if not api_name:
                raise ValidationError("Nome da API não pode ser vazio")
                
            # Valida formato do nome da API usando regex
            if not re.match(r'^[a-zA-Z0-9_-]+$', api_name):
                raise ValidationError(
                    "Nome da API deve conter apenas letras, números, hífens e underscores"
                )
            
            # Obtém o limite configurado
            try:
                limit = self._get_limit(api_name)
            except KeyError:
                logger.warning(f"API {api_name} não configurada, usando limite padrão")
                limit = self.limits.get("default", {"calls": 30, "period": 60})
            
            # Verifica estrutura do limite
            if not isinstance(limit, dict) or not all(k in limit for k in ("calls", "period")):
                raise ConfigurationError(f"Configuração inválida para {api_name}: {limit}")
            
            # Obtém lock específico da API
            with self.api_locks[api_name]:
                current_time = time.time()
                cutoff = current_time - limit["period"]
                
                # Remove timestamps antigos de forma eficiente
                if api_name in self.requests:
                    self.requests[api_name] = [
                        t for t in self.requests[api_name] if t > cutoff
                    ]
                    
                # Verifica o limite
                current_count = len(self.requests.get(api_name, []))
                within_limit = current_count < limit["calls"]
                
                # Atualiza métricas
                with self._global_lock:
                    if not within_limit:
                        self.stats["throttled_requests"] += 1
                        self.stats["last_throttle"] = current_time
                        self.stats["throttle_ratio"] = (
                            self.stats["throttled_requests"] / 
                            (self.stats["total_requests"] or 1)
                        )
                        
                        # Atualiza saúde da API
                        if api_name in self.stats["api_health"]:
                            self.stats["api_health"][api_name] = "degraded"
                
                return within_limit
                
        except (ValidationError, ConfigurationError):
            raise
        except Exception as e:
            logger.error(f"Erro ao verificar limite para {api_name}: {str(e)}")
            return False  # Por segurança, assume que o limite foi atingido
            
    def add_request(self, api_name: str) -> None:
        """
        Registra uma nova requisição de forma thread-safe.
        
        Args:
            api_name: Nome da API
            
        Raises:
            ValidationError: Se o nome da API for inválido
        """
        try:
            # Valida nome da API
            if not isinstance(api_name, str) or not api_name.strip():
                raise ValidationError("Nome da API não pode ser vazio")
                
            # Usa limite default se API não configurada
            if api_name not in self.limits:
                api_name = "default"
                
            current_time = time.time()
            
            # Obtém locks necessários em ordem específica para evitar deadlocks
            with self._global_lock:
                with self.api_locks[api_name]:
                    # Adiciona timestamp
                    self.requests[api_name].append(current_time)
                    
                    # Atualiza estatísticas
                    self.stats["total_requests"] += 1
                    self.stats["current_counts"][api_name] += 1
                    
                    # Atualiza métricas da API
                    metrics = self.api_metrics[api_name]["requests"]
                    metrics["count"] += 1
                    metrics["last_success_time"] = current_time
                    
                    # Calcula taxa de utilização
                    current_count = len(self.requests[api_name])
                    limit = self.limits[api_name]["calls"]
                    usage_ratio = current_count / limit
                    
                    # Atualiza status de saúde da API
                    health_status = self.stats["api_health"][api_name]
                    if usage_ratio >= 0.9:  # 90% do limite
                        health_status.update({
                            "status": "warning",
                            "last_check": current_time,
                            "usage_ratio": usage_ratio,
                            "reason": "Alto uso da API"
                        })
                    elif usage_ratio >= 0.7:  # 70% do limite
                        health_status.update({
                            "status": "notice",
                            "last_check": current_time,
                            "usage_ratio": usage_ratio,
                            "reason": "Uso moderado da API"
                        })
                    else:
                        health_status.update({
                            "status": "healthy",
                            "last_check": current_time,
                            "usage_ratio": usage_ratio
                        })
                    
                    # Log para monitoramento
                    self.logger.debug(
                        f"Requisição registrada para {api_name}. "
                        f"Total: {current_count}/{limit} "
                        f"({usage_ratio*100:.1f}%) - "
                        f"Status: {health_status['status']}"
                    )
                    
        except Exception as e:
            self.logger.error(f"Erro ao registrar requisição para {api_name}: {str(e)}")
            raise
            
    def get_wait_time(self, api_name: str) -> Optional[float]:
        """
        Calcula tempo de espera até próxima requisição permitida.
        
        Args:
            api_name: Nome da API
            
        Returns:
            Tempo em segundos ou None se não precisar esperar
        """
        try:
            # Usa limite default se API não configurada
            if api_name not in self.limits:
                api_name = "default"
                
            with self.api_locks[api_name]:
                if not self.requests[api_name]:
                    return None
                    
                current_time = time.time()
                period = self.limits[api_name]["period"]
                
                # Remove timestamps antigos
                self.requests[api_name] = [
                    ts for ts in self.requests[api_name] 
                    if current_time - ts <= period
                ]
                
                if len(self.requests[api_name]) < self.limits[api_name]["calls"]:
                    return None
                    
                # Calcula tempo até liberar uma vaga
                oldest_request = min(self.requests[api_name])
                return max(0, oldest_request + period - current_time)
                
        except Exception as e:
            self.logger.error(f"Erro ao calcular tempo de espera para {api_name}: {str(e)}")
            return None
            
    def reset(self, operation: Optional[str] = None) -> None:
        """
        Reseta contadores do rate limiter.
        
        Args:
            operation: Operação específica ou None para resetar todas
        """
        try:
            if operation:
                if operation not in self.limits:
                    raise ValueError(f"Operação não configurada: {operation}")
                self.requests[operation] = []
                logger.info(f"Contadores resetados para operação: {operation}")
            else:
                self.requests = defaultdict(list)
                logger.info("Todos os contadores foram resetados")
                
        except Exception as e:
            logger.error(f"Erro ao resetar contadores: {str(e)}")
    
    def _get_limit(self, api_name: str) -> Dict[str, int]:
        """Retorna o limite para uma API."""
        with self.api_locks[api_name]:
            return self.limits.get(api_name, self.limits["default"])
    
    def _update_counts(self, api_name: str) -> None:
        """
        Atualiza contadores de requisições.
        
        Args:
            api_name: Nome da API
        """
        with self.api_locks[api_name]:
            current_time = time.time()
            
            # Inicializa métricas se necessário
            if api_name not in self.api_metrics:
                self.api_metrics[api_name] = {
                    "requests": {
                        "count": 0,
                        "window_start": current_time,
                        "avg_response_time": 0.0,
                        "error_count": 0,
                        "success_count": 0,
                        "last_error": None,
                        "last_success_time": None
                    }
                }
            
            metrics = self.api_metrics[api_name]["requests"]
            limit = self._get_limit(api_name)
            
            # Reseta contador se a janela expirou
            if current_time - metrics["window_start"] >= limit["period"]:
                metrics["count"] = 0
                metrics["window_start"] = current_time
            
            metrics["count"] += 1
            self.stats["current_counts"][api_name] = metrics["count"]
    
    def _should_throttle(self, api_name: str) -> bool:
        """
        Verifica se deve aplicar throttling.
        
        Args:
            api_name: Nome da API
            
        Returns:
            bool indicando se deve aplicar throttling
        """
        with self.api_locks[api_name]:
            if api_name not in self.api_metrics:
                return False
            
            current_time = time.time()
            limit = self._get_limit(api_name)
            count = self.api_metrics[api_name]["requests"]["count"]
            window_start = self.api_metrics[api_name]["requests"]["window_start"]
            
            # Reset se janela expirou
            if current_time - window_start > limit["period"]:
                self.api_metrics[api_name]["requests"] = {
                    "count": 0,
                    "window_start": current_time
                }
                return False
            
            return count >= limit["calls"]
    
    def acquire(self, api_name: str, callback: Optional[Callable] = None, timeout: Optional[float] = None) -> bool:
        """
        Solicita permissão para fazer uma requisição.
        
        Args:
            api_name: Nome da API para requisitar permissão. Deve ser uma string não vazia
                     contendo apenas caracteres alfanuméricos, hífens ou underscores.
            callback: Função opcional a ser executada quando a requisição for permitida.
                     Deve ser uma função callable ou None.
            timeout: Tempo máximo de espera em segundos. Deve ser um número positivo ou None
                    para esperar indefinidamente.
            
        Returns:
            bool: True se a requisição foi enfileirada com sucesso, False caso contrário
            
        Raises:
            ValidationError: Se os parâmetros forem inválidos
            QueueFullError: Se a fila estiver cheia
        """
        try:
            # Validação rigorosa dos parâmetros
            if not isinstance(api_name, str):
                raise ValidationError("Nome da API deve ser uma string")
            
            api_name = api_name.strip()
            if not api_name:
                raise ValidationError("Nome da API não pode ser vazio")
                
            # Valida formato do nome da API usando regex
            if not re.match(r'^[a-zA-Z0-9_-]+$', api_name):
                raise ValidationError(
                    "Nome da API deve conter apenas letras, números, hífens e underscores"
                )
            
            # Valida callback
            if callback is not None and not callable(callback):
                raise ValidationError("callback deve ser uma função callable ou None")
                
            # Valida timeout
            if timeout is not None:
                if not isinstance(timeout, (int, float)):
                    raise ValidationError("timeout deve ser um número ou None")
                if timeout <= 0:
                    raise ValidationError("timeout deve ser um valor positivo")
            
            # Usa limite default se API não configurada
            if api_name not in self.limits:
                logger.warning(f"API {api_name} não configurada, usando limite padrão")
                api_name = "default"
            
            # Verifica saúde do sistema
            with self._global_lock:
                health = self.stats["api_health"][api_name]
                if health.get("status") == "error":
                    logger.warning(
                        f"API {api_name} em estado crítico: {health.get('reason', 'Desconhecido')}"
                    )
            
            # Cria requisição com prioridade
            current_time = time.time()
            request = QueuedRequest(
                api_name=api_name,
                timestamp=current_time,
                priority=current_time,
                callback=callback,
                timeout=timeout
            )
            
            # Tenta enfileirar com timeout curto para evitar bloqueio
            try:
                self.request_queue.put(request, timeout=0.1)  # 100ms timeout
            except queue.Full:
                # Atualiza métricas em caso de fila cheia
                with self._global_lock:
                    self.stats["api_health"][api_name].update({
                        "status": "error",
                        "last_check": current_time,
                        "reason": "Fila de requisições cheia"
                    })
                    logger.error(f"Fila cheia para {api_name}, requisição rejeitada")
                raise QueueFullError(f"Fila de requisições cheia para {api_name}")
            
            # Atualiza estatísticas
            with self._global_lock:
                self.stats["queued_requests"] += 1
                self.stats["current_counts"][api_name] = (
                    self.stats["current_counts"].get(api_name, 0) + 1
                )
                
                # Atualiza métricas da API
                if api_name not in self.api_metrics:
                    self.api_metrics[api_name] = {
                        "requests": {
                            "count": 0,
                            "window_start": current_time,
                            "avg_response_time": 0.0,
                            "error_count": 0,
                            "success_count": 0,
                            "last_error": None,
                            "last_success_time": None
                        }
                    }
                
                metrics = self.api_metrics[api_name]["requests"]
                metrics["count"] += 1
            
            logger.debug(
                f"Requisição enfileirada para {api_name} "
                f"(timeout={timeout}, prioridade={request.priority:.2f})"
            )
            return True
            
        except (ValidationError, QueueFullError):
            raise
        except Exception as e:
            logger.error(f"Erro ao adquirir permissão para {api_name}: {str(e)}")
            return False
            
    def release(self, api_name: str) -> None:
        """
        Libera uma requisição da contagem.
        
        Args:
            api_name: Nome da API
        """
        try:
            with self.api_locks[api_name]:
                if api_name in self.requests and self.requests[api_name]:
                    self.requests[api_name].pop(0)
                    
        except Exception as e:
            self.logger.error(f"Erro ao liberar requisição para {api_name}: {str(e)}")
            
    def _update_success_metrics(self, api_name: str, process_time: float) -> None:
        """Atualiza métricas para uma requisição bem sucedida."""
        metrics = self.api_metrics[api_name]["requests"]
        metrics["success_count"] += 1
        metrics["last_success_time"] = time.time()
        
        # Atualiza contador de requisições bem sucedidas
        with self._global_lock:
            self.stats["successful_requests"] += 1
        
        # Atualiza tempo médio de resposta
        if metrics["avg_response_time"] == 0:
            metrics["avg_response_time"] = process_time
        else:
            metrics["avg_response_time"] = (
                0.9 * metrics["avg_response_time"] + 
                0.1 * process_time
            )
        
        # Atualiza saúde da API
        self.stats["api_health"][api_name].update({
            "status": "healthy",
            "last_check": time.time(),
            "avg_response_time": metrics["avg_response_time"]
        })
    
    def _update_error_metrics(self, api_name: str, error_msg: str, process_time: float) -> None:
        """Atualiza métricas para uma requisição com erro."""
        metrics = self.api_metrics[api_name]["requests"]
        metrics["error_count"] += 1
        metrics["last_error"] = error_msg
        
        # Atualiza tempo médio de resposta
        if metrics["avg_response_time"] == 0:
            metrics["avg_response_time"] = process_time
        else:
            metrics["avg_response_time"] = (
                0.9 * metrics["avg_response_time"] + 
                0.1 * process_time
            )
        
        # Atualiza saúde da API
        error_count = metrics["error_count"]
        total_requests = metrics["success_count"] + error_count
        error_rate = error_count / max(1, total_requests)
        
        status = "warning" if error_rate < 0.5 else "error"
        self.stats["api_health"][api_name].update({
            "status": status,
            "last_check": time.time(),
            "error_rate": error_rate,
            "last_error": error_msg,
            "avg_response_time": metrics["avg_response_time"]
        })
    
    def _timeout_callback(self, request: QueuedRequest) -> None:
        """Função chamada quando um callback atinge o timeout."""
        logger.warning(
            f"Callback para {request.api_name} interrompido por timeout "
            f"após {time.time() - request.start_time:.2f}s"
        )
        with self._global_lock:
            self._update_error_metrics(
                request.api_name,
                "Timeout no callback",
                time.time() - request.start_time
            )

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do rate limiter.
        
        Returns:
            Dicionário com estatísticas
        """
        with self._global_lock:
            stats = {
                "total_requests": self.stats["total_requests"],
                "throttled_requests": self.stats["throttled_requests"],
                "current_counts": dict(self.stats["current_counts"]),
                "api_metrics": {}
            }
            
            for api_name in self.limits:
                stats["api_metrics"][api_name] = {
                    "requests": self.api_metrics[api_name]["requests"]["count"],
                    "success_rate": (
                        self.api_metrics[api_name]["requests"]["success_count"] /
                        max(1, self.api_metrics[api_name]["requests"]["count"])
                    ),
                    "avg_response_time": self.api_metrics[api_name]["requests"]["avg_response_time"]
                }
                
            return stats
    
    def update_limits(self, api_name: str, calls: int, period: int) -> bool:
        """
        Atualiza limites para uma API.
        
        Args:
            api_name: Nome da API
            calls: Número máximo de chamadas
            period: Período em segundos
            
        Returns:
            bool indicando sucesso
            
        Raises:
            ValidationError: Se os parâmetros forem inválidos
        """
        if not isinstance(api_name, str) or not api_name.strip():
            raise ValidationError("Nome da API inválido")
        
        try:
            self._validate_and_set_limit(api_name, {"calls": calls, "period": period})
            
            # Se tiver arquivo de configuração, persiste as alterações
            if self.config_file:
                config_path = Path(self.config_file)
                
                try:
                    # Carrega configuração existente
                    if config_path.exists():
                        with open(config_path, 'r') as f:
                            try:
                                current_config = json.load(f)
                            except json.JSONDecodeError:
                                current_config = yaml.safe_load(f)
                    else:
                        current_config = {}
                    
                    # Atualiza configuração
                    current_config[api_name] = {"calls": calls, "period": period}
                    
                    # Salva no mesmo formato que estava
                    with open(config_path, 'w') as f:
                        if config_path.suffix == '.yaml':
                            yaml.dump(current_config, f, default_flow_style=False)
                        else:
                            json.dump(current_config, f, indent=4)
                            
                except Exception as e:
                    logger.error(f"Erro ao persistir configuração: {e}")
                    return False
                    
            return True
            
        except ValidationError as e:
            logger.error(f"Erro de validação ao atualizar limites: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar limites: {e}")
            return False
    
    def reset_counts(self, api_name: Optional[str] = None) -> bool:
        """
        Reseta contadores de requisições.
        
        Args:
            api_name: Nome da API ou None para resetar todos
            
        Returns:
            bool indicando sucesso
        """
        try:
            with self._global_lock:
                if api_name:
                    if api_name in self.api_metrics:
                        del self.api_metrics[api_name]
                else:
                    self.api_metrics.clear()
                
                with self._global_lock:
                    if not api_name:
                        self.stats["total_requests"] = 0
                        self.stats["throttled_requests"] = 0
                        self.stats["current_counts"].clear()
                    else:
                        self.stats["current_counts"].pop(api_name, None)
                
                return True
                
        except Exception as e:
            logger.error(f"Erro ao resetar contadores: {e}")
            return False
    
    def __del__(self):
        """Garante limpeza adequada ao destruir objeto."""
        self._running = False
        if hasattr(self, '_queue_processor'):
            self._queue_processor.join(timeout=1.0)

    def _update_metrics(self, api_name: str, success: bool, response_time: float, error_msg: Optional[str] = None) -> None:
        """
        Atualiza métricas para uma API específica.
        
        Args:
            api_name: Nome da API
            success: Se a requisição foi bem sucedida
            response_time: Tempo de resposta em segundos
            error_msg: Mensagem de erro, se houver
        """
        with self.api_locks[api_name]:
            if api_name not in self.api_metrics:
                self.api_metrics[api_name] = {
                    "requests": {
                        "count": 0,
                        "window_start": time.time(),
                        "avg_response_time": 0.0,
                        "error_count": 0,
                        "success_count": 0,
                        "last_error": None,
                        "last_success_time": None
                    }
                }
            
            metrics = self.api_metrics[api_name]["requests"]
            
            # Atualiza tempo médio de resposta
            current_avg = metrics["avg_response_time"]
            total_requests = metrics["error_count"] + metrics["success_count"]
            if total_requests > 0:
                metrics["avg_response_time"] = (current_avg * total_requests + response_time) / (total_requests + 1)
            else:
                metrics["avg_response_time"] = response_time
            
            # Atualiza contadores de sucesso/erro
            if success:
                metrics["success_count"] += 1
                metrics["last_success_time"] = time.time()
            else:
                metrics["error_count"] += 1
                metrics["last_error"] = error_msg
            
            # Atualiza métricas de saúde da API
            error_rate = metrics["error_count"] / (total_requests + 1) if total_requests > 0 else 0
            self.stats["current_counts"][api_name] = metrics["count"]

    def get_detailed_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas detalhadas do rate limiter incluindo métricas por API,
        tempos de resposta, saúde do sistema e informações da fila.
        
        Returns:
            Dict com estatísticas detalhadas
        """
        with self._global_lock:
            try:
                current_time = time.time()
                
                # Calcula estatísticas da fila
                queue_stats = {
                    "current_size": self.request_queue.qsize(),
                    "wait_times": {
                        "current": statistics.mean(self.stats["queue_wait_times"]) if self.stats["queue_wait_times"] else 0,
                        "min": min(self.stats["queue_wait_times"]) if self.stats["queue_wait_times"] else 0,
                        "max": max(self.stats["queue_wait_times"]) if self.stats["queue_wait_times"] else 0,
                        "avg": statistics.mean(self.stats["queue_wait_times"]) if self.stats["queue_wait_times"] else 0,
                        "median": statistics.median(self.stats["queue_wait_times"]) if self.stats["queue_wait_times"] else 0
                    } if self.stats["queue_wait_times"] else {},
                    "total_queued": self.stats["queued_requests"]
                }
                
                # Estatísticas por API
                api_stats = {}
                for api_name in self.limits.keys():
                    metrics = self.api_metrics[api_name]["requests"]
                    current_count = len([ts for ts in self.requests[api_name] 
                                      if current_time - ts <= self.limits[api_name]["period"]])
                    
                    api_stats[api_name] = {
                        "current_usage": {
                            "count": current_count,
                            "limit": self.limits[api_name]["calls"],
                            "period": self.limits[api_name]["period"],
                            "usage_ratio": current_count / self.limits[api_name]["calls"]
                        },
                        "metrics": {
                            "total_requests": metrics["count"],
                            "success_count": metrics["success_count"],
                            "error_count": metrics["error_count"],
                            "success_rate": (metrics["success_count"] / max(1, metrics["count"])) * 100,
                            "avg_response_time": metrics["avg_response_time"],
                            "last_error": metrics["last_error"],
                            "last_success": metrics["last_success_time"]
                        },
                        "health": self.stats["api_health"][api_name]
                    }
                
                # Estatísticas globais
                global_stats = {
                    "total_requests": self.stats["total_requests"],
                    "throttled_requests": self.stats["throttled_requests"],
                    "throttle_ratio": (
                        self.stats["throttled_requests"] / max(1, self.stats["total_requests"])
                    ) * 100,
                    "last_throttle": self.stats["last_throttle"],
                    "uptime": current_time - self.api_metrics["default"]["requests"]["window_start"]
                }
                
                # Status geral do sistema
                system_health = "healthy"
                health_reasons = []
                
                # Verifica saúde baseado em métricas
                if global_stats["throttle_ratio"] > 20:  # Mais de 20% throttled
                    system_health = "warning"
                    health_reasons.append("Alta taxa de throttling")
                
                if queue_stats["current_size"] > 100:  # Fila muito grande
                    system_health = "warning"
                    health_reasons.append("Fila de requisições grande")
                
                # Verifica APIs com problemas
                problem_apis = [
                    api for api, stats in api_stats.items()
                    if stats["health"]["status"] in ("warning", "error")
                ]
                if problem_apis:
                    system_health = "warning"
                    health_reasons.append(f"APIs com problemas: {', '.join(problem_apis)}")
                
                return {
                    "timestamp": current_time,
                    "system_status": {
                        "health": system_health,
                        "reasons": health_reasons
                    },
                    "global_stats": global_stats,
                    "queue_stats": queue_stats,
                    "api_stats": api_stats
                }
                
            except Exception as e:
                logger.error(f"Erro ao gerar estatísticas detalhadas: {str(e)}")
                return {
                    "error": str(e),
                    "timestamp": current_time
                }

    def _validate_and_update_limits(self, limits: Dict[str, Dict[str, int]]) -> None:
        """
        Valida e atualiza os limites de API de forma thread-safe.
        
        Args:
            limits: Dicionário com limites por API
            
        Raises:
            ConfigurationError: Se a configuração for inválida
            ValidationError: Se os valores forem inválidos
        """
        if not isinstance(limits, dict):
            raise ConfigurationError("limits deve ser um dicionário")
            
        with self._global_lock:
            try:
                validated_limits = {}
                
                for api_name, config in limits.items():
                    # Valida nome da API
                    if not isinstance(api_name, str) or not api_name.strip():
                        raise ValidationError(f"Nome da API inválido: {api_name}")
                        
                    if not re.match(r"^[a-zA-Z0-9_-]+$", api_name):
                        raise ValidationError(f"Nome de API contém caracteres inválidos: {api_name}")
                        
                    # Valida configuração
                    if not isinstance(config, dict):
                        raise ConfigurationError(f"Configuração inválida para {api_name}")
                        
                    # Compatibilidade com configuração antiga (calls/period)
                    calls = config.get("calls", config.get("requests"))
                    period = config.get("period", config.get("window", self.default_window))
                    
                    # Validação rigorosa dos valores
                    if not isinstance(calls, int):
                        raise ValidationError(f"calls deve ser um inteiro para {api_name}")
                    if calls <= 0:
                        raise ValidationError(f"calls deve ser positivo para {api_name}")
                        
                    if not isinstance(period, int):
                        raise ValidationError(f"period deve ser um inteiro para {api_name}")
                    if period <= 0:
                        raise ValidationError(f"period deve ser positivo para {api_name}")
                    
                    # Adiciona configuração validada
                    validated_limits[api_name] = {
                        "calls": calls,
                        "period": period
                    }
                
                # Atualiza limites apenas se todas as validações passarem
                for api_name, config in validated_limits.items():
                    self.limits[api_name] = config
                    
                    # Inicializa ou reseta métricas se necessário
                    if api_name not in self.api_metrics:
                        self.api_metrics[api_name] = {
                            "requests": {
                                "count": 0,
                                "window_start": time.time(),
                                "avg_response_time": 0.0,
                                "error_count": 0,
                                "success_count": 0,
                                "last_error": None,
                                "last_success_time": None
                            }
                        }
                    
                    # Limpa requisições antigas
                    current_time = time.time()
                    self.requests[api_name] = [
                        ts for ts in self.requests[api_name]
                        if current_time - ts <= config["period"]
                    ]
                    
                    # Atualiza status de saúde
                    self.stats["api_health"][api_name].update({
                        "status": "healthy",
                        "last_check": current_time,
                        "reason": "Limites atualizados"
                    })
                    
                self.logger.info(f"Limites atualizados com sucesso: {validated_limits}")
                
            except Exception as e:
                self.logger.error(f"Erro ao atualizar limites: {str(e)}")
                raise 