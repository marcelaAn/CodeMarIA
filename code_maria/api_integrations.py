"""
Módulo de Integrações da CodeMaria
Responsável por gerenciar as integrações com APIs externas e extração de conteúdo web.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from urllib.parse import urlparse
from .cache_manager import CacheManager
from .rate_limiter import RateLimiter, ValidationError as RateLimitValidationError
from fastapi import HTTPException
import time

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Exceção base para erros de API."""
    def __init__(self, message: str, status_code: Optional[int] = None, api_name: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.api_name = api_name

class ValidationError(Exception):
    """Exceção para erros de validação de parâmetros."""
    def __init__(self, message: str, param_name: Optional[str] = None):
        super().__init__(message)
        self.param_name = param_name

class ConfigurationError(Exception):
    """Exceção para erros de configuração."""
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message)
        self.config_key = config_key

class APIIntegrations:
    """Gerenciador de integrações com APIs externas."""
    
    def __init__(self):
        """Inicializa o gerenciador de APIs."""
        self.logger = logging.getLogger(__name__)
        try:
            # Carrega variáveis de ambiente
            if not os.path.exists('.env'):
                logger.warning("Arquivo .env não encontrado. Usando valores padrão.")
            load_dotenv()

            self.api_keys = self._load_api_keys()
            if not isinstance(self.api_keys, dict):
                raise ConfigurationError("api_keys deve ser um dicionário", "api_keys")

            self.base_urls = {
                "news": "https://newsapi.org/v2",
                "google_search": "https://www.googleapis.com/customsearch/v1",
                "openai": "https://api.openai.com/v1",
                "scholar": "https://serpapi.com/search"
            }
            
            # Inicializa cache com validação do TTL
            try:
                cache_ttl = int(os.getenv("CACHE_EXPIRY", "3600"))
                if cache_ttl <= 0:
                    logger.warning("CACHE_EXPIRY inválido. Usando valor padrão de 3600 segundos.")
                    cache_ttl = 3600
            except ValueError:
                logger.warning("CACHE_EXPIRY inválido. Usando valor padrão de 3600 segundos.")
                cache_ttl = 3600
            
            self.cache = CacheManager(ttl=cache_ttl)
            
            # Configura limites de requisições
            rate_limits = {
                "default": {
                    "requests": 30,
                    "window": 60
                },
                "google_search": {
                    "requests": 100,
                    "window": 60
                },
                "news_api": {
                    "requests": 500,
                    "window": 3600
                },
                "openai": {
                    "requests": 3000,
                    "window": 60
                },
                "scholar": {
                    "requests": 100,
                    "window": 60
                },
                "web_extract": {
                    "requests": 60,
                    "window": 60
                }
            }
            
            # Inicializa rate limiter
            self.rate_limiter = RateLimiter(limits=rate_limits)
            self.request_history = []
            self.metrics = {}
            
            logger.info("Gerenciador de APIs inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro na inicialização do gerenciador de APIs: {str(e)}")
            raise
    
    def _check_rate_limit(self, api_name: str) -> bool:
        """
        Verifica se o rate limit foi excedido para uma determinada API.
        
        Args:
            api_name: Nome da API
            
        Returns:
            bool: True se dentro do limite, False se excedido
        """
        if not isinstance(api_name, str) or not api_name.strip():
            self.logger.error("Nome da API inválido")
            return False

        if not hasattr(self, 'rate_limiter'):
            self.logger.error("Rate limiter não inicializado")
            return True  # Se não há rate limiter, permite a requisição

        try:
            # Verifica se a API tem limite configurado
            if api_name not in self.rate_limiter.limits:
                self.logger.warning(f"API {api_name} não tem limite configurado")
                return True

            # Verifica se os métodos necessários existem e são chamáveis
            required_methods = ["is_rate_limited", "get_wait_time", "add_request"]
            for method in required_methods:
                if not hasattr(self.rate_limiter, method) or not callable(getattr(self.rate_limiter, method)):
                    self.logger.error(f"Método {method} não encontrado ou não é chamável no rate_limiter")
                    return True  # Se método não existe, permite a requisição por segurança

            # Verifica o rate limit
            if self.rate_limiter.is_rate_limited(api_name):
                wait_time = self.rate_limiter.get_wait_time(api_name)
                self.logger.warning(f"Rate limit atingido para {api_name}. Aguardando {wait_time:.2f} segundos.")
                return False

            # Registra a requisição no rate limiter
            self.rate_limiter.add_request(api_name)
            return True

        except AttributeError as e:
            self.logger.error(f"Método não encontrado no rate_limiter: {str(e)}")
            return True  # Se ocorrer erro, permite a requisição por segurança
        except Exception as e:
            self.logger.error(f"Erro ao verificar rate limit para {api_name}: {str(e)}")
            return True  # Se ocorrer erro, permite a requisição por segurança
    
    def _load_api_keys(self) -> Dict[str, str]:
        """
        Carrega e valida as chaves de API do arquivo .env
        
        Returns:
            Dict com as chaves de API
        """
        required_keys = {
            "OPENAI_API_KEY": "openai",
            "GOOGLE_API_KEY": "google",
            "GOOGLE_CX": "google_cx",  # Adicionado
            "NEWS_API_KEY": "news_api",
            "SERPAPI_KEY": "scholar"
        }
        api_keys = {}
        
        for env_key, api_name in required_keys.items():
            value = os.getenv(env_key)
            if not value:
                logger.warning(f"Chave de API não encontrada: {env_key}")
            api_keys[api_name] = value
            
            # Adiciona aliases para manter compatibilidade com os testes
            if api_name == "google":
                api_keys["google_search"] = value
            elif api_name == "news_api":
                api_keys["news"] = value
        
        return api_keys
    
    def _log_request(self, api_name: str, method: str, status_code: int) -> None:
        """
        Registra uma requisição no histórico.
        
        Args:
            api_name: Nome da API
            method: Método HTTP
            status_code: Código de status da resposta
        """
        timestamp = datetime.now().isoformat()
        request_info = {
            "api": api_name,
            "method": method,
            "status_code": status_code,
            "timestamp": timestamp
        }
        self.request_history.append(request_info)
    
    def get_request_history(self) -> List[Dict[str, Any]]:
        """Retorna o histórico de requisições."""
        return self.request_history
    
    def get_api_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna o status detalhado de todas as APIs.
        
        Returns:
            Dict com status de cada API
        """
        status = {}
        rate_stats = self.rate_limiter.get_stats()
        
        # Adiciona status para todas as APIs configuradas
        for api_name in self.rate_limiter.limits.keys():
            api_stats = {
                "has_key": bool(self.api_keys.get(api_name)),
                "total_requests": rate_stats["total_requests"],
                "throttled_requests": rate_stats["throttled_requests"],
                "last_throttle": rate_stats["last_throttle"],
                "current_usage": rate_stats["current_counts"].get(api_name, 0),
                "throttle_ratio": rate_stats["throttle_ratio"],
                "last_request": datetime.now().isoformat()
            }
            
            # Converte o nome da API para o formato usado nos testes
            if api_name == "google_search":
                api_name = "google"
            elif api_name == "news_api":
                api_name = "news"
            
            status[api_name] = api_stats
        
        # Adiciona aliases para manter compatibilidade com os testes
        status["google_search"] = status.get("google", {})
        status["news_api"] = status.get("news", {})
        
        return status
    
    # Alias para manter compatibilidade com os testes
    check_api_status = get_api_status
    
    def google_search(
        self,
        query: str,
        search_type: str = "web",
        language: str = "en",
        num_results: int = 10,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Realiza uma busca no Google.
        
        Args:
            query: Termo de busca
            search_type: Tipo de busca (web, image, news)
            language: Código do idioma
            num_results: Número de resultados
            use_cache: Se deve usar cache
            
        Returns:
            Resultados da busca
            
        Raises:
            ValidationError: Se os parâmetros forem inválidos
            APIError: Se houver erro na API
        """
        try:
            # Valida parâmetros
            if not query or not query.strip():
                raise ValidationError("Query não pode ser vazia", "query")
                
            if search_type not in ["web", "image", "news"]:
                raise ValidationError("Tipo de busca inválido", "search_type")
                
            if not isinstance(num_results, int) or num_results < 1:
                raise ValidationError("Número de resultados deve ser um inteiro positivo", "num_results")
            
            # Verifica cache
            cache_key = f"google_search:{query}:{search_type}:{language}:{num_results}"
            if use_cache:
                cached = self.cache.get(cache_key)
                if cached:
                    return cached
            
            # Verifica rate limit
            if not self._check_rate_limit("google_search"):
                raise APIError("Rate limit excedido para Google Search", 429, "google_search")
            
            # Prepara parâmetros
            params = {
                "q": query,
                "key": self.api_keys["google_search"],
                "cx": self.api_keys["google_cx"],
                "num": num_results,
                "lr": f"lang_{language}",
                "safe": "active"
            }
            
            # Adiciona parâmetros específicos por tipo
            if search_type == "image":
                params["searchType"] = "image"
            elif search_type == "news":
                params["sort"] = "date"
            
            # Faz requisição
            start_time = time.time()
            response = requests.get(
                self.base_urls["google_search"],
                params=params,
                timeout=int(os.getenv("API_TIMEOUT", "30"))
            )
            response_time = time.time() - start_time
            
            # Processa resposta
            if response.status_code == 200:
                data = response.json()
                result = self._process_google_result(data, query)
                
                # Atualiza métricas
                self._update_metrics(
                    "google_search",
                    True,
                    response_time
                )
                
                # Salva no cache
                if use_cache:
                    self.cache.set(cache_key, result)
                
                return result
            else:
                error_msg = f"Erro na API do Google: {response.status_code}"
                self._update_metrics(
                    "google_search",
                    False,
                    response_time,
                    error_msg
                )
                raise APIError(error_msg, response.status_code, "google_search")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição: {str(e)}"
            self._update_metrics(
                "google_search",
                False,
                time.time() - start_time,
                error_msg
            )
            raise APIError(error_msg, 500, "google_search")
            
        except Exception as e:
            logger.error(f"Erro na busca do Google: {str(e)}")
            raise
    
    def search_scientific_articles(
        self,
        query: str,
        max_results: int = 10,
        sort_by: str = "relevance",
        use_cache: bool = True
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Busca artigos científicos usando a API do Google Scholar."""
        try:
            # Validação dos parâmetros
            valid_sort = ["relevance", "date"]
            if sort_by not in valid_sort:
                return {"error": f"Critério de ordenação inválido. Use um dos seguintes: {valid_sort}"}
            
            if not isinstance(max_results, int) or max_results <= 0:
                return {"error": "max_results deve ser um número inteiro positivo"}
            
            if not query or not isinstance(query, str):
                return {"error": "Query inválida"}

            # Verifica o rate limit
            if not self._check_rate_limit("scholar"):
                wait_time = getattr(self.rate_limiter, "get_wait_time", lambda x: 60)("scholar")
                return {
                    "error": "Rate limit excedido para scholar",
                    "retry_after": wait_time
                }

            # Gera a chave do cache
            cache_key = f"scholar:{query}:{max_results}:{sort_by}"
            
            # Tenta recuperar do cache
            if use_cache:
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    return cached_result

            # Verifica se a chave da API existe
            api_key = self.api_keys.get("serpapi")
            if not api_key:
                return {"error": "Chave da API SerpAPI não configurada"}

            # Prepara os parâmetros da requisição
            params = {
                "engine": "google_scholar",
                "q": query,
                "api_key": api_key,
                "num": max_results,
                "sort": sort_by
            }

            # Faz a requisição HTTP
            try:
                response = requests.get(
                    "https://serpapi.com/search",
                    params=params,
                    timeout=30
                )
            except requests.exceptions.Timeout:
                return {"error": "Timeout na requisição ao Google Scholar"}
            except requests.exceptions.RequestException as e:
                return {"error": f"Erro na requisição: {str(e)}"}

            # Registra a requisição
            self._log_request("scholar", "GET", response.status_code)

            # Processa a resposta
            if response.status_code == 200:
                try:
                    data = response.json()
                    results = []
                    
                    for article in data.get("organic_results", []):
                        result = {
                            "title": article.get("title", ""),
                            "authors": article.get("authors", []),
                            "journal": article.get("publication_info", {}).get("summary", ""),
                            "abstract": article.get("snippet", ""),
                            "citations": article.get("cited_by", {}).get("total", 0),
                            "link": article.get("link", ""),
                            "year": article.get("year", "")
                        }
                        results.append(result)

                    # Armazena no cache se necessário
                    if use_cache:
                        self.cache.set(cache_key, results)

                    return results
                except json.JSONDecodeError:
                    return {"error": "Erro ao decodificar resposta do Google Scholar"}
            else:
                return {
                    "error": f"Erro na requisição: {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            self.logger.error(f"Erro ao buscar artigos científicos: {str(e)}")
            return {
                "error": "Erro ao buscar artigos",
                "details": str(e)
            }
    
    def extract_webpage_content(
        self,
        url: str,
        extract_images: bool = False,
        extract_links: bool = False,
        use_cache: bool = True
    ) -> dict:
        """
        Extrai conteúdo de uma página web.
        
        Args:
            url: URL da página
            extract_images: Se deve extrair imagens
            extract_links: Se deve extrair links
            use_cache: Se deve usar cache
            
        Returns:
            Conteúdo extraído da página
            
        Raises:
            ValueError: Se a URL for inválida
            HTTPError: Se houver erro na requisição
        """
        try:
            # Valida URL
            if not url or not url.startswith(("http://", "https://")):
                raise ValidationError("URL inválida", "url")
            
            # Verifica cache
            cache_key = f"webpage:{url}"
            if use_cache:
                cached = self.cache.get(cache_key)
                if cached:
                    logger.info(f"Conteúdo recuperado do cache: {url}")
                    return cached
            
            # Verifica rate limit
            if not self._check_rate_limit("web_extract"):
                raise HTTPException(status_code=429, detail="Rate limit excedido")
            
            # Faz requisição
            start_time = time.time()
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Processa resposta
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content = {
                "url": url,
                "title": self._extract_title(soup),
                "meta_description": self._extract_meta_description(soup),
                "text_content": self._extract_text_content(soup)
            }
            
            if extract_images:
                content["images"] = self._extract_images(soup)
            
            if extract_links:
                content["links"] = self._extract_links(soup)
            
            # Atualiza métricas
            process_time = time.time() - start_time
            self._update_metrics("web_extract", True, process_time)
            
            # Salva no cache
            if use_cache:
                self.cache.set(cache_key, content, persist=True)
            
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição HTTP: {str(e)}")
            self._update_metrics("web_extract", False, 0.0, str(e))
            raise HTTPException(status_code=e.response.status_code if hasattr(e, 'response') else 500, detail=str(e))
            
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo web: {str(e)}")
            self._update_metrics("web_extract", False, 0.0, str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extrai o título da página.
        
        Args:
            soup: Objeto BeautifulSoup com o HTML da página
            
        Returns:
            Título da página ou string vazia se não encontrado
        """
        try:
            # Tenta extrair do meta title primeiro
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            else:
                # Tenta extrair do h1
                h1 = soup.find('h1')
                title = h1.get_text().strip() if h1 else ""
                
                # Se não encontrou, tenta meta og:title
                if not title:
                    og_title = soup.find("meta", property="og:title")
                    title = og_title.get("content", "").strip() if og_title else ""
            
            # Limita o tamanho e remove caracteres inválidos
            title = "".join(char for char in title if char.isprintable())
            return title[:200] if title else ""  # Limita a 200 caracteres
            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair título: {str(e)}")
            return ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """
        Extrai a meta descrição da página.
        
        Args:
            soup: Objeto BeautifulSoup com o HTML da página
            
        Returns:
            Meta descrição da página ou string vazia se não encontrada
        """
        try:
            # Tenta diferentes meta tags
            meta_tags = [
                ("name", "description"),
                ("property", "og:description"),
                ("name", "twitter:description")
            ]
            
            for attr, value in meta_tags:
                meta = soup.find("meta", {attr: value})
                if meta and meta.get("content"):
                    description = meta.get("content", "").strip()
                    description = "".join(char for char in description if char.isprintable())
                    return description[:500]  # Limita a 500 caracteres
            
            return ""
            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair meta descrição: {str(e)}")
            return ""
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """
        Extrai o conteúdo principal da página.
        
        Args:
            soup: Objeto BeautifulSoup com o HTML da página
            
        Returns:
            Conteúdo textual da página
        """
        try:
            # Remove tags indesejadas
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'form']):
                tag.decompose()
            
            # Lista de seletores para conteúdo principal em ordem de prioridade
            main_selectors = [
                'main',
                'article',
                'div[role="main"]',
                'div.content',
                'div.main',
                'div#content',
                'div#main'
            ]
            
            # Tenta encontrar o conteúdo principal
            for selector in main_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    text = main_content.get_text(separator='\n').strip()
                    if len(text) > 100:  # Considera válido se tiver mais de 100 caracteres
                        return self._clean_text(text)
            
            # Se não encontrou, usa todo o body
            body = soup.find('body')
            if body:
                return self._clean_text(body.get_text(separator='\n').strip())
            
            return ""
            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair conteúdo: {str(e)}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """
        Limpa e formata o texto extraído.
        
        Args:
            text: Texto a ser limpo
            
        Returns:
            Texto limpo e formatado
        """
        try:
            # Remove caracteres não imprimíveis
            text = "".join(char for char in text if char.isprintable() or char in ['\n', '\t'])
            
            # Remove linhas vazias múltiplas
            lines = [line.strip() for line in text.splitlines()]
            lines = [line for line in lines if line]
            
            # Limita o tamanho total
            text = '\n'.join(lines)
            return text[:100000]  # Limita a 100K caracteres
            
        except Exception as e:
            self.logger.warning(f"Erro ao limpar texto: {str(e)}")
            return text[:100000]  # Retorna o texto original limitado em caso de erro
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extrai links relevantes da página."""
        links = []
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if href.startswith(('http', 'https')):
                links.append({
                    "text": a.get_text().strip(),
                    "url": href,
                    "title": a.get('title', '')
                })
        return links
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extrai imagens da página."""
        images = []
        for img in soup.find_all('img', src=True):
            images.append({
                "src": img.get('src'),
                "alt": img.get('alt', ''),
                "title": img.get('title', '')
            })
        return images

    def _process_google_result(self, data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Processa o resultado da busca do Google.
        
        Args:
            data: Dados retornados pela API
            query: Query original da busca
            
        Returns:
            Resultado processado
            
        Raises:
            ValueError: Se os dados estiverem incompletos
        """
        try:
            if not isinstance(data, dict):
                raise ValueError("Dados inválidos: deve ser um dicionário")
            
            # Valida campos obrigatórios
            required_fields = ["searchInformation", "items"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing_fields)}")
            
            # Extrai informações
            search_info = data.get("searchInformation", {})
            total_results = search_info.get("totalResults")
            search_time = search_info.get("searchTime")
            
            # Valida números
            try:
                total_results = int(total_results) if total_results else 0
                search_time = float(search_time) if search_time else 0.0
            except (ValueError, TypeError) as e:
                logger.error(f"Erro ao converter valores numéricos: {str(e)}")
                total_results = 0
                search_time = 0.0
            
            # Processa itens
            items = []
            for item in data.get("items", []):
                try:
                    processed_item = {
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "type": item.get("type", "web")
                    }
                    items.append(processed_item)
                except Exception as e:
                    logger.error(f"Erro ao processar item: {str(e)}")
                    continue
            
            result = {
                "query": query,
                "total_results": total_results,
                "time_taken": search_time,
                "items": items
            }
            
            # Atualiza métricas
            self._update_metrics("google_search", True, search_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao processar resultado do Google: {str(e)}")
            self._update_metrics("google_search", False, 0.0, str(e))
            return {
                "query": query,
                "total_results": 0,
                "time_taken": 0.0,
                "items": [],
                "error": str(e)
            }

    def _update_metrics(self, api_name: str, success: bool, response_time: float, error_msg: Optional[str] = None) -> None:
        """
        Atualiza métricas para uma API.
        
        Args:
            api_name: Nome da API
            success: Se a requisição foi bem sucedida
            response_time: Tempo de resposta em segundos
            error_msg: Mensagem de erro opcional
        """
        try:
            if not hasattr(self, 'metrics'):
                self.metrics = {}
                
            if api_name not in self.metrics:
                self.metrics[api_name] = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "avg_response_time": 0.0,
                    "last_error": None,
                    "last_success": None
                }
            
            metrics = self.metrics[api_name]
            metrics["total_requests"] += 1
            
            if success:
                metrics["successful_requests"] += 1
                metrics["last_success"] = time.time()
            else:
                metrics["failed_requests"] += 1
                metrics["last_error"] = error_msg
            
            # Atualiza tempo médio de resposta
            total = metrics["successful_requests"] + metrics["failed_requests"]
            if total > 0:
                metrics["avg_response_time"] = (
                    (metrics["avg_response_time"] * (total - 1) + response_time) / total
                )
                
        except Exception as e:
            logger.error(f"Erro ao atualizar métricas para {api_name}: {str(e)}")

    def _validate_query(self, query: Optional[str], min_length: int = 1, max_length: int = 1000) -> str:
        """
        Valida e processa uma query.
        
        Args:
            query: Query a ser validada
            min_length: Comprimento mínimo da query após strip
            max_length: Comprimento máximo da query
            
        Returns:
            Query processada
            
        Raises:
            ValidationError: Se a query for inválida
        """
        if not query:
            raise ValidationError("Query não pode ser None", "query")
            
        if not isinstance(query, str):
            raise ValidationError("Query deve ser uma string", "query")
            
        query = query.strip()
        if len(query) < min_length:
            raise ValidationError(f"Query deve ter pelo menos {min_length} caracteres", "query")
            
        if len(query) > max_length:
            raise ValidationError(f"Query não pode ter mais de {max_length} caracteres", "query")
            
        return query

    def _validate_url(self, url: str) -> str:
        """
        Valida uma URL.
        
        Args:
            url: URL a ser validada
            
        Returns:
            URL validada
            
        Raises:
            ValidationError: Se a URL for inválida
        """
        if not url or not isinstance(url, str):
            raise ValidationError("URL inválida", "url")
            
        url = url.strip()
        if not url:
            raise ValidationError("URL não pode ser vazia", "url")
            
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValidationError("URL deve ter esquema (http/https) e host", "url")
            
        if parsed.scheme not in ["http", "https"]:
            raise ValidationError("URL deve começar com http:// ou https://", "url")
            
        return url

    def _validate_api_key(self, api_name: str) -> str:
        """
        Valida se existe uma chave de API válida.
        
        Args:
            api_name: Nome da API
            
        Returns:
            Chave da API
            
        Raises:
            ConfigurationError: Se a chave não existir ou for inválida
        """
        api_key = self.api_keys.get(api_name)
        if not api_key:
            raise ConfigurationError(f"Chave da API não encontrada: {api_name}", api_name)
            
        if not isinstance(api_key, str) or not api_key.strip():
            raise ConfigurationError(f"Chave da API inválida: {api_name}", api_name)
            
        return api_key.strip()

if __name__ == "__main__":
    # Exemplo de uso
    api = APIIntegrations()
    
    # Verifica status das APIs
    print("Status das APIs:")
    print(json.dumps(api.get_api_status(), indent=2))
    
    # Exemplo de busca no Google
    results = api.google_search("Python programming tutorials")
    print("\nResultados da busca Google:")
    print(json.dumps(results, indent=2))
    
    # Exibe estatísticas
    print("\nEstatísticas de uso:")
    print(json.dumps(api.get_stats(), indent=2)) 