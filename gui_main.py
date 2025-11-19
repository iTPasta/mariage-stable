#!/usr/bin/env python3
"""Interface graphique moderne pour le système d'affectation."""
import tkinter as tk
from tkinter import ttk, messagebox
import random
from typing import Optional

from models import Student, University, SimulationData, StudentKey, UniversityKey
from data.data_loader import load_students_from_csv, load_universities_from_csv
from preferences import generer_preferences_etudiants, generer_preferences_universites
from matching import algorithme_affectation
from satisfaction import mesurer_satisfaction_globale
from config import AppConfig


class ModernMatchingApp:
    """Application GUI moderne pour le matching d'affectation."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🎓 Système d'Affectation - Mariage Stable")
        self.root.geometry(f"{AppConfig.UI.WINDOW_WIDTH}x{AppConfig.UI.WINDOW_HEIGHT}")
        self.root.configure(bg=AppConfig.UI.BG_COLOR)
        
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
        
        style.configure("Title.TLabel", 
                       font=AppConfig.UI.TITLE_FONT, 
                       foreground=AppConfig.UI.PRIMARY_COLOR, 
                       background=AppConfig.UI.BG_COLOR)
        style.configure("Subtitle.TLabel", 
                       font=AppConfig.UI.SUBTITLE_FONT, 
                       foreground=AppConfig.UI.TEXT_COLOR, 
                       background=AppConfig.UI.BG_COLOR)
        style.configure("Header.TLabel", 
                       font=AppConfig.UI.HEADER_FONT, 
                       foreground=AppConfig.UI.TEXT_COLOR, 
                       background=AppConfig.UI.WHITE)
        style.configure("Modern.TFrame", background=AppConfig.UI.BG_COLOR)
        style.configure("Card.TFrame", background=AppConfig.UI.WHITE, relief="flat")
        
        # Treeview moderne
        style.configure("Treeview", 
                       background=AppConfig.UI.WHITE,
                       foreground="#1e293b",
                       fieldbackground=AppConfig.UI.WHITE,
                       font=(AppConfig.UI.TEXT_FONT[0], 10),
                       rowheight=28)
        style.configure("Treeview.Heading", 
                       font=(AppConfig.UI.BUTTON_FONT[0], 10, "bold"),
                       background="#1e40af",
                       foreground=AppConfig.UI.WHITE,
                       relief="flat")
        style.map("Treeview.Heading",
                 background=[("active", "#1e3a8a")])
    
    def create_widgets(self):
        """Crée l'interface utilisateur."""
        main_container = ttk.Frame(self.root, style="Modern.TFrame")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # En-tête
        header_frame = ttk.Frame(main_container, style="Modern.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="SYSTÈME D'AFFECTATION PAR MARIAGE STABLE", 
                              font=("Segoe UI", 22, "bold"), fg="#0f172a", bg=AppConfig.UI.BG_COLOR)
        title_label.pack()
        ttk.Label(header_frame, text="Algorithme de Gale-Shapley avec satisfaction exponentielle", 
                 style="Subtitle.TLabel").pack()
        
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
                       font=(AppConfig.UI.BUTTON_FONT[0], 11, "bold"),
                       bg="#059669", fg=AppConfig.UI.WHITE,
                       activebackground="#047857", activeforeground=AppConfig.UI.WHITE,
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
        self.notebook.add(config_frame, text="CONFIGURATION")
        
        card = ttk.Frame(config_frame, style="Card.TFrame", padding=30)
        card.pack(fill="both", expand=True)
        
        ttk.Label(card, text="PARAMÈTRES DE SIMULATION", 
                 font=(AppConfig.UI.BUTTON_FONT[0], 14, "bold"),
                 foreground="#0f172a", background=AppConfig.UI.WHITE).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 20))
        
        # Nombre d'étudiants
        row = 1
        ttk.Label(card, text="Nombre d'étudiants:", font=(AppConfig.UI.TEXT_FONT[0], 11, "bold"), 
                 foreground="#334155", background=AppConfig.UI.WHITE).grid(row=row, column=0, sticky="w", pady=10, padx=(0, 20))
        self.nb_students_var = tk.IntVar(value=AppConfig.UI.DEFAULT_NB_STUDENTS)
        ttk.Spinbox(card, from_=1, to=100, textvariable=self.nb_students_var, width=15).grid(
            row=row, column=1, sticky="w", pady=10)
        self.students_info = ttk.Label(card, text="", font=AppConfig.UI.SMALL_FONT, 
                                       foreground=AppConfig.UI.GRAY, background=AppConfig.UI.WHITE)
        self.students_info.grid(row=row, column=2, sticky="w", padx=10)
        
        # Nombre d'universités
        row += 1
        ttk.Label(card, text="Nombre d'universités:", font=(AppConfig.UI.TEXT_FONT[0], 11, "bold"), 
                 foreground="#334155", background=AppConfig.UI.WHITE).grid(row=row, column=0, sticky="w", pady=10, padx=(0, 20))
        self.nb_universities_var = tk.IntVar(value=AppConfig.UI.DEFAULT_NB_UNIVERSITIES)
        ttk.Spinbox(card, from_=1, to=100, textvariable=self.nb_universities_var, width=15).grid(
            row=row, column=1, sticky="w", pady=10)
        self.universities_info = ttk.Label(card, text="", font=AppConfig.UI.SMALL_FONT, 
                                          foreground=AppConfig.UI.GRAY, background=AppConfig.UI.WHITE)
        self.universities_info.grid(row=row, column=2, sticky="w", padx=10)
        
        # Séparateur
        row += 1
        ttk.Separator(card, orient="horizontal").grid(row=row, column=0, columnspan=3, sticky="ew", pady=20)
        
        # Paramètre Alpha
        row += 1
        ttk.Label(card, text="Satisfaction étudiants (α):", font=(AppConfig.UI.TEXT_FONT[0], 11, "bold"), 
                 foreground="#334155", background=AppConfig.UI.WHITE).grid(row=row, column=0, sticky="w", pady=10, padx=(0, 20))
        
        self.alpha_var = tk.StringVar(value="flexible")
        alpha_frame = ttk.Frame(card, style="Card.TFrame")
        alpha_frame.grid(row=row, column=1, columnspan=2, sticky="w", pady=10)
        
        for i, (name, value) in enumerate(AppConfig.ALPHA.get_all().items()):
            ttk.Radiobutton(alpha_frame, text=f"{name.capitalize()} (α={value})", 
                           variable=self.alpha_var, value=name).pack(anchor="w", pady=2)
        
        # Description
        row += 1
        desc_frame = ttk.Frame(card, style="Card.TFrame")
        desc_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(20, 0))
        
        ttk.Label(desc_frame, 
                 text="ℹ️ Le paramètre α contrôle la satisfaction exponentielle. Plus α est élevé, plus les étudiants préfèrent leurs premiers choix.",
                 font=AppConfig.UI.SMALL_FONT, foreground=AppConfig.UI.GRAY, background=AppConfig.UI.WHITE,
                 wraplength=700, justify="left").pack(anchor="w")
        
        # Bouton
        row += 1
        button_frame = ttk.Frame(card, style="Card.TFrame")
        button_frame.grid(row=row, column=0, columnspan=3, pady=(30, 0))
        
        self.run_button = tk.Button(button_frame, text="LANCER LA SIMULATION", 
                                    font=(AppConfig.UI.BUTTON_FONT[0], 12, "bold"),
                                    bg="#16a34a", fg=AppConfig.UI.WHITE, 
                                    activebackground="#15803d", activeforeground=AppConfig.UI.WHITE,
                                    cursor="hand2", relief="flat", padx=40, pady=18,
                                    borderwidth=0, highlightthickness=0,
                                    command=self.run_simulation)
        self.run_button.pack()
        
        # Status
        self.status_label = ttk.Label(card, text="", font=AppConfig.UI.TEXT_FONT, 
                                     foreground=AppConfig.UI.SECONDARY_COLOR, background=AppConfig.UI.WHITE)
        self.status_label.grid(row=row+1, column=0, columnspan=3, pady=(10, 0))
    
    def create_results_tab(self):
        """Crée l'onglet de résultats."""
        results_frame = ttk.Frame(self.notebook, style="Modern.TFrame", padding=20)
        self.notebook.add(results_frame, text="VUE D'ENSEMBLE")
        
        # Container pour le contenu
        content_frame = ttk.Frame(results_frame, style="Modern.TFrame")
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        cards_container = ttk.Frame(content_frame, style="Modern.TFrame")
        cards_container.pack(fill="both", expand=True)
        
        # Statistiques globales
        stats_card = ttk.Frame(cards_container, style="Card.TFrame", padding=20)
        stats_card.pack(fill="x", pady=(0, 15))
        
        ttk.Label(stats_card, text="STATISTIQUES GLOBALES", 
                 font=(AppConfig.UI.BUTTON_FONT[0], 14, "bold"),
                 foreground="#0f172a", background=AppConfig.UI.WHITE).pack(
            anchor="w", pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_card, style="Card.TFrame")
        stats_grid.pack(fill="x")
        
        self.stat_labels = {}
        stats_info = [
            ("students", "Étudiants", "0"),
            ("universities", "Universités", "0"),
            ("assigned", "Affectés", "0 / 0"),
            ("unassigned", "Non affectés", "0"),
            ("avg_students", "Satisf. Moy. Étudiants", "0%"),
            ("avg_universities", "Satisf. Moy. Universités", "0%"),
        ]
        
        for i, (key, label, default) in enumerate(stats_info):
            row, col = i // 3, (i % 3) * 2
            ttk.Label(stats_grid, text=label + ":", font=AppConfig.UI.TEXT_FONT, 
                     background=AppConfig.UI.WHITE).grid(row=row, column=col, sticky="w", padx=10, pady=8)
            self.stat_labels[key] = ttk.Label(stats_grid, text=default, 
                                             font=(AppConfig.UI.BUTTON_FONT[0], 10, "bold"), 
                                             foreground=AppConfig.UI.PRIMARY_COLOR, background=AppConfig.UI.WHITE)
            self.stat_labels[key].grid(row=row, column=col+1, sticky="w", padx=10, pady=8)
        
        # Préférences - deux tableaux côte à côte
        prefs_card = ttk.Frame(cards_container, style="Card.TFrame", padding=20)
        prefs_card.pack(fill="both", expand=True)
        
        ttk.Label(prefs_card, text="PRÉFÉRENCES ET PRIORITÉS", 
                 font=(AppConfig.UI.BUTTON_FONT[0], 14, "bold"),
                 foreground="#0f172a", background=AppConfig.UI.WHITE).pack(anchor="w", pady=(0, 15))
        
        columns_frame = ttk.Frame(prefs_card, style="Card.TFrame")
        columns_frame.pack(fill="both", expand=True)
        
        # Préférences étudiants (gauche)
        left_frame = ttk.Frame(columns_frame, style="Card.TFrame")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Choix des Étudiants", 
                 font=(AppConfig.UI.BUTTON_FONT[0], 11, "bold"),
                 foreground="#1e40af", background=AppConfig.UI.WHITE).pack(anchor="w", pady=(0, 8))
        
        self.students_prefs_tree = self.create_tree(
            left_frame,
            columns=("num", "name", "prefs"),
            headings=("#", "Étudiant", "Choix"),
            widths=(40, 150, 1200)
        )
        
        # Priorités universités (droite)
        right_frame = ttk.Frame(columns_frame, style="Card.TFrame")
        right_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        ttk.Label(right_frame, text="Priorités des Universités", 
                 font=(AppConfig.UI.BUTTON_FONT[0], 11, "bold"),
                 foreground="#1e40af", background=AppConfig.UI.WHITE).pack(anchor="w", pady=(0, 8))
        
        self.universities_prefs_tree = self.create_tree(
            right_frame,
            columns=("num", "name", "prefs"),
            headings=("#", "Université", "Priorités"),
            widths=(40, 250, 1200)
        )
        
        # Ajouter le bouton de nouvelle simulation
        self.add_new_simulation_button(results_frame)
    
    def create_students_tab(self):
        """Crée l'onglet étudiants."""
        students_frame = ttk.Frame(self.notebook, style="Modern.TFrame", padding=20)
        self.notebook.add(students_frame, text="ÉTUDIANTS")
        
        content_frame = ttk.Frame(students_frame, style="Modern.TFrame")
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        card = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)
        
        ttk.Label(card, text="TOUS LES ÉTUDIANTS", 
                 font=(AppConfig.UI.BUTTON_FONT[0], 14, "bold"),
                 foreground="#0f172a", background=AppConfig.UI.WHITE).pack(anchor="w", pady=(0, 15))
        
        self.students_tree = self.create_tree(
            card,
            columns=("name", "university", "wish", "satisfaction"),
            headings=("Étudiant", "Université affectée", "Vœu", "Satisfaction"),
            widths=(220, 350, 80, 120)
        )
        
        # Ajouter le bouton de nouvelle simulation
        self.add_new_simulation_button(students_frame)
    
    def create_universities_tab(self):
        """Crée l'onglet universités."""
        universities_frame = ttk.Frame(self.notebook, style="Modern.TFrame", padding=20)
        self.notebook.add(universities_frame, text="UNIVERSITÉS")
        
        content_frame = ttk.Frame(universities_frame, style="Modern.TFrame")
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        card = ttk.Frame(content_frame, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)
        
        ttk.Label(card, text="TOUTES LES UNIVERSITÉS", 
                 font=(AppConfig.UI.BUTTON_FONT[0], 14, "bold"),
                 foreground="#0f172a", background=AppConfig.UI.WHITE).pack(anchor="w", pady=(0, 15))
        
        self.universities_tree = self.create_tree(
            card,
            columns=("name", "capacity", "assigned", "satisfaction", "students"),
            headings=("Université", "Capacité", "Affectés", "Satisfaction", "Étudiants"),
            widths=(300, 80, 80, 120, 380)
        )
        
        # Ajouter le bouton de nouvelle simulation
        self.add_new_simulation_button(universities_frame)
    
    def create_assignments_tab(self):
        """Crée l'onglet affectations détaillées."""
        assignments_frame = ttk.Frame(self.notebook, style="Modern.TFrame", padding=20)
        self.notebook.add(assignments_frame, text="AFFECTATIONS")
        
        card = ttk.Frame(assignments_frame, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)
        
        ttk.Label(card, text="AFFECTATIONS DÉTAILLÉES", 
                 font=(AppConfig.UI.BUTTON_FONT[0], 14, "bold"),
                 foreground="#0f172a", background=AppConfig.UI.WHITE).pack(anchor="w", pady=(0, 15))
        
        self.assignments_tree = self.create_tree(
            card,
            columns=("university", "student", "wish", "priority"),
            headings=("Université", "Étudiant", "Vœu étudiant", "Priorité université"),
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
        tree.tag_configure('evenrow', background=AppConfig.UI.WHITE)
        
        return tree
    
    def load_data(self):
        """Charge les données depuis les CSV."""
        try:
            self.all_students = load_students_from_csv(AppConfig.DATA.STUDENTS_CSV)
            self.all_universities = load_universities_from_csv(AppConfig.DATA.UNIVERSITIES_CSV)
            
            self.students_info.config(text=f"({len(self.all_students)} disponibles)")
            self.universities_info.config(text=f"({len(self.all_universities)} disponibles)")
            
            if self.all_students:
                self.nb_students_var.set(min(AppConfig.UI.DEFAULT_NB_STUDENTS, len(self.all_students)))
            if self.all_universities:
                self.nb_universities_var.set(min(AppConfig.UI.DEFAULT_NB_UNIVERSITIES, len(self.all_universities)))
                
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
            alpha_map = AppConfig.ALPHA.get_all()
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
