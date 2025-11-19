"""Calcul des satisfactions pour étudiants et universités."""
from typing import Dict, List
import numpy as np

from models import StudentKey, UniversityKey
from config import AlphaCategories


ALPHA_ETUDIANT = AlphaCategories.FLEXIBLE


def satisfaction_etudiant(
    etudiant_key: StudentKey,
    preferences_etudiants: Dict[StudentKey, List[UniversityKey]],
    affectations: Dict[UniversityKey, List[StudentKey]],
    alpha: float = ALPHA_ETUDIANT,
) -> float:
    """
    Calcule la satisfaction exponentielle d'un étudiant.
    
    Formule: S = exp(-alpha * (rang - 1))
    - rang=1 (premier choix) → S = 1.0 (100% satisfait)
    - rang augmente → S diminue exponentiellement
    
    Args:
        etudiant_key: Nom de l'étudiant
        preferences_etudiants: Préférences des étudiants
        affectations: Affectations actuelles
        alpha: Paramètre de contrôle de la satisfaction
        
    Returns:
        Score de satisfaction entre 0 et 1
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
    sat = float(np.exp(-alpha * (rang - 1)))
    return sat


def satisfaction_etablissement(
    universite_key: UniversityKey,
    preferences_universites: Dict[UniversityKey, List[StudentKey]],
    affectations: Dict[UniversityKey, List[StudentKey]],
) -> float:
    """
    Calcule la satisfaction linéaire d'une université.
    
    Formule: S = 1 - (rang - 1) / (n - 1)
    - Le premier étudiant affecté est le plus satisfaisant
    - La satisfaction décroît linéairement avec le rang
    
    Args:
        universite_key: Nom de l'université
        preferences_universites: Préférences des universités
        affectations: Affectations actuelles
        
    Returns:
        Score de satisfaction entre 0 et 1
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

    sat = 1 - (rang - 1) / (n - 1)
    return float(sat)


def mesurer_satisfaction_globale(
    affectations: Dict[UniversityKey, List[StudentKey]],
    preferences_etudiants: Dict[StudentKey, List[UniversityKey]],
    preferences_universites: Dict[UniversityKey, List[StudentKey]],
    capacites: Dict[UniversityKey, int],
    alpha_etu: float = ALPHA_ETUDIANT,
) -> Dict:
    """
    Calcule la satisfaction globale de tous les acteurs.
    
    Args:
        affectations: Affectations actuelles
        preferences_etudiants: Préférences des étudiants
        preferences_universites: Préférences des universités
        capacites: Capacités des universités
        alpha_etu: Paramètre alpha pour satisfaction exponentielle
        
    Returns:
        Dictionnaire contenant:
        - satisfactions_etudiants: {étudiant: score}
        - satisfactions_universites: {université: score}
        - moyenne_etudiants: moyenne des satisfactions des étudiants
        - moyenne_universites: moyenne des satisfactions des universités
        - alpha_etudiant: paramètre alpha utilisé
    """
    satisf_etudiants: Dict[StudentKey, float] = {}
    satisf_universites: Dict[UniversityKey, float] = {}

    # Calculer satisfaction par étudiant
    for etu_key in preferences_etudiants:
        satisf_etudiants[etu_key] = satisfaction_etudiant(
            etu_key, preferences_etudiants, affectations, alpha_etu
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
        "alpha_etudiant": alpha_etu,
    }
