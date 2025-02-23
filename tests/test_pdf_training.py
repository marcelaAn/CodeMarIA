"""
Teste de treinamento com PDFs
"""

import os
import logging
from pathlib import Path
from code_maria.pdf_trainer import PDFTrainer

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_training():
    """Executa teste completo de treinamento."""
    
    # Configuração
    test_dir = Path("pdfs/training/test")
    trainer = PDFTrainer(str(test_dir))
    
    # Verifica diretório
    logger.info(f"Verificando diretório de teste: {test_dir}")
    if not test_dir.exists():
        logger.error(f"Diretório {test_dir} não encontrado")
        return
        
    # Lista PDFs disponíveis
    pdf_files = list(test_dir.glob("*.pdf"))
    logger.info(f"PDFs encontrados: {len(pdf_files)}")
    
    if not pdf_files:
        logger.warning("Nenhum PDF encontrado para teste")
        return
        
    # Executa treinamento
    logger.info("Iniciando treinamento...")
    result = trainer.train()
    
    # Analisa resultado
    if result["status"] == "error":
        logger.error(f"Erro no treinamento: {result['message']}")
        return
        
    summary = result["summary"]
    logger.info("\n=== Resumo do Treinamento ===")
    logger.info(f"Total de arquivos: {summary['total_files']}")
    logger.info(f"Processados com sucesso: {summary['successful']}")
    logger.info(f"Falhas: {summary['failed']}")
    
    # Analisa métricas
    metrics = trainer.metrics
    logger.info("\n=== Métricas de Processamento ===")
    logger.info(f"Tempo médio de processamento: {metrics['avg_processing_time']:.2f}s")
    logger.info(f"Cache hits: {metrics['cache_hits']}")
    logger.info(f"Cache misses: {metrics['cache_misses']}")
    
    if metrics["successful"] > 0:
        logger.info("\n=== Análise de Conteúdo ===")
        logger.info(f"Total de sentenças: {metrics['grammar_stats']['total_sentences']}")
        logger.info(f"Total de palavras: {metrics['grammar_stats']['total_words']}")
        logger.info(f"Tamanho médio de sentença: {metrics['grammar_stats']['avg_sentence_length']:.2f}")
        logger.info(f"Distribuição de sentimentos: {metrics['sentiment_distribution']}")
    
    if metrics["failed"] > 0:
        logger.info("\n=== Erros Encontrados ===")
        for error_type, count in metrics["errors"].items():
            logger.info(f"{error_type}: {count} ocorrências")

if __name__ == "__main__":
    test_training() 