"""
Módulo de Treinamento com PDFs da CodeMaria
Responsável por gerenciar o treinamento usando documentos PDF.
"""

import logging
import concurrent.futures
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import os
import json
from datetime import datetime, timedelta
from .pdf_processor import PDFProcessor
from .learning import LearningEngine
import hashlib
import time
import shutil

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFTrainer:
    """Gerencia o treinamento usando documentos PDF."""
    
    def __init__(self, base_dir: str = "pdfs"):
        """
        Inicializa o treinador de PDFs.
        
        Args:
            base_dir: Diretório base contendo os PDFs
        """
        # Verifica e prepara ambiente
        self._check_environment()
        
        self.base_dir = Path(base_dir)
        self.training_dir = self.base_dir / "training"
        self.processed_dir = self.training_dir / "processed"
        self.failed_dir = self.training_dir / "failed"
        self.cache_dir = self.training_dir / "cache"
        
        self.pdf_processor = PDFProcessor()
        self.learning_engine = LearningEngine()
        self.training_history = []
        self.cache = {}
        self.cache_ttl = timedelta(hours=24)
        
        # Métricas de monitoramento
        self.metrics = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_processing_time": 0,
            "avg_processing_time": 0,
            "errors": {},
            "last_training": None,
            "sentiment_distribution": {},
            "grammar_stats": {
                "total_sentences": 0,
                "total_words": 0,
                "avg_sentence_length": 0
            }
        }
        
        # Cria estrutura de diretórios
        self._setup_directories()
        
        # Arquivos de histórico e cache
        self.history_file = self.training_dir / "training_history.json"
        self.cache_file = self.training_dir / "processing_cache.json"
        self.metrics_file = self.training_dir / "training_metrics.json"
        
        self._load_history()
        self._load_cache()
        self._load_metrics()
        
        logger.info(f"PDFTrainer inicializado em {base_dir}")
        
    def _check_environment(self) -> None:
        """Verifica e prepara o ambiente necessário."""
        try:
            import nltk
            required_packages = ['punkt', 'averaged_perceptron_tagger']
            for package in required_packages:
                try:
                    nltk.data.find(f'tokenizers/{package}')
                except LookupError:
                    logger.info(f"Baixando pacote NLTK: {package}")
                    nltk.download(package, quiet=True)
            
            # Verifica disponibilidade de GPU
            import torch
            if torch.cuda.is_available():
                logger.info("GPU disponível para processamento")
            else:
                logger.warning("GPU não disponível. Usando CPU para processamento")
                
        except Exception as e:
            logger.error(f"Erro na verificação do ambiente: {str(e)}")
            raise

    def _setup_directories(self) -> None:
        """Configura estrutura de diretórios necessária."""
        try:
            # Cria diretórios necessários
            dirs = [
                self.training_dir,
                self.training_dir / "processed",
                self.training_dir / "failed",
                self.training_dir / "cache"
            ]
            
            for dir_path in dirs:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Diretório criado/verificado: {dir_path}")
                
        except Exception as e:
            logger.error(f"Erro na configuração de diretórios: {str(e)}")
            raise

    def _load_history(self) -> None:
        """Carrega histórico de treinamento do arquivo."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.training_history = json.load(f)
                logger.info(f"Histórico carregado: {len(self.training_history)} registros")
        except Exception as e:
            logger.error(f"Erro ao carregar histórico: {str(e)}")
            self.training_history = []
            
    def _save_history(self) -> None:
        """Salva histórico de treinamento no arquivo."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_history, f, indent=2, ensure_ascii=False)
            logger.info("Histórico salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar histórico: {str(e)}")
            
    def _load_cache(self) -> None:
        """Carrega cache do arquivo."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    # Filtra entradas expiradas
                    now = datetime.now()
                    self.cache = {
                        k: v for k, v in cached_data.items()
                        if datetime.fromisoformat(v['cache_time']) + self.cache_ttl > now
                    }
                logger.info(f"Cache carregado: {len(self.cache)} entradas válidas")
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {str(e)}")
            self.cache = {}

    def _save_cache(self) -> None:
        """Salva cache no arquivo."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            logger.info("Cache salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {str(e)}")

    def _get_file_hash(self, file_path: str) -> str:
        """
        Calcula hash do arquivo para identificação no cache.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            String com hash do arquivo
        """
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Erro ao calcular hash: {str(e)}")
            return ""

    def _load_metrics(self) -> None:
        """Carrega métricas do arquivo."""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    self.metrics = json.load(f)
                logger.info("Métricas carregadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar métricas: {str(e)}")

    def _save_metrics(self) -> None:
        """Salva métricas no arquivo."""
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2, ensure_ascii=False)
            logger.info("Métricas salvas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar métricas: {str(e)}")

    def _update_metrics(self, result: Dict[str, Any], processing_time: float) -> None:
        """
        Atualiza métricas com base no resultado do processamento.
        
        Args:
            result: Resultado do processamento
            processing_time: Tempo de processamento em segundos
        """
        self.metrics["total_processed"] += 1
        self.metrics["total_processing_time"] += processing_time
        self.metrics["avg_processing_time"] = (
            self.metrics["total_processing_time"] / self.metrics["total_processed"]
        )
        self.metrics["last_training"] = datetime.now().isoformat()
        
        if result["status"] == "success":
            self.metrics["successful"] += 1
            
            # Atualiza distribuição de sentimento
            sentiment = result["sentiment"]["label"]
            self.metrics["sentiment_distribution"][sentiment] = (
                self.metrics["sentiment_distribution"].get(sentiment, 0) + 1
            )
            
            # Atualiza estatísticas gramaticais
            grammar = result["grammar_analysis"]
            self.metrics["grammar_stats"]["total_sentences"] += grammar["num_sentences"]
            self.metrics["grammar_stats"]["total_words"] += grammar["num_words"]
            self.metrics["grammar_stats"]["avg_sentence_length"] = (
                self.metrics["grammar_stats"]["total_words"] /
                self.metrics["grammar_stats"]["total_sentences"]
                if self.metrics["grammar_stats"]["total_sentences"] > 0 else 0
            )
        else:
            self.metrics["failed"] += 1
            error_type = type(result.get("error", "")).__name__
            self.metrics["errors"][error_type] = (
                self.metrics["errors"].get(error_type, 0) + 1
            )
        
        self._save_metrics()

    def _process_single_pdf(self, pdf_file: str) -> Dict[str, Any]:
        """
        Processa um único arquivo PDF com monitoramento.
        
        Args:
            pdf_file: Nome do arquivo PDF
            
        Returns:
            Dict com resultado do processamento
        """
        start_time = time.time()
        try:
            file_path = str(self.base_dir / pdf_file)
            
            # Validação do arquivo
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
                
            if not file_path.lower().endswith('.pdf'):
                raise ValueError(f"Arquivo não é um PDF: {file_path}")
                
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                raise ValueError(f"Arquivo vazio: {file_path}")
                
            # Verifica se arquivo está corrompido
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(4)
                    if header != b'%PDF':
                        raise ValueError(f"Arquivo PDF inválido: {file_path}")
            except Exception as e:
                raise ValueError(f"Erro ao ler arquivo: {str(e)}")
            
            file_hash = self._get_file_hash(file_path)
            
            # Verifica cache
            if file_hash and file_hash in self.cache:
                cached_result = self.cache[file_hash]
                cache_time = datetime.fromisoformat(cached_result['cache_time'])
                
                if cache_time + self.cache_ttl > datetime.now():
                    self.metrics["cache_hits"] += 1
                    logger.info(f"Usando resultado em cache para {pdf_file}")
                    return cached_result['result']
            
            self.metrics["cache_misses"] += 1
            
            # Processa normalmente se não estiver em cache
            result = self.pdf_processor.process_pdf(file_path)
            
            if result["error"]:
                processed_result = {
                    "file": pdf_file,
                    "timestamp": datetime.now().isoformat(),
                    "error": result["error"],
                    "status": "error"
                }
                # Move arquivo para pasta de falhas
                failed_path = self.failed_dir / pdf_file
                shutil.copy2(file_path, failed_path)
                logger.warning(f"Arquivo movido para {failed_path}")
            else:
                # Analisa conteúdo
                text = result["text"]
                metadata = result["metadata"]
                
                # Realiza análises
                grammar_analysis = self.pdf_processor.analyze_grammar(text)
                sentiment = self.learning_engine.analyze_sentiment(text[:5000])
                
                processed_result = {
                    "file": pdf_file,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": metadata,
                    "grammar_analysis": grammar_analysis,
                    "sentiment": sentiment,
                    "status": "success"
                }
                # Move arquivo para pasta processados
                processed_path = self.processed_dir / pdf_file
                shutil.copy2(file_path, processed_path)
                logger.info(f"Arquivo movido para {processed_path}")
            
            # Atualiza cache
            if file_hash:
                self.cache[file_hash] = {
                    'result': processed_result,
                    'cache_time': datetime.now().isoformat()
                }
                self._save_cache()
            
            # Atualiza métricas
            processing_time = time.time() - start_time
            self._update_metrics(processed_result, processing_time)
            
            return processed_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_result = {
                "file": pdf_file,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }
            self._update_metrics(error_result, processing_time)
            logger.error(f"Erro ao processar {pdf_file}: {str(e)}")
            
            # Move arquivo para pasta de falhas em caso de erro
            try:
                failed_path = self.failed_dir / pdf_file
                shutil.copy2(str(self.base_dir / pdf_file), str(failed_path))
                logger.warning(f"Arquivo movido para {failed_path}")
            except Exception as move_error:
                logger.error(f"Erro ao mover arquivo: {str(move_error)}")
            
            return error_result

    def _get_unique_pdfs(self) -> List[str]:
        """
        Retorna lista de PDFs únicos, ignorando arquivos com ' - Copia' no nome.
        
        Returns:
            Lista de nomes de arquivos PDF únicos
        """
        all_pdfs = [f.name for f in self.base_dir.glob("*.pdf")]
        unique_pdfs = []
        
        for pdf in all_pdfs:
            if " - Copia" not in pdf:
                unique_pdfs.append(pdf)
                
        return unique_pdfs

    def train(self, pdf_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Realiza treinamento com PDFs usando processamento paralelo.
        
        Args:
            pdf_files: Lista opcional de arquivos específicos para treinar.
                      Se None, usa todos os PDFs únicos do diretório.
                      
        Returns:
            Dict com resultados do treinamento
        """
        try:
            # Lista arquivos para treinamento
            if pdf_files:
                files_to_train = [
                    f for f in pdf_files 
                    if Path(self.base_dir / f).exists() and f.lower().endswith('.pdf')
                ]
            else:
                files_to_train = self._get_unique_pdfs()
                
            if not files_to_train:
                return {
                    "status": "error",
                    "message": "Nenhum arquivo PDF encontrado para treinamento"
                }
                
            logger.info(f"Iniciando treinamento paralelo com {len(files_to_train)} arquivos")
            
            # Processa arquivos em paralelo
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_file = {
                    executor.submit(self._process_single_pdf, pdf_file): pdf_file
                    for pdf_file in files_to_train
                }
                
                results = []
                for future in concurrent.futures.as_completed(future_to_file):
                    result = future.result()
                    results.append(result)
                    
                    if result["status"] == "success":
                        # Atualiza base de conhecimento
                        self.learning_engine.update_knowledge_base(
                            "pdf_training",
                            result
                        )
                    
                    # Adiciona ao histórico
                    self.training_history.append(result)
            
            # Salva histórico atualizado
            self._save_history()
            
            # Prepara resumo
            summary = {
                "total_files": len(files_to_train),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "error"]),
                "results": results
            }
            
            return {
                "status": "success",
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    def get_training_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do treinamento.
        
        Returns:
            Dict com estatísticas detalhadas
        """
        try:
            if not self.training_history:
                return {
                    "status": "info",
                    "message": "Nenhum treinamento realizado ainda"
                }
                
            # Calcula estatísticas
            total_files = len(self.training_history)
            successful = len([
                r for r in self.training_history 
                if r.get("status") == "success"
            ])
            failed = total_files - successful
            
            # Análise de sentimento
            sentiments = [
                r["sentiment"]["label"] 
                for r in self.training_history 
                if r.get("sentiment")
            ]
            sentiment_dist = {
                label: sentiments.count(label) 
                for label in set(sentiments)
            }
            
            # Análise gramatical
            grammar_stats = {
                "total_sentences": sum(
                    r["grammar_analysis"]["num_sentences"]
                    for r in self.training_history
                    if r.get("grammar_analysis")
                ),
                "total_words": sum(
                    r["grammar_analysis"]["num_words"]
                    for r in self.training_history
                    if r.get("grammar_analysis")
                ),
                "avg_sentence_length": sum(
                    r["grammar_analysis"]["avg_sentence_length"]
                    for r in self.training_history
                    if r.get("grammar_analysis")
                ) / successful if successful else 0
            }
            
            return {
                "status": "success",
                "statistics": {
                    "total_files": total_files,
                    "successful": successful,
                    "failed": failed,
                    "success_rate": (successful / total_files) * 100,
                    "sentiment_distribution": sentiment_dist,
                    "grammar_statistics": grammar_stats,
                    "last_training": self.training_history[-1]["timestamp"]
                        if self.training_history else None
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    def clear_history(self) -> Dict[str, Any]:
        """
        Limpa histórico de treinamento e cache.
        
        Returns:
            Dict indicando resultado da operação
        """
        try:
            # Limpa histórico
            self.training_history = []
            if self.history_file.exists():
                self.history_file.unlink()
                
            # Limpa cache
            self.cache = {}
            if self.cache_file.exists():
                self.cache_file.unlink()
                
            # Limpa métricas
            self.metrics = {
                "total_processed": 0,
                "successful": 0,
                "failed": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "total_processing_time": 0,
                "avg_processing_time": 0,
                "errors": {},
                "last_training": None,
                "sentiment_distribution": {},
                "grammar_stats": {
                    "total_sentences": 0,
                    "total_words": 0,
                    "avg_sentence_length": 0
                }
            }
            if self.metrics_file.exists():
                self.metrics_file.unlink()
            
            # Remove arquivos processados e falhas
            for file in self.processed_dir.glob("*"):
                file.unlink()
            for file in self.failed_dir.glob("*"):
                file.unlink()
            
            logger.info("Histórico de treinamento e cache limpos")
            return {
                "status": "success",
                "message": "Histórico e cache limpos com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao limpar histórico e cache: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            } 