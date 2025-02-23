"""
Schemas de validação de dados da CodeMaria
Define os schemas para validação de dados de entrada e saída das APIs.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, HttpUrl, model_validator
from datetime import datetime
import re

class GoogleSearchParams(BaseModel):
    """Schema para parâmetros de busca do Google."""
    query: str = Field(..., min_length=1, max_length=2048)
    search_type: str = Field(
        "web",
        pattern="^(web|image|news)$"
    )
    language: str = Field(
        "en",
        pattern="^[a-z]{2}(-[A-Z]{2})?$"
    )
    num_results: int = Field(
        10,
        ge=1,
        le=100
    )
    
    @model_validator(mode='before')
    @classmethod
    def validate_query(cls, values):
        """Valida a query de busca."""
        if isinstance(values, dict) and 'query' in values and not values['query'].strip():
            raise ValueError("Query não pode ser vazia")
        return values

class GoogleSearchResult(BaseModel):
    """Schema para resultados de busca do Google."""
    query: str
    total_results: int = Field(ge=0)
    search_time: float = Field(ge=0.0)
    items: List[Dict[str, Any]]
    error: Optional[str] = None

class ScientificArticleParams(BaseModel):
    """Schema para parâmetros de busca de artigos científicos."""
    query: str = Field(..., min_length=1, max_length=2048)
    max_results: int = Field(
        10,
        ge=1,
        le=100
    )
    sort_by: str = Field(
        "relevance",
        pattern="^(relevance|date)$"
    )
    
    @model_validator(mode='before')
    def validate_query(cls, values):
        """Valida a query de busca."""
        if 'query' in values and not values['query'].strip():
            raise ValueError("Query não pode ser vazia")
        return values

class ScientificArticleResult(BaseModel):
    """Schema para resultados de busca de artigos científicos."""
    query: str
    total_results: int = Field(ge=0)
    articles: List[Dict[str, Any]]
    error: Optional[str] = None

class WebContentParams(BaseModel):
    """Schema para parâmetros de extração de conteúdo web."""
    url: HttpUrl
    extract_images: bool = False
    extract_links: bool = False
    
    @model_validator(mode='before')
    @classmethod
    def validate_url(cls, values):
        """Valida a URL."""
        if isinstance(values, dict) and 'url' in values and not str(values['url']).startswith(("http://", "https://")):
            raise ValueError("URL deve começar com http:// ou https://")
        return values

class WebContentResult(BaseModel):
    """Schema para resultados de extração de conteúdo web."""
    url: HttpUrl
    title: str
    meta_description: Optional[str]
    text_content: str
    images: Optional[List[Dict[str, str]]]
    links: Optional[List[Dict[str, str]]]
    error: Optional[str] = None

class APIMetrics(BaseModel):
    """Schema para métricas de uso de API."""
    success_rate: float = Field(ge=0.0, le=1.0)
    error_rate: float = Field(ge=0.0, le=1.0)
    avg_response_time: float = Field(ge=0.0)
    samples: int = Field(ge=0)

class RateLimitConfig(BaseModel):
    """Schema para configuração de rate limiting."""
    calls: int = Field(ge=1)
    period: int = Field(ge=1)

class CacheItem(BaseModel):
    """Schema para itens do cache."""
    value: Any
    expiry: float = Field(ge=0.0)
    namespace: Optional[str]

class CacheStats(BaseModel):
    """Schema para estatísticas do cache."""
    hits: int = Field(ge=0)
    misses: int = Field(ge=0)
    sets: int = Field(ge=0)
    evictions: int = Field(ge=0)

class UserInfo(BaseModel):
    """Informações do usuário."""
    nome: str
    nivel: str
    linguagem_preferida: str

class ProcessRequest(BaseModel):
    """Requisição de processamento."""
    text: str
    type: str
    user_info: Optional[UserInfo] = None

class ProcessResponse(BaseModel):
    """Resposta de processamento."""
    status: str
    type: str
    response: str
    style: Dict[str, float]

class PDFAnalysis(BaseModel):
    """Análise de um arquivo PDF."""
    num_sentences: int
    num_words: int
    num_unique_words: int
    avg_sentence_length: float
    most_common_words: Dict[str, int]
    pos_distribution: Dict[str, int]

class PDFProcessingResult(BaseModel):
    """Resultado do processamento de um PDF."""
    file: str
    size: int
    analysis: PDFAnalysis

class PDFStats(BaseModel):
    """Estatísticas gerais de processamento de PDFs."""
    total_files_processed: int
    processed_files: List[str]
    grammar_statistics: Dict[int, PDFAnalysis]

class PDFLearningResult(BaseModel):
    """Resultado do aprendizado a partir de um PDF."""
    file: str
    grammar_analysis: PDFAnalysis
    sentiment: Dict[str, Any]
    timestamp: str

class TrainingResult(BaseModel):
    """Resultado de um treinamento."""
    file: str
    timestamp: str
    metadata: Dict[str, Any]
    grammar_analysis: PDFAnalysis
    sentiment: Dict[str, Any]
    status: str
    error: Optional[str] = None

class TrainingSummary(BaseModel):
    """Resumo de um treinamento."""
    total_files: int
    successful: int
    failed: int
    results: List[TrainingResult]

class TrainingResponse(BaseModel):
    """Resposta de uma operação de treinamento."""
    status: str
    summary: Optional[TrainingSummary] = None
    message: Optional[str] = None

class TrainingStatistics(BaseModel):
    """Estatísticas detalhadas do treinamento."""
    total_files: int
    successful: int
    failed: int
    success_rate: float
    sentiment_distribution: Dict[str, int]
    grammar_statistics: Dict[str, Union[int, float]]
    last_training: Optional[str]

class TrainingStatsResponse(BaseModel):
    """Resposta com estatísticas de treinamento."""
    status: str
    statistics: Optional[TrainingStatistics] = None
    message: Optional[str] = None

def validate_google_search_params(params: Dict[str, Any]) -> GoogleSearchParams:
    """
    Valida parâmetros de busca do Google.
    
    Args:
        params: Dicionário com parâmetros
        
    Returns:
        Objeto GoogleSearchParams validado
        
    Raises:
        ValidationError: Se os parâmetros forem inválidos
    """
    return GoogleSearchParams(**params)

def validate_google_search_result(result: Dict[str, Any]) -> GoogleSearchResult:
    """
    Valida resultado de busca do Google.
    
    Args:
        result: Dicionário com resultado
        
    Returns:
        Objeto GoogleSearchResult validado
        
    Raises:
        ValidationError: Se o resultado for inválido
    """
    return GoogleSearchResult(**result)

def validate_scientific_article_params(params: Dict[str, Any]) -> ScientificArticleParams:
    """
    Valida parâmetros de busca de artigos científicos.
    
    Args:
        params: Dicionário com parâmetros
        
    Returns:
        Objeto ScientificArticleParams validado
        
    Raises:
        ValidationError: Se os parâmetros forem inválidos
    """
    return ScientificArticleParams(**params)

def validate_scientific_article_result(result: Dict[str, Any]) -> ScientificArticleResult:
    """
    Valida resultado de busca de artigos científicos.
    
    Args:
        result: Dicionário com resultado
        
    Returns:
        Objeto ScientificArticleResult validado
        
    Raises:
        ValidationError: Se o resultado for inválido
    """
    return ScientificArticleResult(**result)

def validate_web_content_params(params: Dict[str, Any]) -> WebContentParams:
    """
    Valida parâmetros de extração de conteúdo web.
    
    Args:
        params: Dicionário com parâmetros
        
    Returns:
        Objeto WebContentParams validado
        
    Raises:
        ValidationError: Se os parâmetros forem inválidos
    """
    return WebContentParams(**params)

def validate_web_content_result(result: Dict[str, Any]) -> WebContentResult:
    """
    Valida resultado de extração de conteúdo web.
    
    Args:
        result: Dicionário com resultado
        
    Returns:
        Objeto WebContentResult validado
        
    Raises:
        ValidationError: Se o resultado for inválido
    """
    return WebContentResult(**result)

def validate_api_metrics(metrics: Dict[str, Any]) -> APIMetrics:
    """
    Valida métricas de uso de API.
    
    Args:
        metrics: Dicionário com métricas
        
    Returns:
        Objeto APIMetrics validado
        
    Raises:
        ValidationError: Se as métricas forem inválidas
    """
    return APIMetrics(**metrics)

def validate_rate_limit_config(config: Dict[str, Any]) -> RateLimitConfig:
    """
    Valida configuração de rate limiting.
    
    Args:
        config: Dicionário com configuração
        
    Returns:
        Objeto RateLimitConfig validado
        
    Raises:
        ValidationError: Se a configuração for inválida
    """
    return RateLimitConfig(**config)

def validate_cache_item(item: Dict[str, Any]) -> CacheItem:
    """
    Valida item do cache.
    
    Args:
        item: Dicionário com item
        
    Returns:
        Objeto CacheItem validado
        
    Raises:
        ValidationError: Se o item for inválido
    """
    return CacheItem(**item)

def validate_cache_stats(stats: Dict[str, Any]) -> CacheStats:
    """
    Valida estatísticas do cache.
    
    Args:
        stats: Dicionário com estatísticas
        
    Returns:
        Objeto CacheStats validado
        
    Raises:
        ValidationError: Se as estatísticas forem inválidas
    """
    return CacheStats(**stats) 