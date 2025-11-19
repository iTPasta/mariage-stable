"""Génération des préférences pour étudiants et universités."""
import random
from typing import Dict, List

from models import Student, University, StudentKey, UniversityKey


def generer_preferences_etudiants(
    etudiants: List[Student],
    universites: List[University]
) -> Dict[StudentKey, List[UniversityKey]]:
    """
    Génère les préférences aléatoires pour chaque étudiant.
    
    Args:
        etudiants: Liste des étudiants
        universites: Liste des universités
        
    Returns:
        Dictionnaire {nom_etudiant: [liste_universites_ordonnees]}
    """
    preferences: Dict[StudentKey, List[UniversityKey]] = {}
    uni_names = [u.name for u in universites]

    for etu in etudiants:
        prefs = uni_names.copy()
        random.shuffle(prefs)
        preferences[etu.full_name] = prefs

    return preferences


def generer_preferences_universites(
    etudiants: List[Student],
    universites: List[University]
) -> Dict[UniversityKey, List[StudentKey]]:
    """
    Génère les préférences aléatoires pour chaque université.
    
    Args:
        etudiants: Liste des étudiants
        universites: Liste des universités
        
    Returns:
        Dictionnaire {nom_universite: [liste_etudiants_ordonnes]}
    """
    preferences: Dict[UniversityKey, List[StudentKey]] = {}
    etu_names = [e.full_name for e in etudiants]

    for uni in universites:
        prefs = etu_names.copy()
        random.shuffle(prefs)
        preferences[uni.name] = prefs

    return preferences
