# models.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Student:
    """
    Représentation d'un étudiant.
    """
    full_name: str

    def __str__(self) -> str:
        return self.full_name


@dataclass(frozen=True)
class University:
    """
    Représentation d'une université.
    """
    name: str
    capacity: int = 1

    def __str__(self) -> str:
        return self.name
