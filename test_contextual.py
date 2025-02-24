import unittest
from code_maria.core import CodeMaria
from code_maria.learning import LearningEngine
from code_maria.creativity import CreativityEngine
from code_maria.persona import Persona

class TestContextual(unittest.TestCase):
    """Testes para funcionalidades contextuais."""
    
    def setUp(self):
        """Configura ambiente de teste."""
        self.code_maria = CodeMaria()
        
    def test_educational_context(self):
        """Testa processamento de contexto educacional."""
        input_data = {
            "text": "Como aprender Python para iniciantes?",
            "user_info": {
                "linguagem_preferida": "python",
                "nivel": "iniciante"
            }
        }
        
        response = self.code_maria.process_input(input_data)
        
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["type"], "educational")
        self.assertIn("Python", response["response"])
        
    def test_technical_context(self):
        """Testa processamento de contexto técnico."""
        input_data = {
            "text": "Como implementar um decorator em Python?",
            "user_info": {
                "linguagem_preferida": "python",
                "nivel": "avançado"
            }
        }
        
        response = self.code_maria.process_input(input_data)
        
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["type"], "technical")
        self.assertIn("decorator", response["response"].lower())
        
    def test_cultural_context(self):
        """Testa processamento de contexto cultural."""
        input_data = {
            "text": "Qual a história da programação no Brasil?",
            "user_info": {
                "linguagem_preferida": "português",
                "nivel": "intermediário"
            }
        }
        
        response = self.code_maria.process_input(input_data)
        
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["type"], "cultural")
        self.assertIn("Brasil", response["response"])
        
    def test_geographic_context(self):
        """Testa processamento de contexto geográfico."""
        input_data = {
            "text": "Onde encontro cursos de programação em São Paulo?",
            "user_info": {
                "linguagem_preferida": "português",
                "nivel": "iniciante"
            }
        }
        
        response = self.code_maria.process_input(input_data)
        
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["type"], "geographic")
        self.assertIn("São Paulo", response["response"])
        
    def test_invalid_input(self):
        """Testa tratamento de entrada inválida."""
        input_data = "texto inválido"
        
        response = self.code_maria.process_input(input_data)
        
        self.assertEqual(response["status"], "error")
        self.assertIn("inválida", response["message"].lower())
        
    def test_response_style(self):
        """Testa ajuste de estilo da resposta."""
        input_data = {
            "text": "Me explique sobre classes em Python",
            "user_info": {
                "linguagem_preferida": "python",
                "nivel": "iniciante"
            }
        }
        
        response = self.code_maria.process_input(input_data)
        
        self.assertIn("style", response)
        self.assertIsInstance(response["style"], dict)
        self.assertIn("didático", response["style"])
        
    def test_context_analysis(self):
        """Testa análise de contexto."""
        input_data = {
            "text": "Como otimizar queries SQL?",
            "user_info": {
                "linguagem_preferida": "sql",
                "nivel": "avançado"
            }
        }
        
        response = self.code_maria.process_input(input_data)
        
        self.assertIn("context_analysis", response)
        self.assertIn("main_context", response["context_analysis"])
        self.assertIn("complexity_level", response["context_analysis"])
        
if __name__ == "__main__":
    unittest.main() 