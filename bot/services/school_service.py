from sqlalchemy.orm import Session
from typing import List, Optional

from bot.models.school import School
from bot.models.subscription import Subscription
from bot.models.statistics import Statistics
from bot.utils.validators import validate_school_name


class SchoolService:
    """Сервис для работы со школами"""

    def __init__(self, db: Session):
        self.db = db

    def add_school(self, name: str) -> Optional[School]:
        """Добавить школу"""
        if not validate_school_name(name):
            return None
        
        # Проверка на дубликат
        existing = self.get_school_by_name(name.strip())
        if existing:
            return None
        
        school = School(name=name.strip())
        self.db.add(school)
        
        # Создаем статистику для школы
        stats = Statistics(school_id=school.id)
        self.db.add(stats)
        
        self.db.commit()
        self.db.refresh(school)
        return school

    def delete_school(self, school_id: int) -> bool:
        """Удалить школу"""
        school = self.get_school(school_id)
        if not school:
            return False
        
        self.db.delete(school)
        self.db.commit()
        return True

    def get_all_schools(self) -> List[School]:
        """Получить все школы"""
        return self.db.query(School).order_by(School.name).all()

    def get_school(self, school_id: int) -> Optional[School]:
        """Получить школу по ID"""
        return self.db.query(School).filter(School.id == school_id).first()

    def get_school_by_name(self, name: str) -> Optional[School]:
        """Получить школу по названию"""
        return self.db.query(School).filter(School.name == name.strip()).first()

    def school_exists(self, school_id: int) -> bool:
        """Проверить существование школы"""
        return self.get_school(school_id) is not None
