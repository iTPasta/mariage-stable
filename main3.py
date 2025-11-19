import random
from typing import List, Dict, Tuple
import numpy as np

###############################################################
#  GÉNÉRATION DES DONNÉES
###############################################################

def generer_universites(nb_universites: int = 5) -> List[str]:
    universites_fr = [
        "Sorbonne Université", "Université Paris-Saclay", "Université PSL", 
        "Université de Lyon", "Université Aix-Marseille", "Université de Bordeaux",
        "Université de Strasbourg", "Université de Lille", "Université de Montpellier",
        "Université de Toulouse", "Université de Nantes", "Université Grenoble Alpes",
        "Université de Rennes", "Université de Nice", "Université de Reims",
        "Université de Poitiers", "Université de Caen", "Université de Dijon",
        "Université de Limoges", "Université de Toulon"
    ]
    universites_selectionnees = random.sample(universites_fr, nb_universites)
    random.shuffle(universites_selectionnees)
    return universites_selectionnees

def generer_etudiants(nb_etudiants: int = 5) -> List[str]:
    prenoms = ["Jean", "Marie", "Pierre", "Sophie", "Luc", "Anne", "Paul", "Claire", 
               "Thomas", "Julie", "Antoine", "Camille", "Nicolas", "Laura", "David", "Sarah"]
    noms = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", 
            "Petit", "Durand", "Leroy", "Moreau", "Simon", "Laurent"]

    etudiants = []
    for _ in range(nb_etudiants):
        etudiants.append(f"{random.choice(prenoms)} {random.choice(noms)}")
    return etudiants

def generer_preferences_etudiants(etudiants: List[str], universites: List[str]) -> Dict[str, List[str]]:
    preferences = {}
    for etu in etudiants:
        prefs = universites.copy()
        random.shuffle(prefs)
        preferences[etu] = prefs
    return preferences

def generer_preferences_universites(etudiants: List[str], universites: List[str]) -> Dict[str, List[str]]:
    preferences = {}
    for uni in universites:
        prefs = etudiants.copy()
        random.shuffle(prefs)
        preferences[uni] = prefs
    return preferences

###############################################################
#  MESURE DE SATISFACTION — VERSION EXPONENTIELLE
###############################################################

# Paramètre alpha pour la décroissance exponentielle
# Plus alpha est élevé, plus les mauvais rangs sont pénalisés
ALPHA_ETUDIANT = 0.3      # Décroissance modérée pour étudiants
ALPHA_ETABLISSEMENT = 0.5  # Décroissance plus forte pour établissements (plus exigeants)

# Option B : Catégories prédéfinies pour α
CATEGORIES_ALPHA = {
    "flexible": 0.3,
    "moyen": 0.6,
    "exigeant": 0.9,
}

def satisfaction_etudiant(etudiant: str, preferences_etudiants: Dict[str, List[str]], affectations: Dict[str, List[str]], alpha: float = ALPHA_ETUDIANT) -> float:
    """
    Satisfaction exponentielle: e^(-alpha * (rang - 1))
    
    Avantages:
    - 1er choix = satisfaction maximale (e^0 = 1.0)
    - Chaque rang suivant diminue exponentiellement
    - Modélise l'importance cruciale des premiers choix
    
    Args:
        alpha: Facteur de décroissance (0.2-1.0)
               - 0.2-0.3: décroissance douce
               - 0.5: décroissance modérée
               - 0.8-1.0: décroissance forte (très exigeant)
    """
    prefs = preferences_etudiants[etudiant]
    m = len(prefs)

    # Trouver l'université où l'étudiant est affecté
    universite = None
    for u, etus in affectations.items():
        if etudiant in etus:
            universite = u
            break

    if universite is None:
        return 0.0  # Non affecté

    if m == 1:
        return 1.0

    rang = prefs.index(universite) + 1
    
    # Formule exponentielle: e^(-alpha * (rang - 1))
    sat = np.exp(-alpha * (rang - 1))
    return sat

def satisfaction_etablissement(universite: str, preferences_universites: Dict[str, List[str]], affectations: Dict[str, List[str]]) -> float:
    """
    Satisfaction linéaire (universités) :
        s(r) = 1 - (r - 1) / (n - 1)

    Justification: priorités administratives → décroissance linéaire plus réaliste.
    """
    prefs = preferences_universites[universite]
    affectes = affectations.get(universite, [])
    n = len(prefs)
    if len(affectes) == 0:
        return 0.0  # Aucun étudiant affecté

    # Mariage stable 1-à-1: un seul étudiant maximum
    etudiant = affectes[0]
    
    if etudiant not in prefs:
        return 0.0  # Étudiant hors liste (cas anormal)
    
    rang = prefs.index(etudiant) + 1

    if n == 1:
        return 1.0

    # Formule linéaire normalisée
    sat = 1 - (rang - 1) / (n - 1)
    return sat

def mesurer_satisfaction_globale(affectations, preferences_etudiants, preferences_universites, capacites, alpha_etu=ALPHA_ETUDIANT):
    """
    Mesure la satisfaction globale (étudiants: exponentielle; universités: linéaire).
    
    Args:
        alpha_etu: Facteur de décroissance exponentielle pour étudiants
    """
    satisf_etudiants = {}
    satisf_universites = {}

    for etu in preferences_etudiants:
        satisf_etudiants[etu] = satisfaction_etudiant(etu, preferences_etudiants, affectations, alpha_etu)

    for uni in preferences_universites:
        satisf_universites[uni] = satisfaction_etablissement(uni, preferences_universites, affectations)

    return {
        "satisfactions_etudiants": satisf_etudiants,
        "satisfactions_universites": satisf_universites,
        "moyenne_etudiants": np.mean(list(satisf_etudiants.values())),
        "moyenne_universites": np.mean(list(satisf_universites.values())),
        "alpha_etudiant": alpha_etu
    }

###############################################################
#  ALGORITHME D’ACCEPTATION DIFFÉRÉE (GALE–SHAPLEY)
###############################################################

def algorithme_affectation(preferences_etudiants, preferences_universites, capacites):
    affectations = {uni: [] for uni in preferences_universites}
    rang_voeux = {etu: 0 for etu in preferences_etudiants}
    etudiants_sans_affect = list(preferences_etudiants.keys())

    while etudiants_sans_affect:
        candidatures = {}

        # Chaque étudiant propose
        for etu in etudiants_sans_affect[:]:
            prefs = preferences_etudiants[etu]
            if rang_voeux[etu] >= len(prefs):
                continue
            uni = prefs[rang_voeux[etu]]

            if uni not in candidatures:
                candidatures[uni] = []
            candidatures[uni].append(etu)

        # Universités examinent
        for uni, candidats in candidatures.items():
            capacite = capacites.get(uni, 1)

            # Candidats actuels + anciens acceptés
            pool = affectations[uni] + candidats

            # Trier selon les priorités
            pool_tries = sorted(pool, key=lambda e: preferences_universites[uni].index(e))

            # Les meilleurs sont acceptés
            nouveaux_acceptes = pool_tries[:capacite]

            # Rejetés
            rejetes = [e for e in pool if e not in nouveaux_acceptes]

            # Mise à jour
            affectations[uni] = nouveaux_acceptes

            for rej in rejetes:
                rang_voeux[rej] += 1
                if rej not in etudiants_sans_affect:
                    etudiants_sans_affect.append(rej)

            for acc in nouveaux_acceptes:
                if acc in etudiants_sans_affect:
                    etudiants_sans_affect.remove(acc)

        # Stop si aucun n'est rejeté
        if all(rang_voeux[etu] >= len(preferences_etudiants[etu]) for etu in etudiants_sans_affect):
            break

    return affectations

###############################################################
#  AFFICHAGE ET CLI
###############################################################

def afficher_titre():
    print("\n" + "="*70)
    print(" "*15 + "🎓 SYSTÈME D'AFFECTATION PAR MARIAGE STABLE")
    print(" "*20 + "(Algorithme de Gale-Shapley)")
    print(" "*18 + "Satisfaction exponentielle: e^(-α·rang)")
    print("="*70)

def afficher_donnees(universites, etudiants, prefs_etud, prefs_uni):
    print("\n" + "─"*70)
    print("📚 DONNÉES GÉNÉRÉES")
    print("─"*70)
    
    print(f"\n🏛️  Universités ({len(universites)}):")
    for i, u in enumerate(universites, 1):
        print(f"   {i}. {u}")
    
    print(f"\n👨‍🎓 Étudiants ({len(etudiants)}):")
    for i, e in enumerate(etudiants, 1):
        print(f"   {i}. {e}")
    
    print("\n" + "─"*70)
    print("🎯 PRÉFÉRENCES DES ÉTUDIANTS")
    print("─"*70)
    for etu, prefs in prefs_etud.items():
        print(f"\n{etu}:")
        for i, uni in enumerate(prefs, 1):
            print(f"   {i}° → {uni}")
    
    print("\n" + "─"*70)
    print("🏆 PRIORITÉS DES UNIVERSITÉS")
    print("─"*70)
    for uni, prefs in prefs_uni.items():
        print(f"\n{uni}:")
        for i, etu in enumerate(prefs, 1):
            print(f"   {i}° → {etu}")

def afficher_affectations(affectations, prefs_etud, prefs_uni):
    print("\n" + "="*70)
    print("✅ AFFECTATIONS FINALES")
    print("="*70)
    
    # Affichage par université
    print("\n📋 Vue par université:")
    for uni, etus in sorted(affectations.items()):
        if etus:
            print(f"\n🏛️  {uni}:")
            for etu in etus:
                rang_uni = prefs_etud[etu].index(uni) + 1
                rang_etu = prefs_uni[uni].index(etu) + 1
                print(f"   → {etu}")
                print(f"      • Rang de l'université pour l'étudiant: {rang_uni}°")
                print(f"      • Rang de l'étudiant pour l'université: {rang_etu}°")
        else:
            print(f"\n🏛️  {uni}: (aucun étudiant)")
    
    # Affichage par étudiant
    print("\n📋 Vue par étudiant:")
    for etu in prefs_etud.keys():
        uni_affectee = None
        for uni, etus in affectations.items():
            if etu in etus:
                uni_affectee = uni
                break
        
        if uni_affectee:
            rang_uni = prefs_etud[etu].index(uni_affectee) + 1
            print(f"\n👨‍🎓 {etu} → {uni_affectee} (vœu n°{rang_uni})")
        else:
            print(f"\n👨‍🎓 {etu} → Non affecté ❌")

def afficher_satisfaction(stats, affectations, prefs_etud, prefs_uni):
    print("\n" + "="*70)
    print("📊 MESURE DE SATISFACTION (Étudiants: exponentielle / Universités: linéaire)")
    print("="*70)
    
    # Paramètres alpha
    print("\n⚙️  PARAMÈTRES:")
    print(f"   Étudiants: α = {stats.get('alpha_etudiant', ALPHA_ETUDIANT):.2f}  → e^(-α × (rang - 1))")
    print("   Universités: linéaire → 1 - (rang - 1) / (n - 1)")
    
    # Statistiques globales
    print("\n📈 STATISTIQUES GLOBALES:")
    print(f"   Satisfaction moyenne étudiants:    {stats['moyenne_etudiants']:.1%}")
    print(f"   Satisfaction moyenne universités:  {stats['moyenne_universites']:.1%}")
    
    # Distribution satisfaction étudiants
    satisf_etud = list(stats["satisfactions_etudiants"].values())
    print(f"\n   Distribution étudiants:")
    print(f"      Min: {min(satisf_etud):.1%}  |  Max: {max(satisf_etud):.1%}  |  Médiane: {np.median(satisf_etud):.1%}")
    
    # Distribution satisfaction universités
    satisf_uni = list(stats["satisfactions_universites"].values())
    print(f"\n   Distribution universités:")
    print(f"      Min: {min(satisf_uni):.1%}  |  Max: {max(satisf_uni):.1%}  |  Médiane: {np.median(satisf_uni):.1%}")
    
    # Détail étudiants
    print("\n" + "─"*70)
    print("👨‍🎓 SATISFACTION PAR ÉTUDIANT:")
    print("─"*70)
    
    satisf_tries = sorted(stats["satisfactions_etudiants"].items(), 
                         key=lambda x: x[1], reverse=True)
    
    for etu, sat in satisf_tries:
        uni_affectee = None
        for uni, etus in affectations.items():
            if etu in etus:
                uni_affectee = uni
                break
        
        if uni_affectee:
            rang = prefs_etud[etu].index(uni_affectee) + 1
            barre = "█" * int(sat * 30)
            print(f"{etu:25} │ {sat:>6.1%} {barre}")
            print(f"{'':25} └─ {uni_affectee} (vœu n°{rang})")
        else:
            print(f"{etu:25} │   0.0% (non affecté)")
    
    # Détail universités
    print("\n" + "─"*70)
    print("🏛️  SATISFACTION PAR UNIVERSITÉ:")
    print("─"*70)
    
    satisf_uni_tries = sorted(stats["satisfactions_universites"].items(), 
                              key=lambda x: x[1], reverse=True)
    
    for uni, sat in satisf_uni_tries:
        etus = affectations.get(uni, [])
        barre = "█" * int(sat * 30)
        
        if etus:
            print(f"{uni:35} │ {sat:>6.1%} {barre}")
            for etu in etus:
                rang = prefs_uni[uni].index(etu) + 1
                print(f"{'':35} └─ {etu} (priorité n°{rang})")
        else:
            print(f"{uni:35} │   0.0% (vide)")

def demander_parametres():
    print("\n" + "─"*70)
    print("⚙️  CONFIGURATION")
    print("─"*70)
    
    while True:
        try:
            nb_uni = input("\n📚 Nombre d'universités (défaut: 5): ").strip()
            nb_uni = int(nb_uni) if nb_uni else 5
            if nb_uni < 2 or nb_uni > 20:
                print("   ⚠️  Veuillez choisir entre 2 et 20")
                continue
            break
        except ValueError:
            print("   ❌ Veuillez entrer un nombre valide")
    
    while True:
        try:
            nb_etu = input("👨‍🎓 Nombre d'étudiants (défaut: 5): ").strip()
            nb_etu = int(nb_etu) if nb_etu else 5
            if nb_etu < 1 or nb_etu > 50:
                print("   ⚠️  Veuillez choisir entre 1 et 50")
                continue
            break
        except ValueError:
            print("   ❌ Veuillez entrer un nombre valide")
    
    print("\n💡 Capacité des universités: 1 place (mariage stable classique)")
    
    # Configuration des paramètres alpha (Étudiants uniquement)
    print("\n📐 Paramètres de satisfaction exponentielle:")
    print("   Étudiants → exponentielle | Universités → linéaire")
    print("   Choisissez la méthode de configuration de α (étudiants):")
    print("   1) Option B : Catégories (flexible / moyen / exigeant)")
    print("   2) Valeurs personnalisées (décimales)")
    
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
        # Option B : Catégories (Étudiants)
        print("\n   🔹 Catégories disponibles:")
        print("      1) flexible  (α=0.3)")
        print("      2) moyen     (α=0.6)")
        print("      3) exigeant  (α=0.9)")

        # Étudiants
        while True:
            cat_etu = input("   Catégorie étudiants [1/2/3] (défaut: 1): ").strip()
            if cat_etu == "" or cat_etu == "1":
                alpha_etu = CATEGORIES_ALPHA["flexible"]
                break
            elif cat_etu == "2":
                alpha_etu = CATEGORIES_ALPHA["moyen"]
                break
            elif cat_etu == "3":
                alpha_etu = CATEGORIES_ALPHA["exigeant"]
                break
            else:
                print("   ❌ Choix invalide. Tapez 1, 2 ou 3.")
        print("   (Universités: satisfaction linéaire, pas de paramètre à saisir)")
    else:
        # Option A : valeurs personnalisées (Étudiants)
        print("\n   (Laissez vide pour valeurs par défaut actuelles)")
        while True:
            try:
                alpha_etu_in = input(f"   Alpha étudiants [0.2-1.0] (défaut: {ALPHA_ETUDIANT}): ").strip()
                if alpha_etu_in == "":
                    alpha_etu = ALPHA_ETUDIANT
                else:
                    alpha_etu = float(alpha_etu_in)
                    if alpha_etu < 0.1 or alpha_etu > 1.5:
                        print("   ⚠️  Veuillez choisir entre 0.1 et 1.5")
                        continue
                break
            except ValueError:
                print("   ❌ Veuillez entrer un nombre décimal valide")
        print("   (Universités: satisfaction linéaire, pas de paramètre à saisir)")
    
    return nb_uni, nb_etu, alpha_etu

def menu_principal():
    while True:
        print("\n" + "─"*70)
        print("📋 MENU")
        print("─"*70)
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

###############################################################
#  PROGRAMME PRINCIPAL
###############################################################

def main():
    afficher_titre()
    
    continuer = True
    while continuer:
        nb_uni, nb_etu, alpha_etu = demander_parametres()
        
        print("\n⏳ Génération des données...")
        universites = generer_universites(nb_uni)
        etudiants = generer_etudiants(nb_etu)
        prefs_etud = generer_preferences_etudiants(etudiants, universites)
        prefs_uni = generer_preferences_universites(etudiants, universites)
        capacites = {u: 1 for u in universites}
        
        afficher_donnees(universites, etudiants, prefs_etud, prefs_uni)
        
        input("\n⏎ Appuyez sur Entrée pour lancer l'algorithme d'affectation...")
        
        print("\n⚙️  Exécution de l'algorithme de Gale-Shapley...")
        affectations = algorithme_affectation(prefs_etud, prefs_uni, capacites)
        
        afficher_affectations(affectations, prefs_etud, prefs_uni)
        
        print("\n⏳ Calcul des satisfactions...")
        stats = mesurer_satisfaction_globale(affectations, prefs_etud, prefs_uni, capacites, alpha_etu)
        
        afficher_satisfaction(stats, affectations, prefs_etud, prefs_uni)
        
        continuer = menu_principal()

if __name__ == "__main__":
    main()
