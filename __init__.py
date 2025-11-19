"""
Système d'Affectation par Mariage Stable

Implémentation de l'algorithme de Gale-Shapley pour l'affectation 
étudiants-universités avec mesure de satisfaction.
"""

__version__ = "2.0.0"
__author__ = "iTaPasta"

from models import Student, University, SimulationData
from preferences import generer_preferences_etudiants, generer_preferences_universites
from matching import algorithme_affectation
from satisfaction import mesurer_satisfaction_globale

__all__ = [
    "Student",
    "University",
    "SimulationData",
    "generer_preferences_etudiants",
    "generer_preferences_universites",
    "algorithme_affectation",
    "mesurer_satisfaction_globale",
]
