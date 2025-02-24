"""
Módulo de Criatividade da CodeMaria
Responsável por gerar conteúdo criativo e educacional usando diferentes técnicas de IA.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from transformers import pipeline
import torch
import random
import json
from pathlib import Path
import openai
import os
import time
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CreativityEngine:
    """Motor de criatividade para gerar conteúdo contextualizado."""
    
    def __init__(self):
        """Inicializa o motor de criatividade."""
        try:
            nltk.download('punkt')
            nltk.download('stopwords')
            self.stop_words = set(stopwords.words('portuguese'))
            
            # Carrega chave da API OpenAI
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                logger.warning("Chave da API OpenAI não configurada. Algumas funcionalidades estarão indisponíveis.")
            
            # Configurações de criatividade
            self.creativity_level = 0.8
            self.difficulty_levels = ["basic", "intermediate", "advanced"]
            self.content_types = ["tutorial", "quiz", "code_example"]
            
            # Inicializa memória criativa
            self.creative_memory = []
            
            # Carrega templates
            self.templates = self._load_templates()
            
            # Inicializa gerador de texto
            if self.api_key:
                self.text_generator = pipeline(
                    "text-generation",
                    model="gpt2",
                    device="cuda" if torch.cuda.is_available() else "cpu"
                )
            else:
                logger.warning("CreativityEngine inicializado em modo limitado - API OpenAI indisponível")
                self.text_generator = None
            
            # Inicializa estatísticas
            self.stats = {
                "total_generations": 0,
                "successful_generations": 0,
                "failed_generations": 0,
                "avg_generation_time": 0.0
            }
            
            # Inicializa métricas
            self.metrics = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_tokens": 0,
                "average_tokens": 0.0
            }
            
        except Exception as e:
            logger.error(f"Erro na inicialização do CreativityEngine: {str(e)}")
            raise
        
    def _load_templates(self) -> Dict[str, List[str]]:
        """Carrega templates para diferentes tipos de conteúdo."""
        return {
            "educational": [
                "Vamos aprender sobre {topic}! {content}",
                "Aqui está um tutorial sobre {topic}: {content}",
                "Entenda {topic} passo a passo: {content}"
            ],
            "technical": [
                "Explicação técnica de {topic}: {content}",
                "Documentação sobre {topic}: {content}",
                "Guia técnico - {topic}: {content}"
            ],
            "cultural": [
                "Aspectos culturais de {topic}: {content}",
                "Explorando a cultura {topic}: {content}",
                "Tradições de {topic}: {content}"
            ],
            "geographic": [
                "Localização e características de {topic}: {content}",
                "Geografia de {topic}: {content}",
                "Aspectos geográficos de {topic}: {content}"
            ]
        }
        
    def generate_educational_content(
        self, 
        topic: str,
        difficulty: str = "basic",
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Gera conteúdo educacional contextualizado.
        """
        try:
            # Ajusta complexidade do conteúdo
            if difficulty == "basic":
                content = self._generate_basic_tutorial(topic, language)
            elif difficulty == "intermediate":
                content = self._generate_intermediate_tutorial(topic, language)
            else:
                content = self._generate_advanced_tutorial(topic, language)
                
            template = random.choice(self.templates["educational"])
            formatted_content = template.format(
                topic=topic,
                content=content
            )
            
            return {
                "content": formatted_content,
                "difficulty": difficulty,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo educacional: {str(e)}")
            return {"content": str(e)}
            
    def _generate_basic_tutorial(self, topic: str, language: str) -> str:
        """Gera tutorial básico."""
        return f"""
        Conceitos básicos de {topic}:
        1. O que é {topic}?
        2. Por que usar {topic}?
        3. Primeiros passos com {topic}
        4. Exemplo simples em {language}
        """
        
    def _generate_intermediate_tutorial(self, topic: str, language: str) -> str:
        """Gera tutorial intermediário."""
        return f"""
        Aprofundando em {topic}:
        1. Conceitos avançados
        2. Boas práticas
        3. Padrões comuns
        4. Exemplos práticos em {language}
        5. Exercícios sugeridos
        """
        
    def _generate_advanced_tutorial(self, topic: str, language: str) -> str:
        """Gera tutorial avançado."""
        return f"""
        Dominando {topic}:
        1. Arquitetura e design
        2. Otimização e performance
        3. Casos de uso avançados
        4. Implementação em {language}
        5. Projetos práticos
        6. Recursos adicionais
        """
        
    def _generate_code_example(
        self,
        topic: str,
        language: str = "python",
        difficulty: str = "basic"
    ) -> str:
        """Gera exemplo de código."""
        if language.lower() == "python":
            return self._generate_python_example(topic, difficulty)
        else:
            return f"Exemplo em {language} para {topic}"
            
    def _generate_python_example(self, topic: str, difficulty: str) -> str:
        """Gera exemplo em Python."""
        if difficulty == "basic":
            return f"""
            # Exemplo básico de {topic}
            def exemplo_{topic.lower()}():
                print("Olá! Este é um exemplo básico.")
                # Implementação básica aqui
                
            if __name__ == "__main__":
                exemplo_{topic.lower()}()
            """
        else:
            return f"""
            # Exemplo avançado de {topic}
            class Exemplo{topic.title()}:
                def __init__(self):
                    self.config = dict()
                    
                def processar(self, dados):
                    # Implementação avançada aqui
                    pass
                    
                def executar(self):
                    print("Executando exemplo avançado")
                    # Lógica principal aqui
                    
            if __name__ == "__main__":
                exemplo = Exemplo{topic.title()}()
                exemplo.executar()
            """
            
    def generate_text(
        self,
        prompt: str,
        creative_level: float = 0.5
    ) -> str:
        """
        Gera texto criativo baseado no prompt.
        
        Args:
            prompt: Texto base para geração
            creative_level: Nível de criatividade (0.0 a 1.0)
            
        Returns:
            Texto gerado
        """
        try:
            # Tokeniza e remove stopwords
            tokens = word_tokenize(prompt.lower())
            keywords = [
                token 
                for token in tokens 
                if token not in self.stop_words
            ]
            
            # Ajusta criatividade
            if creative_level < 0.3:
                # Mais formal e direto
                return f"Informações sobre {' '.join(keywords)}"
            elif creative_level < 0.7:
                # Balanceado
                return f"Explorando {' '.join(keywords)} de forma prática"
            else:
                # Mais criativo
                return f"Uma jornada fascinante por {' '.join(keywords)}"
                
        except Exception as e:
            logger.error(f"Erro ao gerar texto: {str(e)}")
            return str(e)
    
    def _update_metrics(self, success: bool, tokens: int = 0) -> None:
        """
        Atualiza métricas de uso.
        
        Args:
            success: Se a requisição foi bem sucedida
            tokens: Número de tokens usados
        """
        self.metrics["total_requests"] += 1
        
        if success:
            self.metrics["successful_requests"] += 1
            self.metrics["total_tokens"] += tokens
            self.metrics["average_tokens"] = (
                self.metrics["total_tokens"] / 
                self.metrics["successful_requests"]
            )
        else:
            self.metrics["failed_requests"] += 1
            
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas de uso.
        
        Returns:
            Dicionário com métricas
        """
        return {
            "total_requests": self.metrics["total_requests"],
            "successful_requests": self.metrics["successful_requests"],
            "failed_requests": self.metrics["failed_requests"],
            "total_tokens": self.metrics["total_tokens"],
            "average_tokens": round(self.metrics["average_tokens"], 2),
            "success_rate": round(
                (self.metrics["successful_requests"] / 
                self.metrics["total_requests"]) * 100 
                if self.metrics["total_requests"] > 0 else 0,
                2
            )
        }
    
    def get_creativity_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre a criatividade.
        
        Returns:
            Dict com estatísticas de criatividade
        """
        return {
            "total_creations": len(self.creative_memory),
            "creativity_level": self.creativity_level,
            "last_creation": self.creative_memory[-1] if self.creative_memory else None,
            "templates_available": list(self.templates.keys()),
            "difficulty_levels": self.difficulty_levels
        }

if __name__ == "__main__":
    # Exemplo de uso
    engine = CreativityEngine()
    
    # Gera um tutorial
    tutorial = engine.generate_educational_content(
        topic="Funções em Python",
        difficulty="basic"
    )
    print(json.dumps(tutorial, indent=4, ensure_ascii=False)) 