# skills/time_skill.py
"""
Compétence temps et date
"""
import datetime
import logging
import random
from typing import Dict, Any, Optional
from .base_skill import BaseSkill, SkillResponse


class TimeSkill(BaseSkill):
    """Donne l'heure et la date"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__("time_skill", "Informations sur le temps")
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, **kwargs) -> SkillResponse:
        """Donne l'heure ou la date"""
        message = kwargs.get('message', '').lower()
        now = datetime.datetime.now()

        if "heure" in message:
            return self._get_time(now)
        elif "date" in message:
            return self._get_date(now)
        else:
            return self._get_full_datetime(now)

    def _get_time(self, now: datetime.datetime) -> SkillResponse:
        """Retourne l'heure"""
        time_str = now.strftime('%Hh%M')
        return SkillResponse(
            success=True,
            message=f"🕐 Il est {time_str}",
            data={"time": time_str}
        )

    def _get_date(self, now: datetime.datetime) -> SkillResponse:
        """Retourne la date"""
        date_str = now.strftime('%d/%m/%Y')
        return SkillResponse(
            success=True,
            message=f"📅 Nous sommes le {date_str}",
            data={"date": date_str}
        )

    def _get_full_datetime(self, now: datetime.datetime) -> SkillResponse:
        """Retourne l'heure et la date"""
        full_str = now.strftime('%d/%m/%Y à %Hh%M')
        return SkillResponse(
            success=True,
            message=f"📅 {full_str}",
            data={"datetime": full_str}
        )

    def can_handle(self, intent: str, entities: Dict[str, Any]) -> bool:
        return intent == "time"