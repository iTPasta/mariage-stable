# satisfaction.py
from typing import Dict, List
import numpy as np
from preferences import StudentKey, UniversityKey


ALPHA_ETUDIANT = 0.3
ALPHA_ETABLISSEMENT = 0.5  # Gardé pour extension éventuelle
CATEGORIES_ALPHA = {
    "flexible": 0.3,
    "moyen": 0.6,
    "exigeant": 0.9,
}


def satisfaction_etudiant(
    etudiant_key: StudentKey,
    preferences_etudiants: Dict[StudentKey, List[UniversityKey]],
    affectations: Dict[UniversityKey, List[StudentKey]],
    alpha: float = ALPHA_ETUDIANT,
) -> float:
    """
    Satisfaction exponentielle de l'étudiant :
        S = exp(-alpha * (rang - 1))
    rang = 1 → S = 1
    """
    prefs = preferences_etudiants[etudiant_key]
    m = len(prefs)

    # Trouver l'université où l'étudiant est affecté
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
    Satisfaction linéaire de l'université :
        S = 1 - (rang - 1) / (n - 1)
    en fonction du rang de l'étudiant affecté.
    Ici on prend le premier étudiant affecté (capacité = 1 par défaut).
    """
    prefs = preferences_universites[universite_key]
    affectes = affectations.get(universite_key, [])
    n = len(prefs)

    if len(affectes) == 0:
        return 0.0

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
):
    satisf_etudiants: Dict[StudentKey, float] = {}
    satisf_universites: Dict[UniversityKey, float] = {}

    for etu_key in preferences_etudiants:
        satisf_etudiants[etu_key] = satisfaction_etudiant(
            etu_key, preferences_etudiants, affectations, alpha_etu
        )

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
