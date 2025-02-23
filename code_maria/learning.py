"""
Módulo de Aprendizado da CodeMaria
Responsável por implementar as estratégias de auto-aprendizado e evolução contínua.
"""

import logging
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from .pdf_processor import PDFProcessor
import os
import torch
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LearningEngine:
    """Motor de aprendizado da CodeMaria."""
    
    def __init__(self):
        """Inicializa o motor de aprendizado."""
        self.knowledge_base = {}
        self.learning_history = []
        
        # Configuração do modelo de sentimento
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if device == "cpu":
                torch.set_num_threads(4)  # Limita threads na CPU
            
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=device
            )
            logger.info(f"Analisador de sentimento inicializado usando {device}")
        except Exception as e:
            logger.error(f"Erro ao inicializar analisador de sentimento: {str(e)}")
            self.sentiment_analyzer = None
        
        self.pdf_processor = PDFProcessor()
        logger.info("Motor de aprendizado inicializado")
    
    def learn_from_web(self, url: str) -> Dict[str, Any]:
        """
        Extrai e aprende com conteúdo da web.
        
        Args:
            url: URL para extrair conteúdo
            
        Returns:
            Dicionário com informações extraídas
        """
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.get_text()
            
            # Análise básica do conteúdo
            sentiment = self.analyze_sentiment(content)
            
            learned_data = {
                "url": url,
                "content_length": len(content),
                "sentiment": sentiment,
                "timestamp": "auto_now"
            }
            
            self.learning_history.append(learned_data)
            return learned_data
            
        except Exception as e:
            logger.error(f"Erro ao aprender da web: {str(e)}")
            return {"error": str(e)}
    
    def learn_from_pdfs(self, folder_path: str) -> List[Dict[str, Any]]:
        """
        Aprende a partir de PDFs em uma pasta.
        
        Args:
            folder_path: Caminho para a pasta com PDFs
            
        Returns:
            Lista de resultados de aprendizado por arquivo
            
        Raises:
            FileNotFoundError: Se a pasta não existir
            ValueError: Se houver erro no processamento
        """
        try:
            if not os.path.exists(folder_path):
                raise FileNotFoundError(f"Pasta não encontrada: {folder_path}")
            
            # Processa os PDFs
            pdf_results = self.pdf_processor.process_pdf_folder(folder_path)
            
            # Analisa e armazena os resultados
            learning_results = []
            for result in pdf_results:
                try:
                    file_path = result["file_path"]
                    text = result["text"]
                    metadata = result["metadata"]
                    error = result["error"]
                    
                    if error:
                        logger.warning(f"Erro ao processar {file_path}: {error}")
                        continue
                    
                    # Analisa o texto extraído
                    analysis = self.pdf_processor.analyze_grammar(text)
                    sentiment = self.analyze_sentiment(text[:5000])  # Limita tamanho para análise
                    
                    learned_data = {
                        "file": os.path.basename(file_path),
                        "metadata": metadata,
                        "grammar_analysis": analysis,
                        "sentiment": sentiment,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    self.learning_history.append(learned_data)
                    learning_results.append(learned_data)
                    
                    # Atualiza a base de conhecimento
                    self.update_knowledge_base("pdf_learning", learned_data)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
                    learning_results.append({
                        "file": os.path.basename(file_path),
                        "error": str(e)
                    })
            
            return learning_results
            
        except Exception as e:
            logger.error(f"Erro ao aprender de PDFs: {str(e)}")
            raise ValueError(f"Erro ao processar PDFs: {str(e)}")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analisa o sentimento do texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Dicionário com scores de sentimento
            
        Raises:
            ValueError: Se o analisador não estiver disponível
        """
        try:
            if not self.sentiment_analyzer:
                raise ValueError("Analisador de sentimento não inicializado")
                
            if not text or not text.strip():
                return {"label": "NEUTRAL", "score": 0.5}
                
            result = self.sentiment_analyzer(text[:512])[0]
            return {
                "label": result["label"],
                "score": float(result["score"])
            }
        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {str(e)}")
            return {
                "error": str(e),
                "label": "ERROR",
                "score": 0.0
            }
    
    def update_knowledge_base(self, category: str, data: Any) -> bool:
        """
        Atualiza a base de conhecimento.
        
        Args:
            category: Categoria do conhecimento
            data: Dados para armazenar
            
        Returns:
            bool indicando sucesso da operação
        """
        try:
            if category not in self.knowledge_base:
                self.knowledge_base[category] = []
            self.knowledge_base[category].append(data)
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar base de conhecimento: {str(e)}")
            return False
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo do aprendizado.
        
        Returns:
            Dict com estatísticas de aprendizado
        """
        summary = {
            "total_entries": len(self.learning_history),
            "knowledge_categories": list(self.knowledge_base.keys()),
            "last_learning": self.learning_history[-1] if self.learning_history else None
        }
        
        # Adiciona estatísticas de PDFs se disponíveis
        if hasattr(self, 'pdf_processor'):
            pdf_stats = self.pdf_processor.get_processing_summary()
            summary["pdf_statistics"] = pdf_stats
            
        return summary

if __name__ == "__main__":
    # Exemplo de uso
    engine = LearningEngine()
    
    # Aprende da web
    web_result = engine.learn_from_web("https://example.com")
    
    # Aprende de PDFs
    pdf_results = engine.learn_from_pdfs("./pdfs")
    
    # Mostra resumo
    print(engine.get_learning_summary()) 