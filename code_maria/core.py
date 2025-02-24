"""
CodeMaria - Módulo Principal
Este módulo contém a classe principal da IA CodeMaria, responsável por coordenar
todas as funcionalidades e comportamentos.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from nltk import word_tokenize

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
        Processa a entrada do usuário com base no contexto detectado.
        
        Args:
            input_data: Dicionário com texto e informações do usuário
            
        Returns:
            Dict com a resposta processada
        """
        try:
            # Valida entrada
            if not isinstance(input_data, dict) or "text" not in input_data:
                raise ValueError("Entrada inválida")
            
            text = input_data["text"]
            user_info = input_data.get("user_info", {})
            
            # Detecta contexto
            context_analysis = self.learning_engine._detect_user_input_context(text)
            main_context = context_analysis["main_context"]
            
            # Ajusta estilo de resposta
            style = self.persona.get_response_style(main_context)
            
            # Processa de acordo com o contexto
            if main_context == "educational":
                response = self._process_educational_request(
                    text, 
                    user_info, 
                    style,
                    context_analysis["complexity_level"]
                )
            elif main_context == "geographic":
                response = self._process_geographic_request(
                    text, 
                    user_info, 
                    style,
                    context_analysis["urgency_score"]
                )
            elif main_context == "technical":
                response = self._process_technical_request(
                    text, 
                    user_info, 
                    style,
                    context_analysis["context_scores"]["technical"]["subcategories"]
                )
            elif main_context == "cultural":
                response = self._process_cultural_request(
                    text, 
                    user_info, 
                    style,
                    context_analysis["context_scores"]["cultural"]["subcategories"]
                )
            
            # Ajusta resposta final
            final_response = self.persona.adjust_response(response["content"], main_context)
            
            # Aprende com a interação
            self.learn({
                "input": text,
                "context": context_analysis,
                "response": final_response,
                "user_info": user_info
            })
            
            return {
                "status": "success",
                "type": main_context,
                "response": final_response,
                "style": style,
                "context_analysis": context_analysis
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar entrada: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _process_educational_request(
        self, 
        text: str, 
        user_info: Dict[str, Any], 
        style: Dict[str, float],
        complexity: str
    ) -> Dict[str, Any]:
        """
        Processa requisições educacionais.
        """
        try:
            # Ajusta nível de complexidade
            if complexity == "basic":
                style["didático"] = min(1.0, style["didático"] + 0.1)
                style["técnico"] = max(0.3, style["técnico"] - 0.1)
            elif complexity == "advanced":
                style["técnico"] = min(1.0, style["técnico"] + 0.1)
                style["didático"] = max(0.5, style["didático"] - 0.1)
            
            # Gera conteúdo educacional
            content = self.creativity_engine.generate_educational_content(
                topic=text,
                difficulty=complexity,
                language=user_info.get("linguagem_preferida", "python")
            )
            
            return {
                "content": content["content"],
                "style": style
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar requisição educacional: {str(e)}")
            return {"content": str(e)}
    
    def _process_geographic_request(
        self, 
        text: str, 
        user_info: Dict[str, Any], 
        style: Dict[str, float],
        urgency: int
    ) -> Dict[str, Any]:
        """
        Processa requisições geográficas.
        """
        try:
            # Extrai termos geográficos do texto
            words = word_tokenize(text.lower())
            geo_terms = [w for w in words if w[0].isupper() or w in ["onde", "em"]]
            
            # Ajusta estilo baseado na urgência
            if urgency > 2:
                style["formal"] = min(1.0, style["formal"] + 0.2)
                style["preciso"] = min(1.0, style["preciso"] + 0.2)
            
            # Gera resposta mantendo os termos geográficos
            content = self.creativity_engine.generate_text(
                prompt=text,
                creative_level=0.6
            )
            
            # Garante que os termos geográficos estejam na resposta
            for term in geo_terms:
                if term not in content.lower():
                    content = f"Explorando {text} de forma prática\n\n{content}"
            
            return {
                "content": content,
                "style": style
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar requisição geográfica: {str(e)}")
            return {"content": str(e)}
    
    def _process_technical_request(
        self, 
        text: str, 
        user_info: Dict[str, Any], 
        style: Dict[str, float],
        technical_scores: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Processa requisições técnicas.
        """
        try:
            # Ajusta estilo baseado nas subcategorias
            if technical_scores.get("programming", 0) > technical_scores.get("concepts", 0):
                style["técnico"] = min(1.0, style["técnico"] + 0.2)
                content = self.creativity_engine._generate_code_example(
                    topic=text,
                    language=user_info.get("linguagem_preferida", "python"),
                    difficulty="intermediate"
                )
            else:
                style["didático"] = min(1.0, style["didático"] + 0.1)
                content = self.creativity_engine.generate_text(
                    prompt=text,
                    creative_level=0.7
                )
            
            return {
                "content": content,
                "style": style
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar requisição técnica: {str(e)}")
            return {"content": str(e)}
    
    def _process_cultural_request(
        self, 
        text: str, 
        user_info: Dict[str, Any], 
        style: Dict[str, float],
        cultural_scores: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Processa requisições culturais.
        """
        try:
            # Extrai termos culturais do texto preservando capitalização
            words = word_tokenize(text)
            cultural_terms = [w for w in words if w[0].isupper() or w.lower() in ["história", "cultura", "arte"]]
            
            # Ajusta estilo baseado nas subcategorias
            if cultural_scores.get("history", 0) > cultural_scores.get("arts", 0):
                style["formal"] = min(1.0, style["formal"] + 0.1)
            else:
                style["informal"] = min(1.0, style["informal"] + 0.1)
            
            # Gera resposta mantendo os termos culturais
            content = self.creativity_engine.generate_text(
                prompt=text,
                creative_level=0.9
            )
            
            # Garante que os termos culturais estejam na resposta com a capitalização correta
            for term in cultural_terms:
                if term not in content:
                    content = f"Uma jornada fascinante por {text}\n\n{content}"
            
            return {
                "content": content,
                "style": style
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar requisição cultural: {str(e)}")
            return {"content": str(e)}
    
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