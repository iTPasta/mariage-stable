"""Modèles de données pour le système d'affectation."""
from dataclasses import dataclass
from typing import Dict, List


StudentKey = str       # full_name de l'étudiant
UniversityKey = str    # name de l'université


@dataclass(frozen=True)
class Student:
    """Représentation d'un étudiant."""
    full_name: str

    def __str__(self) -> str:
        return self.full_name


@dataclass(frozen=True)
class University:
    """Représentation d'une université."""
    name: str
    capacity: int = 1

    def __str__(self) -> str:
        return self.name


@dataclass
class SimulationData:
    """Conteneur pour toutes les données de simulation."""
    students: List[Student]
    universities: List[University]
    preferences_students: Dict[StudentKey, List[UniversityKey]]
    preferences_universities: Dict[UniversityKey, List[StudentKey]]
    assignments: Dict[UniversityKey, List[StudentKey]]
    satisfaction_stats: Dict
    
    @property
    def capacities(self) -> Dict[UniversityKey, int]:
        """Retourne les capacités des universités."""
        return {u.name: u.capacity for u in self.universities}
    
    @property
    def assignment_map(self) -> Dict[StudentKey, UniversityKey]:
        """Retourne un mapping étudiant -> université."""
        mapping = {}
        for uni_name, students_list in self.assignments.items():
            for student_name in students_list:
                mapping[student_name] = uni_name
        return mapping
