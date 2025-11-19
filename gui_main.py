#!/usr/bin/env python3
"""Interface graphique moderne pour le système d'affectation."""
import tkinter as tk
from tkinter import ttk, messagebox
import random
from typing import Optional
import os

from models import Student, University, SimulationData, StudentKey, UniversityKey
from data.data_loader import load_students_from_csv, load_universities_from_csv
from preferences import generer_preferences_etudiants, generer_preferences_universites
from matching import algorithme_affectation
from satisfaction import mesurer_satisfaction_globale

# Constantes locales (remplace config.py)
class UI:
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    DEFAULT_NB_STUDENTS = 10
    DEFAULT_NB_UNIVERSITIES = 10
    BG_COLOR = "#f0f4f8"
    PRIMARY_COLOR = "#3b82f6"
    SECONDARY_COLOR = "#10b981"
    TEXT_COLOR = "#1f2937"
    WHITE = "white"
    GRAY = "#6b7280"
    TITLE_FONT = ("Segoe UI", 24, "bold")
    SUBTITLE_FONT = ("Segoe UI", 12)
    HEADER_FONT = ("Segoe UI", 14, "bold")
    BUTTON_FONT = ("Segoe UI", 11, "bold")
    TEXT_FONT = ("Segoe UI", 10)
    SMALL_FONT = ("Segoe UI", 9)

ALPHA_PRESETS = {
    "flexible": 0.3,
    "moyen": 0.6,
    "exigeant": 0.9,
}

STUDENTS_CSV = os.path.join("data", "etudiants.csv")
UNIVERSITIES_CSV = os.path.join("data", "universites.csv")


class ModernMatchingApp:
    """Application GUI moderne pour le matching d'affectation."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Algorithme du Mariage Stable - Étudiants/Établissements")
        self.root.geometry(f"{UI.WINDOW_WIDTH}x{UI.WINDOW_HEIGHT}")
        self.root.configure(bg=UI.BG_COLOR)
        
        # Gérer la fermeture de la fenêtre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Données
        self.all_students = []
        self.all_universities = []
        self.simulation_data: Optional[SimulationData] = None
        
        # Style
        self.setup_styles()
        
        # Interface
        self.create_widgets()
        
        # Charger les données
        self.load_data()
    
    def on_closing(self):
        """Gère la fermeture de l'application."""
        self.root.quit()
        self.root.destroy()
    
    def setup_styles(self):
        """Configure les styles de l'interface."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Couleurs modernes
        self.root.configure(bg="#f8fafc")
        
        style.configure("Title.TLabel", 
                   font=UI.TITLE_FONT, 
                       foreground="#0f172a", 
                       background="#f8fafc")
        style.configure("Subtitle.TLabel", 
                   font=UI.SUBTITLE_FONT, 
                       foreground="#475569", 
                       background="#f8fafc")
        style.configure("Header.TLabel", 
                   font=UI.HEADER_FONT, 
                       foreground="#0f172a", 
                   background=UI.WHITE)
        style.configure("Modern.TFrame", background="#f8fafc")
        style.configure("Card.TFrame", background=UI.WHITE, relief="flat", borderwidth=1)
        
        # Style Notebook moderne
        style.configure("TNotebook", background="#f8fafc", borderwidth=0)
        style.configure("TNotebook.Tab", 
                       font=("Segoe UI", 10, "bold"),
                       padding=[20, 10],
                       background="#e2e8f0",
                       foreground="#475569")
        style.map("TNotebook.Tab",
                 background=[("selected", "#3b82f6")],
                 foreground=[("selected", "white")])
        
        # Treeview moderne avec gradient
        style.configure("Treeview", 
                   background=UI.WHITE,
                       foreground="#1e293b",
                   fieldbackground=UI.WHITE,
                       font=("Segoe UI", 10),
                       rowheight=32,
                       borderwidth=0)
        style.configure("Treeview.Heading", 
                       font=("Segoe UI", 11, "bold"),
                       background="#2563eb",
                   foreground=UI.WHITE,
                       relief="flat",
                       borderwidth=0)
        style.map("Treeview.Heading",
                 background=[("active", "#1d4ed8")])
        style.map("Treeview",
                 background=[("selected", "#dbeafe")],
                 foreground=[("selected", "#1e293b")])
    
    def create_widgets(self):
        """Crée l'interface utilisateur."""
        main_container = ttk.Frame(self.root, style="Modern.TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # En-tête moderne avec dégradé
        header_frame = tk.Frame(main_container, bg="#ffffff", relief="flat", borderwidth=0)
        header_frame.pack(fill="x", pady=(0, 25))
        
        # Barre de couleur en haut
        top_bar = tk.Frame(header_frame, bg="#3b82f6", height=4)
        top_bar.pack(fill="x")
        
        # Contenu de l'en-tête
        content = tk.Frame(header_frame, bg="#ffffff")
        content.pack(fill="x", padx=30, pady=20)
        
        title_label = tk.Label(content, text="⚡ ALGORITHME DU MARIAGE STABLE", 
                              font=("Segoe UI", 26, "bold"), fg="#1e40af", bg="#ffffff")
        title_label.pack()
        
        subtitle = tk.Label(content, text="Affectation Étudiants-Établissements | Algorithme de Gale-Shapley",
                           font=("Segoe UI", 12), fg="#64748b", bg="#ffffff")
        subtitle.pack(pady=(5, 0))
        
        desc = tk.Label(content, text="📊 Analyse de satisfaction avec paramètre α configurable", 
                       font=("Segoe UI", 10), fg="#94a3b8", bg="#ffffff")
        desc.pack(pady=(3, 0))
        
        # Notebook
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        self.create_config_tab()
        self.create_results_tab()
        self.create_students_tab()
        self.create_universities_tab()
        self.create_assignments_tab()
    
    def add_new_simulation_button(self, parent):
        """Ajoute un bouton 'Nouvelle simulation' en bas de l'onglet."""
        button_frame = ttk.Frame(parent, style="Modern.TFrame", padding=10)
        button_frame.pack(fill="x", side="bottom")
        
        btn = tk.Button(button_frame, text="← NOUVELLE SIMULATION", 
                   font=(UI.BUTTON_FONT[0], 11, "bold"),
                   bg="#059669", fg=UI.WHITE,
                   activebackground="#047857", activeforeground=UI.WHITE,
                       cursor="hand2", relief="flat", padx=25, pady=12,
                       borderwidth=0, highlightthickness=0,
                       command=self.back_to_config)
        btn.pack(side="left", padx=5)
    
    def back_to_config(self):
        """Retour à l'onglet de configuration."""
        self.notebook.select(0)
    
    def create_config_tab(self):
        """Crée l'onglet de configuration."""
        config_frame = ttk.Frame(self.notebook, style="Modern.TFrame", padding=20)
        self.notebook.add(config_frame, text="⚙️ Paramètres")
        
        card = ttk.Frame(config_frame, style="Card.TFrame", padding=30)
        card.pack(fill="both", expand=True)
        
        ttk.Label(card, text="PARAMÈTRES DE SIMULATION", 
             font=(UI.BUTTON_FONT[0], 14, "bold"),
                 foreground="#0f172a", background=UI.WHITE).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 20))
        
        # Nombre d'étudiants
        row = 1
        ttk.Label(card, text="Nombre d'étudiants:", font=(UI.TEXT_FONT[0], 11, "bold"), 
                 foreground="#334155", background=UI.WHITE).grid(row=row, column=0, sticky="w", pady=10, padx=(0, 20))
        self.nb_students_var = tk.IntVar(value=UI.DEFAULT_NB_STUDENTS)
        ttk.Spinbox(card, from_=1, to=100, textvariable=self.nb_students_var, width=15).grid(
            row=row, column=1, sticky="w", pady=10)
        self.students_info = ttk.Label(card, text="", font=UI.SMALL_FONT, 
                           foreground=UI.GRAY, background=UI.WHITE)
        self.students_info.grid(row=row, column=2, sticky="w", padx=10)
        
        # Nombre d'établissements
        row += 1
        ttk.Label(card, text="Nombre d'établissements:", font=(UI.TEXT_FONT[0], 11, "bold"), 
                 foreground="#334155", background=UI.WHITE).grid(row=row, column=0, sticky="w", pady=10, padx=(0, 20))
        self.nb_universities_var = tk.IntVar(value=UI.DEFAULT_NB_UNIVERSITIES)
        ttk.Spinbox(card, from_=1, to=100, textvariable=self.nb_universities_var, width=15).grid(
            row=row, column=1, sticky="w", pady=10)
        self.universities_info = ttk.Label(card, text="", font=UI.SMALL_FONT, 
                          foreground=UI.GRAY, background=UI.WHITE)
        self.universities_info.grid(row=row, column=2, sticky="w", padx=10)
        
        # Séparateur
        row += 1
        ttk.Separator(card, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=20)
        
        # Paramètre Alpha
        row += 1
        ttk.Label(card, text="Satisfaction étudiants (α):", font=(UI.TEXT_FONT[0], 11, "bold"), 
             foreground="#334155", background=UI.WHITE).grid(row=row, column=0, sticky="w", pady=10, padx=(0, 20))
        
        self.alpha_var = tk.StringVar(value="flexible")
        self.custom_alpha_var = tk.StringVar()
        alpha_frame = ttk.Frame(card, style="Card.TFrame")
        alpha_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=10)
        
        for i, (name, value) in enumerate(ALPHA_PRESETS.items()):
            ttk.Radiobutton(alpha_frame, text=f"{name.capitalize()} (α={value})", 
                           variable=self.alpha_var, value=name).pack(anchor="w", pady=2)
        
        # Option personnalisée
        custom_frame = ttk.Frame(alpha_frame, style="Card.TFrame")
        custom_frame.pack(anchor="w", pady=2)
        ttk.Radiobutton(custom_frame, text="Personnalisé:", 
                       variable=self.alpha_var, value="custom").pack(side="left")
        ttk.Entry(custom_frame, textvariable=self.custom_alpha_var, width=10).pack(side="left", padx=5)
        
        # Description
        row += 1
        desc_frame = ttk.Frame(card, style="Card.TFrame")
        desc_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(20, 0))
        
        ttk.Label(desc_frame, 
             text="ℹ️ Le paramètre α contrôle la satisfaction exponentielle. Plus α est élevé, plus les étudiants préfèrent leurs premiers choix.",
             font=UI.SMALL_FONT, foreground=UI.GRAY, background=UI.WHITE,
                 wraplength=700, justify="left").pack(anchor="w")
        
        # Bouton
        row += 1
        button_frame = ttk.Frame(card, style="Card.TFrame")
        button_frame.grid(row=row, column=0, columnspan=3, pady=(30, 0))
        
        self.run_button = tk.Button(button_frame, text="LANCER LA SIMULATION", 
                        font=(UI.BUTTON_FONT[0], 12, "bold"),
                        bg="#16a34a", fg=UI.WHITE, 
                        activebackground="#15803d", activeforeground=UI.WHITE,
                                    cursor="hand2", relief="flat", padx=40, pady=18,
                                    borderwidth=0, highlightthickness=0,
                                    command=self.run_simulation)
        self.run_button.pack()
        
        # Status
        self.status_label = ttk.Label(card, text="", font=UI.TEXT_FONT, 
                         foreground=UI.SECONDARY_COLOR, background=UI.WHITE)
        self.status_label.grid(row=row+1, column=0, columnspan=3, pady=(10, 0))
    
    def create_results_tab(self):
        """Crée l'onglet de résultats."""
        results_frame = ttk.Frame(self.notebook, style="Modern.TFrame", padding=20)
        self.notebook.add(results_frame, text="📊 Résultats Globaux")
        
        # Container pour le contenu
        content_frame = ttk.Frame(results_frame, style="Modern.TFrame")
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        cards_container = ttk.Frame(content_frame, style="Modern.TFrame")
        cards_container.pack(fill="both", expand=True)
        
        # Statistiques globales
        stats_card = ttk.Frame(cards_container, style="Card.TFrame", padding=20)
        stats_card.pack(fill="x", pady=(0, 15))
        
        ttk.Label(stats_card, text="STATISTIQUES GLOBALES", 
             font=(UI.BUTTON_FONT[0], 14, "bold"),
             foreground="#0f172a", background=UI.WHITE).pack(
            anchor="w", pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_card, style="Card.TFrame")
        stats_grid.pack(fill="x")
        
        self.stat_labels = {}
        stats_info = [
            ("students", "Nombre d'étudiants", "0"),
            ("universities", "Nombre d'établissements", "0"),
            ("assigned", "Étudiants affectés", "0 / 0"),
            ("unassigned", "Non affectés", "0"),
            ("avg_students", "Satisfaction moyenne étudiants", "0%"),
            ("avg_universities", "Satisfaction moyenne établissements", "0%"),
        ]
        
        for i, (key, label, default) in enumerate(stats_info):
            row, col = i // 3, (i % 3) * 2
            ttk.Label(stats_grid, text=label + ":", font=UI.TEXT_FONT, 
                     background=UI.WHITE).grid(row=row, column=col, sticky="w", padx=10, pady=8)
            self.stat_labels[key] = ttk.Label(stats_grid, text=default, 
                                             font=(UI.BUTTON_FONT[0], 10, "bold"), 
                                             foreground=UI.PRIMARY_COLOR, background=UI.WHITE)
            self.stat_labels[key].grid(row=row, column=col+1, sticky="w", padx=10, pady=8)
        
        # Préférences - deux tableaux côte à côte
        prefs_card = ttk.Frame(cards_container, style="Card.TFrame", padding=20)
        prefs_card.pack(fill="both", expand=True)
        
        ttk.Label(prefs_card, text="CHOIX ORDONNÉS DES PRÉFÉRENCES", 
             font=(UI.BUTTON_FONT[0], 14, "bold"),
             foreground="#0f172a", background=UI.WHITE).pack(anchor="w", pady=(0, 15))
        
        columns_frame = ttk.Frame(prefs_card, style="Card.TFrame")
        columns_frame.pack(fill="both", expand=True)
        
        # Préférences étudiants (gauche)
        left_frame = ttk.Frame(columns_frame, style="Card.TFrame")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Classement des établissements par les étudiants", 
             font=(UI.BUTTON_FONT[0], 11, "bold"),
             foreground="#1e40af", background=UI.WHITE).pack(anchor="w", pady=(0, 8))
        
        self.students_prefs_tree = self.create_tree(
            left_frame,
            columns=("num", "name", "prefs"),
            headings=("#", "Étudiant", "Choix d'établissements"),
            widths=(40, 180, 420)
        )
        
        # Priorités universités (droite)
        right_frame = ttk.Frame(columns_frame, style="Card.TFrame")
        right_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        ttk.Label(right_frame, text="Classement des étudiants par les établissements", 
             font=(UI.BUTTON_FONT[0], 11, "bold"),
             foreground="#1e40af", background=UI.WHITE).pack(anchor="w", pady=(0, 8))
        
        self.universities_prefs_tree = self.create_tree(
            right_frame,
            columns=("num", "name", "prefs"),
            headings=("#", "Établissement", "Priorités"),
            widths=(40, 260, 340)
        )
        
        # Ajouter le bouton de nouvelle simulation
        self.add_new_simulation_button(results_frame)
    
    def create_students_tab(self):
        """Crée l'onglet étudiants."""
        students_frame = ttk.Frame(self.notebook, style="Modern.TFrame", padding=20)
        self.notebook.add(students_frame, text="🎓 Étudiants")
        
        content_frame = ttk.Frame(students_frame, style="Modern.TFrame")
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        card = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)
        
        ttk.Label(card, text="TOUS LES ÉTUDIANTS", 
             font=(UI.BUTTON_FONT[0], 14, "bold"),
             foreground="#0f172a", background=UI.WHITE).pack(anchor="w", pady=(0, 15))
        
        self.students_tree = self.create_tree(
            card,
            columns=("name", "university", "wish", "satisfaction"),
            headings=("Étudiant", "Établissement affecté", "Vœu", "Satisfaction"),
            widths=(220, 350, 80, 120)
        )
        
        # Ajouter le bouton de nouvelle simulation
        self.add_new_simulation_button(students_frame)
    
    def create_universities_tab(self):
        """Crée l'onglet universités."""
        universities_frame = ttk.Frame(self.notebook, style="Modern.TFrame", padding=20)
        self.notebook.add(universities_frame, text="🏛️ Établissements")
        
        content_frame = ttk.Frame(universities_frame, style="Modern.TFrame")
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        card = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)
        
        ttk.Label(card, text="TOUS LES ÉTABLISSEMENTS", 
             font=(UI.BUTTON_FONT[0], 14, "bold"),
             foreground="#0f172a", background=UI.WHITE).pack(anchor="w", pady=(0, 15))
        
        self.universities_tree = self.create_tree(
            card,
            columns=("name", "capacity", "assigned", "satisfaction", "students"),
            headings=("Établissement", "Capacité", "Affectés", "Satisfaction", "Étudiants"),
            widths=(300, 80, 80, 120, 380)
        )
        
        # Ajouter le bouton de nouvelle simulation
        self.add_new_simulation_button(universities_frame)
    
    def create_assignments_tab(self):
        """Crée l'onglet affectations détaillées."""
        assignments_frame = ttk.Frame(self.notebook, style="Modern.TFrame", padding=20)
        self.notebook.add(assignments_frame, text="✓ Affectations Détaillées")
        
        card = ttk.Frame(assignments_frame, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)
        
        ttk.Label(card, text="AFFECTATIONS DÉTAILLÉES", 
             font=(UI.BUTTON_FONT[0], 14, "bold"),
             foreground="#0f172a", background=UI.WHITE).pack(anchor="w", pady=(0, 15))
        
        self.assignments_tree = self.create_tree(
            card,
            columns=("university", "student", "wish", "priority"),
            headings=("Établissement", "Étudiant", "Vœu étudiant", "Priorité établissement"),
            widths=(350, 220, 120, 160)
        )
    
    def create_tree(self, parent, columns, headings, widths):
        """Crée un tableau avec scrollbars."""
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        
        vsb = ttk.Scrollbar(frame, orient="vertical")
        hsb = ttk.Scrollbar(frame, orient="horizontal")
        
        tree = ttk.Treeview(frame, columns=columns, show="headings",
                           yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)
        
        for col, heading, width in zip(columns, headings, widths):
            tree.heading(col, text=heading)
            tree.column(col, width=width)
        
        tree.tag_configure('oddrow', background='#f9fafb')
        tree.tag_configure('evenrow', background=UI.WHITE)
        
        return tree
    
    def load_data(self):
        """Charge les données depuis les CSV."""
        try:
            self.all_students = load_students_from_csv(STUDENTS_CSV)
            self.all_universities = load_universities_from_csv(UNIVERSITIES_CSV)
            
            self.students_info.config(text=f"({len(self.all_students)} disponibles)")
            self.universities_info.config(text=f"({len(self.all_universities)} disponibles)")
            
            if self.all_students:
                self.nb_students_var.set(min(UI.DEFAULT_NB_STUDENTS, len(self.all_students)))
            if self.all_universities:
                self.nb_universities_var.set(min(UI.DEFAULT_NB_UNIVERSITIES, len(self.all_universities)))
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les données:\n{str(e)}")
    
    def run_simulation(self):
        """Lance la simulation."""
        try:
            nb_students = self.nb_students_var.get()
            nb_universities = self.nb_universities_var.get()
            
            if nb_students > len(self.all_students) or nb_universities > len(self.all_universities):
                messagebox.showwarning("Attention", "Nombre insuffisant de données disponibles")
                return
            
            self.status_label.config(text="⏳ Simulation en cours...")
            self.run_button.config(state="disabled")
            self.root.update()
            
            # Sélection aléatoire
            selected_students = random.sample(self.all_students, nb_students)
            selected_universities = random.sample(self.all_universities, nb_universities)
            
            # Alpha
            # Alpha : priorité à la valeur personnalisée si valide
            if self.alpha_var.get() == "custom":
                custom_alpha = self.custom_alpha_var.get().strip()
                try:
                    alpha = float(custom_alpha)
                    if not (0 < alpha <= 1):
                        messagebox.showerror("Erreur", "Alpha doit être entre 0 et 1")
                        self.run_button.config(state="normal")
                        return
                except ValueError:
                    messagebox.showerror("Erreur", "Veuillez saisir une valeur numérique valide pour alpha")
                    self.run_button.config(state="normal")
                    return
            else:
                alpha_map = ALPHA_PRESETS
                alpha = alpha_map[self.alpha_var.get()]
            
            # Générer les préférences
            prefs_etud = generer_preferences_etudiants(selected_students, selected_universities)
            prefs_uni = generer_preferences_universites(selected_students, selected_universities)
            
            # Capacités
            capacites = {u.name: u.capacity for u in selected_universities}
            
            # Algorithme d'affectation
            affectations = algorithme_affectation(prefs_etud, prefs_uni, capacites)
            
            # Satisfactions
            stats = mesurer_satisfaction_globale(affectations, prefs_etud, prefs_uni, capacites, alpha)
            
            # Stocker les données
            self.simulation_data = SimulationData(
                students=selected_students,
                universities=selected_universities,
                preferences_students=prefs_etud,
                preferences_universities=prefs_uni,
                assignments=affectations,
                satisfaction_stats=stats,
                alpha=alpha
            )
            
            # Mettre à jour l'affichage
            self.update_results()
            
            # Passer aux résultats
            self.notebook.select(1)
            
            self.status_label.config(text="✅ Simulation terminée avec succès!")
            self.run_button.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la simulation:\n{str(e)}")
            self.status_label.config(text="❌ Erreur lors de la simulation")
            self.run_button.config(state="normal")
    
    def update_results(self):
        """Met à jour l'affichage des résultats."""
        if not self.simulation_data:
            return
        
        data = self.simulation_data
        assignment_map = data.assignment_map
        
        nb_assigned = len(assignment_map)
        nb_total = len(data.students)
        
        # Statistiques
        self.stat_labels["students"].config(text=str(nb_total))
        self.stat_labels["universities"].config(text=str(len(data.universities)))
        self.stat_labels["assigned"].config(text=f"{nb_assigned} / {nb_total}")
        self.stat_labels["unassigned"].config(text=str(nb_total - nb_assigned))
        self.stat_labels["avg_students"].config(
            text=f"{data.satisfaction_stats['moyenne_etudiants']:.1%}")
        self.stat_labels["avg_universities"].config(
            text=f"{data.satisfaction_stats['moyenne_universites']:.1%}")
        
        # Préférences des étudiants
        self.clear_tree(self.students_prefs_tree)
        # Créer un mapping université -> numéro
        uni_to_num = {uni.name: i+1 for i, uni in enumerate(data.universities)}
        for i, student in enumerate(data.students, 1):
            etu_name = student.full_name
            prefs = data.preferences_students.get(etu_name, [])
            prefs_nums = ", ".join([str(uni_to_num.get(uni_name, "?")) for uni_name in prefs])
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.students_prefs_tree.insert("", "end", values=(i, etu_name, prefs_nums), tags=(tag,))
        
        # Priorités des universités
        self.clear_tree(self.universities_prefs_tree)
        # Créer un mapping étudiant -> numéro
        etu_to_num = {stu.full_name: i+1 for i, stu in enumerate(data.students)}
        for i, university in enumerate(data.universities, 1):
            uni_name = university.name
            prefs = data.preferences_universities.get(uni_name, [])
            prefs_nums = ", ".join([str(etu_to_num.get(etu_name, "?")) for etu_name in prefs])
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.universities_prefs_tree.insert("", "end", values=(i, uni_name, prefs_nums), tags=(tag,))
        
        # Tous les étudiants
        self.clear_tree(self.students_tree)
        for i, student in enumerate(data.students):
            etu_name = student.full_name
            sat = data.satisfaction_stats["satisfactions_etudiants"].get(etu_name, 0.0)
            uni = assignment_map.get(etu_name, "Non affecté")
            wish = "-" if uni == "Non affecté" else str(data.preferences_students[etu_name].index(uni) + 1)
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.students_tree.insert("", "end", values=(etu_name, uni, wish, f"{sat:.1%}"), tags=(tag,))
        
        # Toutes les universités
        self.clear_tree(self.universities_tree)
        for i, university in enumerate(data.universities):
            uni_name = university.name
            sat = data.satisfaction_stats["satisfactions_universites"].get(uni_name, 0.0)
            etus = data.assignments.get(uni_name, [])
            etus_str = ", ".join(etus) if etus else "Aucun"
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.universities_tree.insert("", "end", 
                values=(uni_name, university.capacity, len(etus), f"{sat:.1%}", etus_str),
                tags=(tag,))
        
        # Affectations détaillées
        self.clear_tree(self.assignments_tree)
        i = 0
        for uni_name, etus in data.assignments.items():
            for etu_name in etus:
                wish = data.preferences_students[etu_name].index(uni_name) + 1
                priority = data.preferences_universities[uni_name].index(etu_name) + 1
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.assignments_tree.insert("", "end", 
                    values=(uni_name, etu_name, f"{wish}°", f"{priority}°"),
                    tags=(tag,))
                i += 1
    
    def clear_tree(self, tree):
        """Vide un tableau."""
        for item in tree.get_children():
            tree.delete(item)


def main():
    """Point d'entrée de l'application."""
    root = tk.Tk()
    app = ModernMatchingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
        # Container principal
