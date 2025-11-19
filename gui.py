# gui.py
import tkinter as tk
from tkinter import ttk
from typing import Dict, List

from models import Student, University
from preferences import StudentKey, UniversityKey
from satisfaction import mesurer_satisfaction_globale


def _create_scrollable_tree(parent, columns, headings, column_widths=None):
    """
    Crée un ttk.Treeview avec barres de scroll verticales et horizontales.
    """
    frame = ttk.Frame(parent)

    tree = ttk.Treeview(frame, columns=columns, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    for col, head in zip(columns, headings):
        tree.heading(col, text=head)
        width = 120
        if column_widths and col in column_widths:
            width = column_widths[col]
        tree.column(col, width=width, anchor="w")

    return frame, tree


def afficher_bilan_graphique(
    affectations: Dict[UniversityKey, List[StudentKey]],
    etudiants: List[Student],
    universites: List[University],
    prefs_etud: Dict[StudentKey, List[UniversityKey]],
    prefs_uni: Dict[UniversityKey, List[StudentKey]],
    alpha_etu: float,
):
    """
    Ouvre une fenêtre Tkinter qui présente un bilan graphique complet :
    - Vue d'ensemble
    - Détail par étudiant
    - Détail par université
    - Tableau des affectations
    """
    # Calcul des stats de satisfaction
    capacites = {u.name: u.capacity for u in universites}
    stats = mesurer_satisfaction_globale(
        affectations, prefs_etud, prefs_uni, capacites, alpha_etu
    )

    satisf_etudiants = stats["satisfactions_etudiants"]
    satisf_universites = stats["satisfactions_universites"]

    # Préparation des mappings utiles
    etu_names = [e.full_name for e in etudiants]
    uni_names = [u.name for u in universites]

    affectation_par_etu: Dict[StudentKey, UniversityKey] = {}
    for uni_name, etus in affectations.items():
        for etu_name in etus:
            affectation_par_etu[etu_name] = uni_name

    nb_etudiants = len(etu_names)
    nb_universites = len(uni_names)
    nb_etudiants_affectes = len(affectation_par_etu)
    nb_etudiants_non_affectes = nb_etudiants - nb_etudiants_affectes

    # Création de la fenêtre principale
    root = tk.Tk()
    root.title("Bilan de la simulation d'affectation")
    root.geometry("1100x700")

    # Notebook (onglets)
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # ===================== Onglet 1 : Vue d'ensemble =====================
    tab_overview = ttk.Frame(notebook)
    notebook.add(tab_overview, text="Vue d'ensemble")

    # Frame haute : résumé général
    frame_top = ttk.Frame(tab_overview, padding=10)
    frame_top.pack(fill="x")

    label_title = ttk.Label(
        frame_top,
        text="Résumé de la simulation",
        font=("Segoe UI", 14, "bold")
    )
    label_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

    # Colonnes de résumé
    ttk.Label(frame_top, text=f"Nombre d'étudiants : {nb_etudiants}").grid(
        row=1, column=0, sticky="w", pady=2
    )
    ttk.Label(frame_top, text=f"Nombre d'universités : {nb_universites}").grid(
        row=2, column=0, sticky="w", pady=2
    )
    ttk.Label(
        frame_top,
        text=f"Étudiants affectés : {nb_etudiants_affectes} / {nb_etudiants}"
    ).grid(row=3, column=0, sticky="w", pady=2)
    ttk.Label(
        frame_top,
        text=f"Étudiants non affectés : {nb_etudiants_non_affectes}"
    ).grid(row=4, column=0, sticky="w", pady=2)

    ttk.Label(
        frame_top,
        text=f"Satisfaction moyenne étudiants : {stats['moyenne_etudiants']:.1%}"
    ).grid(row=1, column=1, sticky="w", padx=30, pady=2)
    ttk.Label(
        frame_top,
        text=f"Satisfaction moyenne universités : {stats['moyenne_universites']:.1%}"
    ).grid(row=2, column=1, sticky="w", padx=30, pady=2)
    ttk.Label(
        frame_top,
        text=f"Paramètre α (étudiants) : {stats['alpha_etudiant']:.2f}"
    ).grid(row=3, column=1, sticky="w", padx=30, pady=2)

    # Séparateur
    ttk.Separator(tab_overview, orient="horizontal").pack(fill="x", pady=5)

    # Frame bas : meilleurs / pires
    frame_bottom = ttk.Frame(tab_overview, padding=10)
    frame_bottom.pack(fill="both", expand=True)

    # Tri des satisfactions
    etud_sorted = sorted(
        satisf_etudiants.items(), key=lambda x: x[1], reverse=True
    )
    uni_sorted = sorted(
        satisf_universites.items(), key=lambda x: x[1], reverse=True
    )

    top_n = 10

    # Colonnes "Top étudiants" / "Étudiants les moins satisfaits"
    frame_etud = ttk.Frame(frame_bottom)
    frame_etud.pack(side="left", fill="both", expand=True, padx=(0, 10))

    ttk.Label(frame_etud, text="Top étudiants (satisfaction)", font=("Segoe UI", 11, "bold")).pack(anchor="w")
    cols = ("etud", "satisfaction", "universite", "voeu")
    frame_tree_top, tree_top = _create_scrollable_tree(
        frame_etud,
        columns=cols,
        headings=("Étudiant", "Satisf.", "Université", "Vœu"),
        column_widths={"etud": 200, "universite": 200, "satisfaction": 80, "voeu": 60},
    )
    frame_tree_top.pack(fill="both", expand=True, pady=(5, 10))

    for etu_name, sat in etud_sorted[:top_n]:
        uni_name = affectation_par_etu.get(etu_name, "Non affecté")
        if uni_name != "Non affecté":
            voeu = prefs_etud[etu_name].index(uni_name) + 1
        else:
            voeu = "-"
        tree_top.insert(
            "",
            "end",
            values=(etu_name, f"{sat:.1%}", uni_name, voeu),
        )

    ttk.Label(frame_etud, text="Étudiants les moins satisfaits", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 0))
    frame_tree_low, tree_low = _create_scrollable_tree(
        frame_etud,
        columns=cols,
        headings=("Étudiant", "Satisf.", "Université", "Vœu"),
        column_widths={"etud": 200, "universite": 200, "satisfaction": 80, "voeu": 60},
    )
    frame_tree_low.pack(fill="both", expand=True, pady=5)

    for etu_name, sat in etud_sorted[-top_n:]:
        uni_name = affectation_par_etu.get(etu_name, "Non affecté")
        if uni_name != "Non affecté":
            voeu = prefs_etud[etu_name].index(uni_name) + 1
        else:
            voeu = "-"
        tree_low.insert(
            "",
            "end",
            values=(etu_name, f"{sat:.1%}", uni_name, voeu),
        )

    # Colonne "Universités"
    frame_uni = ttk.Frame(frame_bottom)
    frame_uni.pack(side="left", fill="both", expand=True, padx=(10, 0))

    ttk.Label(frame_uni, text="Universités les plus satisfaites", font=("Segoe UI", 11, "bold")).pack(anchor="w")
    cols_u = ("uni", "satisfaction", "etudiants")
    frame_tree_uni_top, tree_uni_top = _create_scrollable_tree(
        frame_uni,
        columns=cols_u,
        headings=("Université", "Satisf.", "Étudiants affectés"),
        column_widths={"uni": 220, "satisfaction": 80, "etudiants": 260},
    )
    frame_tree_uni_top.pack(fill="both", expand=True, pady=(5, 10))

    for uni_name, sat in uni_sorted[:top_n]:
        etus = affectations.get(uni_name, [])
        etus_str = ", ".join(etus) if etus else "Aucun"
        tree_uni_top.insert(
            "",
            "end",
            values=(uni_name, f"{sat:.1%}", etus_str),
        )

    ttk.Label(frame_uni, text="Universités les moins satisfaites", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 0))
    frame_tree_uni_low, tree_uni_low = _create_scrollable_tree(
        frame_uni,
        columns=cols_u,
        headings=("Université", "Satisf.", "Étudiants affectés"),
        column_widths={"uni": 220, "satisfaction": 80, "etudiants": 260},
    )
    frame_tree_uni_low.pack(fill="both", expand=True, pady=5)

    for uni_name, sat in uni_sorted[-top_n:]:
        etus = affectations.get(uni_name, [])
        etus_str = ", ".join(etus) if etus else "Aucun"
        tree_uni_low.insert(
            "",
            "end",
            values=(uni_name, f"{sat:.1%}", etus_str),
        )

    # ===================== Onglet 2 : Étudiants =====================
    tab_students = ttk.Frame(notebook)
    notebook.add(tab_students, text="Étudiants")

    cols = ("etud", "universite", "voeu", "satisfaction")
    frame_tree_etud_all, tree_etud_all = _create_scrollable_tree(
        tab_students,
        columns=cols,
        headings=("Étudiant", "Université", "Vœu", "Satisfaction"),
        column_widths={"etud": 250, "universite": 250, "voeu": 60, "satisfaction": 100},
    )
    frame_tree_etud_all.pack(fill="both", expand=True, padx=10, pady=10)

    for etu_name in etu_names:
        sat = satisf_etudiants.get(etu_name, 0.0)
        uni_name = affectation_par_etu.get(etu_name, "Non affecté")
        if uni_name != "Non affecté":
            voeu = prefs_etud[etu_name].index(uni_name) + 1
        else:
            voeu = "-"
        tree_etud_all.insert(
            "",
            "end",
            values=(etu_name, uni_name, voeu, f"{sat:.1%}"),
        )

    # ===================== Onglet 3 : Universités =====================
    tab_universities = ttk.Frame(notebook)
    notebook.add(tab_universities, text="Universités")

    cols = ("uni", "capacite", "nb_affectes", "satisfaction", "etudiants")
    frame_tree_uni_all, tree_uni_all = _create_scrollable_tree(
        tab_universities,
        columns=cols,
        headings=("Université", "Capacité", "Affectés", "Satisfaction", "Étudiants"),
        column_widths={
            "uni": 250,
            "capacite": 70,
            "nb_affectes": 80,
            "satisfaction": 100,
            "etudiants": 300,
        },
    )
    frame_tree_uni_all.pack(fill="both", expand=True, padx=10, pady=10)

    for u in universites:
        uni_name = u.name
        sat = satisf_universites.get(uni_name, 0.0)
        etus = affectations.get(uni_name, [])
        etus_str = ", ".join(etus) if etus else "Aucun"
        tree_uni_all.insert(
            "",
            "end",
            values=(
                uni_name,
                u.capacity,
                len(etus),
                f"{sat:.1%}",
                etus_str,
            ),
        )

    # ===================== Onglet 4 : Affectations =====================
    tab_affectations = ttk.Frame(notebook)
    notebook.add(tab_affectations, text="Affectations")

    cols = ("universite", "etudiant", "voeu_etudiant", "rang_universite")
    frame_tree_aff, tree_aff = _create_scrollable_tree(
        tab_affectations,
        columns=cols,
        headings=(
            "Université",
            "Étudiant",
            "Vœu de l'étudiant",
            "Rang de l'étudiant pour l'université",
        ),
        column_widths={
            "universite": 260,
            "etudiant": 260,
            "voeu_etudiant": 140,
            "rang_universite": 200,
        },
    )
    frame_tree_aff.pack(fill="both", expand=True, padx=10, pady=10)

    for uni_name, etus in affectations.items():
        for etu_name in etus:
            voeu = prefs_etud[etu_name].index(uni_name) + 1
            rang_uni = prefs_uni[uni_name].index(etu_name) + 1
            tree_aff.insert(
                "",
                "end",
                values=(uni_name, etu_name, voeu, rang_uni),
            )

    # Lancement de la boucle Tkinter
    root.mainloop()
