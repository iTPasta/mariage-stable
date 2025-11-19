# data_loader.py
import csv
import random
from typing import List
from models import Student, University


def load_students_from_csv(path: str) -> List[Student]:
    """
    Charge les étudiants depuis un CSV.
    Format :
        full_name
        Jean Martin
        Marie Dubois
        ...

    La première ligne est considérée comme un header.
    """
    students: List[Student] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            full_name = row.get("full_name")
            if not full_name:
                continue
            full_name = full_name.strip()
            if full_name:
                students.append(Student(full_name=full_name))
    return students


def load_universities_from_csv(path: str) -> List[University]:
    """
    Charge les universités depuis un CSV.
    Format :
        name,capacity
        Sorbonne Université,1
        Université Paris-Saclay,1
        ...

    capacity est optionnelle (1 par défaut si vide).
    """
    universities: List[University] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name")
            if not name:
                continue
            name = name.strip()
            if not name:
                continue

            cap_str = (row.get("capacity") or "").strip()
            capacity = int(cap_str) if cap_str.isdigit() else 1
            universities.append(University(name=name, capacity=capacity))
    return universities


# ====== Fonctions de génération aléatoire (pour tests) ======

def generate_random_universities(nb_universites: int = 5) -> List[University]:
    universites_fr = [
        "Sorbonne Université", "Université Paris-Saclay", "Université PSL",
        "Université de Lyon", "Université Aix-Marseille", "Université de Bordeaux",
        "Université de Strasbourg", "Université de Lille", "Université de Montpellier",
        "Université de Toulouse", "Université de Nantes", "Université Grenoble Alpes",
        "Université de Rennes", "Université Côte d'Azur", "Université de Reims",
        "Université de Poitiers", "Université de Caen", "Université de Dijon",
        "Université de Limoges", "Université de Toulon"
    ]
    noms = random.sample(universites_fr, min(nb_universites, len(universites_fr)))
    random.shuffle(noms)

    universities: List[University] = []
    for name in noms:
        universities.append(University(name=name, capacity=1))
    return universities


def generate_random_students(nb_etudiants: int = 5) -> List[Student]:
    prenoms = ["Jean", "Marie", "Pierre", "Sophie", "Luc", "Anne", "Paul", "Claire",
               "Thomas", "Julie", "Antoine", "Camille", "Nicolas", "Laura", "David", "Sarah"]
    noms = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard",
            "Petit", "Durand", "Leroy", "Moreau", "Simon", "Laurent"]

    students: List[Student] = []
    for _ in range(nb_etudiants):
        full_name = f"{random.choice(prenoms)} {random.choice(noms)}"
        students.append(Student(full_name=full_name))
    return students
