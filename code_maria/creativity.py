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

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CreativityEngine:
    """
    Motor de criatividade usando GPT para gerar conteúdo
    """
    
    def __init__(self):
        """Inicializa o motor de criatividade."""
        try:
            # Carrega chave da API OpenAI
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                logger.warning("Chave da API OpenAI não configurada. Algumas funcionalidades estarão indisponíveis.")
            
            # Configurações de criatividade
            self.creativity_level = 0.8
            self.difficulty_levels = ["iniciante", "intermediário", "avançado"]
            self.content_types = ["tutorial", "quiz", "code_example"]
            
            # Inicializa memória criativa
            self.creative_memory = []
            
            # Carrega templates
            self.templates = {
                "tutorial": {
                    "title": "Tutorial: {topic}",
                    "base": "# {title}\n\n## Introdução\n{intro}\n\n## Conceitos\n{concepts}\n\n## Exemplos\n{examples}\n\n## Exercícios\n{exercises}\n\n## Conclusão\n{conclusion}",
                    "sections": ["introdução", "conceitos", "exemplos", "exercícios", "conclusão"],
                    "section_names": {
                        "introdução": "Introdução",
                        "conceitos": "Conceitos",
                        "exemplos": "Exemplos",
                        "exercícios": "Exercícios",
                        "conclusão": "Conclusão"
                    }
                },
                "quiz": {
                    "title": "Quiz: {topic}",
                    "base": "# {title}\n\n{questions}",
                    "sections": ["questões", "alternativas", "respostas", "explicações"],
                    "section_names": {
                        "questões": "Questões",
                        "alternativas": "Alternativas",
                        "respostas": "Respostas",
                        "explicações": "Explicações"
                    },
                    "question_types": ["múltipla escolha", "verdadeiro/falso", "completar"]
                },
                "code_example": {
                    "title": "Exemplo de Código: {topic}",
                    "base": "# {title}\n\n## Descrição\n{description}\n\n## Código\n```{language}\n{code}\n```\n\n## Explicação\n{explanation}\n\n## Uso\n{usage}\n\n## Saída\n```\n{output}\n```",
                    "sections": ["descrição", "código", "explicação", "uso", "saída"],
                    "section_names": {
                        "descrição": "Descrição",
                        "código": "Código",
                        "explicação": "Explicação",
                        "uso": "Uso",
                        "saída": "Saída"
                    }
                }
            }
            
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
        
    def generate_content(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ) -> Dict[str, Any]:
        """
        Gera conteúdo usando GPT.
        
        Args:
            prompt: Prompt para geração
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura da amostragem
            top_p: Probabilidade acumulada para amostragem
            frequency_penalty: Penalidade de frequência
            presence_penalty: Penalidade de presença
            
        Returns:
            Dicionário com conteúdo gerado e métricas
            
        Raises:
            ValueError: Se os parâmetros forem inválidos
            RuntimeError: Se houver erro na API
        """
        try:
            # Verifica se a API está disponível
            if not self.api_key:
                return {
                    "content": "API OpenAI não configurada. Por favor, configure a chave da API.",
                    "tokens_used": 0,
                    "model": self.model,
                    "error": "API indisponível"
                }
            
            # Valida parâmetros
            if not prompt or not isinstance(prompt, str):
                raise ValueError("Prompt inválido")
                
            if not 0 <= temperature <= 2:
                raise ValueError("Temperature deve estar entre 0 e 2")
                
            if not 0 <= top_p <= 1:
                raise ValueError("Top_p deve estar entre 0 e 1")
                
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                raise ValueError("Max_tokens deve ser um inteiro positivo")
                
            # Prepara mensagens
            messages = [
                {"role": "system", "content": "Você é um assistente criativo e prestativo."},
                {"role": "user", "content": prompt}
            ]
            
            # Faz requisição
            start_time = time.time()
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            
            # Processa resposta
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
            # Atualiza métricas
            self._update_metrics(True, tokens)
            
            result = {
                "content": content,
                "tokens_used": tokens,
                "model": self.model,
                "time_taken": time.time() - start_time,
                "error": None
            }
            
            return result
            
        except openai.error.InvalidRequestError as e:
            logger.error(f"Erro de requisição inválida: {str(e)}")
            self._update_metrics(False)
            return {
                "content": None,
                "tokens_used": 0,
                "model": self.model,
                "error": f"Requisição inválida: {str(e)}"
            }
            
        except openai.error.AuthenticationError as e:
            logger.error(f"Erro de autenticação: {str(e)}")
            self._update_metrics(False)
            return {
                "content": None,
                "tokens_used": 0,
                "model": self.model,
                "error": "Erro de autenticação com a API"
            }
            
        except openai.error.RateLimitError as e:
            logger.error(f"Rate limit excedido: {str(e)}")
            self._update_metrics(False)
            return {
                "content": None,
                "tokens_used": 0,
                "model": self.model,
                "error": "Rate limit excedido, tente novamente mais tarde"
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo: {str(e)}")
            self._update_metrics(False)
            return {
                "content": None,
                "tokens_used": 0,
                "model": self.model,
                "error": str(e)
            }
            
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
    
    def generate_educational_content(
        self,
        topic: str,
        content_type: str = "tutorial",
        difficulty: str = "iniciante",
        language: str = "python",
        creative_level: float = 0.8
    ) -> Dict[str, Any]:
        """
        Gera conteúdo educacional personalizado.
        
        Args:
            topic: Tópico do conteúdo
            content_type: Tipo de conteúdo (tutorial, quiz, exemplo)
            difficulty: Nível de dificuldade
            language: Linguagem de programação
            creative_level: Nível de criatividade (0.0 a 1.0)
            
        Returns:
            Conteúdo educacional estruturado
            
        Raises:
            ValueError: Se o nível de dificuldade ou tipo de conteúdo for inválido
        """
        if difficulty not in self.difficulty_levels:
            raise ValueError(f"Nível de dificuldade inválido. Use: {self.difficulty_levels}")
        
        if content_type not in ["tutorial", "quiz", "code_example"]:
            raise ValueError("Tipo de conteúdo não suportado")
        
        try:
            if content_type == "tutorial":
                return self._generate_tutorial(topic, difficulty, language, creative_level)
            elif content_type == "quiz":
                return self._generate_quiz(topic, difficulty)
            else:  # code_example
                return self._generate_code_example(topic, language, difficulty)
                
        except Exception as e:
            logger.error(f"Erro na geração de conteúdo educacional: {str(e)}")
            return {"error": str(e)}
    
    def _generate_tutorial(
        self,
        topic: str,
        difficulty: str,
        language: str,
        creative_level: float
    ) -> Dict[str, Any]:
        """Gera um tutorial educacional."""
        template = self.templates["tutorial"]
        
        # Adapta objetivos baseado na dificuldade
        objectives = {
            "iniciante": "os conceitos básicos e fundamentos essenciais",
            "intermediário": "conceitos avançados e boas práticas",
            "avançado": "técnicas avançadas e otimizações"
        }
        
        tutorial = {
            "título": f"Tutorial de {topic} - Nível {difficulty}",
            "nível": difficulty,
            "linguagem": language,
            "seções": []
        }
        
        # Gera conteúdo para cada seção
        for section in template["sections"]:
            section_name = template["section_names"][section]
            content = self.generate_text(
                f"{section_name} sobre {topic} para nível {difficulty}",
                creative_level=creative_level
            )
            
            # Adiciona exemplos de código quando apropriado
            if section in ["exemplos", "exercícios"]:
                code = self._generate_code_snippet(topic, language, difficulty)
                tutorial["seções"].append({
                    "tipo": section,
                    "nome": section_name,
                    "conteúdo": content,
                    "código": code
                })
            else:
                tutorial["seções"].append({
                    "tipo": section,
                    "nome": section_name,
                    "conteúdo": content
                })
        
        return tutorial
    
    def _generate_quiz(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Gera um quiz educacional."""
        template = self.templates["quiz"]
        
        quiz = {
            "título": f"Quiz sobre {topic} - Nível {difficulty}",
            "nível": difficulty,
            "questões": []
        }
        
        # Número de questões baseado na dificuldade
        num_questions = {
            "iniciante": 5,
            "intermediário": 8,
            "avançado": 10
        }
        
        for i in range(num_questions[difficulty]):
            question_type = random.choice(template["question_types"])
            question = self._generate_question(topic, question_type, difficulty)
            quiz["questões"].append(question)
        
        return quiz
    
    def _generate_question(
        self,
        topic: str,
        question_type: str,
        difficulty: str
    ) -> Dict[str, Any]:
        """Gera uma questão para o quiz."""
        if question_type == "múltipla escolha":
            return {
                "tipo": question_type,
                "pergunta": self.generate_text(f"Pergunta sobre {topic}"),
                "alternativas": [
                    self.generate_text(f"Alternativa sobre {topic}")
                    for _ in range(4)
                ],
                "resposta_correta": 0  # Índice da resposta correta
            }
        elif question_type == "verdadeiro/falso":
            return {
                "tipo": question_type,
                "pergunta": self.generate_text(f"Afirmação sobre {topic}"),
                "resposta_correta": random.choice([True, False])
            }
        else:  # completar
            return {
                "tipo": question_type,
                "texto": self.generate_text(f"Texto com lacuna sobre {topic}"),
                "resposta_correta": self.generate_text("Resposta correta")
            }
    
    def _generate_code_example(
        self,
        topic: str,
        language: str,
        difficulty: str
    ) -> Dict[str, Any]:
        """
        Gera um exemplo de código com explicações.
        
        Args:
            topic: Tópico do exemplo
            language: Linguagem de programação
            difficulty: Nível de dificuldade
            
        Returns:
            Dicionário com o exemplo gerado
        """
        example = {
            "título": f"Exemplo de {topic} em {language}",
            "seções": [
                {
                    "tipo": "descrição",
                    "conteúdo": self._generate_description(topic, language, difficulty)
                },
                {
                    "tipo": "código",
                    "conteúdo": self._generate_code(topic, language, difficulty)
                },
                {
                    "tipo": "explicação",
                    "conteúdo": self._generate_explanation(topic, difficulty)
                },
                {
                    "tipo": "uso",
                    "conteúdo": self._generate_usage(topic, language)
                },
                {
                    "tipo": "saída",
                    "conteúdo": self._generate_output(topic, language)
                }
            ]
        }
        
        self.logger.info(f"Exemplo de código gerado para {topic} em {language}")
        return example
    
    def _generate_code_snippet(
        self,
        topic: str,
        language: str,
        difficulty: str
    ) -> str:
        """Gera um snippet de código educacional."""
        # Exemplos básicos para diferentes linguagens e dificuldades
        snippets = {
            "python": {
                "iniciante": """
def exemplo_basico():
    print("Olá, Mundo!")
    # Demonstração de conceito básico
    numeros = [1, 2, 3, 4, 5]
    for numero in numeros:
        print(numero)
""",
                "intermediário": """
class ExemploIntermediario:
    def __init__(self, valor):
        self.valor = valor
    
    def processa_valor(self):
        return [x * self.valor for x in range(5)]
""",
                "avançado": """
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class ExemploAvancado:
    valores: List[int]
    multiplicador: Optional[float] = 1.0
    
    def processa_valores(self) -> List[float]:
        return [v * self.multiplicador for v in self.valores]
"""
            }
        }
        
        return snippets.get(language, {}).get(difficulty, "# Código não disponível")
    
    def generate_text(
        self,
        prompt: str,
        max_length: int = 100,
        creative_level: float = None
    ) -> str:
        """
        Gera texto criativo baseado em um prompt.
        
        Args:
            prompt: Texto inicial para geração
            max_length: Tamanho máximo do texto gerado
            creative_level: Nível de criatividade (0.0 a 1.0)
            
        Returns:
            Texto gerado
            
        Raises:
            Exception: Se houver erro na geração do texto
        """
        try:
            # Ajusta temperatura baseado no nível de criatividade
            temperature = creative_level if creative_level is not None else self.creativity_level
            
            result = self.text_generator(
                prompt,
                max_length=max_length,
                num_return_sequences=1,
                temperature=temperature
            )[0]["generated_text"]
            
            self.creative_memory.append({
                "type": "text",
                "prompt": prompt,
                "result": result,
                "creative_level": temperature
            })
            
            return result
        except Exception as e:
            logger.error(f"Erro na geração de texto: {str(e)}")
            raise  # Re-lança a exceção para ser tratada pelo chamador
    
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

    def _generate_description(self, topic: str, language: str, difficulty: str) -> str:
        """
        Gera uma descrição para o exemplo de código.
        
        Args:
            topic: Tópico do exemplo
            language: Linguagem de programação
            difficulty: Nível de dificuldade
            
        Returns:
            Descrição gerada
        """
        return self.generate_text(
            f"Descrição sobre {topic} em {language} para nível {difficulty}",
            max_length=200
        )

    def _generate_code(self, topic: str, language: str, difficulty: str) -> str:
        """
        Gera o código do exemplo.
        
        Args:
            topic: Tópico do exemplo
            language: Linguagem de programação
            difficulty: Nível de dificuldade
            
        Returns:
            Código gerado
        """
        return self._generate_code_snippet(topic, language, difficulty)

    def _generate_explanation(self, topic: str, difficulty: str) -> str:
        """
        Gera uma explicação para o código.
        
        Args:
            topic: Tópico do exemplo
            difficulty: Nível de dificuldade
            
        Returns:
            Explicação gerada
        """
        return self.generate_text(
            f"Explicação sobre {topic} para nível {difficulty}",
            max_length=300
        )

    def _generate_usage(self, topic: str, language: str) -> str:
        """
        Gera exemplos de uso do código.
        
        Args:
            topic: Tópico do exemplo
            language: Linguagem de programação
            
        Returns:
            Exemplos de uso gerados
        """
        return self.generate_text(
            f"Exemplos de uso de {topic} em {language}",
            max_length=200
        )

    def _generate_output(self, topic: str, language: str) -> str:
        """
        Gera a saída esperada do código.
        
        Args:
            topic: Tópico do exemplo
            language: Linguagem de programação
            
        Returns:
            Saída esperada gerada
        """
        return self.generate_text(
            f"Saída esperada do exemplo de {topic} em {language}",
            max_length=150
        )

if __name__ == "__main__":
    # Exemplo de uso
    engine = CreativityEngine()
    
    # Gera um tutorial
    tutorial = engine.generate_educational_content(
        topic="Funções em Python",
        content_type="tutorial",
        difficulty="iniciante"
    )
    print(json.dumps(tutorial, indent=4, ensure_ascii=False)) 