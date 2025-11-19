# main.py
import random
from typing import Dict, List

from models import Student, University
from data_loader import (
    load_students_from_csv,
    load_universities_from_csv,
)
from preferences import generer_preferences_etudiants, generer_preferences_universites
from matching import algorithme_affectation
from ui import (
    afficher_titre,
    afficher_donnees,
    afficher_affectations,
    afficher_satisfaction,
    demander_parametres_satisfaction,
    menu_principal,
)


DEFAULT_STUDENTS_CSV = "etudiants.csv"
DEFAULT_UNIVERSITIES_CSV = "universites.csv"


def charger_donnees() -> tuple[List[Student], List[University]]:
    """
    Charge les données depuis les CSV, puis sélectionne aléatoirement
    n universités et m étudiants parmi ceux disponibles.

    Si n ou m est supérieur au nombre disponible, on redemande
    des valeurs valides.
    """
    while True:
        print("\n" + "─" * 70)
        print("📦 CHARGEMENT DES DONNÉES DEPUIS DES FICHIERS CSV")
        print("─" * 70)

        path_unis = input(
            f"   Chemin du CSV des universités (défaut: {DEFAULT_UNIVERSITIES_CSV}): "
        ).strip() or DEFAULT_UNIVERSITIES_CSV
        path_etus = input(
            f"   Chemin du CSV des étudiants (défaut: {DEFAULT_STUDENTS_CSV}): "
        ).strip() or DEFAULT_STUDENTS_CSV

        universities = load_universities_from_csv(path_unis)
        students = load_students_from_csv(path_etus)

        if not universities:
            print("❌ Aucun enregistrement université trouvé dans le CSV.")
            print("   Veuillez vérifier le fichier et réessayer.")
            continue
        if not students:
            print("❌ Aucun enregistrement étudiant trouvé dans le CSV.")
            print("   Veuillez vérifier le fichier et réessayer.")
            continue

        nb_unis_total = len(universities)
        nb_etus_total = len(students)

        print("\n✅ Fichiers chargés avec succès :")
        print(f"   • Universités disponibles : {nb_unis_total}")
        print(f"   • Étudiants disponibles   : {nb_etus_total}")

        # Demander n universités à sélectionner aléatoirement
        while True:
            try:
                nb_uni_in = input(
                    f"\n📚 Nombre d'universités à sélectionner aléatoirement [1-{nb_unis_total}]: "
                ).strip()
                nb_uni = int(nb_uni_in)
                if not (1 <= nb_uni <= nb_unis_total):
                    print(f"   ⚠️  Veuillez choisir un nombre entre 1 et {nb_unis_total}.")
                    continue
                break
            except ValueError:
                print("   ❌ Veuillez entrer un nombre entier valide.")

        # Demander m étudiants à sélectionner aléatoirement
        while True:
            try:
                nb_etu_in = input(
                    f"👨‍🎓 Nombre d'étudiants à sélectionner aléatoirement [1-{nb_etus_total}]: "
                ).strip()
                nb_etu = int(nb_etu_in)
                if not (1 <= nb_etu <= nb_etus_total):
                    print(f"   ⚠️  Veuillez choisir un nombre entre 1 et {nb_etus_total}.")
                    continue
                break
            except ValueError:
                print("   ❌ Veuillez entrer un nombre entier valide.")

        # Sélection aléatoire
        selected_universities = random.sample(universities, nb_uni)
        selected_students = random.sample(students, nb_etu)

        print("\n🎲 Sélection aléatoire effectuée :")
        print(f"   • Universités sélectionnées : {len(selected_universities)}")
        print(f"   • Étudiants sélectionnés    : {len(selected_students)}")

        return selected_students, selected_universities


def main():
    afficher_titre()

    continuer = True
    while continuer:
        # 1. Chargement ou sélection aléatoire dans les CSV
        etudiants, universites = charger_donnees()

        # 2. Paramètres de satisfaction
        alpha_etu = demander_parametres_satisfaction()

        # 3. Préférences
        print("\n⏳ Génération des préférences...")
        prefs_etud = generer_preferences_etudiants(etudiants, universites)
        prefs_uni = generer_preferences_universites(etudiants, universites)

        # Capacités : clé = nom de l'université
        capacites: Dict[str, int] = {u.name: u.capacity for u in universites}

        # 4. Affichage des données
        afficher_donnees(universites, etudiants, prefs_etud, prefs_uni)

        input("\n⏎ Appuyez sur Entrée pour lancer l'algorithme d'affectation...")

        # 5. Matching
        print("\n⚙️  Exécution de l'algorithme de Gale-Shapley...")
        affectations = algorithme_affectation(prefs_etud, prefs_uni, capacites)

        # 6. Affichage affectations
        afficher_affectations(affectations, etudiants, universites, prefs_etud, prefs_uni)

        # 7. Satisfaction
        print("\n⏳ Calcul des satisfactions...")
        afficher_satisfaction(affectations, etudiants, universites, prefs_etud, prefs_uni, alpha_etu)

        # 8. Menu
        continuer = menu_principal()


if __name__ == "__main__":
    main()
