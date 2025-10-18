# skills/calculator.py
"""
Compétence calculatrice
"""
import re
import math
import logging
from typing import Dict, Any, Optional

from ml import TrainingData
from .base_skill import BaseSkill, SkillResponse


class Calculator(BaseSkill, TrainingData):
    """Calculatrice mathématique"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__("calculator", "Calculatrice mathématique")
        self.logger = logger or logging.getLogger(__name__)

        self.safe_functions = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'pi': math.pi,
            'e': math.e
        }

    def execute(self, **kwargs) -> SkillResponse:
        """Exécute un calcul"""
        intent = kwargs.get('intent', '')
        message = kwargs.get('message', '')
        entities = kwargs.get('entities', {})

        expression = entities.get("expression", "")
        if not expression:
            expression = self._extract_expression(message)

        if not expression:
            return SkillResponse(
                success=False,
                message="❌ Je n'ai pas trouvé d'expression à calculer. Exemple: 'calcule 5 + 3'"
            )

        try:
            result = self._safe_eval(expression)
            return SkillResponse(
                success=True,
                message=f"🧮 {expression} = **{result}**",
                data={"expression": expression, "result": result}
            )

        except Exception as e:
            self.logger.error(f"Erreur calcul: {e}")
            return SkillResponse(
                success=False,
                message=f"❌ Erreur de calcul : {str(e)}"
            )

    def _extract_expression(self, text: str) -> str:
        """Extrait l'expression mathématique"""
        text = re.sub(r'calculer|calcule|combien fait', '', text, flags=re.IGNORECASE)
        expression = ''.join(re.findall(r'[0-9+\-*/().\s\w]', text))
        return re.sub(r'\s+', ' ', expression).strip()

    def _safe_eval(self, expression: str):
        """Évalue l'expression de manière sécurisée"""
        if not re.match(r'^[\d+\-*/().\s\w]+$', expression):
            raise ValueError("Expression non valide")

        for func_name, func in self.safe_functions.items():
            if func_name in expression and not callable(func):
                expression = expression.replace(func_name, str(func))

        allowed_names = {**self.safe_functions, '__builtins__': {}}

        try:
            result = eval(expression, allowed_names)

            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)

            return result

        except ZeroDivisionError:
            raise ValueError("Division par zéro")
        except Exception as e:
            raise ValueError(f"Erreur d'évaluation: {str(e)}")

    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        return intent == "calculation"