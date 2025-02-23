"""
Testes unitários para o módulo api_integrations da CodeMaria
"""

import pytest
from unittest.mock import MagicMock, patch
from code_maria.api_integrations import APIIntegrations
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
import requests

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture para simular variáveis de ambiente."""
    env_vars = {
        "OPENAI_API_KEY": "test_openai_key",
        "GOOGLE_API_KEY": "test_google_key",
        "NEWS_API_KEY": "test_news_key",
        "GOOGLE_SEARCH_CX": "test_cx",
        "SERPAPI_KEY": "test_serpapi_key"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

@pytest.fixture
def api_integrations(mock_env_vars):
    """Fixture para criar uma instância do APIIntegrations com mocks."""
    return APIIntegrations()

def test_initialization(api_integrations):
    """Testa a inicialização do APIIntegrations."""
    assert api_integrations.api_keys["openai"] == "test_openai_key"
    assert api_integrations.api_keys["google"] == "test_google_key"
    assert api_integrations.api_keys["news_api"] == "test_news_key"
    assert isinstance(api_integrations.request_history, list)
    assert "google_search" in api_integrations.base_urls

def test_load_api_keys_warning(caplog):
    """Testa o aviso quando uma chave de API está faltando."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "", "GOOGLE_API_KEY": "test"}):
        api = APIIntegrations()
        assert "Chave de API não encontrada: OPENAI_API_KEY" in caplog.text

@pytest.mark.parametrize("search_type,language,num_results", [
    ("web", "pt", 5),
    ("image", "en", 3),
    ("news", "es", 10)
])
def test_google_search(api_integrations, search_type, language, num_results):
    """Testa a busca no Google com diferentes parâmetros."""
    mock_response = {
        "searchInformation": {
            "totalResults": "1000",
            "searchTime": 0.5
        },
        "items": [
            {
                "title": "Test Result",
                "link": "https://test.com",
                "snippet": "Test snippet",
                "pagemap": {
                    "metatags": [{"article:published_time": "2024-03-15"}]
                }
            }
        ]
    }

    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200

        results = api_integrations.google_search(
            "test query",
            search_type=search_type,
            language=language,
            num_results=num_results
        )

        assert results["query"] == "test query"
        assert results["total_results"] == 1000
        assert len(results["items"]) == 1
        assert results["items"][0]["title"] == "Test Result"

        # Verifica se os parâmetros corretos foram passados
        mock_get.assert_called_once()
        call_args = mock_get.call_args.kwargs["params"]
        assert call_args["q"] == "test query"
        assert call_args["hl"] == language
        assert call_args["num"] == num_results
        if search_type != "web":
            assert call_args["searchType"] == search_type

def test_search_scientific_articles(api_integrations):
    """Testa a busca de artigos científicos."""
    mock_response = {
        "organic_results": [
            {
                "title": "Test Article",
                "authors": ["Author 1", "Author 2"],
                "publication_info": {"summary": "Journal of Testing"},
                "snippet": "Test abstract",
                "cited_by": {"total": 42},
                "link": "https://test.com/article",
                "year": "2024"
            }
        ]
    }
    
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200
        
        articles = api_integrations.search_scientific_articles(
            "machine learning",
            max_results=5,
            sort_by="relevance"
        )
        
        assert len(articles) == 1
        article = articles[0]
        assert article["title"] == "Test Article"
        assert len(article["authors"]) == 2
        assert article["citations"] == 42
        assert article["year"] == "2024"

def test_extract_webpage_content(api_integrations):
    """Testa a extração de conteúdo de páginas web."""
    html_content = """
    <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="Test description">
        </head>
        <body>
            <main>
                <h1>Main Content</h1>
                <p>Test paragraph</p>
                <a href="https://test.com" title="Test Link">Link Text</a>
                <img src="test.jpg" alt="Test Image" title="Image Title">
            </main>
        </body>
    </html>
    """
    
    with patch("requests.get") as mock_get:
        mock_get.return_value.text = html_content
        mock_get.return_value.status_code = 200
        
        content = api_integrations.extract_webpage_content(
            "https://test.com",
            extract_images=True,
            extract_links=True
        )
        
        assert content["title"] == "Test Page"
        assert content["meta_description"] == "Test description"
        assert "Main Content" in content["text_content"]
        assert len(content["links"]) == 1
        assert content["links"][0]["text"] == "Link Text"
        assert len(content["images"]) == 1
        assert content["images"][0]["alt"] == "Test Image"

def test_extract_webpage_content_error(api_integrations):
    """Testa o tratamento de erros na extração de conteúdo web."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection error")

        content = api_integrations.extract_webpage_content("https://test.com")
        assert "error" in content
        assert content["error"] == "Connection error"
        assert content["status_code"] == 500
        assert "timestamp" in content

def test_request_history(api_integrations):
    """Testa o registro do histórico de requisições."""
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = {
            "searchInformation": {
                "totalResults": "1000",
                "searchTime": 0.5
            },
            "items": []
        }
        mock_get.return_value.status_code = 200

        api_integrations.google_search("test")
        history = api_integrations.get_request_history()

        assert len(history) == 1
        assert history[0]["api"] == "google_search"
        assert history[0]["method"] == "GET"
        assert history[0]["status_code"] == 200

def test_check_api_status(api_integrations):
    """Testa a verificação detalhada do status das APIs."""
    # Simula algumas requisições
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"items": []}
        mock_get.return_value.status_code = 200
        
        api_integrations.google_search("test1")
        api_integrations.google_search("test2")
        
        status = api_integrations.check_api_status()
        
        assert status["google"]["has_key"] is True
        assert status["google"]["total_requests"] == 2
        assert isinstance(status["google"]["last_request"], str)

def test_process_google_result(api_integrations):
    """Testa o processamento de resultados do Google."""
    test_item = {
        "title": "Test Title",
        "link": "https://test.com",
        "snippet": "Test Snippet",
        "pagemap": {
            "metatags": [{"article:published_time": "2024-03-15"}]
        }
    }
    
    result = api_integrations._process_google_result(test_item)
    
    assert result["title"] == "Test Title"
    assert result["link"] == "https://test.com"
    assert result["snippet"] == "Test Snippet"
    assert result["date"] == "2024-03-15"
    assert result["type"] == "webpage"

@pytest.mark.parametrize("html_content,expected_title", [
    ("<title>Test Title</title>", "Test Title"),
    ("<h1>Test H1</h1>", "Test H1"),
    ("", "")
])
def test_extract_title(api_integrations, html_content, expected_title):
    """Testa a extração de títulos com diferentes estruturas HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    title = api_integrations._extract_title(soup)
    assert title == expected_title

def test_extract_images(api_integrations):
    """Testa a extração de imagens de uma página."""
    html = """
    <div>
        <img src="test1.jpg" alt="Test 1" title="Title 1">
        <img src="test2.jpg" alt="Test 2">
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    images = api_integrations._extract_images(soup)
    
    assert len(images) == 2
    assert images[0]["src"] == "test1.jpg"
    assert images[0]["alt"] == "Test 1"
    assert images[0]["title"] == "Title 1"
    assert images[1]["title"] == ""

def test_extract_links(api_integrations):
    """Testa a extração de links de uma página."""
    html = """
    <div>
        <a href="https://test1.com" title="Link 1">Text 1</a>
        <a href="test2.com">Text 2</a>
        <a href="https://test3.com">Text 3</a>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    links = api_integrations._extract_links(soup)
    
    assert len(links) == 2  # Apenas links com http/https
    assert links[0]["url"] == "https://test1.com"
    assert links[0]["text"] == "Text 1"
    assert links[0]["title"] == "Link 1"

def test_rate_limit_initialization(api_integrations):
    """Testa a inicialização do rate limiter."""
    assert api_integrations.rate_limiter is not None
    
    # Verifica se os limites foram configurados corretamente
    limits = api_integrations.rate_limiter.limits
    assert "google_search" in limits
    assert limits["google_search"]["calls"] == 100
    assert limits["google_search"]["period"] == 60
    
    assert "news_api" in limits
    assert limits["news_api"]["calls"] == 500
    assert limits["news_api"]["period"] == 3600

def test_rate_limit_check(api_integrations):
    """Testa a verificação de rate limit."""
    # Teste com API válida
    assert api_integrations._check_rate_limit("google_search") is True
    
    # Teste com API inválida (usa limite padrão)
    assert api_integrations._check_rate_limit("invalid_api") is True

def test_rate_limit_exceeded(api_integrations):
    """Testa o comportamento quando o rate limit é excedido."""
    # Configura um limite baixo para teste
    api_integrations.rate_limiter.update_limits("test_api", calls=1, period=60)
    
    # Primeira requisição (sucesso)
    assert api_integrations._check_rate_limit("test_api") is True
    
    # Segunda requisição (deve falhar)
    assert api_integrations._check_rate_limit("test_api") is False

@patch("requests.get")
def test_google_search_with_rate_limit(mock_get, api_integrations):
    """Testa a busca no Google com rate limiting."""
    mock_response = {
        "searchInformation": {"totalResults": "1000", "searchTime": 0.5},
        "items": [
            {
                "title": "Test Result",
                "link": "https://test.com",
                "snippet": "Test snippet",
                "pagemap": {"metatags": [{"article:published_time": "2024-03-15"}]}
            }
        ]
    }
    mock_get.return_value = MagicMock()
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.status_code = 200

    # Primeira busca (sucesso)
    result1 = api_integrations.google_search("test query")
    assert "error" not in result1
    assert len(result1["items"]) == 1

    # Força exceder o rate limit
    api_integrations.rate_limiter.update_limits("google_search", calls=0, period=60)

    # Segunda busca (deve falhar por rate limit)
    result2 = api_integrations.google_search("test query")
    assert "error" in result2
    assert result2["status_code"] == 429
    assert "timestamp" in result2

@patch("requests.get")
def test_scientific_articles_with_rate_limit(mock_get, api_integrations):
    """Testa a busca de artigos científicos com rate limiting."""
    mock_response = {
        "organic_results": [
            {
                "title": "Test Article",
                "authors": ["Author 1"],
                "publication_info": {"summary": "Journal"},
                "snippet": "Abstract",
                "cited_by": {"total": 42},
                "link": "https://test.com",
                "year": "2024"
            }
        ]
    }
    mock_get.return_value = MagicMock()
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.status_code = 200

    # Primeira busca (sucesso)
    result1 = api_integrations.search_scientific_articles("test")
    assert len(result1) == 1
    assert result1[0]["title"] == "Test Article"

    # Força exceder o rate limit
    api_integrations.rate_limiter.update_limits("scholar", calls=0, period=60)

    # Segunda busca (deve falhar por rate limit)
    result2 = api_integrations.search_scientific_articles("test")
    assert len(result2) == 0

@patch("requests.get")
def test_webpage_extraction_with_rate_limit(mock_get, api_integrations):
    """Testa a extração de conteúdo web com rate limiting."""
    html_content = """
    <html>
        <head><title>Test Page</title></head>
        <body><p>Test content</p></body>
    </html>
    """
    mock_get.return_value = MagicMock()
    mock_get.return_value.text = html_content
    mock_get.return_value.status_code = 200

    # Primeira extração (sucesso)
    result1 = api_integrations.extract_webpage_content("https://test.com")
    assert "error" not in result1
    assert result1["title"] == "Test Page"

    # Força exceder o rate limit
    api_integrations.rate_limiter.update_limits("web_extract", calls=0, period=60)

    # Segunda extração (deve falhar por rate limit)
    result2 = api_integrations.extract_webpage_content("https://test.com")
    assert "error" in result2
    assert result2["status_code"] == 429
    assert "timestamp" in result2

def test_api_status(api_integrations):
    """Testa o status das APIs com informações de rate limiting."""
    # Realiza algumas requisições para gerar estatísticas
    api_integrations._check_rate_limit("google_search")
    api_integrations._check_rate_limit("news_api")
    
    status = api_integrations.get_api_status()
    
    assert "google_search" in status
    assert "news_api" in status
    
    for api_name, api_status in status.items():
        assert "has_key" in api_status
        assert "total_requests" in api_status
        assert "throttled_requests" in api_status
        assert "throttle_ratio" in api_status
        assert "current_usage" in api_status

def test_concurrent_requests(api_integrations):
    """Testa requisições concorrentes com rate limiting."""
    import threading
    
    def make_requests():
        for _ in range(5):
            api_integrations._check_rate_limit("test_api")
    
    # Configura limite para teste
    api_integrations.rate_limiter.update_limits("test_api", calls=10, period=60)
    
    threads = [
        threading.Thread(target=make_requests)
        for _ in range(3)
    ]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    status = api_integrations.get_api_status()
    assert status["test_api"]["total_requests"] > 0

@pytest.mark.parametrize("api_name,expected_limit", [
    ("google_search", {"calls": 100, "period": 60}),
    ("news_api", {"calls": 500, "period": 3600}),
    ("openai", {"calls": 3000, "period": 60}),
    ("scholar", {"calls": 100, "period": 60}),
    ("web_extract", {"calls": 60, "period": 60})
])
def test_api_rate_limits(api_integrations, api_name, expected_limit):
    """Testa os limites de taxa configurados para cada API."""
    limits = api_integrations.rate_limiter.limits[api_name]
    assert limits["calls"] == expected_limit["calls"]
    assert limits["period"] == expected_limit["period"]

@pytest.mark.parametrize("invalid_api", [
    None,
    "",
    " ",
    123,
    {},
    []
])
def test_check_rate_limit_invalid_api(api_integrations, invalid_api):
    """Testa o _check_rate_limit com APIs inválidas."""
    result = api_integrations._check_rate_limit(invalid_api)
    assert result is False

def test_check_rate_limit_no_limiter(api_integrations):
    """Testa o _check_rate_limit sem rate_limiter inicializado."""
    api_integrations.rate_limiter = None
    result = api_integrations._check_rate_limit("test_api")
    assert result is False

def test_check_rate_limit_invalid_methods(api_integrations):
    """Testa o _check_rate_limit com métodos não chamáveis."""
    api_integrations.rate_limiter.is_rate_limited = "not_callable"
    result = api_integrations._check_rate_limit("test_api")
    assert result is False

@pytest.mark.parametrize("invalid_query", [
    None,
    "",
    " ",
    "\t\n",
])
def test_google_search_invalid_query(api_integrations, invalid_query):
    """Testa google_search com queries inválidas."""
    result = api_integrations.google_search(invalid_query)
    assert "error" in result
    assert "Query não pode estar vazia" in result["error"]

@pytest.mark.parametrize("invalid_type", [
    None,
    "",
    "invalid",
    "video",
    123
])
def test_google_search_invalid_type(api_integrations, invalid_type):
    """Testa google_search com tipos de busca inválidos."""
    result = api_integrations.google_search("test", search_type=invalid_type)
    assert "error" in result
    assert "Tipo de busca inválido" in result["error"]

@pytest.mark.parametrize("invalid_num", [
    None,
    0,
    -1,
    "10",
    1.5
])
def test_google_search_invalid_num_results(api_integrations, invalid_num):
    """Testa google_search com número de resultados inválido."""
    result = api_integrations.google_search("test", num_results=invalid_num)
    assert "error" in result
    assert "num_results deve ser um número inteiro positivo" in result["error"]

@pytest.mark.parametrize("invalid_lang", [
    None,
    "",
    "x",
    123,
    ["pt"]
])
def test_google_search_invalid_language(api_integrations, invalid_lang):
    """Testa google_search com idioma inválido."""
    result = api_integrations.google_search("test", language=invalid_lang)
    assert "error" in result
    assert "language deve ser um código de idioma válido" in result["error"]

@pytest.mark.parametrize("invalid_url", [
    None,
    "",
    " ",
    "not_a_url",
    "http://",
    "https://"
])
def test_extract_webpage_content_invalid_url(api_integrations, invalid_url):
    """Testa extract_webpage_content com URLs inválidas."""
    result = api_integrations.extract_webpage_content(invalid_url)
    assert "error" in result
    assert any(msg in result["error"] for msg in ["URL não pode estar vazia", "URL inválida", "URL mal formatada"])

@patch("requests.get")
def test_extract_webpage_content_http_errors(mock_get, api_integrations):
    """Testa extract_webpage_content com diferentes erros HTTP."""
    test_cases = [
        (requests.exceptions.Timeout, "Timeout na requisição"),
        (requests.exceptions.SSLError, "Erro de SSL"),
        (requests.exceptions.ConnectionError, "Erro de conexão"),
        (requests.exceptions.RequestException, "Erro na requisição")
    ]
    
    for exception, expected_msg in test_cases:
        mock_get.side_effect = exception()
        result = api_integrations.extract_webpage_content("https://example.com")
        assert "error" in result
        assert expected_msg in result["error"]

def test_process_google_result_invalid_numbers(api_integrations):
    """Testa _process_google_result com dados numéricos inválidos."""
    invalid_data = {
        "searchInformation": {
            "totalResults": "not_a_number",
            "searchTime": "invalid"
        }
    }
    
    result = api_integrations._process_google_result(invalid_data, "test")
    assert result["total_results"] == 0
    assert result["time_taken"] == 0.0

def test_process_google_result_incomplete_data(api_integrations):
    """Testa _process_google_result com dados incompletos."""
    incomplete_data = {
        "searchInformation": {}
    }
    
    result = api_integrations._process_google_result(incomplete_data, "test")
    assert result["total_results"] == 0
    assert result["time_taken"] == 0.0
    assert isinstance(result["items"], list)
    assert len(result["items"]) == 0 