"""Algorithme de Gale-Shapley pour le mariage stable."""
from typing import Dict, List

from models import StudentKey, UniversityKey


def algorithme_affectation(
    preferences_etudiants: Dict[StudentKey, List[UniversityKey]],
    preferences_universites: Dict[UniversityKey, List[StudentKey]],
    capacites: Dict[UniversityKey, int],
) -> Dict[UniversityKey, List[StudentKey]]:
    """
    Implémentation de l'algorithme de mariage stable (Gale-Shapley).
    
    Cet algorithme trouve une affectation stable où :
    - Aucun étudiant et université ne préfèrent être ensemble plutôt que leurs affectations actuelles.
    - Les universités remplissent leurs capacités en respectant leurs priorités.

    Contrainte imposée dans cette implémentation: chaque université doit avoir
    une capacité strictement égale à 1. Toute capacité différente provoque une erreur.
    
    Args:
        preferences_etudiants: {étudiant: [universités ordonnées]}
        preferences_universites: {université: [étudiants ordonnés]}
        capacites: {université: capacité}
        
    Returns:
        {université: [étudiants affectés]}
    """
    # Validation stricte des capacités: toutes doivent être = 1
    for uni in preferences_universites:
        if capacites.get(uni, 1) != 1:
            raise ValueError(
                f"Capacité invalide détectée pour '{uni}' (={capacites.get(uni)}). Le mode actuel impose capacity=1 pour chaque université."
            )

    affectations: Dict[UniversityKey, List[StudentKey]] = {uni: [] for uni in preferences_universites}
    rang_voeux: Dict[StudentKey, int] = {etu: 0 for etu in preferences_etudiants}
    etudiants_sans_affect = list(preferences_etudiants.keys())

    while etudiants_sans_affect:
        candidatures: Dict[UniversityKey, List[StudentKey]] = {}

        # Étape 1 : chaque étudiant propose à la prochaine université de sa liste
        for etu in etudiants_sans_affect[:]:
            prefs = preferences_etudiants[etu]
            if rang_voeux[etu] >= len(prefs):
                continue
            uni = prefs[rang_voeux[etu]]

            if uni not in candidatures:
                candidatures[uni] = []
            candidatures[uni].append(etu)

        # Étape 2 : chaque université examine ses candidats et actuels pour garder les meilleurs
        for uni, candidats in candidatures.items():
            capacite = capacites.get(uni, 1)

            # Pool des candidats actuels + nouveaux
            pool = affectations[uni] + candidats

            # Trier selon les priorités de l'université
            pool_tries = sorted(pool, key=lambda e: preferences_universites[uni].index(e))

            # Garder les meilleurs, rejeter les autres
            nouveaux_acceptes = pool_tries[:capacite]
            rejetes = [e for e in pool if e not in nouveaux_acceptes]

            affectations[uni] = nouveaux_acceptes

            # Mettre à jour les statuts
            for rej in rejetes:
                rang_voeux[rej] += 1
                if rej not in etudiants_sans_affect:
                    etudiants_sans_affect.append(rej)

            for acc in nouveaux_acceptes:
                if acc in etudiants_sans_affect:
                    etudiants_sans_affect.remove(acc)

        # Arrêter si personne ne peut proposer
        if all(rang_voeux[etu] >= len(preferences_etudiants[etu]) for etu in etudiants_sans_affect):
            break

    return affectations
