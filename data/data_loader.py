"""Chargement des données depuis les fichiers CSV."""
import csv
from typing import List

from models import Student, University


def load_students_from_csv(path: str) -> List[Student]:
    """
    Charge les étudiants depuis un fichier CSV.
    
    Format attendu:
        full_name
        Jean Martin
        Marie Dubois
        ...
    
    Args:
        path: Chemin vers le fichier CSV des étudiants
        
    Returns:
        Liste des étudiants chargés
    """
    students: List[Student] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            full_name = row.get("full_name", "").strip()
            if full_name:
                students.append(Student(full_name=full_name))
    return students


def load_universities_from_csv(path: str) -> List[University]:
    """
    Charge les universités depuis un fichier CSV.
    
    Format attendu:
        name
        Sorbonne Université
        Université Paris-Saclay
        ...
    
    Note: La capacité est fixée à 1 par défaut pour chaque université.
    
    Args:
        path: Chemin vers le fichier CSV des universités
        
    Returns:
        Liste des universités chargées
    """
    universities: List[University] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            if name:
                universities.append(University(name=name, capacity=1))
    return universities
