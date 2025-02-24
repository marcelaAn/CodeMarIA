"""
Módulo de Aprendizado da CodeMarIA
Responsável por implementar as estratégias de auto-aprendizado e evolução contínua.
"""

import logging
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from collections import Counter
import re
from datetime import datetime
import torch
import json
import os
from math import log
from langdetect import detect
from urllib.parse import urlparse

# Download dos recursos do NLTK
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('mac_morpho')

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LearningEngine:
    """Motor de aprendizado da CodeMarIA."""
    
    def __init__(self, device=None):
        """Inicializa o motor de aprendizado."""
        try:
            # Configuração do dispositivo
            if device is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"
            self.device = device
            logger.info(f"Usando dispositivo: {device}")
            
            # Inicializa modelos de NLP
            self.sentiment_analyzer = pipeline(
                "text-classification",
                model="neuralmind/bert-base-portuguese-cased",
                device=device
            )
            
            # Headers padrão para requisições
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            
            # Configurações por contexto
            self.context_settings = {
                "cultural": {
                    "min_sentence_length": 5,
                    "max_sentence_length": 30,
                    "relevant_pos_tags": ["NOUN", "ADJ", "VERB"]
                },
                "educational": {
                    "min_sentence_length": 10,
                    "max_sentence_length": 50,
                    "relevant_pos_tags": ["NOUN", "VERB", "ADJ", "NUM"]
                },
                "technical": {
                    "min_sentence_length": 8,
                    "max_sentence_length": 40,
                    "relevant_pos_tags": ["NOUN", "VERB", "NUM", "SYM"]
                }
            }
            
            # Inicializa stopwords
            self.stopwords = set(stopwords.words('portuguese'))
            self.stopwords.update(stopwords.words('english'))
            
            logger.info("Motor de aprendizado inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro na inicialização: {str(e)}")
            raise

    def _detect_context(self, url: str) -> str:
        """
        Detecta o contexto do conteúdo baseado na URL e palavras-chave.
        
        Args:
            url: URL do conteúdo
            
        Returns:
            str: Contexto detectado ('cultural', 'educational' ou 'technical')
        """
        domain = urlparse(url).netloc.lower()
        
        # Palavras-chave por contexto
        context_keywords = {
            "cultural": ["cultura", "arte", "teatro", "cinema", "museu", "exposicao"],
            "educational": ["edu", "escola", "universidade", "curso", "biblioteca"],
            "technical": ["tech", "programming", "github", "docs", "api", "dev"]
        }
        
        # Verifica domínio e palavras-chave
        for context, keywords in context_keywords.items():
            if any(kw in domain for kw in keywords):
                return context
            
        # Verifica path da URL
        path = urlparse(url).path.lower()
        for context, keywords in context_keywords.items():
            if any(kw in path for kw in keywords):
                return context
        
        return "technical"  # default

    def _handle_site_access(self, url: str) -> requests.Response:
        """
        Gerencia o acesso aos sites com tratamento de erros e headers apropriados.
        
        Args:
            url: URL para acessar
            
        Returns:
            Response: Resposta da requisição
            
        Raises:
            Exception: Se houver erro no acesso
        """
        try:
            # Adiciona headers específicos para alguns sites
            custom_headers = self.headers.copy()
            domain = urlparse(url).netloc.lower()
            
            if "github" in domain:
                custom_headers['Accept'] = 'application/vnd.github.v3+json'
            elif any(edu in domain for edu in ['.edu', 'universidade', 'escola']):
                custom_headers['Referer'] = 'https://www.google.com/'
            
            response = requests.get(url, headers=custom_headers, timeout=10)
            response.raise_for_status()
            return response
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.warning(f"Acesso negado (403) para {url}, tentando com headers alternativos")
                try:
                    # Tenta novamente com headers diferentes
                    alt_headers = {
                        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                        'Accept': '*/*'
                    }
                    response = requests.get(url, headers=alt_headers, timeout=10)
                    response.raise_for_status()
                    return response
                except:
                    raise
            raise
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao acessar {url}: {str(e)}")
            raise

    def _detect_and_process_language(self, text: str) -> Dict[str, Any]:
        """
        Detecta e processa o texto de acordo com o idioma.
        
        Args:
            text: Texto para processar
            
        Returns:
            Dict com resultados do processamento
        """
        try:
            lang = detect(text)
            
            if lang == 'pt':
                return self._process_portuguese(text)
            elif lang == 'en':
                return self._process_english(text)
            else:
                logger.warning(f"Idioma não suportado: {lang}, usando processamento padrão")
                return self._process_default(text)
                
        except Exception as e:
            logger.error(f"Erro na detecção de idioma: {str(e)}")
            return self._process_default(text)

    def _process_portuguese(self, text: str) -> Dict[str, Any]:
        """
        Processa texto em português com análise específica.
        
        Args:
            text: Texto em português
            
        Returns:
            Dict com resultados da análise
        """
        # Tokenização específica para português
        sentences = sent_tokenize(text, language='portuguese')
        words = word_tokenize(text.lower(), language='portuguese')
        
        # Remove stopwords do português
        stop_words = set(stopwords.words('portuguese'))
        words = [w for w in words if w.isalnum() and w not in stop_words]
        
        # Análise morfológica com mac_morpho
        try:
            pos_tags = nltk.tag.pos_tag(words, lang='por')
        except:
            logger.warning("Erro no POS tagging português, usando tagger padrão")
            pos_tags = pos_tag(words)
        
        return {
            "sentences": sentences,
            "words": words,
            "pos_tags": pos_tags,
            "language": "pt"
        }

    def _process_english(self, text: str) -> Dict[str, Any]:
        """
        Processa texto em inglês.
        
        Args:
            text: Texto em inglês
            
        Returns:
            Dict com resultados da análise
        """
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        words = [w for w in words if w.isalnum() and w not in stop_words]
        pos_tags = pos_tag(words)
        
        return {
            "sentences": sentences,
            "words": words,
            "pos_tags": pos_tags,
            "language": "en"
        }

    def _process_default(self, text: str) -> Dict[str, Any]:
        """
        Processamento padrão para outros idiomas.
        
        Args:
            text: Texto para processar
            
        Returns:
            Dict com resultados da análise
        """
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        words = [w for w in words if w.isalnum()]
        pos_tags = pos_tag(words)
        
        return {
            "sentences": sentences,
            "words": words,
            "pos_tags": pos_tags,
            "language": "unknown"
        }

    def _adjust_analysis_by_context(self, text: str, context: str) -> Dict[str, Any]:
        """
        Ajusta a análise de acordo com o contexto.
        
        Args:
            text: Texto para análise
            context: Contexto do conteúdo
            
        Returns:
            Dict com análise ajustada
        """
        settings = self.context_settings.get(context, self.context_settings["technical"])
        
        # Processa o texto de acordo com o idioma
        processed = self._detect_and_process_language(text)
        
        # Ajusta análise baseado no contexto
        relevant_sentences = [
            s for s in processed["sentences"]
            if settings["min_sentence_length"] <= len(word_tokenize(s)) <= settings["max_sentence_length"]
        ]
        
        relevant_pos = [
            word for word, tag in processed["pos_tags"]
            if any(pos in tag for pos in settings["relevant_pos_tags"])
        ]
        
        return {
            "relevant_sentences": relevant_sentences,
            "relevant_terms": relevant_pos,
            "language": processed["language"],
            "context": context
        }

    def _process_long_text(self, text: str, max_length: int = 512) -> List[str]:
        """
        Processa texto longo dividindo em chunks.
        
        Args:
            text: Texto para processar
            max_length: Tamanho máximo de cada chunk
            
        Returns:
            List[str]: Lista de chunks de texto
        """
        try:
            # Divide em sentenças
            sentences = sent_tokenize(text)
            chunks = []
            current_chunk = []
            current_length = 0
            
            for sentence in sentences:
                sentence_length = len(sentence.split())
                
                if current_length + sentence_length <= max_length:
                    current_chunk.append(sentence)
                    current_length += sentence_length
                else:
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_length = sentence_length
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            return chunks if chunks else [text[:max_length]]
            
        except Exception as e:
            logger.error(f"Erro no processamento de texto longo: {str(e)}")
            return [text[:max_length]]

    def learn_from_web(self, url: str) -> Dict[str, Any]:
        """
        Aprende a partir de conteúdo web.
        
        Args:
            url: URL para aprender
            
        Returns:
            Dict com resultados do aprendizado
        """
        try:
            # Detecta contexto
            context = self._detect_context(url)
            logger.info(f"Contexto detectado para {url}: {context}")
            
            # Acessa site
            response = self._handle_site_access(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrai conteúdo principal
            main_content = self._extract_main_content(soup)
            clean_text = self._clean_text(main_content)
            
            # Análise ajustada por contexto
            context_analysis = self._adjust_analysis_by_context(clean_text, context)
            
            # Análise completa do texto
            text_stats = self._analyze_text(clean_text)
            
            # Extrai código se for contexto técnico
            code_snippets = []
            if context == "technical":
                code_snippets = self._extract_code_snippets(soup)
            
            return {
                "url": url,
                "title": self._extract_title(soup),
                "context": context,
                "content_length": len(clean_text),
                "text_stats": text_stats,
                "context_analysis": context_analysis,
                "sentiment": self.analyze_sentiment(clean_text),
                "topics": self._classify_topics(clean_text),
                "code_snippets": code_snippets if code_snippets else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao aprender da web: {str(e)}")
            raise
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extrai o título da página.
        
        Args:
            soup: BeautifulSoup da página
            
        Returns:
            str: Título da página
        """
        try:
            # Tenta diferentes elementos para encontrar o título
            if soup.title:
                return soup.title.string.strip()
            
            h1 = soup.find('h1')
            if h1:
                return h1.get_text().strip()
            
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                return meta_title.get('content', '').strip()
            
            return "Sem título"
            
        except Exception as e:
            logger.error(f"Erro ao extrair título: {str(e)}")
            return "Erro ao extrair título"

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extrai o conteúdo principal da página.
        
        Args:
            soup: BeautifulSoup da página
            
        Returns:
            str: Conteúdo principal
        """
        try:
            # Lista de tags para conteúdo principal
            main_tags = ['main', 'article', 'div[role="main"]', '#content', '#main']
            content = []
            
            # Tenta encontrar o conteúdo principal
            for tag in main_tags:
                main = soup.select_one(tag)
                if main:
                    content.extend([p.get_text() for p in main.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
                    break
            
            # Se não encontrou conteúdo principal, pega todo o texto
            if not content:
                content = [p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
            
            return ' '.join(content)
            
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo principal: {str(e)}")
            return ""

    def _clean_text(self, text: str) -> str:
        """
        Limpa o texto removendo caracteres indesejados.
        
        Args:
            text: Texto para limpar
            
        Returns:
            str: Texto limpo
        """
        try:
            # Remove caracteres especiais e múltiplos espaços
            text = re.sub(r'[\n\r\t]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"Erro ao limpar texto: {str(e)}")
            return text

    def _extract_code_snippets(self, soup: BeautifulSoup) -> List[str]:
        """
        Extrai snippets de código da página.
        
        Args:
            soup: BeautifulSoup da página
            
        Returns:
            List[str]: Lista de snippets de código
        """
        try:
            # Procura por tags que geralmente contêm código
            code_tags = ['pre', 'code', '.highlight', '.source-code']
            snippets = []
            
            for tag in code_tags:
                elements = soup.select(tag)
                for element in elements:
                    code = element.get_text().strip()
                    if code:
                        snippets.append(code)
            
            return snippets
            
        except Exception as e:
            logger.error(f"Erro ao extrair snippets de código: {str(e)}")
            return []

    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Realiza análise completa do texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Dict com resultados da análise
        """
        try:
            # Tokenização
            sentences = sent_tokenize(text)
            words = word_tokenize(text.lower())
            
            # Remove stopwords e pontuação
            words = [w for w in words if w.isalnum() and w not in self.stopwords]
            
            # Análise morfológica
            pos_tags = pos_tag(words)
            pos_counts = Counter(tag for word, tag in pos_tags)
            
            # Estatísticas básicas
            num_sentences = len(sentences)
            num_words = len(words)
            num_unique_words = len(set(words))
            avg_sentence_length = num_words / num_sentences if num_sentences > 0 else 0
            avg_word_length = sum(len(w) for w in words) / num_words if num_words > 0 else 0
            vocabulary_richness = num_unique_words / num_words if num_words > 0 else 0
            
            # Extração de palavras-chave
            keywords = self._extract_keywords(words, text)
            
            return {
                "num_sentences": num_sentences,
                "num_words": num_words,
                "num_unique_words": num_unique_words,
                "avg_sentence_length": avg_sentence_length,
                "avg_word_length": avg_word_length,
                "vocabulary_richness": vocabulary_richness,
                "pos_counts": dict(pos_counts),
                "keywords": keywords
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de texto: {str(e)}")
            return {
                "error": str(e),
                "num_sentences": 0,
                "num_words": 0,
                "num_unique_words": 0,
                "avg_sentence_length": 0,
                "avg_word_length": 0,
                "vocabulary_richness": 0,
                "pos_counts": {},
                "keywords": []
            }

    def _extract_keywords(self, words: List[str], text: str) -> List[Dict[str, Any]]:
        """
        Extrai palavras-chave do texto usando TF-IDF.
        
        Args:
            words: Lista de palavras tokenizadas
            text: Texto original
            
        Returns:
            List[Dict]: Lista de palavras-chave com scores
        """
        try:
            # Conta frequência das palavras
            word_freq = Counter(words)
            
            # Calcula TF-IDF
            max_freq = max(word_freq.values())
            keywords = []
            
            for word, freq in word_freq.items():
                if len(word) < 3:  # Ignora palavras muito curtas
                    continue
                    
                tf = freq / max_freq
                idf = log(1 + len(text) / (1 + freq))  # Suavizado
                tf_idf = tf * idf
                
                keywords.append({
                    "word": word,
                    "frequency": freq,
                    "tf_idf": tf_idf
                })
            
            # Ordena por TF-IDF
            keywords.sort(key=lambda x: x["tf_idf"], reverse=True)
            
            return keywords[:20]  # Retorna top 20
            
        except Exception as e:
            logger.error(f"Erro na extração de palavras-chave: {str(e)}")
            return []

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analisa o sentimento do texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Dict com resultados da análise de sentimento
        """
        try:
            # Divide o texto em sentenças
            sentences = sent_tokenize(text)
            sentiments = []
            
            # Analisa cada sentença individualmente
            for sentence in sentences:
                try:
                    # Limita o tamanho da sentença
                    if len(sentence.split()) > 100:  # Limite seguro
                        sentence = ' '.join(sentence.split()[:100])
                    
                    result = self.sentiment_analyzer(sentence)[0]
                    sentiments.append({
                        "text": sentence,
                        "label": result["label"],
                        "score": result["score"]
                    })
                except Exception as e:
                    logger.warning(f"Erro ao analisar sentença: {str(e)}")
                    continue
            
            # Agrega resultados
            if sentiments:
                # Calcula média ponderada dos scores por tamanho da sentença
                label_scores = {}
                total_length = 0
                
                for sentiment in sentiments:
                    label = sentiment["label"]
                    score = sentiment["score"]
                    text_length = len(sentiment["text"].split())
                    total_length += text_length
                    
                    if label not in label_scores:
                        label_scores[label] = {
                            "score": 0,
                            "length": 0,
                            "count": 0
                        }
                    
                    label_scores[label]["score"] += score * text_length
                    label_scores[label]["length"] += text_length
                    label_scores[label]["count"] += 1
                
                # Normaliza scores e calcula estatísticas
                for label in label_scores:
                    info = label_scores[label]
                    info["score"] /= info["length"]  # Média ponderada
                    info["percentage"] = info["length"] / total_length
                    info["frequency"] = info["count"] / len(sentiments)
                
                # Encontra label predominante
                final_label = max(label_scores.items(), key=lambda x: x[1]["score"])
                
                return {
                    "label": final_label[0],
                    "score": final_label[1]["score"],
                    "distribution": {
                        label: {
                            "score": info["score"],
                            "percentage": info["percentage"],
                            "frequency": info["frequency"]
                        }
                        for label, info in label_scores.items()
                    },
                    "total_analyzed": len(sentiments),
                    "total_sentences": len(sentences)
                }
            else:
                return {
                    "label": "NEUTRO",
                    "score": 0.0,
                    "distribution": {},
                    "total_analyzed": 0,
                    "total_sentences": len(sentences)
                }
                
        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {str(e)}")
            return {
                "label": "ERRO",
                "score": 0.0,
                "error": str(e),
                "distribution": {},
                "total_analyzed": 0,
                "total_sentences": 0
            }

    def _classify_topics(self, text: str) -> Dict[str, float]:
        """
        Classifica o texto em tópicos.
        
        Args:
            text: Texto para classificação
            
        Returns:
            Dict com scores por tópico
        """
        try:
            # Tópicos possíveis
            topics = {
                "TUTORIAL": ["tutorial", "guia", "passo a passo", "como fazer"],
                "REFERENCIA": ["documentação", "referência", "manual", "especificação"],
                "EXEMPLO": ["exemplo", "demonstração", "amostra", "caso"],
                "TECNICO": ["técnico", "tecnologia", "programação", "desenvolvimento"],
                "EDUCACIONAL": ["curso", "aula", "estudo", "aprendizado"]
            }
            
            # Calcula score para cada tópico
            scores = {}
            text_lower = text.lower()
            
            for topic, keywords in topics.items():
                score = sum(text_lower.count(kw) for kw in keywords)
                scores[topic] = score / len(text.split()) if score > 0 else 0.0
            
            return scores
            
        except Exception as e:
            logger.error(f"Erro na classificação de tópicos: {str(e)}")
            return {}

    def update_knowledge_base(self, category: str, data: Any) -> bool:
        """Atualiza a base de conhecimento."""
        try:
            if category not in self.knowledge_base:
                self.knowledge_base[category] = []
            self.knowledge_base[category].append(data)
            
            # Salva em arquivo para persistência
            self._save_knowledge_base()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar base de conhecimento: {str(e)}")
            return False
    
    def _save_knowledge_base(self) -> None:
        """Salva a base de conhecimento em arquivo."""
        try:
            save_path = "data/knowledge_base.json"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao salvar base de conhecimento: {str(e)}")
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Retorna um resumo do aprendizado."""
        try:
            summary = {
                "total_entries": len(self.learning_history),
                "knowledge_categories": list(self.knowledge_base.keys()),
                "last_learning": self.learning_history[-1] if self.learning_history else None,
                "statistics": {
                    "web_sources": len([e for e in self.learning_history if "url" in e]),
                    "total_content_processed": sum(e.get("content_length", 0) for e in self.learning_history),
                    "topics_distribution": self._get_topics_distribution(),
                    "sentiment_distribution": self._get_sentiment_distribution()
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {str(e)}")
            return {
                "error": str(e),
                "total_entries": 0,
                "knowledge_categories": []
            }
    
    def _get_topics_distribution(self) -> Dict[str, int]:
        """Calcula distribuição de tópicos."""
        topics_count = Counter()
        for entry in self.learning_history:
            if "topics" in entry:
                for topic in entry["topics"]:
                    topics_count[topic] += 1
        return dict(topics_count)
    
    def _get_sentiment_distribution(self) -> Dict[str, int]:
        """Calcula distribuição de sentimentos."""
        sentiment_count = Counter()
        for entry in self.learning_history:
            if "sentiment_analysis" in entry and "overall" in entry["sentiment_analysis"]:
                sentiment_count[entry["sentiment_analysis"]["overall"]["label"]] += 1
        return dict(sentiment_count)

    def get_topics_distribution(self):
        """Retorna a distribuição de tópicos na base de conhecimento."""
        topics_count = Counter()
        for entry in self.knowledge_base.values():
            if "topics" in entry:
                for topic, score in entry["topics"].items():
                    topics_count[topic] += 1
        return dict(topics_count)

    def _count_pos_tags(self, pos_tags: List[tuple]) -> Dict[str, int]:
        """
        Conta e traduz as tags POS para português.
        
        Args:
            pos_tags: Lista de tuplas (palavra, tag)
            
        Returns:
            Dict com contagem de cada categoria gramatical
        """
        # Mapeamento de tags POS para português
        pos_map = {
            'NN': 'substantivo',
            'NNS': 'substantivo_plural',
            'NNP': 'nome_próprio',
            'NNPS': 'nome_próprio_plural',
            'VB': 'verbo',
            'VBD': 'verbo_passado',
            'VBG': 'verbo_gerúndio',
            'VBN': 'verbo_particípio',
            'VBP': 'verbo_presente',
            'VBZ': 'verbo_3pessoa',
            'JJ': 'adjetivo',
            'JJR': 'adjetivo_comparativo',
            'JJS': 'adjetivo_superlativo',
            'RB': 'advérbio',
            'RBR': 'advérbio_comparativo',
            'RBS': 'advérbio_superlativo',
            'IN': 'preposição',
            'DT': 'determinante',
            'CC': 'conjunção',
            'CD': 'número',
            'PRP': 'pronome_pessoal',
            'PRP$': 'pronome_possessivo',
            'WDT': 'pronome_relativo',
            'WP': 'pronome_interrogativo'
        }
        
        # Conta ocorrências
        pos_counts = Counter(tag for _, tag in pos_tags)
        
        # Traduz tags e agrupa categorias similares
        translated_counts = {}
        for tag, count in pos_counts.items():
            # Usa tag traduzida se disponível, senão usa original
            translated_tag = pos_map.get(tag, tag)
            translated_counts[translated_tag] = translated_counts.get(translated_tag, 0) + count
        
        return dict(translated_counts)

    def _detect_user_input_context(self, text: str) -> Dict[str, Any]:
        """
        Detecta o contexto da entrada do usuário.
        
        Args:
            text: Texto da entrada do usuário
            
        Returns:
            Dict com informações do contexto
        """
        try:
            # Palavras-chave para cada contexto
            context_keywords = {
                "educational": {
                    "keywords": [
                        "aprender", "estudar", "ensinar", "tutorial", "curso",
                        "aula", "exemplo", "explicar", "como", "fazer", "criar",
                        "implementar", "desenvolver", "programar", "código"
                    ],
                    "subcategories": {
                        "basic": ["básico", "iniciante", "começar", "primeiro"],
                        "intermediate": ["intermediário", "avançar", "melhorar"],
                        "advanced": ["avançado", "expert", "otimizar", "arquitetura"]
                    }
                },
                "technical": {
                    "keywords": [
                        "implementar", "desenvolver", "arquitetura", "design",
                        "padrão", "framework", "biblioteca", "api", "função",
                        "classe", "método", "objeto", "variável", "decorator",
                        "debug", "erro", "exceção", "performance", "otimizar"
                    ],
                    "subcategories": {
                        "programming": ["código", "programação", "desenvolvimento"],
                        "concepts": ["conceito", "teoria", "princípio", "padrão"]
                    }
                },
                "cultural": {
                    "keywords": [
                        "história", "cultura", "tradição", "arte", "música",
                        "literatura", "filosofia", "sociedade", "comunidade",
                        "movimento", "influência", "impacto", "origem", "evolução"
                    ],
                    "subcategories": {
                        "history": ["história", "origem", "evolução", "passado"],
                        "arts": ["arte", "música", "literatura", "criação"]
                    }
                },
                "geographic": {
                    "keywords": [
                        "onde", "local", "lugar", "região", "país", "cidade",
                        "estado", "endereço", "localização", "encontrar",
                        "próximo", "perto", "distância", "mapa", "rota"
                    ],
                    "subcategories": {
                        "location": ["onde", "local", "lugar", "endereço"],
                        "region": ["região", "país", "cidade", "estado"]
                    }
                }
            }
            
            # Tokeniza o texto
            tokens = word_tokenize(text.lower())
            
            # Remove stopwords
            stop_words = set(stopwords.words('portuguese'))
            tokens = [token for token in tokens if token not in stop_words]
            
            # Calcula pontuação para cada contexto
            context_scores = {
                context: {
                    "score": sum(1 for token in tokens if token in keywords["keywords"]),
                    "subcategories": {
                        subcat: sum(1 for token in tokens if token in subcats)
                        for subcat, subcats in keywords["subcategories"].items()
                    }
                }
                for context, keywords in context_keywords.items()
            }
            
            # Determina o contexto principal
            main_context = max(
                context_scores.items(),
                key=lambda x: x[1]["score"]
            )[0]
            
            # Determina nível de complexidade
            complexity_levels = {
                "basic": sum(1 for token in tokens 
                            if token in context_keywords["educational"]["subcategories"]["basic"]),
                "intermediate": sum(1 for token in tokens 
                                  if token in context_keywords["educational"]["subcategories"]["intermediate"]),
                "advanced": sum(1 for token in tokens 
                              if token in context_keywords["educational"]["subcategories"]["advanced"])
            }
            
            # Se nenhum nível foi detectado, usa o padrão
            if all(score == 0 for score in complexity_levels.values()):
                complexity_level = "basic"
            else:
                complexity_level = max(
                    complexity_levels.items(),
                    key=lambda x: x[1]
                )[0]
            
            # Calcula pontuação de urgência (0-5)
            urgency_keywords = ["urgente", "imediato", "rápido", "agora", "hoje"]
            urgency_score = sum(1 for token in tokens if token in urgency_keywords)
            
            # Analisa sentimento
            sentiment = self.analyze_sentiment(text)
            
            return {
                "main_context": main_context,
                "context_scores": context_scores,
                "complexity_level": complexity_level,
                "urgency_score": urgency_score,
                "sentiment": sentiment,
                "language": self._detect_language(text),
                "words": tokens,
                "pos_tags": pos_tag(tokens)
            }
            
        except Exception as e:
            logger.error(f"Erro ao detectar contexto: {str(e)}")
            return {
                "main_context": "educational",  # Contexto padrão
                "complexity_level": "basic",  # Nível padrão
                "error": str(e)
            }

    def _detect_language(self, text: str) -> str:
        """
        Detecta o idioma do texto.
        
        Args:
            text: Texto para detectar idioma
            
        Returns:
            Código do idioma detectado
        """
        try:
            return detect(text)
        except Exception as e:
            logger.error(f"Erro ao detectar idioma: {str(e)}")
            return "pt"  # Idioma padrão

if __name__ == "__main__":
    # Exemplo de uso
    engine = LearningEngine()
    
    # Aprende da web
    web_result = engine.learn_from_web("https://example.com")
    
    # Mostra resumo
    print(engine.get_learning_summary()) 