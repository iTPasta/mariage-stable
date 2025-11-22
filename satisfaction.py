"""Calcul des satisfactions pour étudiants et universités."""
from typing import Dict, List
import numpy as np

from models import StudentKey, UniversityKey


def satisfaction_etudiant(
    etudiant_key: StudentKey,
    preferences_etudiants: Dict[StudentKey, List[UniversityKey]],
    affectations: Dict[UniversityKey, List[StudentKey]],
) -> float:
    """
    Calcule la satisfaction d'un étudiant avec Normalized Rank Score.
    
    """
    prefs = preferences_etudiants[etudiant_key]
    m = len(prefs)

    # Trouver l'université d'affectation
    universite_key = None
    for uni, etus in affectations.items():
        if etudiant_key in etus:
            universite_key = uni
            break

    if universite_key is None:
        return 0.0

    if m == 1:
        return 1.0

    rang = prefs.index(universite_key) + 1
    sat = (m - rang) / (m - 1)
    return float(sat)


def satisfaction_etablissement(
    universite_key: UniversityKey,
    preferences_universites: Dict[UniversityKey, List[StudentKey]],
    affectations: Dict[UniversityKey, List[StudentKey]],
) -> float:
    """
    Calcule la satisfaction d'une université avec Normalized Rank Score.

    """
    prefs = preferences_universites[universite_key]
    affectes = affectations.get(universite_key, [])
    n = len(prefs)

    if len(affectes) == 0:
        return 0.0

    # Prendre le premier étudiant affecté (capacité=1 par défaut)
    etudiant_key = affectes[0]

    if etudiant_key not in prefs:
        return 0.0

    rang = prefs.index(etudiant_key) + 1

    if n == 1:
        return 1.0

    sat = (n - rang) / (n - 1)
    return float(sat)


def mesurer_satisfaction_globale(
    affectations: Dict[UniversityKey, List[StudentKey]],
    preferences_etudiants: Dict[StudentKey, List[UniversityKey]],
    preferences_universites: Dict[UniversityKey, List[StudentKey]],
    capacites: Dict[UniversityKey, int],
) -> Dict:

    satisf_etudiants: Dict[StudentKey, float] = {}
    satisf_universites: Dict[UniversityKey, float] = {}

    # Calculer satisfaction par étudiant
    for etu_key in preferences_etudiants:
        satisf_etudiants[etu_key] = satisfaction_etudiant(
            etu_key, preferences_etudiants, affectations
        )

    # Calculer satisfaction par université
    for uni_key in preferences_universites:
        satisf_universites[uni_key] = satisfaction_etablissement(
            uni_key, preferences_universites, affectations
        )

    return {
        "satisfactions_etudiants": satisf_etudiants,
        "satisfactions_universites": satisf_universites,
        "moyenne_etudiants": float(np.mean(list(satisf_etudiants.values()))),
        "moyenne_universites": float(np.mean(list(satisf_universites.values()))),
    }
