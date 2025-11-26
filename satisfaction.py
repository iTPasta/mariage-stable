"""Calcul des satisfactions pour étudiants et universités."""
from typing import Dict, List
import numpy as np
import math

from models import StudentKey, UniversityKey


def satisfaction_etudiant(
    etudiant_key: StudentKey,
    preferences_etudiants: Dict[StudentKey, List[UniversityKey]],
    affectations: Dict[UniversityKey, List[StudentKey]],
) -> float:
    """
    Calcule la satisfaction d'un étudiant avec la formule normalisée.
    S = 1 - (r-1)/(n-1) où r est le rang obtenu et n le nombre de choix.
    """
    prefs = preferences_etudiants[etudiant_key]
    n = len(prefs)

    # Trouver l'université d'affectation
    universite_key = None
    for uni, etus in affectations.items():
        if etudiant_key in etus:
            universite_key = uni
            break

    if universite_key is None:
        return 0.0

    if n == 1:
        return 1.0

    rang = prefs.index(universite_key) + 1
    sat = 1 - (rang - 1) / (n - 1)
    return float(sat)


def satisfaction_etablissement(
    universite_key: UniversityKey,
    preferences_universites: Dict[UniversityKey, List[StudentKey]],
    affectations: Dict[UniversityKey, List[StudentKey]],
) -> float:
    """
    Calcule la satisfaction d'une université avec la formule normalisée.
    S = 1 - (r-1)/(n-1) où r est le rang obtenu et n le nombre de choix.
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


def calculer_rang_moyen_etudiants(
    affectations: Dict[UniversityKey, List[StudentKey]],
    preferences_etudiants: Dict[StudentKey, List[UniversityKey]],
) -> float:
    """
    Calcule le rang moyen obtenu par les étudiants (demandeurs/proposants).
    Rang 1 = premier choix, rang n = dernier choix.
    """
    rangs = []
    
    for etu_key in preferences_etudiants:
        prefs = preferences_etudiants[etu_key]
        
        # Trouver l'université d'affectation
        universite_key = None
        for uni, etus in affectations.items():
            if etu_key in etus:
                universite_key = uni
                break
        
        if universite_key is not None and universite_key in prefs:
            rang = prefs.index(universite_key) + 1
            rangs.append(rang)
    
    return float(np.mean(rangs)) if rangs else 0.0


def calculer_rang_moyen_etablissements(
    affectations: Dict[UniversityKey, List[StudentKey]],
    preferences_universites: Dict[UniversityKey, List[StudentKey]],
) -> float:
    """
    Calcule le rang moyen obtenu par les établissements (receveurs).
    Rang 1 = premier choix, rang n = dernier choix.
    """
    rangs = []
    
    for uni_key in preferences_universites:
        prefs = preferences_universites[uni_key]
        affectes = affectations.get(uni_key, [])
        
        if len(affectes) > 0:
            etudiant_key = affectes[0]  # Premier étudiant affecté
            
            if etudiant_key in prefs:
                rang = prefs.index(etudiant_key) + 1
                rangs.append(rang)
    
    return float(np.mean(rangs)) if rangs else 0.0


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

    # Calculer rangs moyens
    rang_moyen_etu = calculer_rang_moyen_etudiants(affectations, preferences_etudiants)
    rang_moyen_etab = calculer_rang_moyen_etablissements(affectations, preferences_universites)
    
    # Calculs théoriques de Pittel 
    n = len(preferences_etudiants)
    log_n = math.log(n) if n > 1 else 1.0
    n_sur_log_n = n / log_n if log_n > 0 else float(n)

    return {
        "satisfactions_etudiants": satisf_etudiants,
        "satisfactions_universites": satisf_universites,
        "moyenne_etudiants": float(np.mean(list(satisf_etudiants.values()))),
        "moyenne_universites": float(np.mean(list(satisf_universites.values()))),
        "rang_moyen_etudiants": rang_moyen_etu,
        "rang_moyen_etablissements": rang_moyen_etab,
        "log_n_theorique": log_n,
        "n_sur_log_n_theorique": n_sur_log_n,
    }
