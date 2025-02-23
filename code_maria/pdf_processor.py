"""
Módulo de Processamento de PDFs da CodeMaria
Responsável por extrair e analisar conteúdo de arquivos PDF.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from PyPDF2 import PdfReader
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, mac_morpho
from nltk.probability import FreqDist
from fastapi import HTTPException
import fitz  # PyMuPDF
from pathlib import Path

# Download dos recursos necessários do NLTK
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('mac_morpho')  # Corpus em português
nltk.download('averaged_perceptron_tagger')

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Processa arquivos PDF para extração de texto e metadados
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Inicializa o processador de PDFs.
        
        Args:
            cache_dir: Diretório para cache de PDFs processados
            
        Raises:
            ValueError: Se o diretório de cache for inválido
        """
        if cache_dir:
            cache_dir = os.path.abspath(cache_dir)
            if not os.path.exists(cache_dir):
                try:
                    os.makedirs(cache_dir)
                except Exception as e:
                    raise ValueError(f"Erro ao criar diretório de cache: {str(e)}")
                    
        self.cache_dir = cache_dir
        self.processed_files = []
        self.grammar_stats = {}
        
        # Inicializa recursos do NLTK
        try:
            self.stopwords = set(stopwords.words('portuguese'))
            # Treina o tagger com o corpus em português
            self.tagger = nltk.UnigramTagger(mac_morpho.tagged_sents())
            self.tagger = nltk.BigramTagger(mac_morpho.tagged_sents(), backoff=self.tagger)
        except Exception as e:
            logger.error(f"Erro ao carregar recursos NLTK: {str(e)}")
            self.stopwords = set()
            self.tagger = None
            
        logger.info(f"PDFProcessor inicializado com cache em: {cache_dir}")
        
    def process_pdf(self, file_path: str) -> Dict:
        """
        Processa um arquivo PDF.
        
        Args:
            file_path: Caminho do arquivo PDF
            
        Returns:
            Dicionário com texto e metadados extraídos
            
        Raises:
            FileNotFoundError: Se o arquivo não existir
            ValueError: Se o arquivo não for um PDF válido
        """
        try:
            # Valida arquivo
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
                
            if not file_path.lower().endswith('.pdf'):
                raise ValueError(f"Arquivo não é um PDF: {file_path}")
                
            # Abre documento
            doc = fitz.open(file_path)
            
            # Extrai metadados
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "keywords": doc.metadata.get("keywords", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "pages": len(doc),
                "file_size": os.path.getsize(file_path)
            }
            
            # Extrai texto
            text = ""
            for page in doc:
                try:
                    text += page.get_text()
                except Exception as e:
                    logger.warning(f"Erro ao extrair texto da página {page.number}: {str(e)}")
                    continue
                    
            doc.close()
            
            # Realiza análise gramatical
            grammar_analysis = self.analyze_grammar(text)
            
            result = {
                "file_path": file_path,
                "metadata": metadata,
                "text": text,
                "grammar_analysis": grammar_analysis,
                "error": None
            }
            
            # Adiciona à lista de arquivos processados
            self.processed_files.append(os.path.basename(file_path))
            
            # Cache resultado se configurado
            if self.cache_dir:
                self._cache_result(file_path, result)
                
            return result
            
        except fitz.FileDataError as e:
            logger.error(f"PDF inválido ou corrompido: {file_path} - {str(e)}")
            return {
                "file_path": file_path,
                "metadata": {},
                "text": "",
                "error": f"PDF inválido ou corrompido: {str(e)}"
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar PDF {file_path}: {str(e)}")
            return {
                "file_path": file_path,
                "metadata": {},
                "text": "",
                "error": str(e)
            }
            
    def process_pdf_folder(self, folder_path: str) -> List[Dict]:
        """
        Processa todos os PDFs em uma pasta.
        
        Args:
            folder_path: Caminho da pasta
            
        Returns:
            Lista com resultados do processamento
            
        Raises:
            FileNotFoundError: Se a pasta não existir
        """
        try:
            # Valida pasta
            if not os.path.exists(folder_path):
                raise FileNotFoundError(f"Pasta não encontrada: {folder_path}")
                
            if not os.path.isdir(folder_path):
                raise ValueError(f"Caminho não é uma pasta: {folder_path}")
                
            # Lista PDFs
            pdf_files = [
                f for f in os.listdir(folder_path)
                if f.lower().endswith('.pdf')
            ]
            
            if not pdf_files:
                logger.warning(f"Nenhum PDF encontrado em: {folder_path}")
                return []
                
            logger.info(f"Processando {len(pdf_files)} PDFs em: {folder_path}")
            
            # Processa cada PDF
            results = []
            for pdf_file in pdf_files:
                file_path = os.path.join(folder_path, pdf_file)
                try:
                    result = self.process_pdf(file_path)
                    results.append(result)
                    
                    if result["error"]:
                        logger.warning(
                            f"PDF {pdf_file} processado com erro: {result['error']}"
                        )
                    else:
                        logger.info(f"PDF processado com sucesso: {pdf_file}")
                        
                except Exception as e:
                    logger.error(f"Erro ao processar {pdf_file}: {str(e)}")
                    results.append({
                        "file_path": file_path,
                        "metadata": {},
                        "text": "",
                        "error": str(e)
                    })
                    
            return results
            
        except Exception as e:
            logger.error(f"Erro ao processar pasta {folder_path}: {str(e)}")
            raise
            
    def _cache_result(self, file_path: str, result: Dict) -> None:
        """
        Salva resultado no cache.
        
        Args:
            file_path: Caminho do arquivo original
            result: Resultado do processamento
        """
        if not self.cache_dir:
            return
            
        try:
            # Gera nome do arquivo de cache
            cache_file = os.path.join(
                self.cache_dir,
                f"{Path(file_path).stem}.json"
            )
            
            # Salva resultado
            import json
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
            logger.debug(f"Resultado salvo em cache: {cache_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {str(e)}")
    
    def analyze_grammar(self, text: str) -> Dict[str, Any]:
        """
        Analisa aspectos gramaticais do texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Dicionário com estatísticas gramaticais
        """
        try:
            if not text or not text.strip():
                return {
                    "num_sentences": 0,
                    "num_words": 0,
                    "num_unique_words": 0,
                    "avg_sentence_length": 0,
                    "most_common_words": {},
                    "pos_distribution": {}
                }

            # Tokenização
            sentences = sent_tokenize(text)
            words = word_tokenize(text.lower())
            
            # Remoção de stopwords
            words_no_stop = [w for w in words if w not in self.stopwords]
            
            # Análise de frequência
            freq_dist = FreqDist(words_no_stop)
            
            # Part-of-speech tagging
            pos_tags = []
            try:
                if self.tagger:
                    pos_tags = self.tagger.tag(words_no_stop)
                else:
                    # Fallback para o tagger padrão se o tagger em português falhar
                    pos_tags = nltk.pos_tag(words_no_stop)
                    logger.warning("Usando tagger padrão em inglês devido a erro no tagger em português")
            except Exception as e:
                logger.error(f"Erro no POS tagging: {str(e)}")
            
            stats = {
                "num_sentences": len(sentences),
                "num_words": len(words),
                "num_unique_words": len(set(words_no_stop)),
                "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
                "most_common_words": dict(freq_dist.most_common(10)),
                "pos_distribution": self._count_pos_tags(pos_tags)
            }
            
            # Atualiza estatísticas globais
            self.grammar_stats[text[:50]] = stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro na análise gramatical: {str(e)}")
            return {
                "num_sentences": 0,
                "num_words": 0,
                "num_unique_words": 0,
                "avg_sentence_length": 0,
                "most_common_words": {},
                "pos_distribution": {},
                "error": str(e)
            }
    
    def _count_pos_tags(self, pos_tags: List[tuple]) -> Dict[str, int]:
        """
        Conta a frequência de cada tipo gramatical.
        
        Args:
            pos_tags: Lista de tuplas (palavra, tipo)
            
        Returns:
            Dicionário com contagem de tipos gramaticais
        """
        pos_counts = {}
        for _, tag in pos_tags:
            pos_counts[tag] = pos_counts.get(tag, 0) + 1
        return pos_counts
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo do processamento.
        
        Returns:
            Dict com estatísticas de processamento
        """
        return {
            "total_files_processed": len(self.processed_files),
            "processed_files": self.processed_files,
            "grammar_statistics": self.grammar_stats
        }

if __name__ == "__main__":
    # Exemplo de uso
    processor = PDFProcessor()
    results = processor.process_pdf_folder("./pdfs")
    print(processor.get_processing_summary()) 