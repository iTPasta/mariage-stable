"""Configuration centralisée de l'application."""
import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class DataConfig:
    """Configuration des données."""
    STUDENTS_CSV = os.path.join("data", "etudiants.csv")
    UNIVERSITIES_CSV = os.path.join("data", "universites.csv")


@dataclass
class AlphaCategories:
    """Catégories de paramètre alpha pour la satisfaction."""
    FLEXIBLE = 0.3
    MOYEN = 0.6
    EXIGEANT = 0.9
    
    @staticmethod
    def get_all() -> Dict[str, float]:
        return {
            "flexible": AlphaCategories.FLEXIBLE,
            "moyen": AlphaCategories.MOYEN,
            "exigeant": AlphaCategories.EXIGEANT,
        }


@dataclass
class UIConfig:
    """Configuration de l'interface utilisateur."""
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    DEFAULT_NB_STUDENTS = 10
    DEFAULT_NB_UNIVERSITIES = 10
    
    # Thème et couleurs
    BG_COLOR = "#f0f4f8"
    PRIMARY_COLOR = "#3b82f6"
    SECONDARY_COLOR = "#10b981"
    TEXT_COLOR = "#1f2937"
    WHITE = "white"
    GRAY = "#6b7280"
    
    # Fonts
    TITLE_FONT = ("Segoe UI", 24, "bold")
    SUBTITLE_FONT = ("Segoe UI", 12)
    HEADER_FONT = ("Segoe UI", 14, "bold")
    BUTTON_FONT = ("Segoe UI", 11, "bold")
    TEXT_FONT = ("Segoe UI", 10)
    SMALL_FONT = ("Segoe UI", 9)


@dataclass
class AppConfig:
    """Configuration globale de l'application."""
    DATA = DataConfig()
    ALPHA = AlphaCategories()
    UI = UIConfig()
