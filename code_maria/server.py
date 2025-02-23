"""
Servidor FastAPI da CodeMaria
"""

import os
from typing import Dict, Any, List, Optional, Union
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .core import CodeMaria
from .schemas import ProcessRequest, ProcessResponse, UserInfo
from .cache_manager import CacheManager
import time
import logging

app = FastAPI(
    title="CodeMarIA API",
    description="API da CodeMarIA - Assistente de Programação em Português",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância global da CodeMaria
code_maria = CodeMaria()

# Configuração do Cache
cache = CacheManager(ttl=3600)

logger = logging.getLogger(__name__)

class ProcessInput(BaseModel):
    """Modelo para entrada de processamento."""
    text: str
    type: str
    user_info: Optional[Union[UserInfo, None]] = None

# Middleware para métricas de performance
@app.middleware("http")
async def add_performance_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
async def root() -> Dict[str, str]:
    """Retorna informações básicas sobre a API."""
    return {
        "name": "CodeMarIA API",
        "version": "1.0.0",
        "status": "online"
    }

@app.post("/process")
async def process_input(request: ProcessRequest) -> ProcessResponse:
    """
    Processa uma entrada do usuário.
    
    Args:
        request: Objeto ProcessRequest com texto e informações do usuário
        
    Returns:
        Objeto ProcessResponse com a resposta processada
    """
    return code_maria.process_input(
        text=request.text,
        input_type=request.type,
        user_info=request.user_info
    )

@app.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Retorna estatísticas sobre a CodeMarIA."""
    return code_maria.get_stats()

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Faz upload de um arquivo PDF para processamento.
    
    Args:
        file: Arquivo PDF enviado
        
    Returns:
        Dicionário com resultado do processamento
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser PDF")
        
    try:
        # Salva o arquivo na pasta pdfs
        file_path = os.path.join("pdfs", file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Processa o PDF
        result = code_maria.learning_engine.pdf_processor.process_pdf(file_path)
        if result["error"]:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao processar PDF: {result['error']}"
            )
            
        # Analisa o texto extraído
        analysis = code_maria.learning_engine.pdf_processor.analyze_grammar(result["text"])
        
        return {
            "filename": file.filename,
            "size": len(content),
            "metadata": result["metadata"],
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-pdf-folder")
async def process_pdf_folder() -> List[Dict[str, Any]]:
    """
    Processa todos os PDFs na pasta pdfs.
    
    Returns:
        Lista com resultados do processamento de cada arquivo
    """
    try:
        folder_path = "pdfs"
        if not os.path.exists(folder_path):
            logger.error(f"Pasta {folder_path} não encontrada")
            raise HTTPException(
                status_code=404,
                detail=f"Pasta {folder_path} não encontrada"
            )
            
        results = code_maria.learning_engine.learn_from_pdfs(folder_path)
        if not results:
            logger.warning("Nenhum resultado retornado do processamento de PDFs")
            return []
            
        logger.info(f"PDFs processados com sucesso: {len(results)} arquivos")
        return results
        
    except Exception as e:
        logger.error(f"Erro ao processar pasta de PDFs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar PDFs: {str(e)}"
        )

@app.get("/pdf-stats")
async def get_pdf_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas sobre os PDFs processados.
    
    Returns:
        Dicionário com estatísticas dos PDFs
    """
    try:
        stats = code_maria.learning_engine.pdf_processor.get_processing_summary()
        if not stats:
            logger.warning("Nenhuma estatística disponível")
            return {"message": "Nenhuma estatística disponível"}
            
        logger.info("Estatísticas de PDFs recuperadas com sucesso")
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao recuperar estatísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao recuperar estatísticas: {str(e)}"
        )

@app.post("/train-pdfs")
async def train_pdfs(files: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Inicia treinamento com PDFs.
    
    Args:
        files: Lista opcional de arquivos específicos para treinar
        
    Returns:
        Resultado do treinamento
    """
    try:
        result = code_maria.pdf_trainer.train(files)
        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
            
        logger.info("Treinamento com PDFs concluído com sucesso")
        return result
        
    except Exception as e:
        logger.error(f"Erro no treinamento com PDFs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro no treinamento: {str(e)}"
        )

@app.get("/training-stats")
async def get_training_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas do treinamento com PDFs.
    
    Returns:
        Estatísticas detalhadas do treinamento
    """
    try:
        stats = code_maria.pdf_trainer.get_training_stats()
        if stats["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=stats["message"]
            )
            
        logger.info("Estatísticas de treinamento recuperadas com sucesso")
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao recuperar estatísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao recuperar estatísticas: {str(e)}"
        )

@app.post("/clear-training-history")
async def clear_training_history() -> Dict[str, Any]:
    """
    Limpa histórico de treinamento.
    
    Returns:
        Resultado da operação
    """
    try:
        result = code_maria.pdf_trainer.clear_history()
        if result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
            
        logger.info("Histórico de treinamento limpo com sucesso")
        return result
        
    except Exception as e:
        logger.error(f"Erro ao limpar histórico: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao limpar histórico: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("code_maria.server:app", host="0.0.0.0", port=8000, reload=True) 