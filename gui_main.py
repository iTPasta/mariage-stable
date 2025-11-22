#!/usr/bin/env python3
"""Interface graphique moderne pour le système d'affectation."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
from typing import Optional, List, Dict
import os
import csv
from datetime import datetime
import time
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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


class ScrollableFrame(ttk.Frame):
    """Cadre scrollable vertical pour contenir beaucoup de widgets."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, background="#f8fafc")
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Contenu scrollable
        self.inner = ttk.Frame(self.canvas, style="Modern.TFrame")
        self._window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        # Ajuster la zone scrollable et la largeur
        def _on_frame_configure(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # forcer la largeur = largeur canvas
            try:
                self.canvas.itemconfigure(self._window, width=self.canvas.winfo_width())
            except Exception:
                pass

        def _on_canvas_configure(event=None):
            _on_frame_configure()

        self.inner.bind("<Configure>", _on_frame_configure)
        self.canvas.bind("<Configure>", _on_canvas_configure)

        # Défilement molette (Linux/Windows)
        def _on_mousewheel(event):
            delta = 0
            if event.num == 4:
                delta = -1
            elif event.num == 5:
                delta = 1
            elif hasattr(event, 'delta') and event.delta:
                delta = -1 if event.delta > 0 else 1
            if delta:
                self.canvas.yview_scroll(delta, "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)      # Windows/Mac
        self.canvas.bind_all("<Button-4>", _on_mousewheel)        # Linux up
        self.canvas.bind_all("<Button-5>", _on_mousewheel)        # Linux down

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
        self.multi_test_results: List[Dict] = []
        
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
        
        desc = tk.Label(content, text="📊 Analyse de satisfaction avec Normalized Rank Score", 
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
        self.create_multi_test_tab()
    
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
        config_frame = ttk.Frame(self.notebook, style="Modern.TFrame", padding=0)
        self.notebook.add(config_frame, text="⚙️ Paramètres")

        # Cadre scrollable pour rendre tout le contenu visible
        outer = ttk.Frame(config_frame, style="Modern.TFrame", padding=20)
        outer.pack(fill="both", expand=True)
        scroll = ScrollableFrame(outer)
        scroll.pack(fill="both", expand=True)

        card = ttk.Frame(scroll.inner, style="Card.TFrame", padding=30)
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
        ttk.Spinbox(card, from_=1, to=1000, textvariable=self.nb_students_var, width=15).grid(
            row=row, column=1, sticky="w", pady=10)
        self.students_info = ttk.Label(card, text="", font=UI.SMALL_FONT, 
                           foreground=UI.GRAY, background=UI.WHITE)
        self.students_info.grid(row=row, column=2, sticky="w", padx=10)
        
        # Nombre d'établissements
        row += 1
        ttk.Label(card, text="Nombre d'établissements:", font=(UI.TEXT_FONT[0], 11, "bold"), 
                 foreground="#334155", background=UI.WHITE).grid(row=row, column=0, sticky="w", pady=10, padx=(0, 20))
        self.nb_universities_var = tk.IntVar(value=UI.DEFAULT_NB_UNIVERSITIES)
        ttk.Spinbox(card, from_=1, to=1000, textvariable=self.nb_universities_var, width=15).grid(
            row=row, column=1, sticky="w", pady=10)
        self.universities_info = ttk.Label(card, text="", font=UI.SMALL_FONT, 
                          foreground=UI.GRAY, background=UI.WHITE)
        self.universities_info.grid(row=row, column=2, sticky="w", padx=10)

        # Séparateur
        row += 1
        ttk.Separator(card, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=20)

        # ===== Préférences manuelles (déplacé en haut) =====
        row += 1
        ttk.Label(card, text="PRÉFÉRENCES MANUELLES (optionnel)", 
             font=(UI.BUTTON_FONT[0], 14, "bold"),
             foreground="#0f172a", background=UI.WHITE).grid(
            row=row, column=0, columnspan=3, sticky="w", pady=(0, 10))

        row += 1
        self.manual_mode_var = tk.BooleanVar(value=False)
        manual_toggle = ttk.Checkbutton(card, text="Configurer les préférences moi-même (ordre des choix)",
                        variable=self.manual_mode_var, command=self.toggle_manual_prefs)
        manual_toggle.grid(row=row, column=0, columnspan=3, sticky="w", pady=(0, 10))

        row += 1
        # Conteneur repliable pour l'édition manuelle
        self.manual_prefs_frame = ttk.Frame(card, style="Card.TFrame")
        self.manual_prefs_frame.grid(row=row, column=0, columnspan=3, sticky="nsew")
        self.manual_prefs_frame.grid_remove()

        # Infos sélection
        info_frame = ttk.Frame(self.manual_prefs_frame, style="Card.TFrame", padding=10)
        info_frame.pack(fill="x")
        self.manual_info_label = ttk.Label(info_frame, text="Sélection actuelle: 0 étudiants, 0 établissements",
                           font=UI.SMALL_FONT, foreground=UI.GRAY, background=UI.WHITE)
        self.manual_info_label.pack(anchor="w")

        # Aide + mapping
        help_label = ttk.Label(self.manual_prefs_frame,
            text="Saisie par ligne et Entrée\nÉtudiants → 1: a,b,c (1..N)\nÉtablissements → a: 3,1,2 (a..)",
            font=UI.SMALL_FONT, foreground=UI.GRAY, background=UI.WHITE, justify="left")
        help_label.pack(anchor="w", pady=(6, 0))

        self.manual_mapping_label = ttk.Label(self.manual_prefs_frame, text="", font=UI.SMALL_FONT,
                                              foreground="#334155", background=UI.WHITE, justify="left")
        self.manual_mapping_label.pack(anchor="w", pady=(6, 8))

        # Deux barres de saisie (étudiants / établissements)
        text_container = ttk.Frame(self.manual_prefs_frame, style="Card.TFrame")
        text_container.pack(fill="x")

        left_text = ttk.Frame(text_container, style="Card.TFrame")
        left_text.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Label(left_text, text="Étudiants (ex: 1: a,b,c)", font=UI.TEXT_FONT, background=UI.WHITE).pack(anchor="w")
        self.student_line_var = tk.StringVar()
        self.student_line_entry = ttk.Entry(left_text, textvariable=self.student_line_var)
        self.student_line_entry.pack(fill="x")
        self.student_line_entry.bind('<Return>', self.on_student_line_enter)
        self.student_line_info = ttk.Label(left_text, text="", font=UI.SMALL_FONT, foreground=UI.GRAY, background=UI.WHITE)
        self.student_line_info.pack(anchor="w", pady=(4,0))

        right_text = ttk.Frame(text_container, style="Card.TFrame")
        right_text.pack(side="left", fill="x", expand=True, padx=(6, 0))
        ttk.Label(right_text, text="Établissements (ex: a: 3,1,2)", font=UI.TEXT_FONT, background=UI.WHITE).pack(anchor="w")
        self.university_line_var = tk.StringVar()
        self.university_line_entry = ttk.Entry(right_text, textvariable=self.university_line_var)
        self.university_line_entry.pack(fill="x")
        self.university_line_entry.bind('<Return>', self.on_university_line_enter)
        self.university_line_info = ttk.Label(right_text, text="", font=UI.SMALL_FONT, foreground=UI.GRAY, background=UI.WHITE)
        self.university_line_info.pack(anchor="w", pady=(4,0))

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

        # Données internes pour le mode manuel
        self.manual_students = []
        self.manual_universities = []
        self.custom_prefs_students = {}
        self.custom_prefs_universities = {}

        # Traces pour mettre à jour l'éditeur quand les nombres changent
        try:
            self.nb_students_var.trace_add('write', lambda *args: self.refresh_manual_entities())
            self.nb_universities_var.trace_add('write', lambda *args: self.refresh_manual_entities())
        except Exception:
            # Compat older Tk versions
            self.nb_students_var.trace('w', lambda *args: self.refresh_manual_entities())
            self.nb_universities_var.trace('w', lambda *args: self.refresh_manual_entities())
    
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
        self.notebook.add(students_frame, text="🎓 Sat. Étudiants")
        
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
        self.notebook.add(universities_frame, text="🏛️ Sat. Établissements")
        
        content_frame = ttk.Frame(universities_frame, style="Modern.TFrame")
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        card = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)
        
        ttk.Label(card, text="TOUS LES ÉTABLISSEMENTS", 
             font=(UI.BUTTON_FONT[0], 14, "bold"),
             foreground="#0f172a", background=UI.WHITE).pack(anchor="w", pady=(0, 15))
        
        self.universities_tree = self.create_tree(
            card,
            columns=("name", "student", "rank", "satisfaction"),
            headings=("Établissement", "Étudiant", "Rang", "Satisfaction"),
            widths=(300, 300, 100, 150)
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
            
            # Sélection des entités
            if self.manual_mode_var.get():
                # Utiliser la sélection déterministe/éditée
                if len(self.manual_students) < nb_students or len(self.manual_universities) < nb_universities:
                    messagebox.showwarning("Attention", "Les listes manuelles ne sont pas prêtes. Elles seront complétées automatiquement.")
                selected_students = self.manual_students[:nb_students] or self.all_students[:nb_students]
                selected_universities = self.manual_universities[:nb_universities] or self.all_universities[:nb_universities]
            else:
                # Sélection aléatoire
                selected_students = random.sample(self.all_students, nb_students)
                selected_universities = random.sample(self.all_universities, nb_universities)
            
            # Générer les préférences (aléatoires ou manuelles)
            if self.manual_mode_var.get():
                prefs_etud = self.build_manual_student_prefs(selected_students, selected_universities)
                prefs_uni = self.build_manual_university_prefs(selected_students, selected_universities)
            else:
                prefs_etud = generer_preferences_etudiants(selected_students, selected_universities)
                prefs_uni = generer_preferences_universites(selected_students, selected_universities)
            
            # Capacités
            capacites = {u.name: u.capacity for u in selected_universities}
            
            # Algorithme d'affectation
            affectations = algorithme_affectation(prefs_etud, prefs_uni, capacites)
            
            # Satisfactions
            stats = mesurer_satisfaction_globale(affectations, prefs_etud, prefs_uni, capacites)
            
            # Stocker les données
            self.simulation_data = SimulationData(
                students=selected_students,
                universities=selected_universities,
                preferences_students=prefs_etud,
                preferences_universities=prefs_uni,
                assignments=affectations,
                satisfaction_stats=stats
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

    # =====================
    # Préférences manuelles
    # =====================
    def toggle_manual_prefs(self):
        if self.manual_mode_var.get():
            self.manual_prefs_frame.grid()
            self.refresh_manual_entities()
        else:
            self.manual_prefs_frame.grid_remove()

    # plus de bascule de mode: saisie texte uniquement

    def refresh_manual_entities(self):
        if not self.manual_mode_var.get():
            return
        nb_s = self.nb_students_var.get()
        nb_u = self.nb_universities_var.get()
        # Construire listes déterministes (premiers de la liste chargée)
        self.manual_students = self.all_students[:nb_s]
        self.manual_universities = self.all_universities[:nb_u]
        self.manual_info_label.config(text=f"Sélection actuelle: {len(self.manual_students)} étudiants, {len(self.manual_universities)} établissements")

        # Initialiser les dicts si vides
        uni_names = [u.name for u in self.manual_universities]
        etu_names = [e.full_name for e in self.manual_students]
        for e in etu_names:
            self.custom_prefs_students.setdefault(e, uni_names.copy())
            # Nettoyer pour ne garder que ceux existants et dans l'ordre actuel
            self.custom_prefs_students[e] = [x for x in self.custom_prefs_students[e] if x in uni_names]
            for x in uni_names:
                if x not in self.custom_prefs_students[e]:
                    self.custom_prefs_students[e].append(x)
        for u in uni_names:
            self.custom_prefs_universities.setdefault(u, etu_names.copy())
            self.custom_prefs_universities[u] = [x for x in self.custom_prefs_universities[u] if x in etu_names]
            for x in etu_names:
                if x not in self.custom_prefs_universities[u]:
                    self.custom_prefs_universities[u].append(x)

        # plus de sélecteurs visuels à rafraîchir (mode texte)

        # Mettre à jour le mapping pour la saisie texte
        try:
            letters = [chr(ord('a') + i) for i in range(len(self.manual_universities))]
        except Exception:
            letters = []
        mapping_lines = []
        mapping_lines.append("Index étudiants ↔ noms:")
        for i, s in enumerate(self.manual_students, start=1):
            mapping_lines.append(f"  {i} = {s.full_name}")
        mapping_lines.append("Lettres établissements ↔ noms:")
        for i, u in enumerate(self.manual_universities):
            if i < 26:
                mapping_lines.append(f"  {letters[i]} = {u.name}")
        mapping_text = "\n".join(mapping_lines)
        if hasattr(self, 'manual_mapping_label'):
            self.manual_mapping_label.config(text=mapping_text)

    # pré-remplissage non nécessaire dans le mode barre unique

    # parsing ligne par ligne via on_student_line_enter / on_university_line_enter

    def on_student_line_enter(self, event=None):
        line = (self.student_line_var.get() or '').strip()
        if not line or ':' not in line:
            self.student_line_info.config(text="Format attendu: 1: a,b,c")
            return
        left, right = line.split(':', 1)
        idx = left.strip()
        order_letters = [t.strip().lower() for t in right.split(',') if t.strip()]
        # mapping
        try:
            idx_int = int(idx)
        except ValueError:
            self.student_line_info.config(text="L'identifiant étudiant doit être un entier (ex: 1)")
            return
        if idx_int < 1 or idx_int > len(self.manual_students):
            self.student_line_info.config(text="Indice étudiant hors sélection")
            return
        stu_name = self.manual_students[idx_int - 1].full_name
        letters = [chr(ord('a') + i) for i in range(min(len(self.manual_universities), 26))]
        uni_letter_to_name = {l: self.manual_universities[i].name for i, l in enumerate(letters)}
        # filtrer et compléter
        seen = []
        for l in order_letters:
            if l in uni_letter_to_name and l not in seen:
                seen.append(l)
        for l in letters:
            if l not in seen:
                seen.append(l)
        self.custom_prefs_students[stu_name] = [uni_letter_to_name[l] for l in seen]
        # clear
        self.student_line_var.set('')
        self.student_line_info.config(text=f"Enregistré pour étudiant {idx} → {','.join(order_letters) if order_letters else 'tous'}")

    def on_university_line_enter(self, event=None):
        line = (self.university_line_var.get() or '').strip()
        if not line or ':' not in line:
            self.university_line_info.config(text="Format attendu: a: 3,1,2")
            return
        left, right = line.split(':', 1)
        letter = (left.strip().lower() or '')
        order_idxs = [t.strip() for t in right.split(',') if t.strip()]
        # mapping
        letters = [chr(ord('a') + i) for i in range(min(len(self.manual_universities), 26))]
        if letter not in letters:
            self.university_line_info.config(text="Lettre établissement hors sélection (a..)")
            return
        uni_name = self.manual_universities[letters.index(letter)].name
        # filtrer et compléter
        n_s = len(self.manual_students)
        idx_set = set(str(i) for i in range(1, n_s+1))
        seen = []
        for i in order_idxs:
            if i in idx_set and i not in seen:
                seen.append(i)
        for i in range(1, n_s+1):
            si = str(i)
            if si not in seen:
                seen.append(si)
        self.custom_prefs_universities[uni_name] = [self.manual_students[int(i)-1].full_name for i in seen]
        # clear
        self.university_line_var.set('')
        self.university_line_info.config(text=f"Enregistré pour établi. {letter} → {','.join(order_idxs) if order_idxs else 'tous'}")

    def load_student_prefs(self, etu_name: str):
        self.student_prefs_listbox.delete(0, tk.END)
        for uni in self.custom_prefs_students.get(etu_name, []):
            self.student_prefs_listbox.insert(tk.END, uni)

    def load_university_prefs(self, uni_name: str):
        self.university_prefs_listbox.delete(0, tk.END)
        for etu in self.custom_prefs_universities.get(uni_name, []):
            self.university_prefs_listbox.insert(tk.END, etu)

    def on_select_student(self, event=None):
        name = self.student_selector.get()
        if name:
            self.load_student_prefs(name)

    def on_select_university(self, event=None):
        name = self.university_selector.get()
        if name:
            self.load_university_prefs(name)

    def move_item(self, listbox: tk.Listbox, delta: int, who: str):
        cur = listbox.curselection()
        if not cur:
            return
        idx = cur[0]
        new_idx = idx + delta
        if new_idx < 0 or new_idx >= listbox.size():
            return
        val = listbox.get(idx)
        listbox.delete(idx)
        listbox.insert(new_idx, val)
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(new_idx)
        listbox.activate(new_idx)
        self.persist_listbox_order(who)

    def randomize_order(self, who: str):
        import random as _r
        if who == "student":
            etu = self.student_selector.get()
            if not etu:
                return
            items = list(self.custom_prefs_students.get(etu, []))
            _r.shuffle(items)
            self.custom_prefs_students[etu] = items
            self.load_student_prefs(etu)
        else:
            uni = self.university_selector.get()
            if not uni:
                return
            items = list(self.custom_prefs_universities.get(uni, []))
            _r.shuffle(items)
            self.custom_prefs_universities[uni] = items
            self.load_university_prefs(uni)

    def reset_order(self, who: str):
        if who == "student":
            etu = self.student_selector.get()
            if not etu:
                return
            uni_names = [u.name for u in self.manual_universities]
            self.custom_prefs_students[etu] = uni_names.copy()
            self.load_student_prefs(etu)
        else:
            uni = self.university_selector.get()
            if not uni:
                return
            etu_names = [e.full_name for e in self.manual_students]
            self.custom_prefs_universities[uni] = etu_names.copy()
            self.load_university_prefs(uni)

    def persist_listbox_order(self, who: str):
        if who == "student":
            etu = self.student_selector.get()
            if not etu:
                return
            items = [self.student_prefs_listbox.get(i) for i in range(self.student_prefs_listbox.size())]
            self.custom_prefs_students[etu] = items
        else:
            uni = self.university_selector.get()
            if not uni:
                return
            items = [self.university_prefs_listbox.get(i) for i in range(self.university_prefs_listbox.size())]
            self.custom_prefs_universities[uni] = items

    def build_manual_student_prefs(self, selected_students, selected_universities):
        uni_names = [u.name for u in selected_universities]
        result = {}
        for s in selected_students:
            order = self.custom_prefs_students.get(s.full_name, uni_names.copy())
            # Compléter pour garantir permutation
            order = [x for x in order if x in uni_names]
            for x in uni_names:
                if x not in order:
                    order.append(x)
            result[s.full_name] = order
        return result

    def build_manual_university_prefs(self, selected_students, selected_universities):
        etu_names = [e.full_name for e in selected_students]
        result = {}
        for u in selected_universities:
            order = self.custom_prefs_universities.get(u.name, etu_names.copy())
            order = [x for x in order if x in etu_names]
            for x in etu_names:
                if x not in order:
                    order.append(x)
            result[u.name] = order
        return result
    
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
        row_index = 0
        for university in data.universities:
            uni_name = university.name
            sat = data.satisfaction_stats["satisfactions_universites"].get(uni_name, 0.0)
            etus = data.assignments.get(uni_name, [])
            prefs_uni = data.preferences_universities.get(uni_name, [])
            
            if etus:
                # Afficher une ligne par étudiant affecté avec son rang
                for etu_name in etus:
                    if etu_name in prefs_uni:
                        rang = prefs_uni.index(etu_name) + 1
                    else:
                        rang = "?"
                    tag = 'evenrow' if row_index % 2 == 0 else 'oddrow'
                    self.universities_tree.insert("", "end", 
                        values=(uni_name, etu_name, f"{rang}°", f"{sat:.1%}"),
                        tags=(tag,))
                    row_index += 1
            else:
                # Si aucun étudiant affecté, afficher une ligne vide
                tag = 'evenrow' if row_index % 2 == 0 else 'oddrow'
                self.universities_tree.insert("", "end", 
                    values=(uni_name, "Aucun", "-", f"{sat:.1%}"),
                    tags=(tag,))
                row_index += 1
        
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
    
    def create_multi_test_tab(self):
        """Crée l'onglet de tests multiples."""
        multi_test_frame = ttk.Frame(self.notebook, style="Modern.TFrame", padding=20)
        self.notebook.add(multi_test_frame, text="🧪 Tests Multiples")
        
        # Container pour le contenu avec grille
        content_frame = ttk.Frame(multi_test_frame, style="Modern.TFrame")
        content_frame.pack(fill="both", expand=True)
        content_frame.grid_rowconfigure(1, weight=3)  # Tableau prend 3 fois l'espace
        content_frame.grid_rowconfigure(2, weight=7)  # Courbe prend 7 fois l'espace
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Card de configuration (compacte)
        config_card = ttk.Frame(content_frame, style="Card.TFrame", padding=15)
        config_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(config_card, text="CONFIGURATION - TESTS DE PERFORMANCE", 
             font=(UI.BUTTON_FONT[0], 12, "bold"),
             foreground="#0f172a", background=UI.WHITE).pack(anchor="w", pady=(0, 5))
        
        ttk.Label(config_card, text="Mesure le temps d'exécution et la complexité avec différentes tailles", 
             font=UI.SMALL_FONT, foreground=UI.GRAY, background=UI.WHITE).pack(anchor="w", pady=(0, 10))
        
        # Grille de configuration (compacte)
        config_grid = ttk.Frame(config_card, style="Card.TFrame")
        config_grid.pack(fill="x")
        
        # Mode de test
        ttk.Label(config_grid, text="Mode:", font=(UI.TEXT_FONT[0], 10, "bold"), 
                 background=UI.WHITE).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.test_mode_var = tk.StringVar(value="simple")
        
        mode_frame = ttk.Frame(config_grid, style="Card.TFrame")
        mode_frame.grid(row=0, column=1, columnspan=2, sticky="w", pady=5)
        ttk.Radiobutton(mode_frame, text="Taille fixe", variable=self.test_mode_var, 
                       value="simple", command=self.toggle_test_mode).pack(side="left", padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="Scalabilité", variable=self.test_mode_var, 
                       value="scalability", command=self.toggle_test_mode).pack(side="left")
        
        # Ligne unique pour les options
        options_frame = ttk.Frame(config_grid, style="Card.TFrame")
        options_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Options pour mode simple
        self.simple_frame = ttk.Frame(options_frame, style="Card.TFrame")
        self.simple_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(self.simple_frame, text="Étudiants:", font=UI.TEXT_FONT, 
                 background=UI.WHITE).pack(side="left", padx=(10, 5))
        self.multi_nb_students_var = tk.IntVar(value=100)
        ttk.Spinbox(self.simple_frame, from_=5, to=1000, textvariable=self.multi_nb_students_var, width=10).pack(side="left", padx=5)
        
        ttk.Label(self.simple_frame, text="Établissements:", font=UI.TEXT_FONT, 
                 background=UI.WHITE).pack(side="left", padx=(15, 5))
        self.multi_nb_universities_var = tk.IntVar(value=100)
        ttk.Spinbox(self.simple_frame, from_=5, to=1000, textvariable=self.multi_nb_universities_var, width=10).pack(side="left", padx=5)
        
        ttk.Label(self.simple_frame, text="Répétitions:", font=UI.TEXT_FONT, 
                 background=UI.WHITE).pack(side="left", padx=(15, 5))
        self.multi_repetitions_var = tk.IntVar(value=10)
        ttk.Spinbox(self.simple_frame, from_=1, to=100, textvariable=self.multi_repetitions_var, width=10).pack(side="left", padx=5)
        
        # Options pour mode scalabilité
        self.scalability_frame = ttk.Frame(options_frame, style="Card.TFrame")
        self.scalability_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(self.scalability_frame, text="Tailles à tester:", font=UI.TEXT_FONT, 
                 background=UI.WHITE).pack(side="left", padx=(10, 5))
        self.sizes_var = tk.StringVar(value="10, 50, 100, 200, 500, 1000")
        ttk.Entry(self.scalability_frame, textvariable=self.sizes_var, width=35).pack(side="left", padx=5)
        
        ttk.Label(self.scalability_frame, text="Répétitions par taille:", font=UI.TEXT_FONT, 
                 background=UI.WHITE).pack(side="left", padx=(15, 5))
        self.scalability_repetitions_var = tk.IntVar(value=5)
        ttk.Spinbox(self.scalability_frame, from_=1, to=50, textvariable=self.scalability_repetitions_var, width=10).pack(side="left", padx=5)
        
        # Cacher le mode scalabilité par défaut
        self.scalability_frame.pack_forget()
        
        # Boutons (compacts)
        button_frame = ttk.Frame(config_card, style="Card.TFrame")
        button_frame.pack(pady=(10, 0))
        
        self.multi_run_button = tk.Button(button_frame, text="🚀 LANCER", 
                        font=(UI.BUTTON_FONT[0], 10, "bold"),
                        bg="#7c3aed", fg=UI.WHITE, 
                        activebackground="#6d28d9", activeforeground=UI.WHITE,
                        cursor="hand2", relief="flat", padx=20, pady=10,
                        borderwidth=0, highlightthickness=0,
                        command=self.run_multi_test)
        self.multi_run_button.pack(side="left", padx=3)
        
        self.multi_export_button = tk.Button(button_frame, text="💾 EXPORTER", 
                        font=(UI.BUTTON_FONT[0], 10, "bold"),
                        bg="#059669", fg=UI.WHITE, 
                        activebackground="#047857", activeforeground=UI.WHITE,
                        cursor="hand2", relief="flat", padx=20, pady=10,
                        borderwidth=0, highlightthickness=0,
                        command=self.export_multi_test_results,
                        state="disabled")
        self.multi_export_button.pack(side="left", padx=3)
        
        # Status
        self.multi_status_label = ttk.Label(config_card, text="", font=UI.SMALL_FONT, 
                         foreground=UI.SECONDARY_COLOR, background=UI.WHITE)
        self.multi_status_label.pack(pady=(5, 0))
        
        # Card de résultats (prend tout l'espace restant)
        results_card = ttk.Frame(content_frame, style="Card.TFrame", padding=15)
        results_card.grid(row=1, column=0, sticky="nsew")
        
        ttk.Label(results_card, text="RÉSULTATS", 
             font=(UI.BUTTON_FONT[0], 12, "bold"),
             foreground="#0f172a", background=UI.WHITE).pack(anchor="w", pady=(0, 10))
        
        self.multi_results_tree = self.create_tree(
            results_card,
            columns=("test", "nb_etu", "nb_uni", "sat_etu", "sat_uni", "temps", "complexite"),
            headings=("Test #", "Étudiants", "Établ.", "Sat. Étu.", "Sat. Établ.", "Temps (ms)", "Complexité"),
            widths=(70, 100, 100, 120, 130, 110, 140)
        )
        
        # Card pour la courbe (séparée avec plus d'espace)
        curve_card = ttk.Frame(content_frame, style="Card.TFrame", padding=15)
        curve_card.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        
        ttk.Label(curve_card, text="COURBE DE SATISFACTION", 
             font=(UI.BUTTON_FONT[0], 12, "bold"),
             foreground="#0f172a", background=UI.WHITE).pack(anchor="w", pady=(0, 10))
        
        # Bouton pour afficher la courbe
        self.show_curve_button = tk.Button(curve_card, text="📈 Afficher la courbe", 
                        font=(UI.BUTTON_FONT[0], 10, "bold"),
                        bg="#2563eb", fg=UI.WHITE, 
                        activebackground="#1d4ed8", activeforeground=UI.WHITE,
                        cursor="hand2", relief="flat", padx=20, pady=10,
                        borderwidth=0, highlightthickness=0,
                        command=self.show_satisfaction_curve,
                        state="disabled")
        self.show_curve_button.pack(pady=(0, 10))
        
        # Zone pour afficher la courbe
        self.curve_frame = ttk.Frame(curve_card, style="Card.TFrame")
        self.curve_frame.pack(fill="both", expand=True)
    
    def toggle_test_mode(self):
        """Bascule entre les modes de test."""
        if self.test_mode_var.get() == "simple":
            self.scalability_frame.pack_forget()
            self.simple_frame.pack(side="left", fill="x", expand=True)
        else:
            self.simple_frame.pack_forget()
            self.scalability_frame.pack(side="left", fill="x", expand=True)
    
    def run_multi_test(self):
        """Lance les tests multiples."""
        try:
            mode = self.test_mode_var.get()
            
            # Vider les résultats précédents
            self.multi_test_results = []
            self.clear_tree(self.multi_results_tree)
            
            # Réinitialiser les données pour la courbe
            self.sat_students_list = []
            self.sat_universities_list = []
            self.sizes_list = []
            
            # Nettoyer la zone de courbe
            for widget in self.curve_frame.winfo_children():
                widget.destroy()
            
            self.multi_status_label.config(text="⏳ Tests en cours...")
            self.multi_run_button.config(state="disabled")
            self.multi_export_button.config(state="disabled")
            self.show_curve_button.config(state="disabled")
            self.root.update()
            
            test_num = 1
            
            if mode == "simple":
                # Mode simple : une seule taille
                nb_students = self.multi_nb_students_var.get()
                nb_universities = self.multi_nb_universities_var.get()
                repetitions = self.multi_repetitions_var.get()
                
                if nb_students > len(self.all_students) or nb_universities > len(self.all_universities):
                    messagebox.showwarning("Attention", "Nombre insuffisant de données disponibles")
                    self.multi_run_button.config(state="normal")
                    return
                
                test_num = self._run_tests_for_size(nb_students, nb_universities, repetitions, test_num)
                
            else:
                # Mode scalabilité : plusieurs tailles
                sizes_str = self.sizes_var.get()
                try:
                    sizes = [int(s.strip()) for s in sizes_str.split(',')]
                except:
                    messagebox.showerror("Erreur", "Format invalide pour les tailles (utilisez: 10, 50, 100)")
                    self.multi_run_button.config(state="normal")
                    return
                
                repetitions = self.scalability_repetitions_var.get()
                
                for size in sizes:
                    if size > len(self.all_students) or size > len(self.all_universities):
                        messagebox.showwarning("Attention", f"Taille {size} ignorée: données insuffisantes")
                        continue
                    
                    test_num = self._run_tests_for_size(size, size, repetitions, test_num)
            
            self.multi_status_label.config(
                text=f"✅ {len(self.multi_test_results)} tests terminés avec succès!")
            self.multi_run_button.config(state="normal")
            self.multi_export_button.config(state="normal")
            self.show_curve_button.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors des tests:\n{str(e)}")
            self.multi_status_label.config(text="❌ Erreur lors des tests")
            self.multi_run_button.config(state="normal")
    
    def _run_tests_for_size(self, nb_students, nb_universities, repetitions, test_num):
        """Lance les tests pour une taille donnée."""
        for rep in range(repetitions):
            # Sélection aléatoire pour cette répétition
            selected_students = random.sample(self.all_students, nb_students)
            selected_universities = random.sample(self.all_universities, nb_universities)
            
            # Générer les préférences
            prefs_etud = generer_preferences_etudiants(selected_students, selected_universities)
            prefs_uni = generer_preferences_universites(selected_students, selected_universities)
            capacites = {u.name: u.capacity for u in selected_universities}
            
            # Mesurer le temps d'exécution
            start_time = time.time()
            affectations = algorithme_affectation(prefs_etud, prefs_uni, capacites)
            end_time = time.time()
            exec_time_ms = (end_time - start_time) * 1000
            
            # Satisfactions
            stats = mesurer_satisfaction_globale(affectations, prefs_etud, prefs_uni, capacites)
            
            # Stocker les données pour la courbe
            self.sat_students_list.append(stats["moyenne_etudiants"])
            self.sat_universities_list.append(stats["moyenne_universites"])
            self.sizes_list.append(nb_students)
            
            # Compter les non affectés
            nb_assigned = sum(len(students) for students in affectations.values())
            nb_unassigned = nb_students - nb_assigned
            
            # Calculer la complexité théorique: O(n²) où n est le nombre d'étudiants
            complexite_theorique = nb_students * nb_students
            # Calculer la complexité observée (temps / opérations théoriques)
            complexite_observee = exec_time_ms / complexite_theorique if complexite_theorique > 0 else 0
            
            # Stocker les résultats
            result = {
                "test_num": test_num,
                "repetition": rep + 1,
                "nb_students": nb_students,
                "nb_universities": nb_universities,
                "sat_students": stats["moyenne_etudiants"],
                "sat_universities": stats["moyenne_universites"],
                "nb_unassigned": nb_unassigned,
                "exec_time_ms": exec_time_ms,
                "complexite_theorique": complexite_theorique,
                "complexite_observee": complexite_observee,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.multi_test_results.append(result)
            
            # Afficher dans le tableau
            tag = 'evenrow' if (test_num - 1) % 2 == 0 else 'oddrow'
            self.multi_results_tree.insert("", "end", 
                values=(
                    test_num,
                    nb_students,
                    nb_universities,
                    f"{stats['moyenne_etudiants']:.1%}",
                    f"{stats['moyenne_universites']:.1%}",
                    f"{exec_time_ms:.2f}",
                    f"{complexite_observee:.6f} ms/n²"
                ),
                tags=(tag,))
            
            test_num += 1
            self.root.update()
        
        return test_num
    
    def show_satisfaction_curve(self):
        """Affiche la courbe de comparaison satisfaction étudiants vs universités."""
        # Nettoyer la zone
        for widget in self.curve_frame.winfo_children():
            widget.destroy()
        
        if not self.sat_students_list or not self.sat_universities_list:
            ttk.Label(self.curve_frame, text="Aucune donnée à afficher", 
                     font=UI.SMALL_FONT, background=UI.WHITE).pack(pady=20)
            return
        
        # Créer la figure matplotlib
        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Tracer les courbes
        ax.plot(range(1, len(self.sat_students_list) + 1), 
                [s * 100 for s in self.sat_students_list], 
                marker='o', linewidth=2, markersize=6, 
                color='#3b82f6', label='Satisfaction Étudiants')
        ax.plot(range(1, len(self.sat_universities_list) + 1), 
                [s * 100 for s in self.sat_universities_list], 
                marker='s', linewidth=2, markersize=6, 
                color='#10b981', label='Satisfaction Établissements')
        
        # Configuration du graphique
        ax.set_xlabel('Numéro de test', fontsize=10)
        ax.set_ylabel('Satisfaction (%)', fontsize=10)
        ax.set_title('Comparaison Satisfaction Étudiants vs Établissements', 
                    fontsize=12, fontweight='bold', pad=15)
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(0, 100)
        
        fig.tight_layout()
        
        # Intégrer dans tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.curve_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def export_multi_test_results(self):
        """Exporte les résultats des tests multiples en CSV."""
        if not self.multi_test_results:
            messagebox.showwarning("Attention", "Aucun résultat à exporter")
            return
        
        try:
            # Demander où sauvegarder
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"tests_multiples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return
            
            # Écrire le CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Test", "Répétition", "Nb_Étudiants", "Nb_Établissements", 
                    "Satisfaction_Étudiants", "Satisfaction_Établissements", 
                    "Non_Affectés", "Temps_Execution_ms", "Complexite_Theorique", "Complexite_Observee",
                    "Timestamp"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for result in self.multi_test_results:
                    writer.writerow({
                        "Test": result["test_num"],
                        "Répétition": result["repetition"],
                        "Nb_Étudiants": result["nb_students"],
                        "Nb_Établissements": result["nb_universities"],
                        "Satisfaction_Étudiants": f"{result['sat_students']:.4f}",
                        "Satisfaction_Établissements": f"{result['sat_universities']:.4f}",
                        "Non_Affectés": result["nb_unassigned"],
                        "Temps_Execution_ms": f"{result['exec_time_ms']:.2f}",
                        "Complexite_Theorique": result["complexite_theorique"],
                        "Complexite_Observee": f"{result['complexite_observee']:.8f}",
                        "Timestamp": result["timestamp"]
                    })
            
            messagebox.showinfo("Succès", f"Résultats exportés vers:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{str(e)}")


def main():
    """Point d'entrée de l'application."""
    root = tk.Tk()
    app = ModernMatchingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
        # Container principal
