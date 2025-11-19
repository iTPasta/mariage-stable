# ui.py
from typing import Dict, List
import numpy as np

from models import Student, University
from preferences import StudentKey, UniversityKey
from satisfaction import (
    mesurer_satisfaction_globale,
    ALPHA_ETUDIANT,
    CATEGORIES_ALPHA,
)


def afficher_titre():
    print("\n" + "=" * 70)
    print(" " * 15 + "🎓 SYSTÈME D'AFFECTATION PAR MARIAGE STABLE")
    print(" " * 20 + "(Algorithme de Gale-Shapley)")
    print(" " * 18 + "Satisfaction exponentielle: e^(-α·rang)")
    print("=" * 70)


def afficher_donnees(
    universites: List[University],
    etudiants: List[Student],
    prefs_etud: Dict[StudentKey, List[UniversityKey]],
    prefs_uni: Dict[UniversityKey, List[StudentKey]],
):
    print("\n" + "─" * 70)
    print("📚 DONNÉES")
    print("─" * 70)

    print(f"\n🏛️  Universités ({len(universites)}):")
    for i, u in enumerate(universites, 1):
        print(f"   {i}. {u.name} (capacité={u.capacity})")

    print(f"\n👨‍🎓 Étudiants ({len(etudiants)}):")
    for i, e in enumerate(etudiants, 1):
        print(f"   {i}. {e.full_name}")

    print("\n" + "─" * 70)
    print("🎯 PRÉFÉRENCES DES ÉTUDIANTS")
    print("─" * 70)
    for etu_name, prefs in prefs_etud.items():
        print(f"\n{etu_name}:")
        for i, uni_name in enumerate(prefs, 1):
            print(f"   {i}° → {uni_name}")

    print("\n" + "─" * 70)
    print("🏆 PRIORITÉS DES UNIVERSITÉS")
    print("─" * 70)
    for uni_name, prefs in prefs_uni.items():
        print(f"\n{uni_name}:")
        for i, etu_name in enumerate(prefs, 1):
            print(f"   {i}° → {etu_name}")


def afficher_affectations(
    affectations: Dict[UniversityKey, List[StudentKey]],
    etudiants: List[Student],
    universites: List[University],
    prefs_etud: Dict[StudentKey, List[UniversityKey]],
    prefs_uni: Dict[UniversityKey, List[StudentKey]],
):
    print("\n" + "=" * 70)
    print("✅ AFFECTATIONS FINALES")
    print("=" * 70)

    # Vue par université
    print("\n📋 Vue par université:")
    for uni_name, etus_names in sorted(affectations.items(), key=lambda x: x[0]):
        if etus_names:
            print(f"\n🏛️  {uni_name}:")
            for etu_name in etus_names:
                rang_uni = prefs_etud[etu_name].index(uni_name) + 1
                rang_etu = prefs_uni[uni_name].index(etu_name) + 1
                print(f"   → {etu_name}")
                print(f"      • Rang de l'université pour l'étudiant: {rang_uni}°")
                print(f"      • Rang de l'étudiant pour l'université: {rang_etu}°")
        else:
            print(f"\n🏛️  {uni_name}: (aucun étudiant)")

    # Vue par étudiant
    print("\n📋 Vue par étudiant:")
    for etu in etudiants:
        etu_name = etu.full_name
        uni_affectee = None
        for uni_name, etus_names in affectations.items():
            if etu_name in etus_names:
                uni_affectee = uni_name
                break

        if uni_affectee:
            rang_uni = prefs_etud[etu_name].index(uni_affectee) + 1
            print(f"\n👨‍🎓 {etu_name} → {uni_affectee} (vœu n°{rang_uni})")
        else:
            print(f"\n👨‍🎓 {etu_name} → Non affecté ❌")


def afficher_satisfaction(
    affectations: Dict[UniversityKey, List[StudentKey]],
    etudiants: List[Student],
    universites: List[University],
    prefs_etud: Dict[StudentKey, List[UniversityKey]],
    prefs_uni: Dict[UniversityKey, List[StudentKey]],
    alpha_etu: float,
):
    stats = mesurer_satisfaction_globale(
        affectations, prefs_etud, prefs_uni, {u.name: u.capacity for u in universites}, alpha_etu
    )

    print("\n" + "=" * 70)
    print("📊 MESURE DE SATISFACTION (Étudiants: exponentielle / Universités: linéaire)")
    print("=" * 70)

    print("\n⚙️  PARAMÈTRES:")
    print(f"   Étudiants: α = {stats.get('alpha_etudiant', ALPHA_ETUDIANT):.2f}  → e^(-α × (rang - 1))")
    print("   Universités: linéaire → 1 - (rang - 1) / (n - 1)")

    print("\n📈 STATISTIQUES GLOBALES:")
    print(f"   Satisfaction moyenne étudiants:    {stats['moyenne_etudiants']:.1%}")
    print(f"   Satisfaction moyenne universités:  {stats['moyenne_universites']:.1%}")

    satisf_etud_vals = list(stats["satisfactions_etudiants"].values())
    satisf_uni_vals = list(stats["satisfactions_universites"].values())

    print(f"\n   Distribution étudiants:")
    print(
        f"      Min: {min(satisf_etud_vals):.1%}  |  Max: {max(satisf_etud_vals):.1%}  |  Médiane: {np.median(satisf_etud_vals):.1%}"
    )

    print(f"\n   Distribution universités:")
    print(
        f"      Min: {min(satisf_uni_vals):.1%}  |  Max: {max(satisf_uni_vals):.1%}  |  Médiane: {np.median(satisf_uni_vals):.1%}"
    )

    # Détail étudiants
    print("\n" + "─" * 70)
    print("👨‍🎓 SATISFACTION PAR ÉTUDIANT:")
    print("─" * 70)

    satisf_tries = sorted(
        stats["satisfactions_etudiants"].items(), key=lambda x: x[1], reverse=True
    )

    for etu_name, sat in satisf_tries:
        # retrouver l'université d'affectation
        uni_affectee = None
        for uni_name, etus_names in affectations.items():
            if etu_name in etus_names:
                uni_affectee = uni_name
                break

        if uni_affectee:
            rang = prefs_etud[etu_name].index(uni_affectee) + 1
            barre = "█" * int(sat * 30)
            print(f"{etu_name:25} │ {sat:>6.1%} {barre}")
            print(f"{'':25} └─ {uni_affectee} (vœu n°{rang})")
        else:
            print(f"{etu_name:25} │   0.0% (non affecté)")

    # Détail universités
    print("\n" + "─" * 70)
    print("🏛️  SATISFACTION PAR UNIVERSITÉ:")
    print("─" * 70)

    satisf_uni_tries = sorted(
        stats["satisfactions_universites"].items(), key=lambda x: x[1], reverse=True
    )

    for uni_name, sat in satisf_uni_tries:
        etus_names = affectations.get(uni_name, [])
        barre = "█" * int(sat * 30)

        if etus_names:
            print(f"{uni_name:35} │ {sat:>6.1%} {barre}")
            for etu_name in etus_names:
                rang = prefs_uni[uni_name].index(etu_name) + 1
                print(f"{'':35} └─ {etu_name} (priorité n°{rang})")
        else:
            print(f"{uni_name:35} │   0.0% (vide)")


def demander_parametres_satisfaction() -> float:
    print("\n" + "─" * 70)
    print("⚙️  CONFIGURATION DE LA SATISFACTION")
    print("─" * 70)

    print("\n📐 Paramètres de satisfaction exponentielle (étudiants):")
    print("   Choisissez la méthode de configuration de α :")
    print("   1) Catégories (flexible / moyen / exigeant)")
    print("   2) Valeur personnalisée")

    mode = None
    while True:
        choix_mode = input("   Votre choix [1/2] (défaut: 1): ").strip()
        if choix_mode == "" or choix_mode == "1":
            mode = 1
            break
        elif choix_mode == "2":
            mode = 2
            break
        else:
            print("   ❌ Choix invalide. Tapez 1 ou 2.")

    if mode == 1:
        print("\n   🔹 Catégories disponibles:")
        print("      1) flexible  (α=0.3)")
        print("      2) moyen     (α=0.6)")
        print("      3) exigeant  (α=0.9)")

        while True:
            cat = input("   Catégorie étudiants [1/2/3] (défaut: 1): ").strip()
            if cat == "" or cat == "1":
                alpha_etu = CATEGORIES_ALPHA["flexible"]
                break
            elif cat == "2":
                alpha_etu = CATEGORIES_ALPHA["moyen"]
                break
            elif cat == "3":
                alpha_etu = CATEGORIES_ALPHA["exigeant"]
                break
            else:
                print("   ❌ Choix invalide. Tapez 1, 2 ou 3.")
    else:
        print("\n   (Laissez vide pour valeur par défaut actuelle)")
        while True:
            try:
                alpha_in = input(
                    f"   Alpha étudiants [0.1-1.5] (défaut: {ALPHA_ETUDIANT}): "
                ).strip()
                if alpha_in == "":
                    alpha_etu = ALPHA_ETUDIANT
                else:
                    alpha_etu = float(alpha_in)
                    if not (0.1 <= alpha_etu <= 1.5):
                        print("   ⚠️  Veuillez choisir entre 0.1 et 1.5")
                        continue
                break
            except ValueError:
                print("   ❌ Veuillez entrer un nombre décimal valide")

    return alpha_etu


def menu_principal() -> bool:
    while True:
        print("\n" + "─" * 70)
        print("📋 MENU")
        print("─" * 70)
        print("1. Nouvelle simulation")
        print("2. Quitter")

        choix = input("\nVotre choix: ").strip()

        if choix == "1":
            return True
        elif choix == "2":
            print("\n👋 Merci d'avoir utilisé le système d'affectation !\n")
            return False
        else:
            print("❌ Choix invalide")
