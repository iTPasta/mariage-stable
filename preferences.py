# preferences.py
import random
from typing import Dict, List
from models import Student, University


StudentKey = str       # full_name de l'étudiant
UniversityKey = str    # name de l'université


def generer_preferences_etudiants(
    etudiants: List[Student],
    universites: List[University]
) -> Dict[StudentKey, List[UniversityKey]]:
    """
    Pour chaque étudiant, on crée une permutation aléatoire des universités.
    Clé = full_name, valeurs = liste des names d'universités.
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
    Pour chaque université, on crée une permutation aléatoire des étudiants.
    Clé = name, valeurs = liste des full_name étudiants.
    """
    preferences: Dict[UniversityKey, List[StudentKey]] = {}
    etu_names = [e.full_name for e in etudiants]

    for uni in universites:
        prefs = etu_names.copy()
        random.shuffle(prefs)
        preferences[uni.name] = prefs

    return preferences
