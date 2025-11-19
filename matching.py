# matching.py
from typing import Dict, List
from preferences import StudentKey, UniversityKey


def algorithme_affectation(
    preferences_etudiants: Dict[StudentKey, List[UniversityKey]],
    preferences_universites: Dict[UniversityKey, List[StudentKey]],
    capacites: Dict[UniversityKey, int],
) -> Dict[UniversityKey, List[StudentKey]]:
    """
    Implémentation de l'algorithme de mariage stable,
    en utilisant uniquement les noms comme clés (str).
    """
    affectations: Dict[UniversityKey, List[StudentKey]] = {
        uni: [] for uni in preferences_universites
    }
    rang_voeux: Dict[StudentKey, int] = {etu: 0 for etu in preferences_etudiants}
    etudiants_sans_affect = list(preferences_etudiants.keys())

    while etudiants_sans_affect:
        candidatures: Dict[UniversityKey, List[StudentKey]] = {}

        # Étape 1 : chaque étudiant propose
        for etu in etudiants_sans_affect[:]:
            prefs = preferences_etudiants[etu]
            if rang_voeux[etu] >= len(prefs):
                continue
            uni = prefs[rang_voeux[etu]]

            if uni not in candidatures:
                candidatures[uni] = []
            candidatures[uni].append(etu)

        # Étape 2 : chaque université examine ses candidats
        for uni, candidats in candidatures.items():
            capacite = capacites.get(uni, 1)

            pool = affectations[uni] + candidats

            # Trier selon les priorités de l'université
            pool_tries = sorted(pool, key=lambda e: preferences_universites[uni].index(e))

            # Les meilleurs sont acceptés
            nouveaux_acceptes = pool_tries[:capacite]
            rejetes = [e for e in pool if e not in nouveaux_acceptes]

            affectations[uni] = nouveaux_acceptes

            for rej in rejetes:
                rang_voeux[rej] += 1
                if rej not in etudiants_sans_affect:
                    etudiants_sans_affect.append(rej)

            for acc in nouveaux_acceptes:
                if acc in etudiants_sans_affect:
                    etudiants_sans_affect.remove(acc)

        # Stop si plus personne ne peut proposer
        if all(rang_voeux[etu] >= len(preferences_etudiants[etu]) for etu in etudiants_sans_affect):
            break

    return affectations
