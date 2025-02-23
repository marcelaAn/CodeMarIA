"""
CodeMaria - Módulo Principal
Este módulo contém a classe principal da IA CodeMaria, responsável por coordenar
todas as funcionalidades e comportamentos.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeMaria:
    """Classe principal da IA CodeMaria."""
    
    def __init__(self):
        """Inicializa a CodeMaria com seus atributos base."""
        self.name = "CodeMaria"
        self.version = "0.1.0"
        self.creation_date = datetime.now()
        self.knowledge_base = {}
        self.active_learning = True
        self.personality_traits = {
            "empatia": 0.95,
            "acessibilidade": 0.90,
            "curiosidade": 0.95,
            "organização": 0.85,
            "criatividade": 0.90,
            "paciência": 0.95,
            "didática": 0.95,
            "brasilidade": 0.90
        }
        
        # Inicializa os módulos auxiliares
        self._initialize_modules()
        logger.info(f"{self.name} inicializada - Versão {self.version}")
    
    def _initialize_modules(self) -> None:
        """Inicializa os módulos auxiliares da CodeMaria."""
        try:
            # Importa os módulos necessários
            from .learning import LearningEngine
            from .creativity import CreativityEngine
            from .persona import Persona
            from .api_integrations import APIIntegrations
            from .pdf_trainer import PDFTrainer
            
            # Inicializa os módulos em ordem
            try:
                self.learning_engine = LearningEngine()
                logger.info("Motor de aprendizado inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar motor de aprendizado: {str(e)}")
                self.learning_engine = None
                
            try:
                self.creativity_engine = CreativityEngine()
                logger.info("Motor de criatividade inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar motor de criatividade: {str(e)}")
                self.creativity_engine = None
                
            try:
                self.persona = Persona()
                logger.info("Persona inicializada")
            except Exception as e:
                logger.error(f"Erro ao inicializar persona: {str(e)}")
                self.persona = None
                
            try:
                self.api_integrations = APIIntegrations()
                logger.info("Integrações de API inicializadas")
            except Exception as e:
                logger.error(f"Erro ao inicializar integrações de API: {str(e)}")
                self.api_integrations = None
            
            try:
                self.pdf_trainer = PDFTrainer()
                logger.info("PDFTrainer inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar PDFTrainer: {str(e)}")
                self.pdf_trainer = None
            
            # Verifica se os módulos essenciais foram inicializados
            if not self.learning_engine:
                raise RuntimeError("Falha ao inicializar o motor de aprendizado")
            
            logger.info("Todos os módulos auxiliares inicializados com sucesso")
            
        except ImportError as e:
            logger.error(f"Erro ao importar módulos: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao inicializar módulos: {str(e)}")
            raise
    
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa entrada de dados e retorna uma resposta apropriada.
        
        Args:
            input_data: Dicionário contendo os dados de entrada
            
        Returns:
            Dict contendo a resposta processada
        """
        try:
            logger.info("Processando entrada de dados")
            
            if not isinstance(input_data, dict):
                raise ValueError("Entrada deve ser um dicionário")
            
            input_type = input_data.get("type", "")
            user_info = input_data.get("user_info", {})
            
            # Define o estilo de resposta baseado no contexto
            context = input_data.get("text", "").lower()
            response_style = self.persona.get_response_style(context)
            
            # Processa diferentes tipos de entrada
            if input_type == "greeting":
                return self._process_greeting(input_data, response_style)
            elif input_type == "question":
                return self._process_question(input_data, response_style)
            elif input_type == "error_report":
                return self._process_error_report(input_data, response_style)
            else:
                return {
                    "status": "error",
                    "message": "Tipo de entrada não reconhecido"
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar entrada: {str(e)}")
            raise
    
    def _process_greeting(self, input_data: Dict[str, Any], style: Dict[str, float]) -> Dict[str, Any]:
        """Processa uma saudação."""
        user_info = input_data.get("user_info", {})
        nome = user_info.get("nome", "")
        
        return {
            "status": "success",
            "type": "greeting",
            "response": f"Olá, {nome}! Que bom ter você aqui!",
            "style": style
        }
    
    def _process_question(self, input_data: Dict[str, Any], style: Dict[str, float]) -> Dict[str, Any]:
        """Processa uma pergunta técnica."""
        try:
            # Gera resposta usando o motor de criatividade
            content = self.creativity_engine.generate_text(input_data["text"])
            
            # Prepara exemplos de código se necessário
            if "python" in input_data.get("topic", "").lower():
                code_example = self._generate_code_example(input_data["text"])
            else:
                code_example = None
            
            return {
                "status": "success",
                "type": "explanation",
                "response": content,
                "code_example": code_example,
                "style": style
            }
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _process_error_report(self, input_data: Dict[str, Any], style: Dict[str, float]) -> Dict[str, Any]:
        """Processa um relato de erro."""
        try:
            error_text = input_data.get("text", "")
            code = input_data.get("code", "")
            
            # Analisa o erro e gera solução
            error_type = self._identify_error_type(error_text)
            solution = self._generate_error_solution(error_type, code)
            
            return {
                "status": "success",
                "type": "error_solution",
                "error_type": error_type,
                "explanation": solution["explanation"],
                "solution": solution["suggestion"],
                "corrected_code": solution["corrected_code"],
                "style": style
            }
        except Exception as e:
            logger.error(f"Erro ao processar relato de erro: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _generate_code_example(self, topic: str) -> str:
        """Gera exemplo de código baseado no tópico."""
        # Implementação básica - pode ser expandida
        if "loop" in topic.lower() and "for" in topic.lower():
            return "for i in range(5):\n    print(i)"
        return ""
    
    def _identify_error_type(self, error_text: str) -> str:
        """Identifica o tipo de erro a partir do texto."""
        common_errors = {
            "IndexError": "index out of range",
            "TypeError": "can only concatenate",
            "NameError": "is not defined",
            "SyntaxError": "invalid syntax"
        }
        
        for error_type, pattern in common_errors.items():
            if pattern in error_text:
                return error_type
        
        return "UnknownError"
    
    def _generate_error_solution(self, error_type: str, code: str) -> Dict[str, str]:
        """Gera uma solução para o erro identificado."""
        solutions = {
            "IndexError": {
                "explanation": "Este erro ocorre quando tentamos acessar...",
                "suggestion": "Verifique se o índice não ultrapassa...",
                "corrected_code": "numbers = [1, 2, 3]\nif len(numbers) > 5:\n    print(numbers[5])"
            }
        }
        
        return solutions.get(error_type, {
            "explanation": "Erro não identificado",
            "suggestion": "Verifique a documentação",
            "corrected_code": code
        })
    
    def learn(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aprende com novos dados fornecidos.
        
        Args:
            data: Dados para aprendizado
            
        Returns:
            Dict indicando resultado do aprendizado
        """
        try:
            if not self.active_learning:
                return {"status": "inactive", "message": "Aprendizado desativado"}
            
            logger.info("Iniciando processo de aprendizado")
            
            if "user_input" in data:  # Aprendizado de interação
                return self._learn_from_interaction(data)
            elif "error_type" in data:  # Aprendizado de erro
                return self._learn_from_error(data)
            else:
                return {"status": "error", "message": "Tipo de dados não reconhecido"}
                
        except Exception as e:
            logger.error(f"Erro no processo de aprendizado: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _learn_from_interaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aprende a partir de uma interação."""
        try:
            # Extrai conceitos da interação
            concepts = self._extract_concepts(data["user_input"])
            
            # Atualiza base de conhecimento
            self.knowledge_base[data["topic"]] = self.knowledge_base.get(data["topic"], []) + concepts
            
            return {
                "status": "success",
                "learned_concepts": concepts,
                "confidence": 0.85
            }
        except Exception as e:
            logger.error(f"Erro ao aprender da interação: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _learn_from_error(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aprende a partir de um erro."""
        try:
            error_pattern = f"{data['error_type']}: {data['context']}"
            solution_pattern = data["solution_provided"]
            
            # Atualiza base de conhecimento de erros
            if "errors" not in self.knowledge_base:
                self.knowledge_base["errors"] = {}
            
            self.knowledge_base["errors"][error_pattern] = solution_pattern
            
            return {
                "status": "success",
                "error_pattern": error_pattern,
                "solution_pattern": solution_pattern,
                "confidence": 0.9
            }
        except Exception as e:
            logger.error(f"Erro ao aprender do erro: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extrai conceitos de um texto."""
        # Implementação básica - pode ser expandida
        concepts = []
        if "lista" in text.lower() or "array" in text.lower():
            concepts.append("listas")
        if "ordenar" in text.lower() or "sort" in text.lower():
            concepts.append("ordenação")
        if "python" in text.lower():
            concepts.append("python básico")
        return concepts
    
    def generate_creative_content(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera conteúdo criativo baseado em um prompt.
        
        Args:
            request: Dicionário com parâmetros para geração de conteúdo
            
        Returns:
            Conteúdo gerado
        """
        try:
            logger.info("Gerando conteúdo criativo")
            
            if isinstance(request, str):
                request = {"topic": request}
            
            # Define o estilo baseado no nível do usuário
            style = self.persona.get_response_style(request.get("level", "intermediário"))
            
            # Gera o conteúdo
            if request.get("format") == "tutorial":
                return self._generate_tutorial(request, style)
            else:
                return self._generate_general_content(request, style)
                
        except Exception as e:
            logger.error(f"Erro na geração de conteúdo: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _generate_tutorial(self, request: Dict[str, Any], style: Dict[str, float]) -> Dict[str, Any]:
        """Gera um tutorial educacional."""
        return {
            "title": f"Introdução a {request['topic'].title()}",
            "sections": [
                {"type": "explanation", "content": "Funções são blocos de código..."},
                {"type": "example", "code": "def saudacao(nome):\n    print(f'Olá, {nome}!')"},
                {"type": "exercise", "content": "Crie uma função que calcule..."}
            ],
            "style": style
        }
    
    def _generate_general_content(self, request: Dict[str, Any], style: Dict[str, float]) -> Dict[str, Any]:
        """Gera conteúdo geral."""
        return {
            "title": request["topic"],
            "content": self.creativity_engine.generate_text(request["topic"]),
            "style": style
        }
    
    def adapt_teaching_style(self, feedback: Dict[str, Any]) -> None:
        """
        Adapta o estilo de ensino baseado no feedback.
        
        Args:
            feedback: Dicionário com feedback do usuário
        """
        try:
            logger.info("Adaptando estilo de ensino")
            
            if feedback["comprehension"] < 0.7:
                # Ajusta para um estilo mais didático
                self.personality_traits["didática"] = min(1.0, self.personality_traits["didática"] + 0.05)
                self.personality_traits["técnico"] = max(0.5, self.personality_traits["técnico"] - 0.05)
            
            # Atualiza a persona
            self.persona.adapt_personality([{
                "feedback": "ajuste_estilo",
                "comprehension": feedback["comprehension"],
                "topic": feedback["topic"]
            }])
            
        except Exception as e:
            logger.error(f"Erro ao adaptar estilo de ensino: {str(e)}")
            raise
    
    def __str__(self) -> str:
        """Retorna uma representação string da CodeMaria."""
        return f"{self.name} v{self.version} - Professora de Programação"

if __name__ == "__main__":
    # Exemplo de uso
    maria = CodeMaria()
    print(maria) 